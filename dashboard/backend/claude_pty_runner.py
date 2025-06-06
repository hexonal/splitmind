#!/usr/bin/env python3
"""
PTY runner for Claude to fix the raw mode issue in tmux
"""
import os
import pty
import subprocess
import sys
import select
import termios
import tty
import signal

def run_claude_with_pty(prompt_file):
    """Run Claude with a proper PTY to avoid raw mode issues"""
    
    # Read the prompt
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Start Claude process with the PTY
    process = subprocess.Popen(
        ['claude', '--dangerously-skip-permissions', '--print', prompt],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        preexec_fn=os.setsid
    )
    
    # Close slave end in parent
    os.close(slave)
    
    # Set up the terminal
    old_tty = termios.tcgetattr(sys.stdin)
    try:
        # Make stdin raw but only if it's a tty
        if sys.stdin.isatty():
            tty.setraw(sys.stdin.fileno())
        
        while process.poll() is None:
            # Check if there's data to read
            r, w, e = select.select([master, sys.stdin], [], [], 0.1)
            
            if master in r:
                try:
                    data = os.read(master, 1024)
                    if data:
                        os.write(sys.stdout.fileno(), data)
                except OSError:
                    break
            
            if sys.stdin in r:
                data = os.read(sys.stdin.fileno(), 1024)
                if data:
                    os.write(master, data)
    
    finally:
        # Restore terminal settings
        if sys.stdin.isatty():
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)
        os.close(master)
    
    return process.returncode

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: claude_pty_runner.py <prompt_file>")
        sys.exit(1)
    
    sys.exit(run_claude_with_pty(sys.argv[1]))