#!/bin/bash
# Test if Claude can connect to MCP server

echo "Testing Claude MCP connection..."

# Create a simple test prompt
PROMPT="List available MCP tools"

# Create MCP config
MCP_CONFIG='{
  "mcpServers": {
    "test": {
      "command": "/Users/jasonbrashear/code/cctg/mcp-wrapper.sh",
      "args": [],
      "env": {}
    }
  }
}'

# Run Claude with MCP config
echo "Running: claude --dangerously-skip-permissions --mcp-config \"\$MCP_CONFIG\" \"\$PROMPT\""
claude --dangerously-skip-permissions --mcp-config "$MCP_CONFIG" "$PROMPT"