#!/usr/bin/env python3
"""
Test the coordination monitoring API
"""

import asyncio
import sys
import os
sys.path.append('dashboard/backend')

from coordination_monitor import coordination_monitor

async def test_coordination():
    """Test coordination monitoring"""
    
    # Override Redis host to connect to Docker
    coordination_monitor.redis_host = "localhost" 
    coordination_monitor.redis_port = 6379
    
    print("🧪 Testing coordination monitoring...")
    
    try:
        # Initialize
        await coordination_monitor.initialize()
        print("✅ Connected to Redis")
        
        # Test getting stats for main-branch-test
        stats = await coordination_monitor.get_project_stats("main-branch-test")
        print(f"✅ Got coordination stats: {stats['total_agents']} agents")
        
        # Show agent details
        for agent_id, agent in stats['agents'].items():
            print(f"   🤖 {agent_id}: {agent['description']} ({'alive' if agent['is_alive'] else 'offline'})")
            print(f"      📝 Todos: {agent['completed_todos']}/{agent['todo_count']}")
        
        print(f"📊 Project stats:")
        print(f"   Active agents: {stats['active_agents']}/{stats['total_agents']}")
        print(f"   Todo completion: {stats['todo_completion_rate']:.1f}%")
        print(f"   File locks: {stats['active_file_locks']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await coordination_monitor.cleanup()

if __name__ == "__main__":
    asyncio.run(test_coordination())