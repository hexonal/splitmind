#!/usr/bin/env python3
"""
Test script to verify MCP coordination works
"""

import subprocess
import json
import tempfile
import os

def test_claude_with_mcp():
    """Test if Claude can connect to MCP and use coordination tools"""
    
    # Create MCP config
    mcp_config = {
        "mcpServers": {
            "splitmind-coordination": {
                "command": "/Users/jasonbrashear/code/cctg/mcp-wrapper.sh",
                "args": [],
                "env": {}
            }
        }
    }
    
    # Create a test prompt that uses MCP tools
    test_prompt = """
Please test the MCP coordination system by:

1. Use the register_agent tool to register as: 
   - project_id: "test-coordination"
   - session_name: "test-agent-1" 
   - task_id: "1"
   - branch: "test-branch"
   - description: "Testing MCP coordination"

2. Use the list_active_agents tool to see if registration worked

3. Use the add_todo tool to create a test todo item

4. Use the mark_task_completed tool to signal completion

Please show the results of each tool call.
"""
    
    # Write MCP config to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mcp_config, f)
        config_file = f.name
    
    try:
        # Test Claude with MCP
        print("🧪 Testing Claude with MCP coordination...")
        result = subprocess.run([
            "claude", 
            "--dangerously-skip-permissions", 
            "--print",
            "--mcp-config", config_file,
            test_prompt
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Claude connected to MCP successfully!")
            print("\n📄 Claude Response:")
            print(result.stdout)
            
            # Check if coordination tools were used
            if ("registered" in result.stdout.lower() or "registration" in result.stdout.lower()) and "completed" in result.stdout.lower():
                print("\n✅ MCP coordination tools are working!")
                return True
            else:
                print("\n⚠️ MCP tools may not be working properly")
                return False
        else:
            print("❌ Claude failed to connect to MCP")
            print(f"Exit code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Test timed out - Claude may be hanging on MCP connection")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Clean up temp file
        try:
            os.unlink(config_file)
        except:
            pass

if __name__ == "__main__":
    print("🚀 Testing MCP Coordination System")
    print("=" * 50)
    
    # First test if MCP server responds
    print("1. Testing MCP server connectivity...")
    try:
        result = subprocess.run([
            "/Users/jasonbrashear/code/cctg/mcp-wrapper.sh", "--help"
        ], capture_output=True, text=True, timeout=5)
        
        if "error" not in result.stderr.lower():
            print("✅ MCP server is responding")
        else:
            print("❌ MCP server has errors:")
            print(result.stderr)
            exit(1)
    except Exception as e:
        print(f"❌ MCP server connection failed: {e}")
        exit(1)
    
    print("\n2. Testing Claude + MCP integration...")
    success = test_claude_with_mcp()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 MCP coordination system is working!")
        print("✅ Agents should now be able to coordinate properly")
    else:
        print("❌ MCP coordination system needs debugging")
        print("🔧 Check Docker container and MCP server logs")