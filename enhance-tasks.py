#!/usr/bin/env python3
"""
Enhance existing tasks with file ownership and merge order
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent / "dashboard"))

from dashboard.backend.project_manager import ProjectManager
from dashboard.backend.task_config import TASK_DEFINITIONS


def enhance_tasks(project_id: str):
    """
    Enhance tasks with file ownership and merge order from task definitions
    """
    pm = ProjectManager(project_id)
    tasks = pm.get_tasks()
    
    updated = False
    
    for task in tasks:
        # Get task configuration
        task_key = task.id
        if "-" in task_key:
            # Remove project prefix
            parts = task_key.split("-")
            if len(parts) > 2:
                task_key = "-".join(parts[2:])
            else:
                task_key = parts[-1]
        
        if task_key in TASK_DEFINITIONS:
            config = TASK_DEFINITIONS[task_key]
            
            # Update task with configuration
            if not hasattr(task, 'merge_order') or task.merge_order == 0:
                task.merge_order = config.get('merge_order', 0)
                updated = True
                
            if not hasattr(task, 'exclusive_files') or not task.exclusive_files:
                task.exclusive_files = config.get('exclusive_files', [])
                updated = True
                
            if not hasattr(task, 'shared_files') or not task.shared_files:
                task.shared_files = config.get('shared_files', [])
                updated = True
                
            if not hasattr(task, 'initialization_deps') or not task.initialization_deps:
                task.initialization_deps = config.get('initialization_deps', [])
                updated = True
            
            print(f"Enhanced task: {task.title}")
            print(f"  - Merge order: {task.merge_order}")
            print(f"  - Exclusive files: {len(task.exclusive_files)} patterns")
            print(f"  - Shared files: {len(task.shared_files)} files")
            print(f"  - Init deps: {task.initialization_deps}")
    
    if updated:
        pm.save_tasks(tasks)
        print("\n✅ Tasks enhanced with file ownership and merge order")
    else:
        print("\n✓ Tasks already have file ownership configured")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: enhance-tasks.py <project_id>")
        print("Example: enhance-tasks.py splitmind-ai")
        sys.exit(1)
    
    project_id = sys.argv[1]
    enhance_tasks(project_id)