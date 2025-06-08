#!/usr/bin/env python3
"""
Simple A2AMCP coordination demo with explicit test scenarios
"""

import httpx
import json
import asyncio
from datetime import datetime

async def create_simple_demo():
    """Create a simple demo to test A2AMCP coordination"""
    
    async with httpx.AsyncClient() as client:
        # Create test project
        project_id = "simple-coord-demo"
        
        # First, check if project exists and delete if needed
        try:
            response = await client.delete(f"http://localhost:8000/api/projects/{project_id}")
            if response.status_code == 200:
                print("🧹 Cleaned up existing project")
        except:
            pass
        
        project_data = {
            "id": project_id,
            "name": "Simple Coordination Demo",
            "path": f"/tmp/{project_id}",
            "description": "Demonstrates A2AMCP agent coordination",
            "max_agents": 3
        }
        
        print("📁 Creating demo project...")
        response = await client.post(
            "http://localhost:8000/api/projects",
            json=project_data
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create project: {response.text}")
            return
        
        # Create specific tasks to demonstrate coordination
        tasks = [
            {
                "title": "Create User and Role interfaces",
                "description": "Create TypeScript interfaces for User and Role in types/models.ts",
                "branch": "feature/interfaces",
                "priority": 1,
                "prompt": """Create TypeScript interfaces in types/models.ts:

1. Create a Role interface with id, name, and permissions array
2. Create a User interface with id, email, name, role (Role type), and createdAt

IMPORTANT: After creating the interfaces, you MUST register them using:
- register_interface("simple-coord-demo", "YOUR_SESSION_NAME", "Role", "interface Role { ... }")
- register_interface("simple-coord-demo", "YOUR_SESSION_NAME", "User", "interface User { ... }")

This allows other agents to use your interfaces."""
            },
            {
                "title": "Create API service using interfaces",
                "description": "Create user service that uses the shared User interface",
                "branch": "feature/user-service",
                "priority": 2,
                "dependencies": [],
                "prompt": """Create a user service in services/userService.ts:

1. First, query the User interface created by another agent:
   - query_interface("simple-coord-demo", "User")
   
2. Import and use the User interface in your service
3. Create methods: getUser, createUser, updateUser, deleteUser

IMPORTANT: You must coordinate with the interfaces agent to get the correct types."""
            },
            {
                "title": "Create config file",
                "description": "Create shared configuration in config/app.config.ts",
                "branch": "feature/config",
                "priority": 1,
                "prompt": """Create a configuration file in config/app.config.ts with:

1. Database configuration
2. API settings
3. Authentication settings

This file will be modified by multiple agents, so use file locking:
- announce_file_change("simple-coord-demo", "YOUR_SESSION_NAME", "config/app.config.ts", "create", "Creating initial config")
- release_file_lock("simple-coord-demo", "YOUR_SESSION_NAME", "config/app.config.ts") when done"""
            }
        ]
        
        # Add tasks
        print("\n📝 Adding coordination test tasks...")
        for i, task_data in enumerate(tasks):
            # Use query parameters for simple task creation with prompt
            params = {
                "title": task_data["title"],
                "description": task_data.get("description", ""),
                "priority": task_data.get("priority", 1)
            }
            
            # Add prompt and dependencies if available
            if "prompt" in task_data:
                params["prompt"] = task_data["prompt"]
            
            response = await client.post(
                f"http://localhost:8000/api/projects/{project_id}/tasks",
                params=params
            )
            if response.status_code == 200:
                task = response.json()
                print(f"✅ Added: {task_data['title']} (ID: {task['id']})")
            else:
                print(f"❌ Failed to add task: {response.text}")
        
        # Start orchestrator
        print("\n🚀 Starting orchestrator with A2AMCP...")
        response = await client.post(
            "http://localhost:8000/api/orchestrator/start",
            params={"project_id": project_id}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start orchestrator: {response.text}")
            return
        
        print("✅ Orchestrator started")
        print(f"\n📊 Monitor coordination with: ./monitor-a2amcp.sh {project_id}")
        print("🌐 Redis Commander: http://localhost:8081")
        print("\n⏳ Waiting for agents to start coordinating...")
        
        # Quick coordination check
        await asyncio.sleep(10)
        
        # Check if agents registered
        print("\n🔍 Checking agent registration...")
        response = await client.get(
            f"http://localhost:8000/api/projects/{project_id}/coordination-stats"
        )
        
        if response.status_code == 200:
            try:
                stats = response.json()
            except:
                print("⚠️  Could not parse coordination stats")
                stats = {}
            if stats.get('enabled'):
                print("✅ A2AMCP is enabled")
                print(f"📊 Active agents: {stats.get('active_agents', 0)}")
                
                if stats.get('active_agents', 0) > 0:
                    print("\n🎉 SUCCESS! Agents are coordinating!")
                    print("\nYou can now:")
                    print("1. Watch tmux sessions: tmux ls")
                    print("2. Attach to agent: tmux attach -t 1-simple-coord-demo")
                    print("3. Monitor Redis: ./monitor-a2amcp.sh simple-coord-demo")
                else:
                    print("\n⚠️  No agents registered yet. Check:")
                    print("1. Is Docker running?")
                    print("2. Did agents accept --dangerously-skip-permissions?")
                    print("3. Check agent logs in tmux")
            else:
                print("❌ A2AMCP is not enabled")
        
        print(f"\n📁 Project ID: {project_id}")

if __name__ == "__main__":
    asyncio.run(create_simple_demo())