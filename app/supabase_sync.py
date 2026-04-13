"""
Supabase Remote Task Sync
Pulls unsynced tasks from the remote_tasks table in Supabase,
creates them in the local SQLite database, and pushes local
status updates back to Supabase for Lisa's dashboard.
"""

import os
import httpx
from app.database import create_task, list_remote_tasks, get_connection, mark_printed

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
TIMEOUT = 10


def _headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


def _rest_url(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"


def fetch_unsynced_tasks() -> list[dict]:
    """Fetch all rows from remote_tasks where synced=false."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []

    response = httpx.get(
        _rest_url("remote_tasks"),
        headers=_headers(),
        params={
            "synced": "eq.false",
            "order": "created_at.asc",
        },
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def mark_synced(remote_ids: list[str], local_status: str = "open") -> None:
    """Mark remote_tasks rows as synced and set local_status."""
    if not remote_ids:
        return

    id_filter = ",".join(remote_ids)
    httpx.patch(
        _rest_url("remote_tasks"),
        headers={**_headers(), "Prefer": "return=minimal"},
        params={"id": f"in.({id_filter})"},
        json={"synced": True, "local_status": local_status},
        timeout=TIMEOUT,
    )


def backfill_remote_ids() -> int:
    """Link local tasks to Supabase rows that were synced before remote_id tracking."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return 0

    # Find Supabase rows that are synced but have no local_status (orphaned)
    response = httpx.get(
        _rest_url("remote_tasks"),
        headers=_headers(),
        params={"synced": "eq.true", "local_status": "is.null", "select": "id,title"},
        timeout=TIMEOUT,
    )
    if response.status_code != 200:
        return 0

    orphans = response.json()
    if not orphans:
        return 0

    conn = get_connection()
    linked = 0
    try:
        for row in orphans:
            local = conn.execute(
                "SELECT id FROM tasks WHERE title = ? AND remote_id IS NULL",
                (row["title"],),
            ).fetchone()
            if local:
                conn.execute(
                    "UPDATE tasks SET remote_id = ? WHERE id = ?",
                    (row["id"], local["id"]),
                )
                linked += 1
        conn.commit()
    finally:
        conn.close()
    return linked


def push_status_updates() -> dict:
    """Push local task status back to Supabase for Lisa's dashboard."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"updated": 0}

    # Auto-link any orphaned tasks first
    backfill_remote_ids()

    tasks = list_remote_tasks()
    if not tasks:
        return {"updated": 0}

    updated = 0
    for task in tasks:
        update_data = {"local_status": task["status"]}
        if task.get("printed_at"):
            update_data["printed_at"] = task["printed_at"]
        if task.get("archived_at"):
            update_data["archived_at"] = task["archived_at"]

        try:
            httpx.patch(
                _rest_url("remote_tasks"),
                headers={**_headers(), "Prefer": "return=minimal"},
                params={"id": f"eq.{task['remote_id']}"},
                json=update_data,
                timeout=TIMEOUT,
            )
            updated += 1
        except Exception:
            pass

    return {"updated": updated}


def sync_remote_tasks() -> dict:
    """
    Pull unsynced tasks from Supabase, create them locally, mark as synced.
    Also pushes status updates back for previously synced tasks.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"synced": 0, "status_pushed": 0, "errors": ["SUPABASE_URL or SUPABASE_ANON_KEY not set"]}

    # Pull new tasks
    pending = fetch_unsynced_tasks()
    synced_ids = []
    created = []
    errors = []

    printed_ids = []

    for row in pending:
        try:
            task = create_task(
                title=row["title"],
                category=row.get("category", "personal"),
                priority=row.get("priority", 2),
                due_date=row.get("due_date"),
                due_time=row.get("due_time"),
                source=row.get("source", "lisa"),
                notes=row.get("notes"),
                remote_id=row["id"],
            )
            synced_ids.append(row["id"])
            created.append(task)

            # Auto quick-print Lisa's tasks or tasks with quick_print flag
            if row.get("source", "lisa") == "lisa" or row.get("quick_print"):
                try:
                    from app.printer import format_ticket, print_tickets
                    ticket = format_ticket(task, ticket_num=1, total=1)
                    print_tickets([ticket])
                    printed_ids.append(task["id"])
                except Exception:
                    pass  # print failure shouldn't block sync
        except Exception as e:
            errors.append(f"Failed to create '{row.get('title')}': {str(e)}")

    if printed_ids:
        mark_printed(printed_ids)

    if synced_ids:
        mark_synced(synced_ids)

    # Push status updates for previously synced tasks
    push_result = push_status_updates()

    return {
        "synced": len(synced_ids),
        "status_pushed": push_result["updated"],
        "errors": errors,
        "tasks": created,
    }
