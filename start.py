"""
MarketMate Startup Script
Runs both the backend API server and frontend HTTP server simultaneously.
"""
import subprocess
import sys
import os
import time

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Server configurations
BACKEND_PORT = 8003
FRONTEND_PORT = 8080

def check_database():
    """Check if MySQL database is accessible"""
    try:
        import pymysql
        from backend.config import settings
        
        conn = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        conn.close()
        print("   ✅ Database connection successful")
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        print("   💡 Make sure MySQL is running and the database exists")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print(f"🚀 Starting Backend API server on http://127.0.0.1:{BACKEND_PORT}")
    
    # Use the virtual environment Python if available
    venv_python = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    
    proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "backend.main:app", 
         "--host", "127.0.0.1", 
         "--port", str(BACKEND_PORT),
         "--reload"],
        cwd=PROJECT_ROOT
    )
    return proc

def start_frontend():
    """Start a simple HTTP server for the frontend"""
    print(f"🌐 Starting Frontend server on http://127.0.0.1:{FRONTEND_PORT}")
    
    # Use the virtual environment Python if available
    venv_python = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable
    
    proc = subprocess.Popen(
        [python_exe, "-m", "http.server", str(FRONTEND_PORT), "--bind", "127.0.0.1"],
        cwd=PROJECT_ROOT
    )
    return proc

def main():
    processes = []
    
    print("=" * 50)
    print("       🛒 MarketMate Server Startup")
    print("=" * 50)
    print()
    
    # Check database connection first
    print("🔍 Checking database connection...")
    if not check_database():
        print("\n⚠️  Proceeding anyway, but login may fail without database.")
    print()
    
    try:
        # Start both servers
        backend_proc = start_backend()
        processes.append(backend_proc)
        
        time.sleep(2)  # Wait for backend to start
        
        frontend_proc = start_frontend()
        processes.append(frontend_proc)
        
        print()
        print("=" * 50)
        print("✅ All servers started successfully!")
        print()
        print(f"   📡 Backend API:  http://127.0.0.1:{BACKEND_PORT}")
        print(f"   📝 API Docs:     http://127.0.0.1:{BACKEND_PORT}/api/docs")
        print(f"   🌐 Frontend:     http://127.0.0.1:{FRONTEND_PORT}/html/home.html")
        print()
        print("   Press Ctrl+C to stop all servers")
        print("=" * 50)
        
        # Wait for processes - simple loop
        while True:
            # Check if any process has died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    print(f"\n⚠️  Server process {i+1} has stopped (exit code: {proc.returncode})")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        for proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                try:
                    proc.kill()
                except:
                    pass
        print("✅ All servers stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")
        for proc in processes:
            try:
                proc.terminate()
            except:
                pass

if __name__ == "__main__":
    main()
