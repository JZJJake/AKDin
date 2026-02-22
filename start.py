
import subprocess
import sys
import os
import time
import signal
import platform

# Global list to track processes
processes = []

def run_process(command, cwd=None, shell=False):
    """Helper to run a process and add it to the list."""
    try:
        # On Windows, we might want shell=True for some commands like 'npm', but subprocess usually handles .cmd resolution on Windows.
        # However, for consistency and ensuring PATH is used, shell=False is safer if we call the executable directly,
        # or shell=True if we rely on shell features.
        # For simplicity in this script, we'll use shell=True for Windows compatibility with commands like 'npm'.
        is_windows = platform.system() == "Windows"
        shell_mode = is_windows or shell

        print(f"[Start] Launching: {' '.join(command) if isinstance(command, list) else command}")

        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=shell_mode,
            stdout=sys.stdout, # Pipe output to main console
            stderr=sys.stderr
        )
        processes.append(process)
        return process
    except Exception as e:
        print(f"[Error] Failed to start command: {command} - {e}")
        return None

def signal_handler(sig, frame):
    """Handle Ctrl+C to terminate all subprocesses."""
    print("\n[Stop] Shutting down services...")
    for p in processes:
        try:
            if platform.system() == "Windows":
                # On Windows, Popen.terminate() might not kill the entire tree if shell=True.
                # Using taskkill is more robust.
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
            else:
                p.terminate()
        except Exception:
            pass
    sys.exit(0)

def main():
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("="*50)
    print("   Stock Strategy Platform - One-Click Start")
    print("="*50)

    # 1. Check if Redis is running (Optional check, skipping for simplicity)

    # 2. Start Backend (FastAPI)
    # Assumes python environment is active
    backend_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    run_process(backend_cmd)

    # 3. Start Celery Worker
    # Note: On Windows, Celery needs 'pool=solo' or 'gevent' usually, but standard 'worker' might fail.
    # For dev, we use standard. If Windows fails, user needs to add -P solo.
    # We will detect OS and add -P solo if Windows.
    celery_cmd = [sys.executable, "-m", "celery", "-A", "app.worker.celery_app", "worker", "--loglevel=info"]
    if platform.system() == "Windows":
        celery_cmd.extend(["-P", "solo"])
    run_process(celery_cmd)

    # 4. Start Celery Beat (Scheduler)
    beat_cmd = [sys.executable, "-m", "celery", "-A", "app.worker.celery_app", "beat", "--loglevel=info"]
    run_process(beat_cmd)

    # 5. Start Frontend (Vite)
    # We assume 'npm' is in PATH.
    frontend_cmd = ["npm", "run", "dev"]
    # On Windows, npm is npm.cmd. subprocess with shell=True handles this.
    run_process(frontend_cmd, cwd="frontend")

    print("\n[Success] All services launched!")
    print(">> Backend: http://localhost:8000")
    print(">> Frontend: http://localhost:5173 (wait for Vite to start)")
    print(">> Press Ctrl+C to stop all services.\n")

    # Keep main process alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
