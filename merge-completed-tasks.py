#!/usr/bin/env python3
"""
Merge all completed tasks in order
"""
import subprocess
import json
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard/backend'))
from dashboard.backend.project_manager import ProjectManager
from dashboard.backend.models import TaskStatus

def merge_completed_tasks(project_id: str):
    """Merge all completed tasks in order"""
    pm = ProjectManager(project_id)
    tasks = pm.get_tasks()
    
    # Get completed tasks sorted by task_id
    completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    completed_tasks.sort(key=lambda x: x.task_id)
    
    if not completed_tasks:
        print("No completed tasks to merge")
        return
    
    print(f"Found {len(completed_tasks)} completed tasks to merge")
    
    # Change to project directory
    os.chdir(pm.project_path)
    
    # Ensure we're on main branch
    result = subprocess.run(["git", "checkout", "main"], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to checkout main: {result.stderr}")
        return
    
    # Merge each task in order
    for task in completed_tasks:
        print(f"\n{'='*60}")
        print(f"Merging Task {task.task_id}: {task.title}")
        print(f"Branch: {task.branch}")
        
        # Check if branch exists
        branch_check = subprocess.run(
            ["git", "rev-parse", "--verify", task.branch],
            capture_output=True
        )
        
        if branch_check.returncode != 0:
            # Try in worktree
            worktree_path = pm.project_path / "worktrees" / task.branch
            if worktree_path.exists():
                print(f"  Pushing branch from worktree...")
                push_result = subprocess.run(
                    ["git", "push", "origin", f"HEAD:{task.branch}"],
                    cwd=str(worktree_path),
                    capture_output=True,
                    text=True
                )
                if push_result.returncode != 0:
                    print(f"  ❌ Failed to push from worktree: {push_result.stderr}")
                    continue
                
                # Fetch in main repo
                subprocess.run(["git", "fetch", "origin", task.branch], capture_output=True)
                subprocess.run(["git", "branch", task.branch, f"origin/{task.branch}"], capture_output=True)
            else:
                print(f"  ❌ Branch {task.branch} not found")
                continue
        
        # Attempt merge
        print(f"  Merging {task.branch}...")
        merge_result = subprocess.run(
            ["git", "merge", task.branch, "--no-ff", "-m", f"Merge task: {task.title}"],
            capture_output=True,
            text=True
        )
        
        if merge_result.returncode == 0:
            print(f"  ✅ Successfully merged {task.title}")
            
            # Update task status
            pm.update_task(task.id, {"status": TaskStatus.MERGED})
            print(f"  ✅ Updated task status to MERGED")
            
            # Clean up worktree if exists
            worktree_path = pm.project_path / "worktrees" / task.branch
            if worktree_path.exists():
                subprocess.run(
                    ["git", "worktree", "remove", str(worktree_path), "--force"],
                    capture_output=True
                )
                print(f"  🧹 Cleaned up worktree")
        else:
            print(f"  ❌ Merge failed: {merge_result.stderr}")
            
            # Check for conflicts
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if "UU" in status_result.stdout:
                print("  ⚠️  Merge conflicts detected")
                # Abort the merge
                subprocess.run(["git", "merge", "--abort"], capture_output=True)
                print("  🔄 Aborted merge due to conflicts")
    
    # Show final status
    print(f"\n{'='*60}")
    print("Merge summary:")
    
    # Reload tasks to get updated statuses
    tasks = pm.get_tasks()
    merged_count = len([t for t in tasks if t.status == TaskStatus.MERGED])
    completed_count = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    
    print(f"  Merged tasks: {merged_count}")
    print(f"  Still completed: {completed_count}")
    
    if completed_count > 0:
        print("\nTasks still in completed status:")
        for task in tasks:
            if task.status == TaskStatus.COMPLETED:
                print(f"  - Task {task.task_id}: {task.title}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python merge-completed-tasks.py <project_id>")
        sys.exit(1)
    
    project_id = sys.argv[1]
    merge_completed_tasks(project_id)