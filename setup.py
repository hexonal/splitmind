#!/usr/bin/env python3
"""
SplitMind First-Time Setup Script
Automatically sets up everything needed to run SplitMind Dashboard
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_banner():
    """Print the SplitMind banner"""
    banner = f"""{Colors.CYAN}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███████╗██████╗ ██╗     ██╗████████╗███╗   ███╗██╗███╗ ║
║   ██╔════╝██╔══██╗██║     ██║╚══██╔══╝████╗ ████║██║████╗║
║   ███████╗██████╔╝██║     ██║   ██║   ██╔████╔██║██║██╔██║
║   ╚════██║██╔═══╝ ██║     ██║   ██║   ██║╚██╔╝██║██║██║╚═║
║   ███████║██║     ███████╗██║   ██║   ██║ ╚═╝ ██║██║██║ ╚║
║   ╚══════╝╚═╝     ╚══════╝╚═╝   ╚═╝   ╚═╝     ╚═╝╚═╝╚═╝  ║
║                                                           ║
║              First-Time Setup Wizard                      ║
╚═══════════════════════════════════════════════════════════╝{Colors.END}
    """
    print(banner)

def run_command(cmd, description, cwd=None, check=True):
    """Run a command and handle errors"""
    print(f"\n{Colors.BLUE}▶ {description}{Colors.END}")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"{Colors.RED}{result.stderr}{Colors.END}")
        
        return result
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}✗ Failed: {e}{Colors.END}")
        if e.stderr:
            print(f"{Colors.RED}{e.stderr}{Colors.END}")
        if check:
            sys.exit(1)
        return None

def check_prerequisites():
    """Check if required tools are installed"""
    print(f"\n{Colors.BOLD}Checking prerequisites...{Colors.END}")
    
    tools = {
        'python3': 'Python 3.8+',
        'pip': 'pip',
        'node': 'Node.js',
        'npm': 'npm',
        'git': 'Git',
        'tmux': 'tmux'
    }
    
    missing = []
    for cmd, name in tools.items():
        result = run_command(f"which {cmd}", f"Checking for {name}", check=False)
        if result and result.returncode == 0:
            print(f"{Colors.GREEN}✓ {name} found{Colors.END}")
        else:
            print(f"{Colors.RED}✗ {name} not found{Colors.END}")
            missing.append(name)
    
    if missing:
        print(f"\n{Colors.RED}Missing required tools: {', '.join(missing)}{Colors.END}")
        print(f"{Colors.YELLOW}Please install the missing tools and run this script again.{Colors.END}")
        
        if platform.system() == 'Darwin':
            print(f"\n{Colors.CYAN}On macOS, you can use Homebrew:{Colors.END}")
            if 'tmux' in ' '.join(missing).lower():
                print("  brew install tmux")
            if 'node' in ' '.join(missing).lower():
                print("  brew install node")
        
        sys.exit(1)
    
    print(f"\n{Colors.GREEN}✓ All prerequisites installed!{Colors.END}")

def setup_python_dependencies():
    """Install Python dependencies"""
    print(f"\n{Colors.BOLD}Installing Python dependencies...{Colors.END}")
    
    # First, upgrade pip
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                "Upgrading pip")
    
    # Check if requirements.txt exists
    requirements_path = Path(__file__).parent / 'requirements.txt'
    if requirements_path.exists():
        # Install from requirements.txt
        run_command([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)],
                    "Installing from requirements.txt")
    else:
        # Fallback to manual installation
        dependencies = [
            'fastapi[all]',
            'uvicorn[standard]',
            'websockets',
            'aiofiles',
            'pydantic',
            'httpx'
        ]
        
        run_command([sys.executable, '-m', 'pip', 'install'] + dependencies,
                    "Installing backend dependencies")
    
    print(f"{Colors.GREEN}✓ Python dependencies installed!{Colors.END}")

def setup_frontend():
    """Set up the frontend"""
    print(f"\n{Colors.BOLD}Setting up frontend...{Colors.END}")
    
    frontend_path = Path(__file__).parent / 'dashboard' / 'frontend'
    
    # Install npm dependencies
    run_command('npm install', "Installing frontend dependencies", cwd=frontend_path)
    
    # Build frontend
    run_command('npm run build', "Building frontend", cwd=frontend_path)
    
    print(f"{Colors.GREEN}✓ Frontend built successfully!{Colors.END}")

def create_directories():
    """Create necessary directories"""
    print(f"\n{Colors.BOLD}Creating directories...{Colors.END}")
    
    directories = [
        'worktrees',
        'docs',
        'scripts',
        '.claude/commands',
        'dashboard/backend',
        'dashboard/frontend'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}✓ Created {dir_path}{Colors.END}")

def check_claude_cli():
    """Check if Claude CLI is installed"""
    print(f"\n{Colors.BOLD}Checking Claude CLI...{Colors.END}")
    
    result = run_command('which claude', "Looking for Claude CLI", check=False)
    
    if result and result.returncode == 0:
        print(f"{Colors.GREEN}✓ Claude CLI found{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ Claude CLI not found{Colors.END}")
        print(f"{Colors.CYAN}To use AI agents, install Claude CLI from:{Colors.END}")
        print("  https://docs.anthropic.com/en/docs/claude-cli")
        print(f"{Colors.CYAN}SplitMind will still work for task management without it.{Colors.END}")

def create_example_tasks():
    """Create an example tasks.md file"""
    print(f"\n{Colors.BOLD}Creating example tasks.md...{Colors.END}")
    
    example_content = """# tasks.md

## Task: Add user authentication

- status: unclaimed
- branch: add-auth
- session: null
- description: Implement user login and registration

## Task: Create API documentation

- status: unclaimed
- branch: api-docs
- session: null
- description: Document all API endpoints with examples

## Task: Add dark mode toggle

- status: unclaimed
- branch: dark-mode
- session: null
- description: Add theme switching functionality
"""
    
    tasks_path = Path('tasks.md')
    if not tasks_path.exists():
        tasks_path.write_text(example_content)
        print(f"{Colors.GREEN}✓ Created example tasks.md{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ tasks.md already exists, skipping{Colors.END}")

def print_next_steps():
    """Print next steps for the user"""
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}{Colors.BOLD}✓ Setup Complete!{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}Next Steps:{Colors.END}")
    print(f"\n1. {Colors.BOLD}Launch the dashboard:{Colors.END}")
    print(f"   {Colors.YELLOW}python launch-dashboard.py{Colors.END}")
    
    print(f"\n2. {Colors.BOLD}Create your first project:{Colors.END}")
    print(f"   - Click the '+' button in the dashboard")
    print(f"   - Enter your project path (must be a git repository)")
    print(f"   - Set the maximum number of concurrent AI agents")
    
    print(f"\n3. {Colors.BOLD}Add tasks to your project:{Colors.END}")
    print(f"   - Edit the tasks.md file in your project's .splitmind directory")
    print(f"   - Or use the dashboard to create tasks")
    
    print(f"\n4. {Colors.BOLD}Start the orchestrator:{Colors.END}")
    print(f"   - Click 'Launch Orchestrator' in the dashboard")
    print(f"   - AI agents will automatically spawn for unclaimed tasks")
    
    print(f"\n{Colors.CYAN}For more information, see the README.md{Colors.END}")
    print(f"{Colors.CYAN}Happy coding with SplitMind! 🚀{Colors.END}\n")

def main():
    """Main setup function"""
    print_banner()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    try:
        check_prerequisites()
        create_directories()
        setup_python_dependencies()
        setup_frontend()
        check_claude_cli()
        create_example_tasks()
        print_next_steps()
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Setup cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Setup failed: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()