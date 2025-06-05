"""
Data models for SplitMind Dashboard
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    UNCLAIMED = "unclaimed"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MERGED = "merged"


class Task(BaseModel):
    """Task model"""
    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.UNCLAIMED
    branch: str
    session: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None


class Agent(BaseModel):
    """AI Agent model"""
    id: str
    session_name: str
    task_id: str
    task_title: str
    branch: str
    status: str = "running"
    progress: int = 0
    started_at: datetime = Field(default_factory=datetime.now)
    logs: List[str] = []


class Project(BaseModel):
    """Project model"""
    id: str
    name: str
    path: str
    description: Optional[str] = None
    project_overview: Optional[str] = None  # Detailed project description
    initial_prompt: Optional[str] = None    # Initial prompt for plan generation
    plan: Optional[str] = None              # Generated project plan
    max_agents: int = 5
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    git_remote: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProjectStats(BaseModel):
    """Project statistics"""
    total_tasks: int = 0
    unclaimed_tasks: int = 0
    claimed_tasks: int = 0
    in_progress_tasks: int = 0
    completed_tasks: int = 0
    merged_tasks: int = 0
    active_agents: int = 0
    total_agents_run: int = 0


class OrchestratorConfig(BaseModel):
    """Orchestrator configuration"""
    max_concurrent_agents: int = 5
    auto_merge: bool = False
    merge_strategy: str = "merge"  # merge, squash, ff
    auto_spawn_interval: int = 60  # seconds
    enabled: bool = False
    anthropic_api_key: Optional[str] = None  # API key for plan generation
    anthropic_model: str = "claude-sonnet-4-20250514"  # Model to use for generation


class PlanGenerationRequest(BaseModel):
    """Request model for plan generation"""
    project_overview: str
    initial_prompt: str


class PlanGenerationResponse(BaseModel):
    """Response model for plan generation"""
    plan: str
    suggested_tasks: List[Dict[str, str]]  # List of task titles and descriptions


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str  # task_update, agent_update, log, notification
    project_id: Optional[str] = None
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)