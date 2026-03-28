# Todo Printer

A thermal receipt printer to-do list system. Add tasks from your phone, manage them on a dashboard, and print them as physical "tickets" on a receipt printer. Stab completed tickets on a receipt spike for maximum satisfaction.

## Architecture

```
[Android Phone] ──> HTTP Shortcuts app ──> FastAPI ──> SQLite
[Lisa's Phone]  ──> /lisa portal ────────>    |
[PC Browser]    ──> React Dashboard ─────>    |
                                              v
                                     NetumScan 8360
                                   (USB thermal printer)
```

## Tech Stack

| Layer            | Tech                  | Status      |
|------------------|-----------------------|-------------|
| Backend API      | FastAPI (Python)      | DONE        |
| Database         | SQLite (WAL mode)     | DONE        |
| Printer          | python-escpos + mock  | DONE        |
| React Dashboard  | React JSX (PWA)       | TODO        |
| Lisa's Portal    | Lightweight HTML page | TODO        |
| Phone Quick-Add  | HTTP Shortcuts app    | TODO        |
| Daily Print      | Scheduled task/cron   | TODO        |
| Calendar Sync    | Google Calendar API   | TODO        |

## Setup

### Prerequisites
- Python 3.10+
- Node.js (for React dashboard, later)
- NetumScan 8360 USB receipt printer (optional, mock mode works without it)

### Install & Run

```bash
cd todo-printer
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Open API docs at http://localhost:8000/docs
```

### Printer Configuration

The printer runs in **mock mode** by default (saves receipts to `mock_prints/` folder).

To switch to live printing, set these environment variables:

```bash
# Find your printer's USB IDs:
lsusb
# Look for something like: Bus 001 Device 005: ID 0416:5011 NetumScan

# Then set:
export PRINTER_MODE=live
export PRINTER_VENDOR=0x0416
export PRINTER_PRODUCT=0x5011
```

On Windows, use the Device Manager or `python -m escpos.cli` to find the IDs.

## API Endpoints

### Tasks CRUD
- `GET    /api/tasks`              - List tasks (query: status, category, sort_by)
- `POST   /api/tasks`              - Create task (JSON body)
- `GET    /api/tasks/{id}`         - Get single task
- `PATCH  /api/tasks/{id}`         - Update task fields
- `POST   /api/tasks/{id}/archive` - Complete/archive a task
- `POST   /api/tasks/{id}/restore` - Restore archived task
- `DELETE /api/tasks/{id}`         - Permanently delete

### Bulk Operations
- `POST /api/tasks/reorder`        - Drag-and-drop reorder (body: task_ids list)

### Printing
- `POST /api/print`                - Print tasks (body: task_ids, category, or all_open)
- `POST /api/print/preview`        - Preview receipt without printing

### Quick Add (for phone shortcuts)
- `POST /api/quick-add?title=...&category=...&priority=...&source=...`

### Dashboard
- `GET  /api/stats`                - Summary stats with overdue detection
- `GET  /`                         - Serve dashboard (once built)
- `GET  /lisa`                     - Serve Lisa's portal (once built)

## Task Schema

| Field       | Type    | Values                          | Default    |
|-------------|---------|---------------------------------|------------|
| title       | string  |                                 | (required) |
| category    | string  | work, school, personal          | personal   |
| priority    | int     | 1 (high), 2 (medium), 3 (low)  | 2          |
| due_date    | string  | ISO date: "2026-03-30"          | null       |
| due_time    | string  | "14:30"                         | null       |
| source      | string  | self, lisa, calendar            | self       |
| notes       | string  |                                 | null       |
| sort_order  | int     | (auto-managed)                  | auto       |
| status      | string  | open, archived                  | open       |

## Receipt Format

Each receipt includes:
- Date/time header
- Tasks grouped by category (Work/School/Personal) with distinct borders
- Priority markers (>>> for high priority)
- Overdue flags
- Source tags ([FROM LISA])
- Summary with overdue count
- "Ticket of the Day" (rotating dad joke + fun fact)
- Auto-cut trigger (live mode)

## Project Structure

```
todo-printer/
  main.py              # FastAPI app, all endpoints
  requirements.txt     # Python dependencies
  app/
    __init__.py
    database.py        # SQLite schema + CRUD helpers
    models.py          # Pydantic request/response models
    printer.py         # Receipt formatter + mock/live printer
  static/              # Dashboard files (TODO)
  templates/           # Server-rendered pages (TODO)
```
