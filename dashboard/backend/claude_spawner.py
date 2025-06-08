#!/usr/bin/env python3
"""
Alternative Claude spawner that avoids Ink raw mode issues
"""

import subprocess
import sys
import os
import pty
import select
import termios
import tty

def spawn_claude_with_prompt(prompt_file):
    """Spawn Claude with a prompt using PTY to avoid raw mode issues"""
    
    # Read the prompt
    with open(prompt_file, 'r') as f:
        prompt = f.read()
    
    # Create a pseudo-terminal
    master, slave = pty.openpty()
    
    # Fork a child process
    pid = os.fork()
    
    if pid == 0:  # Child process
        # Set up the slave end as stdin/stdout/stderr
        os.close(master)
        os.dup2(slave, 0)  # stdin
        os.dup2(slave, 1)  # stdout
        os.dup2(slave, 2)  # stderr
        
        # Close the original slave fd
        if slave > 2:
            os.close(slave)
        
        # Execute Claude
        os.execvp("claude", ["claude", "--dangerously-skip-permissions"])
    
    else:  # Parent process
        os.close(slave)
        
        # Write the prompt to Claude
        os.write(master, prompt.encode('utf-8'))
        os.write(master, b'\n')
        
        # Set the terminal to raw mode
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            
            # Forward input/output between terminal and Claude
            while True:
                r, w, e = select.select([master, sys.stdin], [], [])
                
                if master in r:
                    try:
                        data = os.read(master, 1024)
                        if not data:
                            break
                        os.write(sys.stdout.fileno(), data)
                    except OSError:
                        break
                
                if sys.stdin in r:
                    data = os.read(sys.stdin.fileno(), 1024)
                    if not data:
                        break
                    os.write(master, data)
        
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            os.close(master)
            
            # Wait for child to exit
            _, status = os.waitpid(pid, 0)
            sys.exit(os.WEXITSTATUS(status))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: claude_spawner.py <prompt_file>")
        sys.exit(1)
    
    spawn_claude_with_prompt(sys.argv[1])