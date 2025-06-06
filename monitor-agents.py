#!/usr/bin/env python3
"""
Monitor agent sessions and update task statuses
"""
import subprocess
import sys
import time
import json
from pathlib import Path

def check_agent_completion():
    """Check all tmux sessions for completed agents"""
    # Get all tmux sessions
    result = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("No tmux sessions found")
        return
    
    sessions = result.stdout.strip().split('\n')
    
    for session in sessions:
        if not session.startswith('splitmind-ai-'):
            continue
            
        # Capture session output
        capture = subprocess.run(
            ["tmux", "capture-pane", "-t", session, "-p"],
            capture_output=True,
            text=True
        )
        
        output = capture.stdout
        
        # Check for completion indicators
        if any(marker in output for marker in [
            "✅ Task completed",
            "All changes have been committed",
            "Task completed. Exiting"
        ]):
            print(f"✅ Agent {session} has completed its task")
            
            # Kill the session
            subprocess.run(["tmux", "kill-session", "-t", session])
            print(f"   Killed session {session}")
            
            # Trigger API check
            subprocess.run([
                "curl", "-X", "POST", 
                "http://localhost:8000/api/orchestrator/check-tasks",
                "-H", "Content-Type: application/json"
            ])

if __name__ == "__main__":
    print("🔍 Monitoring agent sessions...")
    while True:
        check_agent_completion()
        time.sleep(10)  # Check every 10 seconds