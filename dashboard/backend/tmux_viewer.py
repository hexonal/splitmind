#!/usr/bin/env python3
"""
Create a tmux session with split panes showing all active agent sessions
"""
import subprocess
import sys
import math


def get_active_sessions(project_id: str):
    """Get list of active tmux sessions for a project"""
    try:
        result = subprocess.run(
            ["tmux", "list-sessions", "-F", "#{session_name}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return []
        
        # Filter sessions for this project
        all_sessions = result.stdout.strip().split('\n')
        project_sessions = [s for s in all_sessions if s.endswith(f"-{project_id}")]
        
        return project_sessions
    except Exception:
        return []


def create_viewer_session(project_id: str):
    """Create a tmux session with split panes for all active agents"""
    
    # Get active sessions
    sessions = get_active_sessions(project_id)
    
    if not sessions:
        print(f"No active sessions found for project {project_id}")
        return False
    
    viewer_name = f"monitor-{project_id}"
    
    # Kill existing viewer session if it exists
    subprocess.run(["tmux", "kill-session", "-t", viewer_name], stderr=subprocess.DEVNULL)
    
    # Create new session with first agent
    subprocess.run([
        "tmux", "new-session", "-d", "-s", viewer_name,
        "tmux", "attach-session", "-t", sessions[0]
    ])
    
    # Add splits for remaining sessions
    if len(sessions) > 1:
        # Calculate grid layout
        count = len(sessions)
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)
        
        # Create initial splits
        for i in range(1, min(cols, len(sessions))):
            subprocess.run([
                "tmux", "split-window", "-t", f"{viewer_name}:0", "-h",
                "tmux", "attach-session", "-t", sessions[i]
            ])
        
        # Select each pane and split vertically for additional rows
        pane_idx = cols
        for col in range(cols):
            for row in range(1, rows):
                if pane_idx < len(sessions):
                    # Select the pane to split
                    subprocess.run([
                        "tmux", "select-pane", "-t", f"{viewer_name}:0.{col}"
                    ])
                    # Split vertically
                    subprocess.run([
                        "tmux", "split-window", "-t", f"{viewer_name}:0", "-v",
                        "tmux", "attach-session", "-t", sessions[pane_idx]
                    ])
                    pane_idx += 1
        
        # Tile the panes evenly
        subprocess.run([
            "tmux", "select-layout", "-t", viewer_name, "tiled"
        ])
    
    # Add status bar with project info
    subprocess.run([
        "tmux", "set-option", "-t", viewer_name, "status-left",
        f"[Monitor: {project_id}] "
    ])
    
    # Set pane borders
    subprocess.run([
        "tmux", "set-option", "-t", viewer_name, "pane-border-style", "fg=cyan"
    ])
    subprocess.run([
        "tmux", "set-option", "-t", viewer_name, "pane-active-border-style", "fg=yellow"
    ])
    
    # Add key bindings for easy navigation
    subprocess.run([
        "tmux", "bind-key", "-T", "prefix", "n", "select-pane", "-t", ":.+"
    ])
    subprocess.run([
        "tmux", "bind-key", "-T", "prefix", "p", "select-pane", "-t", ":.-"
    ])
    
    # Attach to the session
    subprocess.run(["tmux", "attach-session", "-t", viewer_name])
    
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tmux_viewer.py <project_id>")
        sys.exit(1)
    
    project_id = sys.argv[1]
    success = create_viewer_session(project_id)
    sys.exit(0 if success else 1)