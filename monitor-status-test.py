#!/usr/bin/env python3
"""Monitor test with status files"""
import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_tmux_sessions():
    """Get active tmux sessions"""
    result = subprocess.run(['tmux', 'ls'], capture_output=True, text=True)
    if result.returncode == 0:
        sessions = []
        for line in result.stdout.strip().split('\n'):
            if '-hello' in line:
                session_name = line.split(':')[0]
                sessions.append(session_name)
        return sessions
    return []

def check_status_files():
    """Check status files"""
    status_dir = Path("/tmp/splitmind-status")
    if not status_dir.exists():
        return {}
    
    statuses = {}
    for status_file in status_dir.glob("*.status"):
        session_name = status_file.stem
        status = status_file.read_text().strip()
        statuses[session_name] = status
    return statuses

def check_task_statuses():
    """Get task statuses from tasks.md"""
    tasks_file = Path("/Users/jasonbrashear/code/hello-splitmind/.splitmind/tasks.md")
    if not tasks_file.exists():
        return []
    
    tasks = []
    current_task = {}
    
    for line in tasks_file.read_text().split('\n'):
        if line.startswith('## Task:'):
            if current_task:
                tasks.append(current_task)
            current_task = {'title': line.replace('## Task:', '').strip()}
        elif line.startswith('- task_id:'):
            current_task['id'] = line.split(':')[1].strip()
        elif line.startswith('- status:'):
            current_task['status'] = line.split(':')[1].strip()
        elif line.startswith('- session:'):
            session = line.split(':')[1].strip()
            if session != 'null':
                current_task['session'] = session
    
    if current_task:
        tasks.append(current_task)
    
    return tasks

def main():
    print(f"\n{BLUE}=== SplitMind Test Monitor ==={RESET}")
    print(f"Started at {datetime.now().strftime('%H:%M:%S')}\n")
    
    try:
        check_count = 0
        while True:
            check_count += 1
            print(f"\n{YELLOW}--- Check #{check_count} at {datetime.now().strftime('%H:%M:%S')} ---{RESET}")
            
            # Check tmux sessions
            sessions = check_tmux_sessions()
            print(f"\n{BLUE}Active Sessions ({len(sessions)}):{RESET}")
            for session in sessions:
                print(f"  • {session}")
            if not sessions:
                print("  (none)")
            
            # Check status files
            statuses = check_status_files()
            print(f"\n{BLUE}Status Files:{RESET}")
            for session, status in statuses.items():
                color = GREEN if status == "COMPLETED" else YELLOW
                print(f"  • {session}: {color}{status}{RESET}")
            if not statuses:
                print("  (none)")
            
            # Check task statuses
            tasks = check_task_statuses()
            print(f"\n{BLUE}Task Status:{RESET}")
            status_counts = {}
            for task in tasks:
                status = task['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Show details for active tasks
                if status in ['claimed', 'in_progress', 'completed']:
                    session = task.get('session', '(no session)')
                    print(f"  • Task {task['id']}: {task['title'][:30]}... - {status} [{session}]")
            
            # Summary
            print(f"\n{BLUE}Summary:{RESET}")
            for status, count in sorted(status_counts.items()):
                color = GREEN if status == 'merged' else YELLOW if status == 'completed' else RESET
                print(f"  • {status}: {color}{count}{RESET}")
            
            # Check for completion
            if all(task['status'] in ['merged', 'completed'] for task in tasks):
                print(f"\n{GREEN}✅ All tasks completed or merged!{RESET}")
                break
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Monitor stopped by user{RESET}")
    
    # Final summary
    print(f"\n{BLUE}=== Final Summary ==={RESET}")
    tasks = check_task_statuses()
    for task in tasks:
        color = GREEN if task['status'] == 'merged' else YELLOW if task['status'] == 'completed' else RED
        print(f"  Task {task['id']}: {color}{task['status']}{RESET} - {task['title']}")

if __name__ == "__main__":
    main()