import sys
import subprocess
import os
import time

def run_backend():
    print("🚀 Starting FastAPI Backend Server on http://127.0.0.1:8000 ...")
    subprocess.run([sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])

def run_frontend():
    print("🎨 Starting Streamlit Frontend Interface on http://localhost:8501 ...")
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", frontend_path, "--server.port", "8501"])

def run_both():
    print("🌟 Launching Full Stack (FastAPI Backend + Streamlit Frontend) ...")
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
    
    backend_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"])
    time.sleep(2)
    frontend_proc = subprocess.Popen([sys.executable, "-m", "streamlit", "run", frontend_path, "--server.port", "8501"])
    
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "backend":
            run_backend()
        elif arg == "frontend":
            run_frontend()
        else:
            run_both()
    else:
        run_both()
