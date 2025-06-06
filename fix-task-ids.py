#!/usr/bin/env python3
"""
Quick script to fix task IDs with problematic characters
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard/backend'))

from dashboard.backend.project_manager import ProjectManager
from dashboard.backend.models import TaskStatus

def fix_task_ids(project_id: str):
    """Fix task IDs for a project"""
    pm = ProjectManager(project_id)
    
    # Get all tasks
    tasks = pm.get_tasks()
    
    print(f"Found {len(tasks)} tasks")
    
    # Check for problematic IDs
    for task in tasks:
        if '/' in task.id or '&' in task.id or '\\' in task.id:
            print(f"Found problematic task ID: {task.id}")
            print(f"  Title: {task.title}")
            print(f"  Branch: {task.branch}")
    
    # Save tasks - this will automatically sanitize them
    pm.save_tasks(tasks)
    print("Tasks saved with sanitized IDs")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix-task-ids.py <project_id>")
        sys.exit(1)
    
    project_id = sys.argv[1]
    fix_task_ids(project_id)