"""
Todo Printer - FastAPI Application
REST API for task management + thermal receipt printing.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import os

from app.database import (
    init_db, create_task, get_task, list_tasks,
    update_task, archive_task, reorder_tasks,
    delete_task, mark_printed,
)
from app.models import (
    TaskCreate, TaskUpdate, TaskResponse,
    ReorderRequest, PrintRequest,
)

app = FastAPI(title="Todo Printer", version="1.0.0")

# CORS - allow the dashboard and phone shortcuts to hit the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------

@app.get("/api/tasks", response_model=list[TaskResponse])
def api_list_tasks(
    status: str = Query("open", pattern="^(open|archived)$"),
    category: Optional[str] = Query(None, pattern="^(work|school|personal)$"),
    sort_by: str = Query("sort_order", pattern="^(sort_order|priority|due_date|category)$"),
):
    """List tasks with optional filters and sorting."""
    return list_tasks(status=status, category=category, sort_by=sort_by)


@app.post("/api/tasks", response_model=TaskResponse, status_code=201)
def api_create_task(task: TaskCreate):
    """Create a new task."""
    result = create_task(
        title=task.title,
        category=task.category.value,
        priority=task.priority.value,
        due_date=task.due_date,
        due_time=task.due_time,
        source=task.source.value,
        notes=task.notes,
    )
    return result


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def api_get_task(task_id: int):
    """Get a single task by ID."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/api/tasks/{task_id}", response_model=TaskResponse)
def api_update_task(task_id: int, updates: TaskUpdate):
    """Update specific fields on a task."""
    existing = get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = updates.model_dump(exclude_unset=True)
    # Convert enums to values
    for key in ("category", "priority"):
        if key in update_data and update_data[key] is not None:
            update_data[key] = update_data[key].value

    result = update_task(task_id, **update_data)
    return result


@app.post("/api/tasks/{task_id}/archive", response_model=TaskResponse)
def api_archive_task(task_id: int):
    """Archive (complete) a task."""
    existing = get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    return archive_task(task_id)


@app.post("/api/tasks/{task_id}/restore", response_model=TaskResponse)
def api_restore_task(task_id: int):
    """Restore an archived task back to open."""
    existing = get_task(task_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Task not found")
    return update_task(task_id, status="open", archived_at=None)


@app.delete("/api/tasks/{task_id}")
def api_delete_task(task_id: int):
    """Permanently delete a task."""
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"detail": "Task deleted"}


# ---------------------------------------------------------------------------
# Bulk Operations
# ---------------------------------------------------------------------------

@app.post("/api/tasks/reorder")
def api_reorder_tasks(req: ReorderRequest):
    """Reorder tasks via drag-and-drop. task_ids list = new order."""
    reorder_tasks(req.task_ids)
    return {"detail": "Reorder complete"}


# ---------------------------------------------------------------------------
# Print Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/print")
def api_print_tasks(req: PrintRequest):
    """
    Print tasks to the thermal receipt printer.
    Options:
      - task_ids: print specific tasks
      - category: print all open tasks in a category
      - all_open: print all open tasks
    """
    tasks = _resolve_print_tasks(req)

    from app.printer import format_receipt, print_receipt

    receipt_text = format_receipt(tasks)
    result = print_receipt(receipt_text)

    task_ids = [t["id"] for t in tasks]
    mark_printed(task_ids)

    return {
        "detail": f"Printed {len(tasks)} task(s)",
        "printer": result,
    }


@app.post("/api/print/preview")
def api_preview_receipt(req: PrintRequest):
    """Preview what the receipt would look like without printing."""
    tasks = _resolve_print_tasks(req)

    from app.printer import format_receipt
    receipt_text = format_receipt(tasks)

    return {
        "detail": f"Preview of {len(tasks)} task(s)",
        "preview": receipt_text,
    }


def _resolve_print_tasks(req: PrintRequest) -> list[dict]:
    """Resolve which tasks to print based on the request."""
    if req.all_open:
        tasks = list_tasks(status="open", sort_by="priority")
    elif req.category:
        tasks = list_tasks(status="open", category=req.category.value, sort_by="priority")
    elif req.task_ids:
        tasks = [get_task(tid) for tid in req.task_ids]
        tasks = [t for t in tasks if t is not None]
    else:
        raise HTTPException(status_code=400, detail="Specify task_ids, category, or all_open")

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks to print")
    return tasks


# ---------------------------------------------------------------------------
# Quick-Add (for HTTP Shortcuts / Lisa's portal)
# ---------------------------------------------------------------------------

@app.post("/api/quick-add", response_model=TaskResponse, status_code=201)
def api_quick_add(
    title: str = Query(..., min_length=1),
    category: str = Query("personal", pattern="^(work|school|personal)$"),
    priority: int = Query(2, ge=1, le=3),
    source: str = Query("self", pattern="^(self|lisa|calendar)$"),
    due_date: Optional[str] = Query(None),
    due_time: Optional[str] = Query(None),
):
    """
    Simplified endpoint for HTTP Shortcuts / quick add.
    Uses query params instead of JSON body for easy shortcut config.
    """
    result = create_task(
        title=title,
        category=category,
        priority=priority,
        source=source,
        due_date=due_date,
        due_time=due_time,
    )
    return result


# ---------------------------------------------------------------------------
# Dashboard Stats
# ---------------------------------------------------------------------------

@app.get("/api/stats")
def api_stats():
    """Dashboard summary stats."""
    open_tasks = list_tasks(status="open")
    archived_tasks = list_tasks(status="archived")

    from collections import Counter
    cats = Counter(t["category"] for t in open_tasks)
    pris = Counter(t["priority"] for t in open_tasks)

    overdue = []
    from datetime import date
    today = date.today().isoformat()
    for t in open_tasks:
        if t["due_date"] and t["due_date"] < today:
            overdue.append(t)

    return {
        "total_open": len(open_tasks),
        "total_archived": len(archived_tasks),
        "by_category": dict(cats),
        "by_priority": {str(k): v for k, v in pris.items()},
        "overdue_count": len(overdue),
        "overdue_tasks": overdue,
    }


# ---------------------------------------------------------------------------
# Serve Dashboard (static files)
# ---------------------------------------------------------------------------

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_dashboard():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Dashboard not yet built. API is running at /docs"}


@app.get("/lisa")
def serve_lisa_portal():
    lisa_path = os.path.join(STATIC_DIR, "lisa.html")
    if os.path.exists(lisa_path):
        return FileResponse(lisa_path)
    return {"detail": "Lisa's portal not yet built."}
