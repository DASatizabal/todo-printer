"""
Todo Printer - Receipt Formatter & Printer
Formats tasks into styled thermal receipt tickets.
Supports mock mode (text preview) and live mode (ESC/POS USB printer).

Config via environment variables:
  PRINTER_MODE=mock|live  (default: mock)
  PRINTER_VENDOR=0x0  (USB vendor ID, for live mode)
  PRINTER_PRODUCT=0x0  (USB product ID, for live mode)
"""

import os
import random
from datetime import datetime, date
from pathlib import Path

# Receipt width in characters (80mm printer @ standard font = ~42 chars)
RECEIPT_WIDTH = 42

# ---------------------------------------------------------------------------
# Fun stuff for the "Ticket of the Day"
# ---------------------------------------------------------------------------

DAD_JOKES = [
    "Why don't scientists trust atoms? They make up everything.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "What do you call a fake noodle? An impasta.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I'm reading a book about anti-gravity. It's impossible to put down.",
    "What do you call a bear with no teeth? A gummy bear.",
    "Why don't eggs tell jokes? They'd crack each other up.",
    "I used to hate facial hair, but then it grew on me.",
    "What did the ocean say to the beach? Nothing, it just waved.",
    "Why do cows have hooves? Because they lactose.",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "What do you call a lazy kangaroo? A pouch potato.",
    "Why did the bicycle fall over? It was two-tired.",
    "What do you call cheese that isn't yours? Nacho cheese.",
    "I'm on a seafood diet. I see food and I eat it.",
    "Why can't you give Elsa a balloon? Because she'll let it go.",
    "What did the grape do when it got stepped on? It let out a little wine.",
    "I would tell you a construction joke, but I'm still working on it.",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What do you call a dog magician? A Labracadabrador.",
]

FUN_FACTS = [
    "Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs.",
    "A group of flamingos is called a 'flamboyance'.",
    "The shortest war in history lasted 38 minutes (Britain vs Zanzibar, 1896).",
    "Octopuses have three hearts and blue blood.",
    "Bananas are berries, but strawberries aren't.",
    "The inventor of the Pringles can is buried in one.",
    "A jiffy is an actual unit of time: 1/100th of a second.",
    "The moon has moonquakes.",
    "Cows have best friends and get stressed when separated.",
    "The total weight of all ants on Earth roughly equals the weight of all humans.",
    "A bolt of lightning is five times hotter than the surface of the sun.",
    "The first computer programmer was Ada Lovelace in the 1840s.",
    "There are more possible chess games than atoms in the observable universe.",
    "Sea otters hold hands while sleeping so they don't drift apart.",
    "The national animal of Scotland is the unicorn.",
]


def get_daily_joke() -> str:
    """Fetch a random dad joke from icanhazdadjoke.com, with offline fallback."""
    try:
        import httpx
        response = httpx.get(
            "https://icanhazdadjoke.com/",
            headers={
                "Accept": "application/json",
                "User-Agent": "TodoPrinter (https://github.com/DASatizabal/todo-printer)",
            },
            timeout=5,
        )
        if response.status_code == 200:
            return response.json()["joke"]
    except Exception:
        pass
    # Fallback to local jokes if API is unavailable
    day_seed = date.today().toordinal()
    return DAD_JOKES[day_seed % len(DAD_JOKES)]


def get_daily_fact() -> str:
    """Fetch today's useless fact from uselessfacts.jsph.pl, with offline fallback."""
    try:
        import httpx
        response = httpx.get(
            "https://uselessfacts.jsph.pl/api/v2/facts/today",
            headers={
                "Accept": "application/json",
                "User-Agent": "TodoPrinter (https://github.com/DASatizabal/todo-printer)",
            },
            params={"language": "en"},
            timeout=5,
        )
        if response.status_code == 200:
            return response.json()["text"]
    except Exception:
        pass
    # Fallback to local facts if API is unavailable
    day_seed = date.today().toordinal() + 7
    return FUN_FACTS[day_seed % len(FUN_FACTS)]


# ---------------------------------------------------------------------------
# Receipt Formatting
# ---------------------------------------------------------------------------

CATEGORY_HEADERS = {
    "work": (
        "================================",
        "WORK TASKS",
        "================================",
    ),
    "school": (
        "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+",
        "SCHOOL TASKS",
        "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+",
    ),
    "personal": (
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "PERSONAL TASKS",
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    ),
}

# ASCII art icons for at-a-glance ticket identification
CATEGORY_ICONS = {
    "work": [
        "____________",
        "|  ________  |",
        "| |  WORK  | |",
        "| |________| |",
        "|____|_|_____|",
    ],
    "school": [
        "+",
        "A",
        "__/_\\__",
        "/\\-'o'-/\\",
        "_||:<_>:||_",
        "/\\_/=====\\_/\\",
        "_|:_:_[I]_:_:|_",
        "SCHOOL"
    ],
    "personal": [
        "))    ",
        "_-#-----_",
        "/_________\\",
        "|[] _ []|",
        "|  |*|  |",
        "H O M E"
    ],
}

LISA_ICON = [
    "**   **",
    "*  * *  *",
    "*   *   *",
    "*     *",
    "*   *",
    "* *",
    "*",
    "FROM LISA",
]

PRIORITY_LABELS = {
    1: "!!! HIGH",
    2: "MED",
    3: "LOW",
}

PRIORITY_MARKERS = {
    1: ">>> ",
    2: "    ",
    3: "    ",
}


def wrap_text(text: str, width: int, indent: str = "") -> list[str]:
    """Word-wrap text to fit receipt width."""
    words = text.split()
    lines = []
    current = indent
    for word in words:
        if len(current) + len(word) + 1 > width:
            lines.append(current)
            current = indent + word
        else:
            if current == indent:
                current += word
            else:
                current += " " + word
    if current.strip():
        lines.append(current)
    return lines


def center(text: str, width: int = RECEIPT_WIDTH) -> str:
    return text.center(width)


def hr(char: str = "-", width: int = RECEIPT_WIDTH) -> str:
    return char * width


def format_task_line(task: dict, index: int) -> list[str]:
    """Format a single task into receipt lines."""
    lines = []
    marker = PRIORITY_MARKERS.get(task["priority"], "    ")
    pri_label = PRIORITY_LABELS.get(task["priority"], "    ???")

    # Task number + title
    header = f"{marker}{index}. {task['title']}"
    lines.extend(wrap_text(header, RECEIPT_WIDTH))

    # Priority + due info on one line
    meta_parts = [f"[{pri_label}]"]
    if task.get("due_date"):
        due_str = task["due_date"]
        if task.get("due_time"):
            due_str += f" {task['due_time']}"
        # Check if overdue
        try:
            due = date.fromisoformat(task["due_date"])
            if due < date.today():
                due_str = f"OVERDUE: {due_str}"
        except ValueError:
            pass
        meta_parts.append(f"Due: {due_str}")

    lines.append(f"      {' | '.join(meta_parts)}")

    # Source tag
    if task.get("source") == "lisa":
        lines.append("      [FROM LISA]")

    # Notes
    if task.get("notes"):
        note_lines = wrap_text(f"Note: {task['notes']}", RECEIPT_WIDTH, indent="      ")
        lines.extend(note_lines)

    lines.append("")  # blank line separator
    return lines


def format_receipt(
    tasks: list[dict],
    title: str = "TO DO TICKET",
    include_joke: bool = True,
    include_fact: bool = True,
    group_by_category: bool = True,
) -> str:
    """
    Format a full receipt from a list of tasks.
    Returns the receipt as a plain text string.
    """
    lines = []
    now = datetime.now()

    # Header
    lines.append(hr("="))
    lines.append(center(title))
    lines.append(center(now.strftime("%A, %B %d, %Y")))
    lines.append(center(now.strftime("%I:%M %p")))
    lines.append(hr("="))
    lines.append("")

    if not tasks:
        lines.append(center("No tasks! Enjoy your day."))
        lines.append("")
    elif group_by_category:
        # Group tasks by category
        grouped: dict[str, list[dict]] = {}
        for t in tasks:
            cat = t.get("category", "personal")
            grouped.setdefault(cat, []).append(t)

        task_num = 1
        for cat in ["work", "school", "personal"]:
            if cat not in grouped:
                continue

            header_lines = CATEGORY_HEADERS.get(cat, ("---", cat.upper(), "---"))
            lines.append("")
            for h in header_lines:
                lines.append(center(h))
            lines.append("")

            for task in grouped[cat]:
                lines.extend(format_task_line(task, task_num))
                task_num += 1
    else:
        for i, task in enumerate(tasks, 1):
            lines.extend(format_task_line(task, i))

    # Summary
    overdue_count = sum(
        1 for t in tasks
        if t.get("due_date") and t["due_date"] < date.today().isoformat()
    )
    lines.append(hr("-"))
    lines.append(f"  Total: {len(tasks)} task(s)")
    if overdue_count:
        lines.append(f"  !!! {overdue_count} OVERDUE !!!")
    lines.append(hr("-"))

    # Ticket of the Day
    if include_joke or include_fact:
        lines.append("")
        lines.append(center("~ TICKET OF THE DAY ~"))
        lines.append("")

        if include_joke:
            joke = get_daily_joke()
            lines.extend(wrap_text(joke, RECEIPT_WIDTH, indent="  "))
            lines.append("")

        if include_fact:
            lines.append("  Fun fact:")
            fact = get_daily_fact()
            lines.extend(wrap_text(fact, RECEIPT_WIDTH, indent="  "))

    lines.append("")
    lines.append(hr("="))
    lines.append(center("GET IT DONE."))
    lines.append(hr("="))
    lines.append("")
    lines.append("")  # feed for auto-cutter

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Individual Ticket Formatting
# ---------------------------------------------------------------------------

def format_ticket(
    task: dict,
    ticket_num: int = None,
    total: int = None,
) -> str:
    """Format a single task as its own individual receipt ticket."""
    lines = []
    now = datetime.now()

    # Header
    lines.append(hr("="))
    lines.append(center("~ TASK TICKET ~"))
    lines.append(center(now.strftime("%A, %B %d, %Y")))
    lines.append(center(now.strftime("%I:%M %p")))
    lines.append(hr("="))
    lines.append("")

    # Lisa icon (if from Lisa, show heart prominently)
    if task.get("source") == "lisa":
        for icon_line in LISA_ICON:
            lines.append(center(icon_line))
        lines.append("")

    # Category icon
    cat = task.get("category", "personal")
    icon_lines = CATEGORY_ICONS.get(cat, [])
    for icon_line in icon_lines:
        lines.append(center(icon_line))
    lines.append("")

    # Category header
    header_lines = CATEGORY_HEADERS.get(cat, ("---", cat.upper(), "---"))
    for h in header_lines:
        lines.append(center(h))
    lines.append("")

    # Task content (reuse format_task_line)
    idx = ticket_num if ticket_num is not None else 1
    lines.extend(format_task_line(task, idx))

    # Ticket counter
    if ticket_num is not None and total is not None:
        lines.append(center(f"[ {ticket_num} of {total} ]"))
        lines.append("")

    # Footer
    lines.append(hr("="))
    lines.append(center("GET IT DONE."))
    lines.append(hr("="))
    lines.append("")
    lines.append("")  # feed for auto-cutter

    return "\n".join(lines)


def format_daily_ticket() -> str:
    """Format the Ticket of the Day as a standalone receipt."""
    lines = []
    now = datetime.now()

    lines.append(hr("="))
    lines.append(center("~ TICKET OF THE DAY ~"))
    lines.append(center(now.strftime("%A, %B %d, %Y")))
    lines.append(hr("="))
    lines.append("")

    joke = get_daily_joke()
    lines.extend(wrap_text(joke, RECEIPT_WIDTH, indent="  "))
    lines.append("")

    lines.append("  Fun fact:")
    fact = get_daily_fact()
    lines.extend(wrap_text(fact, RECEIPT_WIDTH, indent="  "))
    lines.append("")

    lines.append(hr("="))
    lines.append(center("HAVE A GREAT DAY!"))
    lines.append(hr("="))
    lines.append("")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Printer Interface
# ---------------------------------------------------------------------------

MOCK_OUTPUT_DIR = Path(os.environ.get("MOCK_PRINT_DIR", "mock_prints"))


def print_receipt(receipt_text: str) -> dict:
    """
    Send formatted receipt to printer (live) or save to file (mock).
    Returns status info.
    """
    mode = os.environ.get("PRINTER_MODE", "mock").lower()

    if mode == "live":
        return _print_live(receipt_text)
    else:
        return _print_mock(receipt_text)


def _print_mock(receipt_text: str) -> dict:
    """Save receipt to a timestamped text file for preview."""
    MOCK_OUTPUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = MOCK_OUTPUT_DIR / f"receipt_{ts}.txt"
    filename.write_text(receipt_text)

    return {
        "mode": "mock",
        "status": "saved",
        "file": str(filename),
        "preview": receipt_text,
    }


def print_tickets(ticket_texts: list[str]) -> dict:
    """
    Print multiple individual tickets, each getting its own cut.
    Works in both mock and live mode.
    """
    mode = os.environ.get("PRINTER_MODE", "mock").lower()

    if mode == "live":
        return _print_tickets_live(ticket_texts)
    else:
        return _print_tickets_mock(ticket_texts)


def _print_tickets_mock(ticket_texts: list[str]) -> dict:
    """Save each ticket as a separate file, plus a combined preview."""
    MOCK_OUTPUT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    files = []
    for i, text in enumerate(ticket_texts, 1):
        filename = MOCK_OUTPUT_DIR / f"ticket_{ts}_{i}.txt"
        filename.write_text(text)
        files.append(str(filename))

    combined = "\n".join(ticket_texts)

    return {
        "mode": "mock",
        "status": "saved",
        "files": files,
        "count": len(ticket_texts),
        "preview": combined,
    }


def _print_tickets_live(ticket_texts: list[str]) -> dict:
    """Send each ticket to USB printer with a cut after each one."""
    try:
        from escpos.printer import Usb

        vendor_id = int(os.environ.get("PRINTER_VENDOR", "0x0"), 16)
        product_id = int(os.environ.get("PRINTER_PRODUCT", "0x0"), 16)

        if vendor_id == 0 or product_id == 0:
            return {
                "mode": "live",
                "status": "error",
                "error": "PRINTER_VENDOR and PRINTER_PRODUCT env vars not set. "
                         "Run 'lsusb' to find your NetumScan's IDs.",
            }

        printer = Usb(vendor_id, product_id)
        printer.set(align="left", font="a", width=1, height=1)

        for text in ticket_texts:
            for line in text.split("\n"):
                printer.text(line + "\n")
            printer.cut()

        printer.close()

        return {
            "mode": "live",
            "status": "printed",
            "count": len(ticket_texts),
        }

    except ImportError:
        return {
            "mode": "live",
            "status": "error",
            "error": "python-escpos not installed. Run: pip install python-escpos",
        }
    except Exception as e:
        return {
            "mode": "live",
            "status": "error",
            "error": str(e),
        }


def _print_live(receipt_text: str) -> dict:
    """Send receipt to USB thermal printer via ESC/POS."""
    try:
        from escpos.printer import Usb

        vendor_id = int(os.environ.get("PRINTER_VENDOR", "0x0"), 16)
        product_id = int(os.environ.get("PRINTER_PRODUCT", "0x0"), 16)

        if vendor_id == 0 or product_id == 0:
            return {
                "mode": "live",
                "status": "error",
                "error": "PRINTER_VENDOR and PRINTER_PRODUCT env vars not set. "
                         "Run 'lsusb' to find your NetumScan's IDs.",
            }

        printer = Usb(vendor_id, product_id)
        printer.set(align="left", font="a", width=1, height=1)

        for line in receipt_text.split("\n"):
            printer.text(line + "\n")

        printer.cut()
        printer.close()

        return {
            "mode": "live",
            "status": "printed",
            "preview": receipt_text,
        }

    except ImportError:
        return {
            "mode": "live",
            "status": "error",
            "error": "python-escpos not installed. Run: pip install python-escpos",
        }
    except Exception as e:
        return {
            "mode": "live",
            "status": "error",
            "error": str(e),
            "preview": receipt_text,
        }
