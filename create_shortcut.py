"""
Create a Windows desktop shortcut for Todo Printer.
Run once: python create_shortcut.py

Creates "Todo Printer.lnk" on your Desktop that launches the app
with no console window and uses the custom icon.
"""

import os
import sys
import shutil

try:
    from win32com.client import Dispatch
except ImportError:
    print("Installing pywin32...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
    from win32com.client import Dispatch

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
SHORTCUT_PATH = os.path.join(DESKTOP, "Todo Printer.lnk")
SRC_ICON = os.path.join(PROJECT_DIR, "todo_printer.ico")
LAUNCH_SCRIPT = os.path.join(PROJECT_DIR, "launch.pyw")
PYTHONW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")

# The project lives on a NAS share (L:). Explorer can't reliably load shortcut
# icons from a network drive, so copy the icon to local disk and point there.
LOCAL_ICON_DIR = os.path.join(
    os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "TodoPrinter"
)
LOCAL_ICON = os.path.join(LOCAL_ICON_DIR, "todo_printer.ico")

# Fall back to python.exe if pythonw isn't available
if not os.path.exists(PYTHONW):
    PYTHONW = sys.executable


def _stage_local_icon() -> str:
    """Copy the icon to local disk so Explorer can render it (NAS icons render blank)."""
    if not os.path.exists(SRC_ICON):
        return ""
    os.makedirs(LOCAL_ICON_DIR, exist_ok=True)
    shutil.copy2(SRC_ICON, LOCAL_ICON)
    return LOCAL_ICON


def main():
    icon_path = _stage_local_icon()

    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(SHORTCUT_PATH)
    shortcut.TargetPath = PYTHONW
    shortcut.Arguments = f'"{LAUNCH_SCRIPT}"'
    shortcut.WorkingDirectory = PROJECT_DIR
    shortcut.Description = "Launch Todo Printer dashboard and server"

    if icon_path:
        # Explicit ",0" index keeps the shell from mis-parsing the path.
        shortcut.IconLocation = f"{icon_path},0"

    shortcut.save()
    print(f"Shortcut created: {SHORTCUT_PATH}")
    print(f"  Target: {PYTHONW} \"{LAUNCH_SCRIPT}\"")
    print(f"  Icon: {icon_path or '(none)'}")
    print("\nDouble-click 'Todo Printer' on your Desktop to launch!")


if __name__ == "__main__":
    main()
