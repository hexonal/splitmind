#!/usr/bin/env python3
"""
Auto-format tasks.md file for Claude Orchestrator

This script ensures consistent formatting of the tasks.md file:
- Standardizes task structure
- Validates required fields
- Maintains proper spacing and formatting
"""

import re
import sys
from pathlib import Path


class TaskFormatter:
    def __init__(self, file_path="tasks.md"):
        self.file_path = Path(file_path)
        self.tasks = []
    
    def read_file(self):
        """Read the tasks.md file"""
        if not self.file_path.exists():
            print(f"Error: {self.file_path} not found")
            sys.exit(1)
        
        with open(self.file_path, 'r') as f:
            self.content = f.read()
    
    def parse_tasks(self):
        """Parse tasks from the content"""
        # Split by task headers
        task_blocks = re.split(r'^## Task:', self.content, flags=re.MULTILINE)
        
        for block in task_blocks[1:]:  # Skip the first element (header)
            lines = block.strip().split('\n')
            if not lines:
                continue
            
            task = {
                'title': lines[0].strip(),
                'task_id': None,
                'status': 'unclaimed',
                'branch': None,
                'session': 'null'
            }
            
            # Parse task fields
            for line in lines[1:]:
                line = line.strip()
                if line.startswith('- task_id:'):
                    try:
                        task['task_id'] = int(line.split(':', 1)[1].strip())
                    except ValueError:
                        pass
                elif line.startswith('- status:'):
                    task['status'] = line.split(':', 1)[1].strip()
                elif line.startswith('- branch:'):
                    task['branch'] = line.split(':', 1)[1].strip()
                elif line.startswith('- session:'):
                    task['session'] = line.split(':', 1)[1].strip()
            
            # Generate branch name if missing
            if not task['branch']:
                # Convert title to kebab-case
                branch = task['title'].lower()
                branch = re.sub(r'[^a-z0-9\s-]', '', branch)
                branch = re.sub(r'\s+', '-', branch)
                branch = re.sub(r'-+', '-', branch).strip('-')
                task['branch'] = branch
            
            self.tasks.append(task)
    
    def format_tasks(self):
        """Format tasks into standardized markdown"""
        output = ["# tasks.md\n"]
        
        # Assign task IDs to tasks that don't have them
        max_task_id = 0
        for task in self.tasks:
            if task['task_id']:
                max_task_id = max(max_task_id, task['task_id'])
        
        for task in self.tasks:
            if task['task_id'] is None:
                max_task_id += 1
                task['task_id'] = max_task_id
        
        for task in self.tasks:
            output.append(f"## Task: {task['title']}")
            output.append("")
            output.append(f"- task_id: {task['task_id']}")
            output.append(f"- status: {task['status']}")
            output.append(f"- branch: {task['branch']}")
            output.append(f"- session: {task['session']}")
            output.append("")
        
        return '\n'.join(output)
    
    def write_file(self, content):
        """Write formatted content back to file"""
        with open(self.file_path, 'w') as f:
            f.write(content)
    
    def run(self):
        """Run the formatter"""
        print(f"Formatting {self.file_path}...")
        
        self.read_file()
        self.parse_tasks()
        
        if not self.tasks:
            print("No tasks found in file")
            return
        
        formatted_content = self.format_tasks()
        self.write_file(formatted_content)
        
        print(f"✓ Formatted {len(self.tasks)} tasks")
        print(f"✓ File saved: {self.file_path}")


def main():
    """Main entry point"""
    # Check if a custom file path is provided
    file_path = sys.argv[1] if len(sys.argv) > 1 else "tasks.md"
    
    formatter = TaskFormatter(file_path)
    formatter.run()


if __name__ == "__main__":
    main()