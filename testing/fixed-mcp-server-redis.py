#!/usr/bin/env python3
"""
SplitMind Agent Communication MCP Server with Redis Backend

Multi-project MCP server that enables communication between AI agents
with persistent state storage in Redis.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import redis.asyncio as redis

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('splitmind-mcp')


class AgentCommunicationServer:
    """MCP Server with Redis backend for multi-project agent communication"""
    
    def __init__(self):
        self.server = Server("splitmind-coordination")
        self.redis_client: Optional[redis.Redis] = None
        self._setup_tools()
    
    async def initialize(self):
        """Initialize Redis connection and wait for readiness"""
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        logger.info(f"Connecting to Redis at: {redis_url}")
        
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Wait for Redis to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                await self.redis_client.ping()
                logger.info("Connected to Redis successfully")
                break
            except Exception as e:
                if i < max_retries - 1:
                    logger.info(f"Waiting for Redis... ({i+1}/{max_retries})")
                    await asyncio.sleep(1)
                else:
                    logger.error(f"Failed to connect to Redis after {max_retries} attempts: {e}")
                    raise
    
    async def cleanup(self):
        """Clean up Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    def _get_key(self, project_id: str, *parts: str) -> str:
        """Generate Redis key with proper namespace"""
        return f"splitmind:{project_id}:{':'.join(parts)}"
    
    def _setup_tools(self):
        """Register all MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return [
                Tool(
                    name="register_agent",
                    description="Register an agent for a specific project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Unique project identifier"},
                            "session_name": {"type": "string", "description": "Unique tmux session name"},
                            "task_id": {"type": "string", "description": "The task ID this agent is working on"},
                            "branch": {"type": "string", "description": "Git branch name for this task"},
                            "description": {"type": "string", "description": "Brief description of the task"}
                        },
                        "required": ["project_id", "session_name", "task_id", "branch", "description"]
                    }
                ),
                Tool(
                    name="mark_task_completed",
                    description="Mark a task as completed",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Project identifier"},
                            "session_name": {"type": "string", "description": "Session name"},
                            "task_id": {"type": "string", "description": "Task identifier"}
                        },
                        "required": ["project_id", "session_name", "task_id"]
                    }
                ),
                Tool(
                    name="heartbeat",
                    description="Send periodic heartbeat",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Project identifier"},
                            "session_name": {"type": "string", "description": "Session name"}
                        },
                        "required": ["project_id", "session_name"]
                    }
                ),
                Tool(
                    name="list_active_agents",
                    description="List all active agents in a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "description": "Project identifier"}
                        },
                        "required": ["project_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                if name == "register_agent":
                    project_id = arguments["project_id"]
                    session_name = arguments["session_name"]
                    task_id = arguments["task_id"]
                    branch = arguments["branch"]
                    description = arguments["description"]
                    
                    # Store agent info
                    agent_data = {
                        "task_id": task_id,
                        "branch": branch,
                        "description": description,
                        "status": "active",
                        "started_at": datetime.now().isoformat(),
                        "project_id": project_id
                    }
                    
                    agents_key = self._get_key(project_id, "agents")
                    await self.redis_client.hset(agents_key, session_name, json.dumps(agent_data))
                    
                    # Set initial heartbeat
                    heartbeat_key = self._get_key(project_id, "heartbeat")
                    await self.redis_client.hset(heartbeat_key, session_name, datetime.now().isoformat())
                    
                    logger.info(f"Registered agent {session_name} for project {project_id}")
                    return [TextContent(type="text", text=f"Agent {session_name} registered successfully for project {project_id}")]
                
                elif name == "mark_task_completed":
                    project_id = arguments["project_id"]
                    session_name = arguments["session_name"]
                    task_id = arguments["task_id"]
                    
                    # Store completion status
                    completion_key = self._get_key(project_id, "completed_tasks")
                    completion_data = {
                        "task_id": task_id,
                        "session_name": session_name,
                        "completed_at": datetime.now().isoformat()
                    }
                    await self.redis_client.hset(completion_key, task_id, json.dumps(completion_data))
                    
                    logger.info(f"Task {task_id} marked as completed by agent {session_name}")
                    return [TextContent(type="text", text=f"Task {task_id} marked as completed")]
                
                elif name == "heartbeat":
                    project_id = arguments["project_id"]
                    session_name = arguments["session_name"]
                    
                    heartbeat_key = self._get_key(project_id, "heartbeat")
                    await self.redis_client.hset(heartbeat_key, session_name, datetime.now().isoformat())
                    
                    return [TextContent(type="text", text=f"Heartbeat recorded for {session_name}")]
                
                elif name == "list_active_agents":
                    project_id = arguments["project_id"]
                    
                    agents_key = self._get_key(project_id, "agents")
                    agents = await self.redis_client.hgetall(agents_key)
                    
                    active_agents = []
                    for session, data in agents.items():
                        agent_info = json.loads(data)
                        active_agents.append(f"{session}: {agent_info['description']}")
                    
                    result = "Active agents:\n" + "\n".join(active_agents) if active_agents else "No active agents"
                    return [TextContent(type="text", text=result)]
                
                else:
                    raise ValueError(f"Unknown tool: {name}")
                    
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting SplitMind Agent Communication Server with Redis")
        
        await self.initialize()
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        finally:
            await self.cleanup()


async def run_server():
    """Run the server"""
    server = AgentCommunicationServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(run_server())