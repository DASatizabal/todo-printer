"""
Supabase Remote Task Sync
Pulls unsynced tasks from the remote_tasks table in Supabase
and creates them in the local SQLite database.
"""

import os
import httpx
from app.database import create_task

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


def mark_synced(remote_ids: list[str]) -> None:
    """Mark remote_tasks rows as synced=true."""
    if not remote_ids:
        return

    id_filter = ",".join(remote_ids)
    httpx.patch(
        _rest_url("remote_tasks"),
        headers={**_headers(), "Prefer": "return=minimal"},
        params={"id": f"in.({id_filter})"},
        json={"synced": True},
        timeout=TIMEOUT,
    )


def sync_remote_tasks() -> dict:
    """
    Pull unsynced tasks from Supabase, create them locally, mark as synced.
    Returns a summary of what was synced.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"synced": 0, "errors": ["SUPABASE_URL or SUPABASE_ANON_KEY not set"]}

    pending = fetch_unsynced_tasks()
    if not pending:
        return {"synced": 0, "errors": []}

    synced_ids = []
    created = []
    errors = []

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
            )
            synced_ids.append(row["id"])
            created.append(task)
        except Exception as e:
            errors.append(f"Failed to create '{row.get('title')}': {str(e)}")

    if synced_ids:
        mark_synced(synced_ids)

    return {
        "synced": len(synced_ids),
        "errors": errors,
        "tasks": created,
    }
