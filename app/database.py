"""
Todo Printer - Database Layer
SQLite database with tasks table supporting priorities, categories, due dates, and ordering.
"""

import sqlite3
import os
from datetime import datetime, timezone
from contextlib import contextmanager

DB_PATH = os.environ.get("TODO_DB_PATH", "todos.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'personal'
                    CHECK (category IN ('work', 'school', 'personal')),
                priority INTEGER NOT NULL DEFAULT 2
                    CHECK (priority IN (1, 2, 3)),
                due_date TEXT,
                due_time TEXT,
                sort_order INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'archived')),
                source TEXT NOT NULL DEFAULT 'self'
                    CHECK (source IN ('self', 'lisa', 'calendar')),
                notes TEXT,
                created_at TEXT NOT NULL,
                archived_at TEXT,
                printed_at TEXT
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_category
            ON tasks(category)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_priority
            ON tasks(priority, due_date)
        """)

        # Migration: add remote_id for Supabase sync tracking
        try:
            conn.execute("ALTER TABLE tasks ADD COLUMN remote_id TEXT")
        except Exception:
            pass  # Column already exists


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# CRUD Operations
# ---------------------------------------------------------------------------

def create_task(
    title: str,
    category: str = "personal",
    priority: int = 2,
    due_date: str = None,
    due_time: str = None,
    source: str = "self",
    notes: str = None,
    remote_id: str = None,
) -> dict:
    """Insert a new task and return it as a dict."""
    with get_db() as conn:
        # New tasks get sort_order = max + 1 so they land at the bottom
        row = conn.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM tasks WHERE status = 'open'").fetchone()
        next_order = row[0]

        cursor = conn.execute(
            """
            INSERT INTO tasks (title, category, priority, due_date, due_time,
                               sort_order, source, notes, created_at, remote_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, category, priority, due_date, due_time,
             next_order, source, notes, now_iso(), remote_id),
        )
        # Read from same connection before commit
        result = conn.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return dict(result)


def get_task(task_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def list_tasks(
    status: str = "open",
    category: str = None,
    sort_by: str = "sort_order",
) -> list[dict]:
    """
    List tasks with optional filters.
    sort_by options: 'sort_order', 'priority', 'due_date', 'category'
    """
    query = "SELECT * FROM tasks WHERE status = ?"
    params: list = [status]

    if category:
        query += " AND category = ?"
        params.append(category)

    order_map = {
        "sort_order": "sort_order ASC",
        "priority": "priority ASC, due_date ASC NULLS LAST, sort_order ASC",
        "due_date": "due_date ASC NULLS LAST, priority ASC, sort_order ASC",
        "category": "category ASC, priority ASC, sort_order ASC",
    }
    query += f" ORDER BY {order_map.get(sort_by, 'sort_order ASC')}"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def update_task(task_id: int, **kwargs) -> dict | None:
    """Update specific fields on a task. Only provided kwargs are updated."""
    allowed = {
        "title", "category", "priority", "due_date", "due_time",
        "sort_order", "status", "notes", "printed_at", "archived_at",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return get_task(task_id)

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [task_id]

    with get_db() as conn:
        conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
        result = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(result) if result else None


def archive_task(task_id: int) -> dict | None:
    return update_task(task_id, status="archived", archived_at=now_iso())


def reorder_tasks(task_ids: list[int]) -> None:
    """Bulk update sort_order based on the list position (index = new order)."""
    with get_db() as conn:
        for order, tid in enumerate(task_ids):
            conn.execute(
                "UPDATE tasks SET sort_order = ? WHERE id = ?",
                (order, tid),
            )


def delete_task(task_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def mark_printed(task_ids: list[int]) -> None:
    """Stamp printed_at on a batch of tasks."""
    ts = now_iso()
    with get_db() as conn:
        placeholders = ",".join("?" * len(task_ids))
        conn.execute(
            f"UPDATE tasks SET printed_at = ? WHERE id IN ({placeholders})",
            [ts] + task_ids,
        )


def list_unprinted_tasks(category: str = None, sort_by: str = "priority") -> list[dict]:
    """List open tasks that have not been printed yet."""
    query = "SELECT * FROM tasks WHERE status = 'open' AND printed_at IS NULL"
    params: list = []

    if category:
        query += " AND category = ?"
        params.append(category)

    order_map = {
        "sort_order": "sort_order ASC",
        "priority": "priority ASC, due_date ASC NULLS LAST, sort_order ASC",
        "due_date": "due_date ASC NULLS LAST, priority ASC, sort_order ASC",
        "category": "category ASC, priority ASC, sort_order ASC",
    }
    query += f" ORDER BY {order_map.get(sort_by, 'priority ASC, due_date ASC NULLS LAST, sort_order ASC')}"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def list_remote_tasks() -> list[dict]:
    """List all tasks that originated from Supabase (have a remote_id)."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE remote_id IS NOT NULL"
        ).fetchall()
        return [dict(r) for r in rows]
