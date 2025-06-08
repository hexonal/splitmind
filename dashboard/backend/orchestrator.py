"""
Orchestrator management for spawning and managing AI agents
"""
import asyncio
import subprocess
import os
import shutil
import time
import threading
import tempfile
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import redis
import json

from .models import Task, TaskStatus, OrchestratorConfig, WebSocketMessage
from .config import config_manager
from .project_manager import ProjectManager
from .websocket_manager import WebSocketManager
from .task_config import can_tasks_run_concurrently, get_task_config, get_initialization_script
from .merge_queue import MergeQueue


class OrchestratorManager:
    """Manages the AI agent orchestrator"""
    
    def __init__(self, ws_manager: WebSocketManager):
        self.ws_manager = ws_manager
        self.config = config_manager.get_orchestrator_config()
        self.running = False
        self.current_project_id: Optional[str] = None
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self.merge_queue: Optional[MergeQueue] = None
        
        # Status file directory
        self.status_dir = Path("/tmp/splitmind-status")
        self._ensure_status_dir()
    
    def _ensure_status_dir(self):
        """Ensure status directory exists and clean up old files"""
        self.status_dir.mkdir(exist_ok=True)
        # Clean up any existing status files on startup
        for status_file in self.status_dir.glob("*.status"):
            try:
                status_file.unlink()
            except Exception as e:
                print(f"Error removing old status file {status_file}: {e}")
    
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
        
        # Initialize merge queue for the project with status update callback
        async def update_task_status(task_id: str, status: TaskStatus):
            pm = ProjectManager(project_id)
            pm.update_task(task_id, {"status": status})
            await self.ws_manager.broadcast(WebSocketMessage(
                type="task_status_changed",
                project_id=project_id,
                data={
                    "task_id": task_id,
                    "status": status
                }
            ))
        
        self.merge_queue = MergeQueue(project.path, update_task_status)
        
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
        
        # Clean up status files
        for status_file in self.status_dir.glob("*.status"):
            try:
                status_file.unlink()
            except Exception as e:
                print(f"Error removing status file {status_file}: {e}")
        
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
                    # Get current state once and pass it through
                    pm = ProjectManager(self.current_project_id)
                    project = pm.project
                    tasks = pm.get_tasks()
                    agents = pm.get_agents()
                    
                    await self._manage_task_queue(pm, project, tasks, agents)
                    # Reload tasks after queue management changes
                    tasks = pm.get_tasks()
                    await self._spawn_agents(pm, project, tasks, agents)
                    await self._check_agent_status()
                    # Check for any completed tasks that need auto-merging
                    await self._check_and_merge_completed_tasks(pm, tasks)
                
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
    
    async def _manage_task_queue(self, pm: ProjectManager, project, tasks, agents):
        """Manage the task queue to maintain UP_NEXT tasks based on available slots"""
        if not self.current_project_id:
            return
        
        try:
            
            # Count current task statuses
            active_agents = len([a for a in agents if a.status == "running"])
            up_next_tasks = len([t for t in tasks if t.status == TaskStatus.UP_NEXT])
            in_progress_tasks = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
            unclaimed_tasks_count = len([t for t in tasks if t.status == TaskStatus.UNCLAIMED])
            
            print(f"📊 Current task counts:")
            print(f"   UNCLAIMED: {unclaimed_tasks_count}")
            print(f"   UP_NEXT: {up_next_tasks}")
            print(f"   IN_PROGRESS: {in_progress_tasks}")
            print(f"   Active agents: {active_agents}")
            
            # Calculate how many UP_NEXT slots we should maintain
            max_total_active = min(self.config.max_concurrent_agents, project.max_agents)
            
            # We want to maintain UP_NEXT tasks equal to max_agents (always keep queue full)
            target_up_next = max_total_active
            
            print(f"📊 Queue management:")
            print(f"   Max agents: {max_total_active}")
            print(f"   Target UP_NEXT: {target_up_next}")
            print(f"   Current UP_NEXT: {up_next_tasks}")
            print(f"   Current IN_PROGRESS: {in_progress_tasks}")
            
            if up_next_tasks < target_up_next:
                # Need to promote tasks from UNCLAIMED to UP_NEXT
                unclaimed_tasks = [t for t in tasks if t.status == TaskStatus.UNCLAIMED]
                
                # Filter out tasks with unmet dependencies
                eligible_tasks = []
                for task in unclaimed_tasks:
                    if hasattr(task, 'dependencies') and task.dependencies:
                        all_deps_met = True
                        for dep_id in task.dependencies:
                            dep_task = next((t for t in tasks if t.id == dep_id), None)
                            if dep_task and dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.MERGED]:
                                all_deps_met = False
                                break
                        if all_deps_met:
                            eligible_tasks.append(task)
                    else:
                        eligible_tasks.append(task)
                
                # Sort by priority and merge order
                eligible_tasks.sort(
                    key=lambda t: (getattr(t, 'priority', 10), -getattr(t, 'merge_order', 0))
                )
                
                # Promote tasks to UP_NEXT
                tasks_to_promote = min(target_up_next - up_next_tasks, len(eligible_tasks))
                if tasks_to_promote > 0:
                    print(f"📋 Need to promote {tasks_to_promote} tasks from TODO to UP_NEXT")
                    
                for i in range(tasks_to_promote):
                    task = eligible_tasks[i]
                    print(f"📋 Promoting task '{task.title}' (ID: {task.id}) from {task.status} to UP_NEXT")
                    
                    # Update in database
                    updated_task = pm.update_task(task.id, {"status": TaskStatus.UP_NEXT})
                    print(f"📋 Database updated: {updated_task.title} is now {updated_task.status}")
                    
                    # Notify via websocket
                    await self.ws_manager.broadcast(WebSocketMessage(
                        type="task_status_changed",
                        project_id=self.current_project_id,
                        data={
                            "task_id": task.id,
                            "status": TaskStatus.UP_NEXT
                        }
                    ))
                    
                    print(f"✅ Successfully promoted task '{task.title}' to UP_NEXT queue")
            
            elif up_next_tasks > target_up_next:
                # Too many UP_NEXT tasks, move some back to UNCLAIMED
                up_next_task_list = [t for t in tasks if t.status == TaskStatus.UP_NEXT]
                # Sort by priority (lower priority tasks go back first)
                up_next_task_list.sort(
                    key=lambda t: (-getattr(t, 'priority', 10), getattr(t, 'merge_order', 0))
                )
                
                tasks_to_demote = up_next_tasks - target_up_next
                for i in range(tasks_to_demote):
                    task = up_next_task_list[i]
                    pm.update_task(task.id, {"status": TaskStatus.UNCLAIMED})
                    
                    # Notify via websocket
                    await self.ws_manager.broadcast(WebSocketMessage(
                        type="task_status_changed",
                        project_id=self.current_project_id,
                        data={
                            "task_id": task.id,
                            "status": TaskStatus.UNCLAIMED
                        }
                    ))
                    
                    print(f"📋 Moved task '{task.title}' back to TODO (queue full)")
        
        except Exception as e:
            print(f"Error managing task queue: {e}")
    
    async def _spawn_agents(self, pm: ProjectManager, project, tasks, agents):
        """Spawn agents for UP_NEXT tasks"""
        if not self.current_project_id:
            return
        
        try:
            
            # Count active agents  
            active_agents = len([a for a in agents if a.status == "running"])
            in_progress_tasks = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
            
            # Check if we can spawn more agents (only count IN_PROGRESS, not UP_NEXT)
            max_concurrent = min(self.config.max_concurrent_agents, project.max_agents)
            available_working_slots = max_concurrent - in_progress_tasks
            
            print(f"🚀 Agent spawning check:")
            print(f"   Max concurrent: {max_concurrent}")
            print(f"   In progress: {in_progress_tasks}")
            print(f"   Available working slots: {available_working_slots}")
            
            if available_working_slots <= 0:
                print(f"🚀 No available working slots for agents")
                return
            
            # Find UP_NEXT tasks ready to be spawned
            up_next_tasks = []
            running_tasks = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
            
            up_next_in_db = [t for t in tasks if t.status == TaskStatus.UP_NEXT]
            print(f"🚀 Found {len(up_next_in_db)} UP_NEXT tasks in database: {[t.title for t in up_next_in_db]}")
            
            for task in tasks:
                if task.status == TaskStatus.UP_NEXT:
                    print(f"🚀 Checking UP_NEXT task: {task.title} (Status: {task.status})")
                    # Check for file conflicts with currently running tasks
                    has_conflict = False
                    for running_task in running_tasks:
                        if not can_tasks_run_concurrently(task.id, running_task.id):
                            print(f"⚠️  Task {task.title} conflicts with running task {running_task.title}")
                            has_conflict = True
                            break
                    
                    if not has_conflict:
                        up_next_tasks.append(task)
                        print(f"🚀 Added {task.title} to spawn queue")
                    else:
                        print(f"🚀 Skipped {task.title} due to conflicts")
            
            # Sort by priority and merge order
            # Priority: 1 is highest (process first), 10 is lowest (process last)
            # So we want ascending order for priority
            up_next_tasks.sort(
                key=lambda t: (getattr(t, 'priority', 10), -getattr(t, 'merge_order', 0))
            )
            
            # Spawn agents for UP_NEXT tasks (limited by available working slots)
            if up_next_tasks:
                print(f"🚀 Found {len(up_next_tasks)} UP_NEXT tasks ready to spawn")
                tasks_to_spawn = min(len(up_next_tasks), available_working_slots)
                print(f"🚀 Spawning {tasks_to_spawn} agents (limited by working slots)")
                for task in up_next_tasks[:tasks_to_spawn]:
                    print(f"🚀 Spawning agent for task: {task.title}")
                    await self._spawn_agent_for_task(pm, task)
            else:
                print(f"🚀 No UP_NEXT tasks found to spawn")
        
        except Exception as e:
            print(f"Error spawning agents: {e}")
    
    async def _spawn_agent_for_task(self, pm: ProjectManager, task: Task):
        """Spawn a single agent for a task"""
        try:
            os.chdir(pm.project_path)
            
            # Create worktree from appropriate base
            worktree_path = pm.worktrees_dir / task.branch
            if not worktree_path.exists():
                # Determine base branch
                base_branch = "main"
                task_config = get_task_config(task.id)
                
                # If task has initialization dependencies, start from the latest one
                init_deps = task_config.get("initialization_deps", [])
                if init_deps:
                    # Find the latest merged dependency
                    for dep_id in reversed(init_deps):
                        dep_task = next((t for t in pm.get_tasks() if dep_id in t.id and t.status == TaskStatus.MERGED), None)
                        if dep_task:
                            base_branch = dep_task.branch
                            print(f"📌 Creating worktree from {base_branch} (dependency)")
                            break
                
                subprocess.run([
                    "git", "worktree", "add",
                    str(worktree_path),
                    "-b", task.branch,
                    base_branch
                ], check=True)
                
                # Copy CLAUDE.md and .claude folder if they exist
                claude_md_src = pm.project_path / "CLAUDE.md"
                claude_dir_src = pm.project_path / ".claude"
                
                if claude_md_src.exists():
                    shutil.copy2(claude_md_src, worktree_path / "CLAUDE.md")
                    print(f"📄 Copied CLAUDE.md to worktree")
                
                if claude_dir_src.exists() and claude_dir_src.is_dir():
                    claude_dir_dst = worktree_path / ".claude"
                    if claude_dir_dst.exists():
                        shutil.rmtree(claude_dir_dst)
                    shutil.copytree(claude_dir_src, claude_dir_dst)
                    print(f"📁 Copied .claude folder to worktree")
                
                # Run initialization script
                init_script = get_initialization_script(task.id, str(worktree_path))
                if task_config.get("setup_commands"):
                    with tempfile.NamedTemporaryFile(mode='w', suffix='_init.sh', delete=False) as f:
                        f.write(init_script)
                        init_script_path = f.name
                    
                    os.chmod(init_script_path, 0o755)
                    print(f"🔧 Running initialization for {task.title}...")
                    subprocess.run(["/bin/bash", init_script_path], cwd=str(worktree_path))
                    os.unlink(init_script_path)
            
            # Generate session name with task ID at the front
            if task.task_id:
                session_name = f"{task.task_id}-{pm.project.id}"
            else:
                # Fallback to branch-based naming if no task_id
                session_name = f"{pm.project.id}-{task.branch}"
            
            # Create status file for this agent
            status_file = self.status_dir / f"{session_name}.status"
            status_file.write_text("RUNNING")
            
            # Build agent prompt
            if task.prompt:
                # Use custom prompt if provided
                prompt = task.prompt
                # Add task title and description as context
                prompt += f"\\n\\nTask: {task.title}"
                if task.description:
                    prompt += f"\\nDescription: {task.description}"
            else:
                # Use default prompt
                prompt = f"You are working on {pm.project.name}."
                prompt += f"\\n\\nIMPORTANT: Use the TodoWrite tool to create a todo list for this task. Break down the work into clear, actionable items and track your progress by updating the todo status as you complete each item."
                prompt += f"\\n\\nCreate a plan, review your plan and choose the best option, then accomplish the following task and commit the changes: {task.title}"
                if task.description:
                    prompt += f"\\n\\nDescription: {task.description}"
            
            # Add todo tool reminder
            if "TodoWrite" not in prompt:
                prompt += f"\\n\\nREMINDER: Use the TodoWrite tool to break down this task into manageable todos and track your progress. Mark todos as 'in_progress' when you start them and 'completed' when done."
            
            # Add status file instruction with clear command
            prompt += f"\\n\\nIMPORTANT: When you have completed all work and committed your changes, execute this command as your FINAL action:\\nbash -c 'echo COMPLETED > {status_file}'"
            
            # Create a prompt file for Claude to read
            prompt_file = f"/tmp/claude_prompt_{session_name}.txt"
            with open(prompt_file, 'w') as f:
                f.write(prompt)
            
            # Create the tmux session first
            subprocess.run([
                "tmux", "new-session", "-d",
                "-s", session_name,
                "-c", str(worktree_path)
            ], check=True)
            
            # Get the PTY runner path
            pty_runner_path = Path(__file__).parent / "claude_pty_runner.py"
            
            # Prepare template variables
            project_id = pm.project.id
            task_id = str(task.task_id)
            branch = task.branch
            task_title = task.title
            actual_prompt = prompt
            
            # Create a wrapper script that runs in the foreground
            wrapper_script = '''#!/bin/bash
cd {worktree_path}

echo "🚀 Starting AI agent for task: {task.title}"
echo "📝 Task description: {task.description}"
echo ""
echo "Setting up environment..."

# Check if this is a JavaScript project and run npm install if needed
if [ -f "package.json" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if this is a Python project and set up venv if needed
if [ -f "requirements.txt" ] || [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    echo "🐍 Setting up Python environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
fi

echo ""
echo "Launching Claude Code..."
echo "----------------------------------------"

# Set environment variables for agent coordination
export SPLITMIND_PROJECT_ID="{project_id}"
export SPLITMIND_SESSION_NAME="{session_name}"
export SPLITMIND_TASK_ID="{task_id}"
export SPLITMIND_BRANCH="{branch}"
export SPLITMIND_TASK_TITLE="{task_title}"

echo "📊 Agent Configuration:"
echo "   Project: $SPLITMIND_PROJECT_ID"
echo "   Session: $SPLITMIND_SESSION_NAME"
echo "   Task ID: $SPLITMIND_TASK_ID"
echo "   Branch: $SPLITMIND_BRANCH"
echo ""

# Create MCP config for A2AMCP
MCP_CONFIG='{
  "mcpServers": {
    "splitmind-coordination": {
      "command": "/Users/jasonbrashear/code/cctg/mcp-wrapper.sh",
      "args": [],
      "env": {}
    }
  }
}'

# Add coordination setup to prompt
COORDINATION_PROMPT="IMPORTANT: Read CLAUDE.md for coordination instructions. You MUST register with the coordination system before starting work. Use: register_agent('$SPLITMIND_PROJECT_ID', '$SPLITMIND_SESSION_NAME', '$SPLITMIND_TASK_ID', '$SPLITMIND_BRANCH', '$SPLITMIND_TASK_TITLE')

When you complete your task, use: mark_task_completed('$SPLITMIND_PROJECT_ID', '$SPLITMIND_SESSION_NAME', '$SPLITMIND_TASK_ID')"

# Create combined prompt with proper escaping
FULL_PROMPT="$COORDINATION_PROMPT

{actual_prompt}"

# Run Claude with the prompt as an argument and MCP config
# Use --print for non-interactive mode to avoid Ink raw mode error
claude --dangerously-skip-permissions --print --mcp-config "$MCP_CONFIG" "$FULL_PROMPT"

# Check if Claude exited successfully
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Task completed successfully"
else
    echo ""
    echo "❌ Claude exited with an error"
fi

# This line will only run if Claude exits with an error
echo "Claude exited unexpectedly"
'''
            
            # Replace template variables
            wrapper_script = wrapper_script.replace('{worktree_path}', str(worktree_path))
            wrapper_script = wrapper_script.replace('{task.title}', task.title)
            wrapper_script = wrapper_script.replace('{task.description}', task.description or '')
            wrapper_script = wrapper_script.replace('{project_id}', project_id)
            wrapper_script = wrapper_script.replace('{session_name}', session_name)
            wrapper_script = wrapper_script.replace('{task_id}', task_id)
            wrapper_script = wrapper_script.replace('{branch}', branch)
            wrapper_script = wrapper_script.replace('{task_title}', task_title)
            wrapper_script = wrapper_script.replace('{actual_prompt}', actual_prompt)
            wrapper_script = wrapper_script.replace('{status_file}', str(status_file))
            
            # Write the wrapper script
            wrapper_file = f"/tmp/claude_wrapper_{session_name}.sh"
            with open(wrapper_file, 'w') as f:
                f.write(wrapper_script)
            os.chmod(wrapper_file, 0o755)
            
            # Run the wrapper script directly in tmux
            # Using 'new-window' to ensure clean environment
            subprocess.run([
                "tmux", "send-keys", "-t", session_name,
                f"exec bash {wrapper_file}", "Enter"
            ])
            
            # Clean up files after a delay
            def cleanup():
                time.sleep(5)
                try:
                    os.remove(wrapper_file)
                    os.remove(prompt_file)
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            
            # Ensure session exits when script completes
            subprocess.run([
                "tmux", "set-option", "-t", session_name,
                "remain-on-exit", "off"
            ], check=False)
            
            # Update task status to IN_PROGRESS (since it's moving from UP_NEXT to active work)
            task.status = TaskStatus.IN_PROGRESS
            task.session = session_name
            pm.update_task(task.id, {
                "status": TaskStatus.IN_PROGRESS,
                "session": session_name
            })
            
            # Notify via websocket immediately
            await self.ws_manager.broadcast(WebSocketMessage(
                type="task_status_changed",
                project_id=self.current_project_id,
                data={
                    "task_id": task.id,
                    "status": TaskStatus.IN_PROGRESS
                }
            ))
            print(f"📊 Task {task.title} moved to IN_PROGRESS")
            
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
                result = subprocess.run([
                    "python",
                    str(Path(__file__).parent.parent.parent / "scripts" / "auto-merge.py"),
                    task.branch,
                    "--strategy", self.config.merge_strategy,
                    "--json"
                ], cwd=str(pm.project_path), capture_output=True, text=True)
                
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
    
    async def _check_agent_status(self):
        """Check status of running agents and update task statuses"""
        if not self.current_project_id:
            return
        
        try:
            pm = ProjectManager(self.current_project_id)
            tasks = pm.get_tasks()
            
            # Check Redis for completed tasks
            try:
                # Connect to Redis through Docker container's exposed port
                # The container maps internal port 6379 to external port 6379
                r = redis.Redis(host='localhost', port=6379, decode_responses=True)
                completion_key = f"splitmind:{self.current_project_id}:completed_tasks"
                completed_tasks = r.hgetall(completion_key)
                
                # Process completed tasks from Redis
                for task_id, completion_data in completed_tasks.items():
                    completion_info = json.loads(completion_data)
                    session_name = completion_info.get('session_name')
                    
                    # Find the corresponding task
                    for task in tasks:
                        if str(task.task_id) == task_id and task.session == session_name:
                            print(f"🎯 Redis: Task {task_id} marked as completed by agent {session_name}")
                            
                            # Kill the tmux session
                            subprocess.run(["tmux", "kill-session", "-t", session_name])
                            print(f"✅ Killed session {session_name}")
                            
                            # Clean up status file
                            status_file = self.status_dir / f"{session_name}.status"
                            if status_file.exists():
                                status_file.unlink()
                            
                            # Remove from Redis completed tasks
                            r.hdel(completion_key, task_id)
                            
                            # Mark task as completed
                            pm.update_task(task.id, {
                                "status": TaskStatus.COMPLETED,
                                "completed_at": datetime.now()
                            })
                            
                            await self.ws_manager.broadcast(WebSocketMessage(
                                type="task_completed",
                                project_id=self.current_project_id,
                                data={
                                    "task_id": task.id,
                                    "branch": task.branch
                                }
                            ))
                            
                            print(f"✅ Task {task.title} marked as completed")
                            
                            # Add to merge queue if auto-merge is enabled
                            if self.config.auto_merge and self.merge_queue:
                                all_tasks = pm.get_tasks()
                                await self.merge_queue.add_to_queue(task, all_tasks)
                            
                            break
                
            except Exception as e:
                print(f"Redis check error: {e}")
            
            # Check each in-progress or up_next task
            for task in tasks:
                if task.status in [TaskStatus.UP_NEXT, TaskStatus.IN_PROGRESS] and task.session:
                    # Check if tmux session is still active
                    result = subprocess.run(
                        ["tmux", "has-session", "-t", task.session],
                        capture_output=True
                    )
                    
                    # Check status file first
                    status_file = self.status_dir / f"{task.session}.status"
                    if status_file.exists():
                        status = status_file.read_text().strip()
                        if status == "COMPLETED":
                            # Agent signaled completion
                            print(f"✅ Agent {task.session} signaled COMPLETED via status file")
                            
                            # Kill the session
                            subprocess.run(["tmux", "kill-session", "-t", task.session])
                            status_file.unlink()  # Clean up status file
                            
                            # Update task status immediately
                            pm.update_task(task.id, {
                                "status": TaskStatus.COMPLETED,
                                "completed_at": datetime.now()
                            })
                            
                            await self.ws_manager.broadcast(WebSocketMessage(
                                type="task_completed",
                                project_id=self.current_project_id,
                                data={
                                    "task_id": task.id,
                                    "branch": task.branch
                                }
                            ))
                            
                            print(f"✅ Task {task.title} marked as completed")
                            
                            # Add to merge queue if auto-merge is enabled
                            if self.config.auto_merge and self.merge_queue:
                                all_tasks = pm.get_tasks()
                                await self.merge_queue.add_to_queue(task, all_tasks)
                            
                            # Skip further processing for this task
                            continue
                    
                    elif result.returncode == 0:
                        # Session exists but no status file, check if agent is done by looking at output
                        capture_result = subprocess.run(
                            ["tmux", "capture-pane", "-t", task.session, "-p"],
                            capture_output=True,
                            text=True
                        )
                        
                        output = capture_result.stdout
                        if "✅ Task completed" in output or "Task completed!" in output or "All changes have been committed" in output:
                            # Agent finished, kill the session
                            subprocess.run(["tmux", "kill-session", "-t", task.session])
                            result.returncode = 1  # Pretend session doesn't exist
                    
                    if result.returncode != 0:
                        # Session no longer exists, check if work was done
                        os.chdir(pm.project_path)
                        
                        # Check for commits on the branch
                        result = subprocess.run(
                            ["git", "log", f"main..{task.branch}", "--oneline"],
                            capture_output=True,
                            text=True
                        )
                        
                        if result.stdout.strip():
                            # Commits exist, mark as completed
                            pm.update_task(task.id, {
                                "status": TaskStatus.COMPLETED,
                                "completed_at": datetime.now()
                            })
                            
                            await self.ws_manager.broadcast(WebSocketMessage(
                                type="task_completed",
                                project_id=self.current_project_id,
                                data={
                                    "task_id": task.id,
                                    "branch": task.branch
                                }
                            ))
                            
                            print(f"✅ Task {task.title} completed!")
                            
                            # Add to merge queue if auto-merge is enabled
                            if self.config.auto_merge and self.merge_queue:
                                all_tasks = pm.get_tasks()
                                await self.merge_queue.add_to_queue(task, all_tasks)
                        else:
                            # No commits yet, reset task status so it can be retried
                            print(f"⚠️ Agent for task {task.title} stopped without commits - resetting to UP_NEXT")
                            
                            # Reset task status to UP_NEXT so it can be picked up again
                            pm.update_task(task.id, {
                                "status": TaskStatus.UP_NEXT,
                                "session": None
                            })
                            
                            await self.ws_manager.broadcast(WebSocketMessage(
                                type="task_status_changed",
                                project_id=self.current_project_id,
                                data={
                                    "task_id": task.id,
                                    "status": TaskStatus.UP_NEXT
                                }
                            ))
        
        except Exception as e:
            print(f"Error checking agent status: {e}")
    
    async def _check_and_merge_completed_tasks(self, pm: ProjectManager, tasks: List[Task]):
        """Check for completed tasks and auto-merge if enabled"""
        if not self.config.auto_merge:
            print("🔀 Auto-merge is disabled")
            return
            
        if not self.merge_queue:
            print("⚠️ Merge queue not initialized")
            return
        
        try:
            # Find all completed tasks not yet in merge queue
            completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
            
            if completed_tasks:
                print(f"🔀 Found {len(completed_tasks)} completed task(s)")
                queue_ids = [t.id for t in self.merge_queue.queue]
                
                for task in completed_tasks:
                    # Check if task is already in merge queue by ID
                    if task.id not in queue_ids:
                        print(f"📋 Adding completed task to merge queue: {task.title} (ID: {task.id})")
                        await self.merge_queue.add_to_queue(task, tasks)
                        
                        # Notify via websocket
                        await self.ws_manager.broadcast(WebSocketMessage(
                            type="task_queued_for_merge",
                            project_id=self.current_project_id,
                            data={
                                "task_id": task.id,
                                "title": task.title
                            }
                        ))
                    else:
                        print(f"📋 Task already in merge queue: {task.title}")
        
        except Exception as e:
            print(f"Error checking for completed tasks to merge: {e}")