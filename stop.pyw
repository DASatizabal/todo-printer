"""
Stop the Todo Printer server.
Reads the PID written by launch.pyw and terminates it.
"""

import os
import signal

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_DIR, ".server.pid")

def main():
    if not os.path.exists(PID_FILE):
        return

    with open(PID_FILE) as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, signal.SIGTERM)
    except (ProcessLookupError, OSError):
        pass  # Already stopped

    os.remove(PID_FILE)

if __name__ == "__main__":
    main()
