"""
Real-Time Agent Coordination Monitor

Provides live monitoring of Redis coordination data with WebSocket streaming
for the Agent Coordination Command Center dashboard.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import redis.asyncio as redis
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    AGENT_REGISTERED = "agent_registered"
    AGENT_HEARTBEAT = "agent_heartbeat"
    AGENT_UNREGISTERED = "agent_unregistered"
    TODO_CREATED = "todo_created"
    TODO_UPDATED = "todo_updated"
    TODO_COMPLETED = "todo_completed"
    FILE_LOCKED = "file_locked"
    FILE_UNLOCKED = "file_unlocked"
    INTERFACE_REGISTERED = "interface_registered"
    AGENT_COMMUNICATION = "agent_communication"
    TASK_COMPLETED = "task_completed"


@dataclass
class CoordinationEvent:
    event_type: EventType
    project_id: str
    agent_id: str
    timestamp: str
    data: Dict[str, Any]


@dataclass
class AgentStatus:
    agent_id: str
    project_id: str
    task_id: str
    branch: str
    description: str
    status: str
    started_at: str
    last_heartbeat: Optional[str] = None
    is_alive: bool = True
    todo_count: int = 0
    completed_todos: int = 0
    file_locks: List[str] = None
    
    def __post_init__(self):
        if self.file_locks is None:
            self.file_locks = []


@dataclass
class CoordinationState:
    project_id: str
    agents: Dict[str, AgentStatus]
    active_file_locks: Dict[str, str]  # file_path -> agent_id
    recent_events: List[CoordinationEvent]
    interfaces: Dict[str, Any]
    communication_graph: Dict[str, List[str]]  # agent -> [agents_communicated_with]


class CoordinationMonitor:
    """Real-time monitor for agent coordination data in Redis"""
    
    def __init__(self, redis_host="localhost", redis_port=6379):
        # Use Docker redis host if running in Docker environment
        if os.getenv('DOCKER_ENV'):
            self.redis_host = "redis"
        else:
            self.redis_host = redis_host
        self.redis_client: Optional[redis.Redis] = None
        self.redis_port = redis_port
        self.previous_state: Dict[str, CoordinationState] = {}
        self.event_subscribers: List[callable] = []
        
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis_client = redis.from_url(
            f"redis://{self.redis_host}:{self.redis_port}",
            decode_responses=True
        )
        await self.redis_client.ping()
        logger.info("Coordination monitor connected to Redis")
    
    async def cleanup(self):
        """Clean up Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Coordination monitor disconnected from Redis")
    
    def subscribe_to_events(self, callback):
        """Subscribe to coordination events"""
        self.event_subscribers.append(callback)
    
    async def _emit_event(self, event: CoordinationEvent):
        """Emit event to all subscribers"""
        for callback in self.event_subscribers:
            try:
                await callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")
    
    def _get_key(self, project_id: str, *parts: str) -> str:
        """Generate Redis key with proper namespace"""
        return f"splitmind:{project_id}:{':'.join(parts)}"
    
    async def get_coordination_state(self, project_id: str) -> CoordinationState:
        """Get current coordination state for a project"""
        
        # Get agents
        agents = {}
        agents_key = self._get_key(project_id, "agents")
        agent_data = await self.redis_client.hgetall(agents_key)
        
        # Only process if we have agent data
        if agent_data:
            for agent_id, data_str in agent_data.items():
                try:
                    agent_info = json.loads(data_str)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to parse agent data for {agent_id}: {e}")
                    continue
                
                # Get heartbeat
                heartbeat_key = self._get_key(project_id, "heartbeat")
                last_heartbeat = await self.redis_client.hget(heartbeat_key, agent_id)
                
                # Check if agent is alive (heartbeat within last 2 minutes)
                is_alive = True
                if last_heartbeat:
                    try:
                        heartbeat_time = datetime.fromisoformat(last_heartbeat)
                        is_alive = datetime.now() - heartbeat_time < timedelta(minutes=2)
                    except ValueError:
                        logger.warning(f"Invalid heartbeat timestamp for {agent_id}: {last_heartbeat}")
                        is_alive = False
                
                # Get todos
                todos_key = self._get_key(project_id, "todos", agent_id)
                todos = await self.redis_client.hgetall(todos_key)
                todo_count = len(todos)
                completed_todos = 0
                
                # Safely parse todos
                for todo_str in todos.values():
                    try:
                        todo_data = json.loads(todo_str)
                        if todo_data.get('status') == 'completed':
                            completed_todos += 1
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Failed to parse todo data for {agent_id}: {e}")
                        continue
                
                # Get file locks (need to implement this in MCP server)
                file_locks = []  # TODO: Implement file lock tracking
                
                agents[agent_id] = AgentStatus(
                    agent_id=agent_id,
                    project_id=project_id,
                    task_id=agent_info.get('task_id', 'unknown'),
                    branch=agent_info.get('branch', 'unknown'),
                    description=agent_info.get('description', 'No description'),
                    status=agent_info.get('status', 'unknown'),
                    started_at=agent_info.get('started_at', datetime.now().isoformat()),
                    last_heartbeat=last_heartbeat,
                    is_alive=is_alive,
                    todo_count=todo_count,
                    completed_todos=completed_todos,
                    file_locks=file_locks
                )
        
        # Get active file locks
        active_file_locks = {}  # TODO: Implement file lock tracking
        
        # Get interfaces
        interfaces = {}  # TODO: Implement interface tracking
        
        # Build communication graph
        communication_graph = {}  # TODO: Implement message tracking
        
        # Get recent events (for now, just create from current state)
        recent_events = []
        
        return CoordinationState(
            project_id=project_id,
            agents=agents,
            active_file_locks=active_file_locks,
            recent_events=recent_events,
            interfaces=interfaces,
            communication_graph=communication_graph
        )
    
    async def detect_events(self, project_id: str) -> List[CoordinationEvent]:
        """Detect new coordination events by comparing states"""
        current_state = await self.get_coordination_state(project_id)
        events = []
        
        if project_id not in self.previous_state:
            # First time monitoring this project
            for agent_id, agent in current_state.agents.items():
                events.append(CoordinationEvent(
                    event_type=EventType.AGENT_REGISTERED,
                    project_id=project_id,
                    agent_id=agent_id,
                    timestamp=datetime.now().isoformat(),
                    data=asdict(agent)
                ))
        else:
            prev_state = self.previous_state[project_id]
            
            # Detect new agents
            for agent_id in current_state.agents:
                if agent_id not in prev_state.agents:
                    events.append(CoordinationEvent(
                        event_type=EventType.AGENT_REGISTERED,
                        project_id=project_id,
                        agent_id=agent_id,
                        timestamp=datetime.now().isoformat(),
                        data=asdict(current_state.agents[agent_id])
                    ))
            
            # Detect heartbeats
            for agent_id, agent in current_state.agents.items():
                if agent_id in prev_state.agents:
                    prev_agent = prev_state.agents[agent_id]
                    if agent.last_heartbeat != prev_agent.last_heartbeat:
                        events.append(CoordinationEvent(
                            event_type=EventType.AGENT_HEARTBEAT,
                            project_id=project_id,
                            agent_id=agent_id,
                            timestamp=agent.last_heartbeat or datetime.now().isoformat(),
                            data={"heartbeat": agent.last_heartbeat}
                        ))
            
            # Detect todo changes
            for agent_id, agent in current_state.agents.items():
                if agent_id in prev_state.agents:
                    prev_agent = prev_state.agents[agent_id]
                    if agent.completed_todos > prev_agent.completed_todos:
                        events.append(CoordinationEvent(
                            event_type=EventType.TODO_COMPLETED,
                            project_id=project_id,
                            agent_id=agent_id,
                            timestamp=datetime.now().isoformat(),
                            data={
                                "completed_todos": agent.completed_todos,
                                "total_todos": agent.todo_count
                            }
                        ))
        
        # Store current state for next comparison
        self.previous_state[project_id] = current_state
        
        # Emit events
        for event in events:
            await self._emit_event(event)
        
        return events
    
    async def monitor_project(self, project_id: str, interval: float = 1.0):
        """Monitor a project for coordination events"""
        logger.info(f"Starting coordination monitoring for project: {project_id}")
        
        while True:
            try:
                await self.detect_events(project_id)
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error monitoring coordination for {project_id}: {e}")
                await asyncio.sleep(interval)
    
    async def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get coordination statistics for a project"""
        try:
            state = await self.get_coordination_state(project_id)
            
            total_agents = len(state.agents)
            active_agents = sum(1 for agent in state.agents.values() if agent.is_alive)
            total_todos = sum(agent.todo_count for agent in state.agents.values())
            completed_todos = sum(agent.completed_todos for agent in state.agents.values())
            active_file_locks = len(state.active_file_locks)
            
            return {
                "project_id": project_id,
                "total_agents": total_agents,
                "active_agents": active_agents,
                "total_todos": total_todos,
                "completed_todos": completed_todos,
                "todo_completion_rate": completed_todos / max(total_todos, 1) * 100,
                "active_file_locks": active_file_locks,
                "agents": {agent_id: asdict(agent) for agent_id, agent in state.agents.items()},
                "file_locks": state.active_file_locks,
                "communication_graph": state.communication_graph
            }
        except Exception as e:
            logger.error(f"Error getting coordination stats for {project_id}: {e}")
            # Return empty state
            return {
                "project_id": project_id,
                "total_agents": 0,
                "active_agents": 0,
                "total_todos": 0,
                "completed_todos": 0,
                "todo_completion_rate": 0,
                "active_file_locks": 0,
                "agents": {},
                "file_locks": {},
                "communication_graph": {}
            }


# Global monitor instance
coordination_monitor = CoordinationMonitor()