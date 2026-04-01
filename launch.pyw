"""
Todo Printer Launcher
Double-click to start the server and open the dashboard.
Uses .pyw extension so no console window appears.
"""

import subprocess
import sys
import os
import time
import webbrowser
import socket
import signal

# --- Config ---
HOST = "0.0.0.0"
PORT = 8000
URL = f"http://localhost:{PORT}"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def main():
    os.chdir(PROJECT_DIR)

    # If server is already running, just open the browser
    if is_port_in_use(PORT):
        webbrowser.open(URL)
        return

    # Start uvicorn in the background (no console window via .pyw)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)],
        cwd=PROJECT_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    # Write PID so we can stop it later
    pid_file = os.path.join(PROJECT_DIR, ".server.pid")
    with open(pid_file, "w") as f:
        f.write(str(server.pid))

    # Wait for the server to be ready (up to 10 seconds)
    for _ in range(40):
        if is_port_in_use(PORT):
            break
        time.sleep(0.25)

    webbrowser.open(URL)

if __name__ == "__main__":
    main()
