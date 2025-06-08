#!/usr/bin/env python3
"""
SplitMind Dashboard Launcher
Launch the command center with a single command from project root
"""
import uvicorn
import webbrowser
import argparse
import os
import sys
import time
import subprocess
import signal
import psutil
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn[standard]',
        'websockets': 'websockets',
        'aiofiles': 'aiofiles',
        'psutil': 'psutil'
    }
    missing = []
    
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print(f"\n📦 Install with: pip install {' '.join(missing)}")
        response = input("\nWould you like to install them now? (y/N): ")
        if response.lower() == 'y':
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("✅ Dependencies installed!")
        else:
            sys.exit(1)

def check_running_servers(port=8000):
    """Check for running dashboard processes and optionally shut them down"""
    running_processes = []
    
    # Check for processes using the port (with error handling)
    try:
        for conn in psutil.net_connections():
            try:
                if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    proc = psutil.Process(conn.pid)
                    if 'python' in proc.name().lower() or 'uvicorn' in proc.name().lower():
                        running_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
    except (psutil.AccessDenied, OSError):
        # Fall back to process search only
        pass
    
    # Check for launch-dashboard.py processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and any('launch-dashboard.py' in str(arg) for arg in cmdline):
                if proc.pid != os.getpid():  # Don't include current process
                    running_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Check for uvicorn processes running our API
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if (cmdline and 
                any('uvicorn' in str(arg) for arg in cmdline) and
                any('dashboard.backend.api:app' in str(arg) for arg in cmdline)):
                running_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Remove duplicates by PID
    seen_pids = set()
    unique_processes = []
    for proc in running_processes:
        try:
            if proc.pid not in seen_pids:
                seen_pids.add(proc.pid)
                unique_processes.append(proc)
        except psutil.NoSuchProcess:
            continue
    
    return unique_processes

def shutdown_existing_servers(processes):
    """Gracefully shutdown existing dashboard processes"""
    if not processes:
        return
    
    print(f"🔍 Found {len(processes)} running dashboard process(es)")
    
    # Show what we found
    for proc in processes:
        try:
            cmdline = ' '.join(proc.cmdline()[:3]) if proc.cmdline() else proc.name()
            print(f"   • PID {proc.pid}: {cmdline}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"\n🛑 Shutting down existing processes...")
    
    # First try graceful shutdown (SIGTERM)
    for proc in processes:
        try:
            print(f"   ⏳ Gracefully stopping PID {proc.pid}...")
            proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Wait for graceful shutdown
    time.sleep(2)
    
    # Check what's still running and force kill if needed
    still_running = []
    for proc in processes:
        try:
            if proc.is_running():
                still_running.append(proc)
        except psutil.NoSuchProcess:
            continue
    
    if still_running:
        print(f"   💥 Force killing {len(still_running)} stubborn process(es)...")
        for proc in still_running:
            try:
                proc.kill()
                print(f"   ✅ Killed PID {proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(1)
    
    print(f"✅ Cleanup complete!\n")

def check_frontend_built():
    """Check if frontend is built"""
    frontend_dist = Path(__file__).parent / 'dashboard' / 'frontend' / 'dist'
    if not frontend_dist.exists():
        print("⚠️  Frontend not built yet.")
        print("\n📦 First-time setup required:")
        print("   cd dashboard/frontend")
        print("   npm install")
        print("   npm run build")
        print("   cd ../..")
        print("\nThen run 'python launch-dashboard.py' again.")
        return False
    return True

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n\n👋 Shutting down SplitMind Command Center...")
    print("✨ Thanks for using SplitMind!")
    sys.exit(0)

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    parser = argparse.ArgumentParser(
        description='🚀 Launch SplitMind Command Center',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch-dashboard.py              # Launch on default port 8000
  python launch-dashboard.py --port 3000  # Launch on port 3000
  python launch-dashboard.py --dev        # Launch in development mode
  python launch-dashboard.py --no-browser # Don't open browser
  python launch-dashboard.py --no-cleanup # Skip shutdown check
        """
    )
    parser.add_argument('--port', type=int, default=8000, help='Port to run on (default: 8000)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    parser.add_argument('--dev', action='store_true', help='Run in development mode with auto-reload')
    parser.add_argument('--no-cleanup', action='store_true', help='Skip checking for and shutting down existing processes')
    args = parser.parse_args()
    
    # Check dependencies
    check_dependencies()
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Check for running servers and shut them down
    if not args.no_cleanup:
        running_processes = check_running_servers(args.port)
        if running_processes:
            shutdown_existing_servers(running_processes)
    
    # Check if frontend is built
    frontend_ready = check_frontend_built()
    if not frontend_ready:
        sys.exit(1)
    
    # ASCII art banner
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██████╗ ██╗     ██╗████████╗███╗   ███╗██╗███╗ ║
║   ██╔════╝██╔══██╗██║     ██║╚══██╔══╝████╗ ████║██║██╔██║
║   ███████╗██████╔╝██║     ██║   ██║   ██╔████╔██║██║██╔██║
║   ╚════██║██╔═══╝ ██║     ██║   ██║   ██║╚██╔╝██║██║██║╚═║
║   ███████║██║     ███████╗██║   ██║   ██║ ╚═╝ ██║██║██║ ╚║
║   ╚══════╝╚═╝     ╚══════╝╚═╝   ╚═╝   ╚═╝     ╚═╝╚═╝╚═╝  ║
║                                                           ║
║              Command Center Dashboard                     ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    print(f"🚀 Starting SplitMind Command Center...")
    print(f"📍 URL: http://{args.host}:{args.port}")
    print(f"📁 Project: {project_root}")
    print(f"🔧 Mode: {'Development' if args.dev else 'Production'}")
    
    if frontend_ready:
        print(f"✅ Frontend: Ready")
    else:
        print(f"⚠️  Frontend: Not built (API-only mode)")
    
    print("\n🔌 Starting server...\n")
    
    # Open browser after a short delay
    if not args.no_browser and frontend_ready:
        def open_browser():
            time.sleep(1.5)  # Wait for server to start
            webbrowser.open(f'http://{args.host}:{args.port}')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    # Suppress uvicorn's shutdown errors
    import logging
    logging.getLogger("uvicorn.error").disabled = True
    logging.getLogger("uvicorn.access").disabled = not args.dev
    
    try:
        # Configure uvicorn with custom settings
        config = uvicorn.Config(
            "dashboard.backend.api:app",
            host=args.host,
            port=args.port,
            reload=args.dev,
            log_level="info" if args.dev else "error",
            access_log=args.dev,
            lifespan="on"
        )
        server = uvicorn.Server(config)
        
        # Custom logging
        if not args.dev:
            # Suppress shutdown errors in production
            import asyncio
            
            original_exception_handler = asyncio.get_event_loop().get_exception_handler()
            
            def exception_handler(loop, context):
                exception = context.get("exception")
                if isinstance(exception, asyncio.CancelledError):
                    return
                if original_exception_handler:
                    original_exception_handler(loop, context)
            
            asyncio.get_event_loop().set_exception_handler(exception_handler)
        
        server.run()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down SplitMind Command Center...")
        print("✨ Thanks for using SplitMind!")
        sys.exit(0)
    except Exception as e:
        if not isinstance(e, SystemExit):
            print(f"\n❌ Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()