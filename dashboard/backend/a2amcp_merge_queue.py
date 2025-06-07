"""
A2AMCP-Enhanced Merge Queue for SplitMind
Provides conflict-aware merging with agent coordination
"""

import asyncio
import subprocess
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

try:
    from a2amcp import A2AMCPClient, Project
    A2AMCP_AVAILABLE = True
except ImportError:
    A2AMCP_AVAILABLE = False

from .merge_queue import MergeQueue
from .models import Task, TaskStatus

logger = logging.getLogger(__name__)


class A2AMCPMergeQueue(MergeQueue):
    """Enhanced merge queue with A2AMCP coordination"""
    
    def __init__(self, project_path: str, status_update_callback=None):
        super().__init__(project_path, status_update_callback)
        self.a2amcp_client = None
        self.coordination_enabled = False
        
        if A2AMCP_AVAILABLE:
            try:
                self.a2amcp_client = A2AMCPClient(
                    server_url="localhost:5050",
                    docker_container="splitmind-mcp-server"
                )
                self.coordination_enabled = True
                logger.info("✅ A2AMCP merge coordination enabled")
            except Exception as e:
                logger.error(f"Failed to initialize A2AMCP for merge queue: {e}")
    
    async def can_merge_task(self, task: Task, all_tasks: List[Task]) -> bool:
        """
        Check if task can be merged, including A2AMCP file lock checks
        """
        # First check traditional dependencies
        deps_merged = True
        if hasattr(task, 'dependencies') and task.dependencies:
            for dep_id in task.dependencies:
                dep_task = next((t for t in all_tasks if t.id == dep_id), None)
                if dep_task and dep_task.status != TaskStatus.MERGED:
                    deps_merged = False
                    logger.info(f"Task {task.id} waiting for dependency {dep_id}")
                    break
        
        if not deps_merged:
            return False
        
        # Check A2AMCP file locks if enabled
        if self.coordination_enabled and hasattr(task, 'project_id'):
            try:
                return await self.check_file_locks(task)
            except Exception as e:
                logger.error(f"Error checking A2AMCP locks: {e}")
                # Don't block merge on A2AMCP errors
                return True
        
        return True
    
    async def check_file_locks(self, task: Task) -> bool:
        """Check if any files modified by task are locked by other agents"""
        project = Project(self.a2amcp_client, task.project_id)
        
        # Get files modified in this branch
        modified_files = await self.get_modified_files(task.branch)
        
        # Check each file for locks
        for file_path in modified_files:
            try:
                response = await project.client.call_tool(
                    "check_file_lock",
                    project_id=task.project_id,
                    file_path=file_path
                )
                
                if response.get('locked'):
                    locked_by = response.get('locked_by', 'unknown')
                    session_name = f"{task.task_id}-{task.project_id}"
                    
                    if locked_by != session_name:
                        logger.warning(
                            f"Cannot merge {task.title}: "
                            f"File {file_path} is locked by {locked_by}"
                        )
                        
                        # Query the locking agent about timeline
                        if await self.negotiate_file_access(task, file_path, locked_by):
                            continue  # Agent agreed to release soon
                        
                        return False
            except Exception as e:
                logger.error(f"Error checking lock for {file_path}: {e}")
                # Continue checking other files
        
        return True
    
    async def negotiate_file_access(self, task: Task, file_path: str, locked_by: str) -> bool:
        """Try to negotiate file access with the locking agent"""
        if not self.coordination_enabled:
            return False
        
        try:
            project = Project(self.a2amcp_client, task.project_id)
            session_name = f"{task.task_id}-{task.project_id}"
            
            # Query the agent
            response = await project.client.call_tool(
                "query_agent",
                project_id=task.project_id,
                from_session=session_name,
                to_session=locked_by,
                query_type="merge_request",
                query=f"I need to merge changes to {file_path}. When will you be done?",
                wait_for_response=True,
                timeout=10
            )
            
            if response and response.get('response'):
                # Parse response - this is simplified
                agent_response = response['response'].lower()
                if any(word in agent_response for word in ['done', 'finished', 'released', 'go ahead']):
                    logger.info(f"Agent {locked_by} indicated {file_path} is available")
                    return True
                elif 'minute' in agent_response or 'soon' in agent_response:
                    logger.info(f"Agent {locked_by} will release {file_path} soon")
                    # Could implement a wait mechanism here
                    return False
            
        except Exception as e:
            logger.error(f"Failed to negotiate with {locked_by}: {e}")
        
        return False
    
    async def get_modified_files(self, branch: str) -> List[str]:
        """Get list of files modified in a branch"""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["git", "diff", "--name-only", "main", branch],
                cwd=str(self.project_path),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout:
                return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            
        except Exception as e:
            logger.error(f"Error getting modified files for {branch}: {e}")
        
        return []
    
    async def process_queue(self, all_tasks: List[Task]):
        """
        Process tasks in order, respecting dependencies and A2AMCP locks
        """
        async with self.merge_lock:
            processed = []
            
            for task in self.queue[:]:  # Copy to avoid modification during iteration
                if await self.can_merge_task(task, all_tasks):
                    logger.info(f"🔄 Processing merge for {task.title}...")
                    
                    # Notify agents about pending merge
                    if self.coordination_enabled:
                        await self.broadcast_merge_notification(task)
                    
                    success = await self.merge_task(task)
                    
                    if success:
                        processed.append(task)
                        task.status = TaskStatus.MERGED
                        task.merged_at = datetime.now()
                        logger.info(f"✅ Successfully merged {task.title}")
                        
                        # Update task status
                        if self.status_update_callback:
                            await self.status_update_callback(task.id, TaskStatus.MERGED)
                        
                        # Clean up worktree and A2AMCP resources
                        await self.cleanup_after_merge(task)
                    else:
                        logger.warning(f"⚠️  Failed to merge {task.title}, will retry later")
                else:
                    logger.info(f"⏸️  Skipping {task.title} - not ready to merge")
            
            # Remove processed tasks
            for task in processed:
                self.queue.remove(task)
    
    async def broadcast_merge_notification(self, task: Task):
        """Notify all agents about pending merge"""
        if not self.coordination_enabled or not hasattr(task, 'project_id'):
            return
        
        try:
            project = Project(self.a2amcp_client, task.project_id)
            session_name = f"{task.task_id}-{task.project_id}"
            
            await project.broadcast(
                from_session=session_name,
                message_type="merge_notification",
                content=f"Merging task {task.title} ({task.branch}) to main branch"
            )
        except Exception as e:
            logger.error(f"Failed to broadcast merge notification: {e}")
    
    async def cleanup_after_merge(self, task: Task):
        """Clean up worktree and A2AMCP resources after merge"""
        # Clean up worktree
        await self.cleanup_worktree(task)
        
        # Clean up A2AMCP resources
        if self.coordination_enabled and hasattr(task, 'project_id'):
            try:
                project = Project(self.a2amcp_client, task.project_id)
                session_name = f"{task.task_id}-{task.project_id}"
                
                # Release any remaining locks
                await project.client.call_tool(
                    "release_all_locks",
                    project_id=task.project_id,
                    session_name=session_name
                )
                
                # Mark agent as completed
                await project.client.call_tool(
                    "update_agent_status",
                    project_id=task.project_id,
                    session_name=session_name,
                    status="merged"
                )
                
            except Exception as e:
                logger.error(f"Error cleaning up A2AMCP resources: {e}")
    
    async def handle_merge_conflicts(self, task: Task, conflicts: List[str]) -> bool:
        """Enhanced conflict resolution with A2AMCP awareness"""
        # Try standard conflict resolution first
        resolution_success = await super().handle_merge_conflicts(task, conflicts)
        
        if not resolution_success and self.coordination_enabled:
            # Check if conflicts are due to active file locks
            logger.info("Checking if conflicts are due to active file locks...")
            
            locked_files = []
            for conflict_file in conflicts:
                if await self.is_file_locked(task, conflict_file):
                    locked_files.append(conflict_file)
            
            if locked_files:
                logger.warning(
                    f"Cannot auto-resolve conflicts for {task.title}: "
                    f"Files are actively locked: {', '.join(locked_files)}"
                )
                
                # Abort the merge
                subprocess.run(["git", "merge", "--abort"], cwd=str(self.project_path))
                return False
        
        return resolution_success
    
    async def is_file_locked(self, task: Task, file_path: str) -> bool:
        """Check if a file is currently locked by another agent"""
        if not self.coordination_enabled or not hasattr(task, 'project_id'):
            return False
        
        try:
            project = Project(self.a2amcp_client, task.project_id)
            response = await project.client.call_tool(
                "check_file_lock",
                project_id=task.project_id,
                file_path=file_path
            )
            return response.get('locked', False)
        except:
            return False