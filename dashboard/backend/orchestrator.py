"""
Orchestrator management for spawning and managing AI agents
"""
import asyncio
import subprocess
import os
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from .models import Task, TaskStatus, OrchestratorConfig, WebSocketMessage
from .config import config_manager
from .project_manager import ProjectManager
from .websocket_manager import WebSocketManager


class OrchestratorManager:
    """Manages the AI agent orchestrator"""
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.config = config_manager.get_orchestrator_config()
        self.running = False
        self.current_project_id: Optional[str] = None
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    def update_config(self, config: OrchestratorConfig):
        """Update orchestrator configuration"""
        self.config = config
    
    def is_running(self) -> bool:
        """Check if orchestrator is running"""
        return self.running
    
    async def start(self, project_id: str):
        """Start the orchestrator for a project"""
        if self.running:
            raise ValueError("Orchestrator is already running")
        
        # Verify project exists
        project = config_manager.get_project(project_id)
        if not project:
            raise ValueError(f"Project '{project_id}' not found")
        
        self.current_project_id = project_id
        self.running = True
        self._stop_event.clear()
        
        # Start the orchestrator loop
        self._task = asyncio.create_task(self._orchestrator_loop())
        
        # Notify clients
        await self.ws_manager.broadcast(WebSocketMessage(
            type="orchestrator_started",
            project_id=project_id,
            data={"status": "running"}
        ))
    
    async def stop(self):
        """Stop the orchestrator"""
        if not self.running:
            return
        
        self.running = False
        self._stop_event.set()
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        # Notify clients
        await self.ws_manager.broadcast(WebSocketMessage(
            type="orchestrator_stopped",
            project_id=self.current_project_id,
            data={"status": "stopped"}
        ))
        
        self.current_project_id = None
    
    async def _orchestrator_loop(self):
        """Main orchestrator loop"""
        while self.running:
            try:
                if self.config.enabled:
                    await self._spawn_agents()
                    if self.config.auto_merge:
                        await self._merge_completed_work()
                
                # Wait for interval or stop event
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self.config.auto_spawn_interval
                    )
                    break  # Stop event was set
                except asyncio.TimeoutError:
                    pass  # Continue loop
                    
            except Exception as e:
                print(f"Orchestrator error: {e}")
                await self.ws_manager.broadcast(WebSocketMessage(
                    type="orchestrator_error",
                    project_id=self.current_project_id,
                    data={"error": str(e)}
                ))
    
    async def _spawn_agents(self):
        """Spawn agents for unclaimed tasks"""
        if not self.current_project_id:
            return
        
        try:
            pm = ProjectManager(self.current_project_id)
            project = pm.project
            tasks = pm.get_tasks()
            agents = pm.get_agents()
            
            # Count active agents
            active_agents = len([a for a in agents if a.status == "running"])
            
            # Check if we can spawn more agents
            available_slots = min(
                self.config.max_concurrent_agents - active_agents,
                project.max_agents - active_agents
            )
            
            if available_slots <= 0:
                return
            
            # Find unclaimed tasks
            unclaimed_tasks = [t for t in tasks if t.status == TaskStatus.UNCLAIMED]
            
            # Spawn agents for unclaimed tasks
            for task in unclaimed_tasks[:available_slots]:
                await self._spawn_agent_for_task(pm, task)
        
        except Exception as e:
            print(f"Error spawning agents: {e}")
    
    async def _spawn_agent_for_task(self, pm: ProjectManager, task: Task):
        """Spawn a single agent for a task"""
        try:
            os.chdir(pm.project_path)
            
            # Create worktree
            worktree_path = pm.worktrees_dir / task.branch
            if not worktree_path.exists():
                subprocess.run([
                    "git", "worktree", "add",
                    str(worktree_path),
                    "-b", task.branch
                ], check=True)
            
            # Build agent prompt
            prompt = f"Create a plan, review your plan and choose the best option, then accomplish the following task and commit the changes: {task.title}"
            if task.description:
                prompt += f"\\n\\nDescription: {task.description}"
            
            # Generate session name
            session_name = f"{pm.project.id}-{task.branch}"[:20]  # Limit length
            
            # Launch agent in tmux
            claude_cmd = f'cd {worktree_path} && claude "{prompt}" --allowedTools "Edit,Write,Bash,Replace"'
            
            subprocess.run([
                "tmux", "new-session", "-d",
                "-s", session_name,
                "-c", str(worktree_path),
                claude_cmd
            ], check=True)
            
            # Update task status
            task.status = TaskStatus.CLAIMED
            task.session = session_name
            pm.update_task(task.id, {
                "status": TaskStatus.CLAIMED,
                "session": session_name
            })
            
            # Notify clients
            await self.ws_manager.broadcast(WebSocketMessage(
                type="agent_spawned",
                project_id=self.current_project_id,
                data={
                    "task_id": task.id,
                    "session": session_name,
                    "branch": task.branch
                }
            ))
            
            print(f"✅ Spawned agent for task: {task.title}")
            
        except Exception as e:
            print(f"Error spawning agent for task {task.title}: {e}")
            await self.ws_manager.broadcast(WebSocketMessage(
                type="agent_spawn_failed",
                project_id=self.current_project_id,
                data={
                    "task_id": task.id,
                    "error": str(e)
                }
            ))
    
    async def _merge_completed_work(self):
        """Auto-merge completed work"""
        if not self.current_project_id:
            return
        
        try:
            pm = ProjectManager(self.current_project_id)
            tasks = pm.get_tasks()
            
            # Find completed tasks
            completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
            
            for task in completed_tasks:
                # Run auto-merge script
                os.chdir(pm.project_path)
                
                result = subprocess.run([
                    "python",
                    str(Path(__file__).parent.parent.parent / "scripts" / "auto-merge.py"),
                    task.branch,
                    "--strategy", self.config.merge_strategy,
                    "--json"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Update task status
                    pm.update_task(task.id, {
                        "status": TaskStatus.MERGED,
                        "merged_at": datetime.now()
                    })
                    
                    # Notify clients
                    await self.ws_manager.broadcast(WebSocketMessage(
                        type="task_merged",
                        project_id=self.current_project_id,
                        data={
                            "task_id": task.id,
                            "branch": task.branch
                        }
                    ))
                    
                    print(f"✅ Auto-merged task: {task.title}")
                else:
                    print(f"Failed to auto-merge task {task.title}: {result.stderr}")
        
        except Exception as e:
            print(f"Error during auto-merge: {e}")