"""
Project-specific operations for SplitMind
"""
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from .models import Task, TaskStatus, Agent, ProjectStats
from .config import config_manager


class ProjectManager:
    """Manages operations for a specific project"""
    
    def __init__(self, project_id: str):
        self.project = config_manager.get_project(project_id)
        if not self.project:
            raise ValueError(f"Project '{project_id}' not found")
        
        self.project_path = Path(self.project.path)
        self.splitmind_dir = self.project_path / ".splitmind"
        self.tasks_file = self.splitmind_dir / "tasks.md"
        self.worktrees_dir = self.project_path / "worktrees"
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.splitmind_dir.mkdir(exist_ok=True)
        self.worktrees_dir.mkdir(exist_ok=True)
    
    def get_tasks(self) -> List[Task]:
        """Read and parse tasks from tasks.md"""
        if not self.tasks_file.exists():
            return []
        
        tasks = []
        current_task = None
        
        with open(self.tasks_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith("## Task:"):
                    # Save previous task
                    if current_task:
                        tasks.append(current_task)
                    
                    # Start new task
                    title = line.replace("## Task:", "").strip()
                    current_task = {
                        "id": title.lower().replace(" ", "-"),
                        "title": title,
                        "status": TaskStatus.UNCLAIMED,
                        "branch": None,
                        "session": None,
                        "description": None
                    }
                
                elif current_task and line.startswith("- "):
                    # Parse task properties
                    if line.startswith("- status:"):
                        status_str = line.replace("- status:", "").strip()
                        try:
                            current_task["status"] = TaskStatus(status_str)
                        except ValueError:
                            current_task["status"] = TaskStatus.UNCLAIMED
                    
                    elif line.startswith("- branch:"):
                        branch = line.replace("- branch:", "").strip()
                        if branch != "null":
                            current_task["branch"] = branch
                    
                    elif line.startswith("- session:"):
                        session = line.replace("- session:", "").strip()
                        if session != "null":
                            current_task["session"] = session
                    
                    elif line.startswith("- description:"):
                        current_task["description"] = line.replace("- description:", "").strip()
        
        # Don't forget the last task
        if current_task:
            tasks.append(current_task)
        
        # Convert to Task models
        return [Task(**task) for task in tasks if task.get("branch")]
    
    def save_tasks(self, tasks: List[Task]):
        """Save tasks back to tasks.md"""
        content = ["# tasks.md\n"]
        
        for task in tasks:
            content.append(f"\n## Task: {task.title}\n")
            content.append(f"- status: {task.status.value}")
            content.append(f"- branch: {task.branch}")
            content.append(f"- session: {task.session or 'null'}")
            if task.description:
                content.append(f"- description: {task.description}")
            content.append("")
        
        with open(self.tasks_file, 'w') as f:
            f.write('\n'.join(content))
    
    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """Add a new task"""
        tasks = self.get_tasks()
        
        # Generate branch name
        branch = title.lower()
        branch = ''.join(c if c.isalnum() or c in '-_ ' else '' for c in branch)
        branch = branch.replace(' ', '-')
        branch = '-'.join(filter(None, branch.split('-')))
        
        # Create task
        task = Task(
            id=f"{branch}-{len(tasks)}",
            title=title,
            description=description,
            branch=branch,
            status=TaskStatus.UNCLAIMED
        )
        
        tasks.append(task)
        self.save_tasks(tasks)
        
        return task
    
    def update_task(self, task_id: str, updates: dict) -> Task:
        """Update a task"""
        tasks = self.get_tasks()
        
        for i, task in enumerate(tasks):
            if task.id == task_id:
                # Update fields
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                
                task.updated_at = datetime.now()
                tasks[i] = task
                self.save_tasks(tasks)
                return task
        
        raise ValueError(f"Task '{task_id}' not found")
    
    def delete_task(self, task_id: str):
        """Delete a task"""
        tasks = self.get_tasks()
        tasks = [t for t in tasks if t.id != task_id]
        self.save_tasks(tasks)
    
    def get_agents(self) -> List[Agent]:
        """Get running agents for this project"""
        agents = []
        
        try:
            # Get tmux sessions
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True,
                check=True
            )
            
            sessions = result.stdout.strip().split('\n')
            
            # Match sessions to tasks
            tasks = self.get_tasks()
            for task in tasks:
                if task.session and task.session in sessions:
                    agent = Agent(
                        id=task.session,
                        session_name=task.session,
                        task_id=task.id,
                        task_title=task.title,
                        branch=task.branch,
                        status="running" if task.status != TaskStatus.COMPLETED else "completed",
                        progress=self._estimate_progress(task)
                    )
                    agents.append(agent)
        
        except subprocess.CalledProcessError:
            # tmux not running or no sessions
            pass
        
        return agents
    
    def _estimate_progress(self, task: Task) -> int:
        """Estimate task progress based on status"""
        status_progress = {
            TaskStatus.UNCLAIMED: 0,
            TaskStatus.CLAIMED: 10,
            TaskStatus.IN_PROGRESS: 50,
            TaskStatus.COMPLETED: 90,
            TaskStatus.MERGED: 100
        }
        return status_progress.get(task.status, 0)
    
    def get_stats(self) -> ProjectStats:
        """Get project statistics"""
        tasks = self.get_tasks()
        agents = self.get_agents()
        
        stats = ProjectStats(
            total_tasks=len(tasks),
            active_agents=len([a for a in agents if a.status == "running"])
        )
        
        # Count tasks by status
        for task in tasks:
            if task.status == TaskStatus.UNCLAIMED:
                stats.unclaimed_tasks += 1
            elif task.status == TaskStatus.CLAIMED:
                stats.claimed_tasks += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                stats.in_progress_tasks += 1
            elif task.status == TaskStatus.COMPLETED:
                stats.completed_tasks += 1
            elif task.status == TaskStatus.MERGED:
                stats.merged_tasks += 1
        
        return stats
    
    def get_worktrees(self) -> List[Dict[str, str]]:
        """Get git worktrees for this project"""
        worktrees = []
        
        try:
            os.chdir(self.project_path)
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            
            current_worktree = {}
            for line in result.stdout.strip().split('\n'):
                if line.startswith("worktree"):
                    if current_worktree:
                        worktrees.append(current_worktree)
                    current_worktree = {"path": line.split()[1]}
                elif line.startswith("branch"):
                    current_worktree["branch"] = line.split()[1].replace("refs/heads/", "")
            
            if current_worktree:
                worktrees.append(current_worktree)
        
        except subprocess.CalledProcessError:
            pass
        
        return worktrees