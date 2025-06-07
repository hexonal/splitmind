#!/usr/bin/env python3
"""
Create a test project to demonstrate A2AMCP coordination
"""

import httpx
import json
import time
import asyncio
from datetime import datetime

async def create_coordination_test():
    """Create a test project with tasks designed to show coordination"""
    
    async with httpx.AsyncClient() as client:
        # 1. Create the test project
        project_id = f"coord-test-{int(time.time())}"
        project_data = {
            "id": project_id,
            "name": "A2AMCP Coordination Test",
            "path": f"/tmp/{project_id}",
            "description": "Test project for A2AMCP coordination",
            "project_overview": "A simple user management API to test multi-agent coordination",
            "initial_prompt": """Create a user management system with the following components:
1. TypeScript interfaces for User, Role, and Permission
2. Database models using the interfaces
3. API service layer for user operations
4. REST endpoints for CRUD operations
5. Authentication middleware
6. Unit tests for all components

Make sure to use shared interfaces and coordinate file access.""",
            "max_agents": 3
        }
        
        print(f"📁 Creating project: {project_id}")
        response = await client.post(
            "http://localhost:8000/api/projects",
            json=project_data
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to create project: {response.text}")
            return
        
        project = response.json()
        print(f"✅ Project created: {project['name']}")
        
        # 2. Generate tasks with AI (this will create tasks designed for coordination)
        print(f"🤖 Generating tasks with AI...")
        response = await client.post(
            f"http://localhost:8000/api/projects/{project_id}/generate_plan",
            json={"prompt": project_data["initial_prompt"]}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to generate plan: {response.text}")
            return
        
        print(f"✅ Tasks generated")
        
        # 3. Fetch the generated tasks
        response = await client.get(f"http://localhost:8000/api/projects/{project_id}/tasks")
        tasks = response.json()
        
        print(f"\n📋 Generated {len(tasks)} tasks:")
        for task in tasks:
            print(f"   - Task {task.get('task_id', 'N/A')}: {task['title']}")
            if task.get('dependencies'):
                print(f"     Dependencies: {task['dependencies']}")
        
        # 4. Start the orchestrator with A2AMCP
        print(f"\n🚀 Starting orchestrator with A2AMCP coordination...")
        response = await client.post(
            f"http://localhost:8000/api/orchestrator/start/{project_id}"
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start orchestrator: {response.text}")
            return
        
        print(f"✅ Orchestrator started")
        
        # 5. Monitor coordination
        print(f"\n📊 Monitoring coordination (press Ctrl+C to stop)...")
        print(f"💡 Run this in another terminal to watch live: ./monitor-a2amcp.sh {project_id}")
        print(f"🌐 Or view Redis Commander at: http://localhost:8081")
        
        try:
            while True:
                # Get coordination stats
                response = await client.get(
                    f"http://localhost:8000/api/orchestrator/coordination_stats/{project_id}"
                )
                
                if response.status_code == 200:
                    stats = response.json()
                    
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Coordination Status:")
                    print(f"   - A2AMCP Enabled: {stats.get('enabled', False)}")
                    print(f"   - Active Agents: {stats.get('active_agents', 0)}")
                    print(f"   - Total Todos: {stats.get('total_todos', 0)}")
                    print(f"   - Completed Todos: {stats.get('completed_todos', 0)}")
                    print(f"   - Shared Interfaces: {stats.get('shared_interfaces', 0)}")
                    
                    if stats.get('agents'):
                        print(f"   - Agents:")
                        for agent_id, agent_info in stats['agents'].items():
                            print(f"     • {agent_id}: {agent_info.get('status', 'unknown')}")
                
                # Get task statuses
                response = await client.get(f"http://localhost:8000/api/projects/{project_id}/tasks")
                if response.status_code == 200:
                    tasks = response.json()
                    status_counts = {}
                    for task in tasks:
                        status = task.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    print(f"   - Task Status: {json.dumps(status_counts)}")
                
                await asyncio.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Stopping orchestrator...")
            await client.post(f"http://localhost:8000/api/orchestrator/stop")
            print(f"✅ Test completed")
            print(f"\n📝 Project ID: {project_id}")
            print(f"📁 Project Path: /tmp/{project_id}")

if __name__ == "__main__":
    asyncio.run(create_coordination_test())