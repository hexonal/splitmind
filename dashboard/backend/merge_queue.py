"""
Merge queue system for orderly task merging with conflict resolution
"""
import asyncio
import subprocess
import json
import os
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from .models import Task, TaskStatus
from .task_config import get_task_config


class MergeQueue:
    """
    Manages orderly merging of completed tasks
    """
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.queue: List[Task] = []
        self.merge_lock = asyncio.Lock()
        self.conflict_resolvers = {
            "package.json": self.resolve_package_json,
            ".gitignore": self.resolve_gitignore,
            "README.md": self.resolve_readme,
        }
    
    async def add_to_queue(self, task: Task, all_tasks: List[Task]):
        """
        Add completed task to merge queue
        """
        self.queue.append(task)
        
        # Sort by merge order
        self.queue.sort(key=lambda t: (
            getattr(t, 'merge_order', 999),
            -getattr(t, 'priority', 0)
        ))
        
        # Try to process queue
        await self.process_queue(all_tasks)
    
    async def process_queue(self, all_tasks: List[Task]):
        """
        Process tasks in order, respecting dependencies
        """
        async with self.merge_lock:
            processed = []
            
            for task in self.queue:
                # Check if dependencies are merged
                deps_merged = True
                if hasattr(task, 'dependencies') and task.dependencies:
                    for dep_id in task.dependencies:
                        dep_task = next((t for t in all_tasks if t.id == dep_id), None)
                        if dep_task and dep_task.status != TaskStatus.MERGED:
                            deps_merged = False
                            break
                
                if deps_merged:
                    print(f"\n🔄 Processing merge for {task.title}...")
                    success = await self.merge_task(task)
                    
                    if success:
                        processed.append(task)
                        task.status = TaskStatus.MERGED
                        task.merged_at = datetime.now()
                        print(f"✅ Successfully merged {task.title}")
                        
                        # Clean up worktree
                        await self.cleanup_worktree(task)
                    else:
                        print(f"⚠️  Failed to merge {task.title}, will retry later")
                else:
                    print(f"⏸️  Skipping {task.title} - dependencies not met")
            
            # Remove processed tasks from queue
            for task in processed:
                self.queue.remove(task)
    
    async def merge_task(self, task: Task) -> bool:
        """
        Attempt to merge a task's branch
        """
        os.chdir(self.project_path)
        
        # Ensure we're on main
        subprocess.run(["git", "checkout", "main"], capture_output=True)
        
        # Try to merge
        result = subprocess.run(
            ["git", "merge", task.branch, "--no-ff", "-m", f"Merge branch '{task.branch}'"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True
        
        # Handle conflicts
        print(f"   Merge conflicts detected, attempting auto-resolution...")
        
        # Get conflicted files
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        conflicts = []
        for line in status.stdout.split('\n'):
            if line.startswith('UU '):
                conflicts.append(line[3:])
        
        print(f"   Conflicted files: {', '.join(conflicts)}")
        
        # Try to auto-resolve conflicts
        all_resolved = True
        for file_path in conflicts:
            if file_path in self.conflict_resolvers:
                if await self.conflict_resolvers[file_path](file_path):
                    subprocess.run(["git", "add", file_path])
                    print(f"   ✓ Auto-resolved {file_path}")
                else:
                    all_resolved = False
                    print(f"   ✗ Could not auto-resolve {file_path}")
            else:
                # For other files, prefer theirs (the branch being merged)
                subprocess.run(["git", "checkout", "--theirs", file_path])
                subprocess.run(["git", "add", file_path])
                print(f"   ✓ Accepted changes from branch for {file_path}")
        
        if all_resolved:
            # Complete the merge
            subprocess.run(["git", "commit", "--no-edit"])
            return True
        else:
            # Abort the merge
            subprocess.run(["git", "merge", "--abort"])
            return False
    
    async def cleanup_worktree(self, task: Task):
        """
        Clean up worktree after successful merge
        """
        try:
            worktree_path = self.project_path / "worktrees" / task.branch
            
            if worktree_path.exists():
                # Remove the worktree
                subprocess.run(
                    ["git", "worktree", "remove", str(worktree_path), "--force"],
                    cwd=self.project_path,
                    capture_output=True
                )
                print(f"🧹 Cleaned up worktree for {task.title}")
                
                # Also prune worktree list
                subprocess.run(
                    ["git", "worktree", "prune"],
                    cwd=self.project_path,
                    capture_output=True
                )
        except Exception as e:
            print(f"⚠️  Error cleaning up worktree for {task.title}: {e}")
    
    async def resolve_package_json(self, file_path: str) -> bool:
        """
        Intelligently merge package.json files
        """
        try:
            # Get the three versions
            base = subprocess.run(
                ["git", "show", ":1:" + file_path],
                capture_output=True,
                text=True
            ).stdout
            
            ours = subprocess.run(
                ["git", "show", ":2:" + file_path],
                capture_output=True,
                text=True
            ).stdout
            
            theirs = subprocess.run(
                ["git", "show", ":3:" + file_path],
                capture_output=True,
                text=True
            ).stdout
            
            # Parse JSON
            base_json = json.loads(base) if base else {}
            our_json = json.loads(ours)
            their_json = json.loads(theirs)
            
            # Merge strategy: combine dependencies
            merged = our_json.copy()
            
            # Merge dependencies
            for dep_type in ['dependencies', 'devDependencies']:
                merged[dep_type] = {
                    **base_json.get(dep_type, {}),
                    **our_json.get(dep_type, {}),
                    **their_json.get(dep_type, {})
                }
            
            # Merge scripts (prefer newer)
            merged['scripts'] = {
                **our_json.get('scripts', {}),
                **their_json.get('scripts', {})
            }
            
            # Write merged file
            with open(file_path, 'w') as f:
                json.dump(merged, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"   Error resolving package.json: {e}")
            return False
    
    async def resolve_gitignore(self, file_path: str) -> bool:
        """
        Merge .gitignore by taking union of all entries
        """
        try:
            # Get all versions
            ours = subprocess.run(
                ["git", "show", ":2:" + file_path],
                capture_output=True,
                text=True
            ).stdout
            
            theirs = subprocess.run(
                ["git", "show", ":3:" + file_path],
                capture_output=True,
                text=True
            ).stdout
            
            # Combine unique lines
            all_lines = set(ours.split('\n')) | set(theirs.split('\n'))
            
            # Group by category
            categories = {}
            current_category = "General"
            
            for line in sorted(all_lines):
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    current_category = line
                else:
                    if current_category not in categories:
                        categories[current_category] = []
                    categories[current_category].append(line)
            
            # Write organized file
            with open(file_path, 'w') as f:
                for category, entries in categories.items():
                    if category != "General":
                        f.write(f"\n{category}\n")
                    for entry in sorted(entries):
                        f.write(f"{entry}\n")
            
            return True
            
        except Exception as e:
            print(f"   Error resolving .gitignore: {e}")
            return False
    
    async def resolve_readme(self, file_path: str) -> bool:
        """
        Merge README.md by appending new sections
        """
        try:
            # For now, just take theirs (the newer content)
            subprocess.run(["git", "checkout", "--theirs", file_path])
            return True
            
        except Exception as e:
            print(f"   Error resolving README.md: {e}")
            return False