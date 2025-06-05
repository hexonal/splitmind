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
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn[standard]',
        'websockets': 'websockets',
        'aiofiles': 'aiofiles'
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
        """
    )
    parser.add_argument('--port', type=int, default=8000, help='Port to run on (default: 8000)')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    parser.add_argument('--dev', action='store_true', help='Run in development mode with auto-reload')
    args = parser.parse_args()
    
    # Check dependencies
    check_dependencies()
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
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