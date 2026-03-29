# CLAUDE_CODE_HANDOFF.md

## Context for Claude Code

This project was designed and partially built in a claude.ai conversation. The backend (FastAPI + SQLite) and printer module (ESC/POS + mock mode) are complete and tested. The remaining sections need to be built.

The user is David, a Business Change Manager at Elevance Health who does freelance AI annotation work on the side. He is completing a BS in Applied AI. He uses Python primarily, prefers casual/direct communication, and hates em dashes (use commas, semicolons, or periods instead). He prefers working section by section rather than receiving everything at once.

## Hardware

- **Printer**: NetumScan 8360 USB POS Receipt Printer, 80mm, ESC/POS compatible, auto-cutter. Arriving tomorrow (March 29, 2026). Until then, use PRINTER_MODE=mock.
- **Workstation**: AMD Ryzen 9 9950X, RTX 5080, Windows (primary dev machine)

## What's Done (Sections 1-3)

1. **Database layer** (`app/database.py`): SQLite with WAL, full CRUD, sorting by priority/due_date/category/sort_order, archiving, bulk reorder, batch print stamping.
2. **Pydantic models** (`app/models.py`): Request/response validation for all endpoints.
3. **FastAPI app** (`main.py`): REST endpoints including quick-add (query params for phone shortcuts), individual ticket print/preview, daily ticket print/preview, stats with overdue detection. Auto-loads `.env` via python-dotenv.
4. **Printer module** (`app/printer.py`): Individual ticket formatting (one task per receipt, auto-cutter between each). ASCII art icons per category (work=monitor, school=building, personal=house) and Lisa heart. Live dad jokes from icanhazdadjoke.com API, live fun facts from uselessfacts.jsph.pl API. Static lists as offline fallback. Mock mode saves to files, live mode sends to USB via python-escpos.
5. **React Dashboard** (`frontend/` builds to `static/`): Vite + React + Tailwind CSS v4 + @dnd-kit. Dark mode, responsive grid (1/2/3 col). Task tiles with category color borders, priority badges, overdue red ring, FROM LISA tag, drag-and-drop reorder. Filter by category, sort by manual/priority/due date/category. Add task form, edit modal, archive view with restore. Multi-select with bulk archive/print. Receipt preview side panel (thermal paper aesthetic). Print All, Print Selected, Daily Ticket buttons. Stats bar with open/overdue/archived counts. PWA manifest for home screen install.

## What Needs to Be Built

### Section 4: Lisa's Portal + HTTP Shortcut Config

**Lisa's Portal** (`/lisa` route, `static/lisa.html`):
- Simple, clean page with just a task submission form
- Fields: title, priority (default: high), optional note
- Source is auto-set to "lisa"
- Category could default to "personal" or let her pick
- Confirmation message after submit
- Should feel distinct from the main dashboard (it's her thing)
- Accessible from her phone via bookmark

**HTTP Shortcuts (Android):**
- Provide config instructions for the HTTP Shortcuts app (free on Play Store)
- One-tap shortcut that pops a text input dialog
- Sends POST to /api/quick-add with the task title
- Can configure multiple shortcuts: "Quick Personal", "Quick Work", "Quick School"
- Document the URL format and params

### Section 5: Daily Scheduled Print

- A script (`daily_print.py` or similar) that:
  - Fetches all open tasks sorted by priority
  - Formats and prints the morning briefing receipt
  - Includes the Ticket of the Day (joke + fun fact)
  - Could include weather for Florida City, FL (via free weather API)
  - Could include today's Google Calendar events (future)
- Setup instructions for:
  - Windows Task Scheduler (for the workstation)
  - cron (if migrated to Raspberry Pi later)
- Configurable print time (default: 7:00 AM)

### Section 6: Calendar Integration

- Google Calendar API integration
- Pull today's events and display them on the morning ticket
- Optionally create calendar events from tasks that have due dates
- Skylight Calendar: no public API, but syncs from Google Calendar, so Google Calendar is the source of truth
- This section can be deferred; it's a nice-to-have

## Design Preferences

- Dark mode dashboard preferred
- Receipt preview should look like actual thermal receipt paper (off-white background, monospace font, slight shadow)
- Category colors: Work = blue tones, School = green/teal tones, Personal = warm/orange tones
- Priority indicators: High = red, Medium = yellow/amber, Low = gray
- Clean, functional, not over-designed. Think "productivity tool" not "design showcase"
- No em dashes anywhere in UI text or code comments

## Running the Project

```bash
cd todo-printer
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# API docs at http://localhost:8000/docs
# Dashboard at http://localhost:8000/ (once built)
# Lisa's portal at http://localhost:8000/lisa (once built)
```

## Environment Variables

```
PRINTER_MODE=mock          # mock or live
PRINTER_VENDOR=0x0000      # USB vendor ID (live mode)
PRINTER_PRODUCT=0x0000     # USB product ID (live mode)
TODO_DB_PATH=todos.db      # SQLite database path
MOCK_PRINT_DIR=mock_prints # Where mock receipts are saved
```
