"""
Create a Windows desktop shortcut for Todo Printer.
Run once: python create_shortcut.py

Creates "Todo Printer.lnk" on your Desktop that launches the app
with no console window and uses the custom icon.
"""

import os
import sys

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
ICON_PATH = os.path.join(PROJECT_DIR, "todo_printer.ico")
LAUNCH_SCRIPT = os.path.join(PROJECT_DIR, "launch.pyw")
PYTHONW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")

# Fall back to python.exe if pythonw isn't available
if not os.path.exists(PYTHONW):
    PYTHONW = sys.executable


def main():
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(SHORTCUT_PATH)
    shortcut.TargetPath = PYTHONW
    shortcut.Arguments = f'"{LAUNCH_SCRIPT}"'
    shortcut.WorkingDirectory = PROJECT_DIR
    shortcut.Description = "Launch Todo Printer dashboard and server"

    if os.path.exists(ICON_PATH):
        shortcut.IconLocation = ICON_PATH

    shortcut.save()
    print(f"Shortcut created: {SHORTCUT_PATH}")
    print(f"  Target: {PYTHONW} \"{LAUNCH_SCRIPT}\"")
    print(f"  Icon: {ICON_PATH}")
    print("\nDouble-click 'Todo Printer' on your Desktop to launch!")


if __name__ == "__main__":
    main()
