"""
MarketMate Server Stop Script
Stops all running backend and frontend servers.
"""
import subprocess
import sys

# Server ports to stop
PORTS = [8002, 8080]

def find_and_kill_process_on_port(port):
    """Find and kill process running on specified port (Windows)"""
    try:
        # Find PID using netstat
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            killed_pids = set()
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid not in killed_pids and pid != '0':
                        try:
                            # Kill the process
                            subprocess.run(
                                f'taskkill /PID {pid} /F',
                                shell=True,
                                capture_output=True
                            )
                            killed_pids.add(pid)
                            print(f"   ✅ Killed process {pid} on port {port}")
                        except Exception as e:
                            print(f"   ⚠️  Could not kill process {pid}: {e}")
            
            if killed_pids:
                return True
        
        print(f"   ℹ️  No process found on port {port}")
        return False
        
    except Exception as e:
        print(f"   ❌ Error checking port {port}: {e}")
        return False

def kill_python_servers():
    """Kill any python http.server or uvicorn processes"""
    try:
        # Find uvicorn processes
        result = subprocess.run(
            'tasklist | findstr /I "uvicorn"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            subprocess.run(
                'taskkill /IM uvicorn.exe /F',
                shell=True,
                capture_output=True
            )
            print("   ✅ Killed uvicorn processes")
            
    except Exception:
        pass

def main():
    print("=" * 50)
    print("       🛑 MarketMate Server Shutdown")
    print("=" * 50)
    print()
    
    stopped_any = False
    
    for port in PORTS:
        print(f"🔍 Checking port {port}...")
        if find_and_kill_process_on_port(port):
            stopped_any = True
    
    print()
    kill_python_servers()
    
    print()
    print("=" * 50)
    if stopped_any:
        print("✅ Server shutdown complete!")
    else:
        print("ℹ️  No MarketMate servers were running.")
    print("=" * 50)

if __name__ == "__main__":
    main()
