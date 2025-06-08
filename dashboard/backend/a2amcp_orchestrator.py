"""
A2AMCP-Enhanced Orchestrator for SplitMind
Provides agent coordination through A2AMCP
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    from a2amcp import A2AMCPClient, Project
    A2AMCP_AVAILABLE = True
except ImportError:
    A2AMCP_AVAILABLE = False
    logging.warning("A2AMCP SDK not available. Agent coordination features will be limited.")

from .orchestrator import OrchestratorManager
from .models import Task, TaskStatus
from .websocket_manager import WebSocketManager, WebSocketMessage
from .a2amcp_merge_queue import A2AMCPMergeQueue

logger = logging.getLogger(__name__)


class A2AMCPOrchestrator(OrchestratorManager):
    """Enhanced orchestrator with A2AMCP agent coordination"""
    
    def __init__(self, ws_manager: WebSocketManager):
        super().__init__(ws_manager)
        self.a2amcp_client = None
        self.coordination_enabled = False
        
        if A2AMCP_AVAILABLE:
            try:
                self.a2amcp_client = A2AMCPClient(
                    server_url="localhost:5050",
                    docker_container="splitmind-mcp-server"
                )
                self.coordination_enabled = True
                logger.info("✅ A2AMCP coordination enabled")
            except Exception as e:
                logger.error(f"Failed to initialize A2AMCP client: {e}")
                self.coordination_enabled = False
        else:
            logger.warning("A2AMCP SDK not installed. Run: pip install a2amcp-sdk")
    
    async def start(self, project_id: str):
        """Start orchestrator with A2AMCP-enhanced merge queue"""
        if self.running:
            raise ValueError("Orchestrator is already running")
        
        # Verify project exists
        from .config import config_manager
        project = config_manager.get_project(project_id)
        if not project:
            raise ValueError(f"Project '{project_id}' not found")
        
        self.current_project_id = project_id
        self.running = True
        self._stop_event.clear()
        
        # Initialize merge queue with A2AMCP enhancement if available
        async def update_task_status(task_id: str, status: TaskStatus):
            from .project_manager import ProjectManager
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
        
        # Use A2AMCP merge queue if coordination is enabled
        if self.coordination_enabled:
            logger.info("Using A2AMCP-enhanced merge queue")
            self.merge_queue = A2AMCPMergeQueue(project.path, update_task_status)
        else:
            from .merge_queue import MergeQueue
            self.merge_queue = MergeQueue(project.path, update_task_status)
        
        # Start the orchestrator loop
        self._task = asyncio.create_task(self._orchestrator_loop())
        
        # Notify clients
        await self.ws_manager.broadcast(WebSocketMessage(
            type="orchestrator_started",
            project_id=project_id,
            data={"status": "running", "a2amcp_enabled": self.coordination_enabled}
        ))
    
    def generate_agent_prompt(self, task: Task, project_id: str) -> str:
        """Generate enhanced prompt with A2AMCP instructions"""
        
        # Get base prompt from parent
        base_prompt = super().generate_agent_prompt(task, project_id)
        
        # If A2AMCP is not enabled, return base prompt
        if not self.coordination_enabled:
            return base_prompt
        
        # Generate A2AMCP coordination instructions
        session_name = f"{task.task_id}-{project_id}"
        
        a2amcp_instructions = f"""
# ⚠️ MANDATORY: Agent Coordination Protocol

You are part of a multi-agent system. Other AI agents are working on related tasks in parallel.
You MUST coordinate with them using the MCP communication tools.

## 🚀 FIRST ACTION - Register Yourself

Before doing ANYTHING else, you MUST register:

```
register_agent("{project_id}", "{session_name}", "{task.task_id}", "{task.branch}", "{task.title}")
```

If this fails, STOP and report: "ERROR: Cannot access MCP coordination tools"

## 📋 Create and Share Your Todo List

Break down your task and share your plan:

```
add_todo("{project_id}", "{session_name}", "Research existing code structure", 1)
add_todo("{project_id}", "{session_name}", "Design the implementation approach", 2)
add_todo("{project_id}", "{session_name}", "Implement core functionality", 3)
add_todo("{project_id}", "{session_name}", "Write tests", 4)
add_todo("{project_id}", "{session_name}", "Update documentation", 5)
```

Update status as you progress:
```
update_todo("{project_id}", "{session_name}", "todo-1", "in_progress")
update_todo("{project_id}", "{session_name}", "todo-1", "completed")
```

## 🔍 Check Other Agents

See who else is working and what they're doing:

```
list_active_agents("{project_id}")
get_all_todos("{project_id}")
```

## 📁 Coordinate File Access

BEFORE modifying ANY file:
```
announce_file_change("{project_id}", "{session_name}", "src/components/Button.tsx", "modify", "Adding new prop for color variant")
```

AFTER completing changes:
```
release_file_lock("{project_id}", "{session_name}", "src/components/Button.tsx")
```

If you get a conflict, you can:
1. Wait and retry
2. Query the other agent about their timeline
3. Work on a different file first

## 🔗 Share Interfaces and Types

When you create interfaces, types, or API contracts:
```
register_interface("{project_id}", "{session_name}", "User", "interface User {{ id: string; email: string; role: 'admin' | 'user'; }}")
```

Query interfaces created by others:
```
query_interface("{project_id}", "User")
list_interfaces("{project_id}")
```

## 💬 Communicate with Other Agents

Ask questions:
```
query_agent("{project_id}", "{session_name}", "task-002-{project_id}", "api", "What endpoints are you creating for user management?")
```

Broadcast important updates:
```
broadcast_message("{project_id}", "{session_name}", "refactor", "Starting major refactor of auth system - please avoid auth files for next 30 min")
```

Check your messages regularly:
```
check_messages("{project_id}", "{session_name}")
```

## 💓 Send Heartbeats

Every 30-60 seconds, send a heartbeat to show you're still active:
```
heartbeat("{project_id}", "{session_name}")
```

## 🏁 When Complete

Before marking your task as complete:
1. Ensure all todos are marked as completed
2. Release all file locks
3. Unregister from the coordination system:

```
unregister_agent("{project_id}", "{session_name}")
```

## Your Actual Task:

{base_prompt}

Remember: Coordination is MANDATORY. If you cannot use these tools, stop immediately and report the issue.
"""
        
        return a2amcp_instructions
    
    async def monitor_agent_coordination(self, project_id: str, session_name: str):
        """Monitor agent coordination activities"""
        if not self.coordination_enabled:
            return
        
        try:
            project = Project(self.a2amcp_client, project_id)
            
            # Get initial agent status
            agents = await project.get_active_agents()
            
            # Broadcast to dashboard
            await self.ws_manager.broadcast(WebSocketMessage(
                type="coordination_update",
                project_id=project_id,
                data={
                    "active_agents": len(agents),
                    "agents": {name: agent.__dict__ for name, agent in agents.items()}
                }
            ))
            
            # Monitor for conflicts
            asyncio.create_task(self._monitor_conflicts(project_id))
            
        except Exception as e:
            logger.error(f"Failed to monitor coordination: {e}")
    
    async def _monitor_conflicts(self, project_id: str):
        """Monitor for file conflicts between agents"""
        if not self.coordination_enabled:
            return
        
        project = Project(self.a2amcp_client, project_id)
        
        while self.is_running() and self.current_project_id == project_id:
            try:
                # Check for file locks
                locks = await project.client.call_tool(
                    "list_file_locks",
                    project_id=project_id
                )
                
                if locks:
                    await self.ws_manager.broadcast(WebSocketMessage(
                        type="file_locks_update",
                        project_id=project_id,
                        data={"locks": locks}
                    ))
                
                # Check agent communication
                agents = await project.get_active_agents()
                for agent_name, agent_info in agents.items():
                    # Check if agent has pending messages
                    messages = await project.client.call_tool(
                        "check_messages",
                        project_id=project_id,
                        session_name=agent_name
                    )
                    
                    if messages:
                        await self.ws_manager.broadcast(WebSocketMessage(
                            type="agent_messages",
                            project_id=project_id,
                            data={
                                "agent": agent_name,
                                "pending_messages": len(messages)
                            }
                        ))
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring conflicts: {e}")
                await asyncio.sleep(30)
    
    async def spawn_agent_for_task(self, task: Task, project_id: str) -> Optional[str]:
        """Spawn an agent with A2AMCP coordination"""
        
        # Call parent implementation
        session_name = await super().spawn_agent_for_task(task, project_id)
        
        if session_name and self.coordination_enabled:
            # Start monitoring this agent's coordination
            asyncio.create_task(self.monitor_agent_coordination(project_id, session_name))
        
        return session_name
    
    async def get_coordination_stats(self, project_id: str) -> Dict[str, Any]:
        """Get coordination statistics for a project"""
        if not self.coordination_enabled:
            return {"enabled": False}
        
        try:
            project = Project(self.a2amcp_client, project_id)
            
            # Get active agents
            try:
                agents = await project.get_active_agents()
            except Exception as e:
                logger.error(f"Error getting active agents: {e}")
                agents = {}
            
            # Get all todos
            try:
                all_todos = await project.todos.get_all()
            except Exception as e:
                logger.error(f"Error getting todos: {e}")
                all_todos = {}
            
            # Get interfaces
            try:
                interfaces = await project.interfaces.list()
            except Exception as e:
                logger.error(f"Error getting interfaces: {e}")
                interfaces = {}
            
            # Get recent changes
            try:
                recent_changes = await project.get_recent_changes(limit=50)
            except Exception as e:
                logger.error(f"Error getting recent changes: {e}")
                recent_changes = []
            
            # Calculate stats
            total_todos = 0
            completed_todos = 0
            
            # Parse todo data safely
            for data in all_todos.values():
                try:
                    if isinstance(data, str):
                        parsed_data = json.loads(data)
                    else:
                        parsed_data = data
                    
                    todos = parsed_data.get('todos', []) if isinstance(parsed_data, dict) else []
                    total_todos += len(todos)
                    
                    for todo in todos:
                        if isinstance(todo, dict) and todo.get('status') == 'completed':
                            completed_todos += 1
                            
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to parse todo data: {e}")
                    continue
            
            return {
                "enabled": True,
                "active_agents": len(agents),
                "total_todos": total_todos,
                "completed_todos": completed_todos,
                "completion_rate": (completed_todos / total_todos * 100) if total_todos > 0 else 0,
                "shared_interfaces": len(interfaces),
                "recent_changes": len(recent_changes),
                "agents": agents,
                "interfaces": list(interfaces.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to get coordination stats: {e}")
            return {"enabled": True, "error": str(e)}
    
    async def check_merge_conflicts_a2amcp(self, task: Task) -> bool:
        """Check if task can be merged considering A2AMCP locks"""
        
        # First check traditional merge readiness
        can_merge = await self.check_merge_readiness(task)
        if not can_merge or not self.coordination_enabled:
            return can_merge
        
        try:
            project = Project(self.a2amcp_client, task.project_id)
            
            # Get modified files in task branch
            pm = self.get_project_manager(task.project_id)
            worktree_path = pm.project_path / "worktrees" / task.branch
            
            if not worktree_path.exists():
                return True  # No worktree, no conflicts
            
            # Get modified files
            result = await asyncio.to_thread(
                subprocess.run,
                ["git", "diff", "--name-only", "main", task.branch],
                cwd=str(pm.project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return True  # Can't check, assume OK
            
            modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Check each file for locks
            for file_path in modified_files:
                if not file_path:
                    continue
                    
                lock_check = await project.client.call_tool(
                    "check_file_lock",
                    project_id=task.project_id,
                    file_path=file_path
                )
                
                if lock_check.get('locked'):
                    locked_by = lock_check.get('locked_by', 'unknown')
                    if locked_by != task.session:
                        logger.warning(
                            f"Cannot merge task {task.id}: "
                            f"File {file_path} is locked by {locked_by}"
                        )
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking A2AMCP merge conflicts: {e}")
            return True  # Don't block on errors
    
    async def cleanup_agent_coordination(self, project_id: str, session_name: str):
        """Clean up A2AMCP resources when agent completes"""
        if not self.coordination_enabled:
            return
        
        try:
            project = Project(self.a2amcp_client, project_id)
            
            # Release any remaining file locks
            await project.client.call_tool(
                "release_all_locks",
                project_id=project_id,
                session_name=session_name
            )
            
            # Unregister agent (if not already done)
            await project.client.call_tool(
                "unregister_agent",
                project_id=project_id,
                session_name=session_name
            )
            
            logger.info(f"Cleaned up A2AMCP resources for {session_name}")
            
        except Exception as e:
            logger.error(f"Error cleaning up A2AMCP resources: {e}")


# Helper function to check if A2AMCP is available
def is_a2amcp_available() -> bool:
    """Check if A2AMCP infrastructure is running"""
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=splitmind-mcp-server", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        return "splitmind-mcp-server" in result.stdout
    except:
        return False