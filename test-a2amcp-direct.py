#!/usr/bin/env python3
"""
Direct test of A2AMCP functionality without agents
"""

import asyncio
from a2amcp import A2AMCPClient, Project

async def test_a2amcp_direct():
    """Test A2AMCP features directly"""
    
    print("🧪 Testing A2AMCP Direct Connection")
    print("=" * 50)
    
    # Create client
    client = A2AMCPClient(
        server_url="localhost:5050",
        docker_container="splitmind-mcp-server"
    )
    
    project_id = "test-direct"
    project = Project(client, project_id)
    
    # Test 1: Register an agent
    print("\n📝 Test 1: Agent Registration")
    try:
        result = await client.call_tool(
            "register_agent",
            project_id=project_id,
            session_name="test-agent-1",
            task_id="task-001",
            branch="feature/test",
            description="Test agent for coordination"
        )
        print(f"✅ Agent registered: {result}")
    except Exception as e:
        print(f"❌ Failed to register agent: {e}")
    
    # Test 2: Add todos
    print("\n📋 Test 2: Todo Management")
    try:
        await client.call_tool(
            "add_todo",
            project_id=project_id,
            session_name="test-agent-1",
            description="Research project structure",
            priority=1
        )
        await client.call_tool(
            "add_todo",
            project_id=project_id,
            session_name="test-agent-1",
            description="Implement core feature",
            priority=2
        )
        await client.call_tool(
            "add_todo",
            project_id=project_id,
            session_name="test-agent-1",
            description="Write tests",
            priority=3
        )
        
        todos = await client.call_tool(
            "get_todos",
            project_id=project_id,
            session_name="test-agent-1"
        )
        print(f"✅ Todos added: {len(todos)} items")
        for todo in todos:
            print(f"   - {todo}")
    except Exception as e:
        print(f"❌ Failed to manage todos: {e}")
    
    # Test 3: File locking
    print("\n🔒 Test 3: File Locking")
    try:
        lock_result = await client.call_tool(
            "announce_file_change",
            project_id=project_id,
            session_name="test-agent-1",
            file_path="src/index.ts",
            action="modify",
            description="Adding main function"
        )
        print(f"✅ File locked: {lock_result}")
        
        # Check lock
        locks = await client.call_tool(
            "list_file_locks",
            project_id=project_id
        )
        print(f"📁 Current locks: {locks}")
    except Exception as e:
        print(f"❌ Failed to lock file: {e}")
    
    # Test 4: Interface sharing
    print("\n🔗 Test 4: Interface Sharing")
    try:
        interface_def = """
interface User {
    id: string;
    email: string;
    name: string;
    role: Role;
}
"""
        await client.call_tool(
            "register_interface",
            project_id=project_id,
            session_name="test-agent-1",
            interface_name="User",
            definition=interface_def
        )
        print("✅ Interface registered")
        
        # Query interface
        user_interface = await client.call_tool(
            "query_interface",
            project_id=project_id,
            interface_name="User"
        )
        print(f"📄 Retrieved interface: {user_interface}")
    except Exception as e:
        print(f"❌ Failed to share interface: {e}")
    
    # Test 5: Agent communication
    print("\n💬 Test 5: Agent Communication")
    try:
        # Register second agent
        await client.call_tool(
            "register_agent",
            project_id=project_id,
            session_name="test-agent-2",
            task_id="task-002",
            branch="feature/test2",
            description="Second test agent"
        )
        
        # Send message
        await client.call_tool(
            "broadcast_message",
            project_id=project_id,
            session_name="test-agent-1",
            message_type="status",
            message="Starting work on main feature"
        )
        print("✅ Broadcast sent")
        
        # List active agents
        agents = await client.call_tool(
            "list_active_agents",
            project_id=project_id
        )
        print(f"👥 Active agents: {len(agents)}")
        for name, info in agents.items():
            print(f"   - {name}: {info}")
    except Exception as e:
        print(f"❌ Failed in communication: {e}")
    
    # Test 6: Cleanup
    print("\n🧹 Test 6: Cleanup")
    try:
        # Release file lock
        await client.call_tool(
            "release_file_lock",
            project_id=project_id,
            session_name="test-agent-1",
            file_path="src/index.ts"
        )
        print("✅ File lock released")
        
        # Unregister agents
        await client.call_tool(
            "unregister_agent",
            project_id=project_id,
            session_name="test-agent-1"
        )
        await client.call_tool(
            "unregister_agent",
            project_id=project_id,
            session_name="test-agent-2"
        )
        print("✅ Agents unregistered")
    except Exception as e:
        print(f"❌ Failed to cleanup: {e}")
    
    print("\n✨ A2AMCP Direct Test Complete!")
    
    # Show Redis state
    print("\n📊 Final Redis State:")
    print("Run: ./inspect-redis.sh test-direct")

if __name__ == "__main__":
    asyncio.run(test_a2amcp_direct())