"""
FastAPI backend for SplitMind Dashboard
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
from pathlib import Path
from contextlib import asynccontextmanager
import asyncio
import json
import os
import platform

from .models import (
    Project, Task, Agent, ProjectStats, 
    OrchestratorConfig, WebSocketMessage,
    PlanGenerationRequest, PlanGenerationResponse
)
from .config import config_manager
from .project_manager import ProjectManager
from .orchestrator import OrchestratorManager
from .websocket_manager import WebSocketManager
from .claude_integration import claude

# WebSocket manager
ws_manager = WebSocketManager()

# Orchestrator manager
orchestrator = OrchestratorManager(ws_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    print("🚀 SplitMind Dashboard API started")
    yield
    # Shutdown
    try:
        await orchestrator.stop()
        # Close all websocket connections
        for conn in list(ws_manager.active_connections):
            try:
                await conn.close()
            except:
                pass
        ws_manager.active_connections.clear()
    except Exception:
        pass
    print("👋 SplitMind Dashboard API stopped")

# Create FastAPI app with lifespan management
app = FastAPI(
    title="SplitMind Command Center",
    description="AI Coder Orchestration Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Project Management Endpoints
# ============================================================================

@app.get("/api/projects", response_model=List[Project])
async def get_projects():
    """Get all projects"""
    return config_manager.get_projects()


@app.post("/api/projects", response_model=Project)
async def create_project(project: Project):
    """Create a new project"""
    try:
        new_project = config_manager.add_project(project)
        
        # Notify via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            type="project_created",
            project_id=new_project.id,
            data=new_project.dict()
        ))
        
        return new_project
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project"""
    project = config_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.put("/api/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, updates: dict):
    """Update a project"""
    try:
        updated_project = config_manager.update_project(project_id, updates)
        
        # Notify via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            type="project_updated",
            project_id=updated_project.id,
            data=updated_project.dict()
        ))
        
        return updated_project
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        config_manager.delete_project(project_id)
        
        # Notify via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            type="project_deleted",
            project_id=project_id,
            data={"project_id": project_id}
        ))
        
        return {"message": "Project deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/projects/{project_id}/stats", response_model=ProjectStats)
async def get_project_stats(project_id: str):
    """Get project statistics"""
    try:
        pm = ProjectManager(project_id)
        return pm.get_stats()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Task Management Endpoints
# ============================================================================

@app.get("/api/projects/{project_id}/tasks", response_model=List[Task])
async def get_tasks(project_id: str):
    """Get all tasks for a project"""
    try:
        pm = ProjectManager(project_id)
        return pm.get_tasks()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/projects/{project_id}/tasks", response_model=Task)
async def create_task(project_id: str, title: str, description: Optional[str] = None):
    """Create a new task"""
    try:
        pm = ProjectManager(project_id)
        task = pm.add_task(title, description)
        
        # Notify via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            type="task_created",
            project_id=project_id,
            data=task.dict()
        ))
        
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/api/projects/{project_id}/tasks/{task_id}", response_model=Task)
async def update_task(project_id: str, task_id: str, updates: dict):
    """Update a task"""
    try:
        pm = ProjectManager(project_id)
        task = pm.update_task(task_id, updates)
        
        # Notify via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            type="task_updated",
            project_id=project_id,
            data=task.dict()
        ))
        
        return task
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/projects/{project_id}/tasks/{task_id}")
async def delete_task(project_id: str, task_id: str):
    """Delete a task"""
    try:
        pm = ProjectManager(project_id)
        pm.delete_task(task_id)
        
        # Notify via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            type="task_deleted",
            project_id=project_id,
            data={"task_id": task_id}
        ))
        
        return {"message": "Task deleted"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# Agent Management Endpoints
# ============================================================================

@app.get("/api/projects/{project_id}/agents", response_model=List[Agent])
async def get_agents(project_id: str):
    """Get running agents for a project"""
    try:
        pm = ProjectManager(project_id)
        return pm.get_agents()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/projects/{project_id}/agents/{agent_id}/launch-iterm")
async def launch_iterm(project_id: str, agent_id: str):
    """Launch iTerm for a specific agent session"""
    try:
        import subprocess
        
        # AppleScript to open iTerm and attach to tmux session
        applescript = f'''
        tell application "iTerm"
            create window with default profile
            tell current session of current window
                write text "tmux attach -t {agent_id}"
            end tell
        end tell
        '''
        
        subprocess.run(['osascript', '-e', applescript])
        
        return {"message": f"Launched iTerm for session {agent_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Orchestrator Control Endpoints
# ============================================================================

@app.get("/api/orchestrator/config", response_model=OrchestratorConfig)
async def get_orchestrator_config():
    """Get orchestrator configuration"""
    return config_manager.get_orchestrator_config()


@app.put("/api/orchestrator/config", response_model=OrchestratorConfig)
async def update_orchestrator_config(config: OrchestratorConfig):
    """Update orchestrator configuration"""
    config_manager.update_orchestrator_config(config)
    orchestrator.update_config(config)
    return config


@app.post("/api/orchestrator/start")
async def start_orchestrator(project_id: str):
    """Start the orchestrator for a project"""
    try:
        await orchestrator.start(project_id)
        return {"message": "Orchestrator started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/orchestrator/stop")
async def stop_orchestrator():
    """Stop the orchestrator"""
    await orchestrator.stop()
    return {"message": "Orchestrator stopped"}


@app.get("/api/orchestrator/status")
async def get_orchestrator_status():
    """Get orchestrator status"""
    return {
        "running": orchestrator.is_running(),
        "current_project": orchestrator.current_project_id
    }


# ============================================================================
# Plan Generation Endpoints
# ============================================================================

@app.post("/api/projects/{project_id}/generate-plan")
async def generate_plan(project_id: str, request: dict):
    """Generate a project plan using AI"""
    try:
        project = config_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_overview = request.get("project_overview", "")
        initial_prompt = request.get("initial_prompt", "")
        dart_workspace = request.get("dart_workspace", "")
        dart_dartboard = request.get("dart_dartboard", "")
        
        # Get orchestrator config for API key and model
        orch_config = config_manager.get_orchestrator_config()
        api_key = orch_config.anthropic_api_key
        model = orch_config.anthropic_model
        
        # Use Claude integration to generate plan
        project_info = {
            "project_name": project.name,
            "project_path": project.path,
            "project_overview": project_overview,
            "initial_prompt": initial_prompt,
            "dart_workspace": dart_workspace,
            "dart_dartboard": dart_dartboard
        }
        
        # Generate plan using Anthropic API
        result = claude.generate_plan(project_info, api_key, model)
        
        # Check if generation was successful
        if not result.get("success", False):
            raise HTTPException(
                status_code=400, 
                detail=result.get("error", "Failed to generate plan")
            )
        
        plan = result["plan"]
        suggested_tasks = result["suggested_tasks"]
        
        # Update project with overview, prompt, and plan
        updated_project = config_manager.update_project(project_id, {
            "project_overview": project_overview,
            "initial_prompt": initial_prompt,
            "plan": plan
        })
        
        # Create initial tasks based on the plan
        pm = ProjectManager(project_id)
        created_tasks = []
        
        # Create tasks from suggested tasks
        for task_info in suggested_tasks:
            task = pm.add_task(
                task_info["title"], 
                task_info["description"]
            )
            created_tasks.append(task)
        
        # Notify via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            type="plan_generated",
            project_id=project_id,
            data={
                "plan": plan,
                "tasks_created": len(created_tasks)
            }
        ))
        
        return {
            "plan": plan,
            "tasks_created": len(created_tasks),
            "message": "Plan generated successfully",
            "cost_info": result.get("cost_info", {}),
            "usage": result.get("usage", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except (WebSocketDisconnect, asyncio.CancelledError, Exception):
        ws_manager.disconnect(websocket)


# ============================================================================
# File System Endpoints
# ============================================================================

@app.get("/api/filesystem/browse")
async def browse_filesystem(path: Optional[str] = None):
    """Browse filesystem directories"""
    try:
        if not path:
            # Default to user's home directory
            path = str(Path.home())
        
        current_path = Path(path)
        
        # Security check - ensure path exists and is a directory
        if not current_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")
        
        if not current_path.is_dir():
            # If it's a file, get its parent directory
            current_path = current_path.parent
        
        # Get directory contents
        directories = []
        try:
            for item in sorted(current_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    # Check if it's a git repository
                    is_git_repo = (item / '.git').exists()
                    directories.append({
                        "name": item.name,
                        "path": str(item),
                        "is_git_repo": is_git_repo
                    })
        except PermissionError:
            # Handle permission errors gracefully
            pass
        
        # Get parent directory (if not at root)
        parent_path = None
        if current_path != current_path.parent:
            parent_path = str(current_path.parent)
        
        # Common quick access paths
        quick_access = []
        home = Path.home()
        common_paths = [
            (home, "Home"),
            (home / "Desktop", "Desktop"),
            (home / "Documents", "Documents"),
            (home / "code", "Code"),
            (home / "projects", "Projects"),
            (home / "dev", "Dev"),
        ]
        
        for qpath, name in common_paths:
            if qpath.exists() and qpath.is_dir():
                quick_access.append({
                    "name": name,
                    "path": str(qpath)
                })
        
        return {
            "current_path": str(current_path),
            "parent_path": parent_path,
            "directories": directories,
            "quick_access": quick_access,
            "platform": platform.system()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/filesystem/create-folder")
async def create_folder(parent_path: str, folder_name: str):
    """Create a new folder in the filesystem"""
    try:
        if not parent_path or not folder_name:
            raise HTTPException(status_code=400, detail="Parent path and folder name are required")
        
        # Sanitize folder name
        folder_name = folder_name.strip()
        if not folder_name or '/' in folder_name or '\\' in folder_name:
            raise HTTPException(status_code=400, detail="Invalid folder name")
        
        parent = Path(parent_path)
        if not parent.exists() or not parent.is_dir():
            raise HTTPException(status_code=404, detail="Parent directory not found")
        
        new_folder = parent / folder_name
        
        # Check if folder already exists
        if new_folder.exists():
            raise HTTPException(status_code=409, detail="Folder already exists")
        
        # Create the folder
        new_folder.mkdir(parents=False, exist_ok=False)
        
        # Initialize as git repo if requested
        # For now, we'll just create the folder
        
        return {
            "success": True,
            "path": str(new_folder),
            "name": folder_name
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Static Files and Frontend
# ============================================================================

# Check if frontend is built
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    # Serve static files
    app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")
    
    # Catch-all route for React
    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        """Serve React app"""
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_path / "index.html")
else:
    @app.get("/")
    async def root():
        """API root when frontend is not built"""
        return {
            "message": "SplitMind API",
            "status": "Frontend not built",
            "docs": "/docs"
        }