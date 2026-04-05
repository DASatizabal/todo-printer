"""
Daily Morning Briefing Print
Runs automatically via Windows Task Scheduler (or cron).

Prints:
1. Ticket of the Day (weather + joke + fun fact)
2. Individual tickets for all open tasks, sorted by priority

Usage:
  python daily_print.py              # print everything
  python daily_print.py --daily-only # just the Ticket of the Day
  python daily_print.py --preview    # preview without printing
"""

import sys
import os

# Load .env before any app imports
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from app.database import init_db, list_tasks, mark_printed
from app.printer import format_ticket, format_daily_ticket, print_tickets
from app.weather import fetch_weather
from app.supabase_sync import sync_remote_tasks


def main():
    preview_only = "--preview" in sys.argv
    daily_only = "--daily-only" in sys.argv

    # Initialize database
    init_db()

    # Sync any pending remote tasks first
    try:
        result = sync_remote_tasks()
        if result.get("synced", 0) > 0:
            print(f"Synced {result['synced']} remote task(s)")
        if result.get("status_pushed", 0) > 0:
            print(f"Pushed {result['status_pushed']} status update(s)")
    except Exception as e:
        print(f"Sync skipped: {e}")

    # Fetch weather
    weather = fetch_weather()
    if weather:
        print(f"Weather: {weather['condition']}, {weather['temp']}F (High {weather['high']}F / Low {weather['low']}F)")
    else:
        print("Weather: unavailable")

    # Build tickets
    tickets = []

    # Ticket of the Day always prints first
    tickets.append(format_daily_ticket(weather=weather))

    if not daily_only:
        # Get unprinted open tasks only
        all_open = list_tasks(status="open", sort_by="priority")
        tasks = [t for t in all_open if not t.get("printed_at")]
        print(f"Open tasks: {len(all_open)}, Unprinted: {len(tasks)}")

        for i, task in enumerate(tasks, 1):
            tickets.append(format_ticket(task, ticket_num=i, total=len(tasks)))

    # Print or preview
    if preview_only:
        print("\n" + "=" * 50 + " PREVIEW " + "=" * 50)
        print("\n".join(tickets))
    else:
        result = print_tickets(tickets)
        mode = result.get("mode", "unknown")
        status = result.get("status", "unknown")
        count = result.get("count", len(tickets))
        print(f"Printed {count} ticket(s) [{mode}/{status}]")

        if status == "error":
            print(f"Error: {result.get('error', 'unknown')}")
            sys.exit(1)

        # Mark tasks as printed
        if not daily_only and tasks:
            task_ids = [t["id"] for t in tasks]
            mark_printed(task_ids)
            print(f"Marked {len(task_ids)} task(s) as printed")

    print("Done!")


if __name__ == "__main__":
    main()
