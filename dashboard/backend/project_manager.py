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
# print(f"🏗️  Creating new ProjectManager instance for {project_id}")
        self.project = config_manager.get_project(project_id)
        if not self.project:
            raise ValueError(f"Project '{project_id}' not found")
        
        self.project_path = Path(self.project.path)
        self.splitmind_dir = self.project_path / ".splitmind"
        self.tasks_file = self.splitmind_dir / "tasks.md"
        self.worktrees_dir = self.project_path / "worktrees"
        self.git_dir = self.project_path / ".git"
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.splitmind_dir.mkdir(exist_ok=True)
        self.worktrees_dir.mkdir(exist_ok=True)
    
    def _sanitize_task_id(self, task_id: str) -> str:
        """Sanitize task ID to avoid URL routing issues"""
        # Replace problematic characters
        sanitized = task_id.replace('/', '-')
        sanitized = sanitized.replace('\\', '-')
        sanitized = sanitized.replace('&', 'and')
        return sanitized

    def get_tasks(self) -> List[Task]:
        """Read and parse tasks from tasks.md"""
        if not self.tasks_file.exists():
            return []
        
        tasks = []
        current_task = None
        max_task_id = 0
        
        with open(self.tasks_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith("## Task:"):
                    # Save previous task
                    if current_task:
                        tasks.append(current_task)
                    
                    # Start new task
                    title = line.replace("## Task:", "").strip()
                    # Generate sanitized ID
                    task_id = title.lower().replace(" ", "-")
                    task_id = self._sanitize_task_id(task_id)
                    current_task = {
                        "id": task_id,
                        "task_id": None,
                        "title": title,
                        "status": TaskStatus.UNCLAIMED,
                        "branch": None,
                        "session": None,
                        "description": None,
                        "dependencies": [],
                        "priority": 0,
                        "merge_order": 0,
                        "exclusive_files": [],
                        "shared_files": [],
                        "initialization_deps": []
                    }
                
                elif current_task and line.startswith("- "):
                    # Parse task properties
                    if line.startswith("- task_id:"):
                        try:
                            task_id = int(line.replace("- task_id:", "").strip())
                            current_task["task_id"] = task_id
                            max_task_id = max(max_task_id, task_id)
                        except ValueError:
                            pass
                    
                    elif line.startswith("- status:"):
                        status_str = line.replace("- status:", "").strip()
                        try:
                            current_task["status"] = TaskStatus(status_str)
                        except ValueError:
                            current_task["status"] = TaskStatus.UNCLAIMED
                    
                    elif line.startswith("- branch:"):
                        branch = line.replace("- branch:", "").strip()
                        if branch != "null":
                            # Sanitize branch name as well
                            branch = self._sanitize_task_id(branch)
                            current_task["branch"] = branch
                    
                    elif line.startswith("- session:"):
                        session = line.replace("- session:", "").strip()
                        if session != "null":
                            current_task["session"] = session
                    
                    elif line.startswith("- description:"):
                        current_task["description"] = line.replace("- description:", "").strip()
                    
                    elif line.startswith("- prompt:"):
                        current_task["prompt"] = line.replace("- prompt:", "").strip()
                    
                    elif line.startswith("- dependencies:"):
                        deps_str = line.replace("- dependencies:", "").strip()
                        if deps_str and deps_str != "[]":
                            current_task["dependencies"] = [d.strip() for d in deps_str.strip("[]").split(",") if d.strip()]
                    
                    elif line.startswith("- priority:"):
                        try:
                            current_task["priority"] = int(line.replace("- priority:", "").strip())
                        except ValueError:
                            current_task["priority"] = 0
                    
                    elif line.startswith("- merge_order:"):
                        try:
                            current_task["merge_order"] = int(line.replace("- merge_order:", "").strip())
                        except ValueError:
                            current_task["merge_order"] = 0
                    
                    elif line.startswith("- exclusive_files:"):
                        files_str = line.replace("- exclusive_files:", "").strip()
                        if files_str and files_str != "[]":
                            current_task["exclusive_files"] = [f.strip() for f in files_str.strip("[]").split(",") if f.strip()]
                    
                    elif line.startswith("- shared_files:"):
                        files_str = line.replace("- shared_files:", "").strip()
                        if files_str and files_str != "[]":
                            current_task["shared_files"] = [f.strip() for f in files_str.strip("[]").split(",") if f.strip()]
                    
                    elif line.startswith("- initialization_deps:"):
                        deps_str = line.replace("- initialization_deps:", "").strip()
                        if deps_str and deps_str != "[]":
                            current_task["initialization_deps"] = [d.strip() for d in deps_str.strip("[]").split(",") if d.strip()]
        
        # Don't forget the last task
        if current_task:
            tasks.append(current_task)
        
        # Assign task IDs to tasks that don't have them
        for task in tasks:
            if task.get("task_id") is None:
                max_task_id += 1
                task["task_id"] = max_task_id
        
        # Convert to Task models
        result_tasks = [Task(**task) for task in tasks if task.get("branch")]
        
        # Sort tasks by priority and task_id to maintain consistent order
        result_tasks.sort(key=lambda t: (t.priority if t.priority is not None else 10, t.task_id or 0))
        
        # print(f"📖 Loaded {len(result_tasks)} tasks from database")
        # for task in result_tasks:
        #     print(f"📖 Loaded {task.title}: status = {task.status}")
        return result_tasks
    
    def save_tasks(self, tasks: List[Task]):
        """Save tasks back to tasks.md"""
        content = ["# tasks.md\n"]
        
        # print(f"💾 Saving {len(tasks)} tasks to database...")
        
        # Sort tasks before saving to maintain consistent order
        sorted_tasks = sorted(tasks, key=lambda t: (t.priority if t.priority is not None else 10, t.task_id or 0))
        
        for task in sorted_tasks:
            content.append(f"\n## Task: {task.title}\n")
            content.append(f"- task_id: {task.task_id}")
            # Always save the enum value, not the enum object
            status_value = task.status.value if hasattr(task.status, 'value') else str(task.status)
            content.append(f"- status: {status_value}")
            # print(f"💾 Saving {task.title}: status = {status_value}")
            content.append(f"- branch: {task.branch}")
            content.append(f"- session: {task.session or 'null'}")
            if task.description:
                content.append(f"- description: {task.description}")
            if task.prompt:
                content.append(f"- prompt: {task.prompt}")
            if hasattr(task, 'dependencies') and task.dependencies:
                content.append(f"- dependencies: [{', '.join(task.dependencies)}]")
            if hasattr(task, 'priority') and task.priority > 0:
                content.append(f"- priority: {task.priority}")
            if hasattr(task, 'merge_order') and task.merge_order > 0:
                content.append(f"- merge_order: {task.merge_order}")
            if hasattr(task, 'exclusive_files') and task.exclusive_files:
                content.append(f"- exclusive_files: [{', '.join(task.exclusive_files)}]")
            if hasattr(task, 'shared_files') and task.shared_files:
                content.append(f"- shared_files: [{', '.join(task.shared_files)}]")
            if hasattr(task, 'initialization_deps') and task.initialization_deps:
                content.append(f"- initialization_deps: [{', '.join(task.initialization_deps)}]")
            content.append("")
        
        with open(self.tasks_file, 'w') as f:
            f.write('\n'.join(content))
    
    def add_task(self, title: str, description: Optional[str] = None, 
                 dependencies: Optional[List[str]] = None, priority: int = 0,
                 prompt: Optional[str] = None) -> Task:
        """Add a new task"""
        tasks = self.get_tasks()
        
        # Find the highest task_id
        max_task_id = 0
        for t in tasks:
            if t.task_id:
                max_task_id = max(max_task_id, t.task_id)
        
        # Create task with auto-incremented task_id
        new_task_id = max_task_id + 1
        
        # Generate simple branch name: task-{number}
        branch = f"task-{new_task_id}"
        # Use simple ID format: task_number-project_id
        simple_id = f"{new_task_id}-{self.project.id}"
        task = Task(
            id=simple_id,
            task_id=new_task_id,
            title=title,
            description=description,
            prompt=prompt,
            branch=branch,
            status=TaskStatus.UNCLAIMED,
            dependencies=dependencies or [],
            priority=priority
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
                        # Convert status strings to TaskStatus enum
                        if key == 'status' and isinstance(value, str):
                            from .models import TaskStatus
                            try:
                                value = TaskStatus(value)
                            except ValueError:
                                pass  # Keep original value if invalid
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
                if task.session:
                    # Check if any session matches or starts with the task session name (handles tmux truncation)
                    matching_session = None
                    
                    # First try exact match
                    if task.session in sessions:
                        matching_session = task.session
                    else:
                        # Then try to find a session that starts with the task's session name
                        # but be more specific by checking branch name too
                        for session in sessions:
                            if session.startswith(task.session[:20]) and task.branch in session:
                                matching_session = session
                                break
                    
                    if matching_session:
                        # Check status file for real-time status
                        status_file = Path(f"/tmp/splitmind-status/{matching_session}.status")
                        agent_status = "running"
                        if status_file.exists():
                            file_status = status_file.read_text().strip()
                            if file_status == "COMPLETED":
                                agent_status = "completed"
                            elif file_status == "RUNNING":
                                agent_status = "running"
                        
                        agent = Agent(
                            id=matching_session,
                            session_name=matching_session,
                            task_id=task.id,
                            task_title=task.title,
                            branch=task.branch,
                            status=agent_status,
                            progress=self._estimate_progress(task),
                            started_at=getattr(task, 'created_at', datetime.now()),
                            logs=[]
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
            TaskStatus.UP_NEXT: 10,
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
            elif task.status == TaskStatus.UP_NEXT:
                stats.up_next_tasks += 1
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
    
    def is_git_repo(self) -> bool:
        """Check if the project path is a Git repository"""
        return self.git_dir.exists() and self.git_dir.is_dir()
    
    def get_git_status(self) -> Dict[str, any]:
        """Get Git repository status"""
        if not self.is_git_repo():
            return {"is_git_repo": False}
        
        status = {"is_git_repo": True}
        
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                check=True
            )
            status["current_branch"] = result.stdout.strip()
            
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                check=True
            )
            status["has_changes"] = bool(result.stdout.strip())
            
            # Get remote URL if exists
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True,
                    check=True
                )
                status["remote_url"] = result.stdout.strip()
            except subprocess.CalledProcessError:
                status["remote_url"] = None
                
        except subprocess.CalledProcessError as e:
            status["error"] = f"Error getting Git info: {str(e)}"
        
        return status