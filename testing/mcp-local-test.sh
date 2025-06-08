#!/bin/bash
# Test if we can connect to the MCP server via Docker

# First, let's check if Docker is accessible
if ! docker ps >/dev/null 2>&1; then
    echo "Error: Docker is not accessible"
    exit 1
fi

# Check if the container is running
if ! docker ps | grep -q splitmind-mcp-server; then
    echo "Error: splitmind-mcp-server container is not running"
    exit 1
fi

# Try to execute a simple command in the container
if docker exec splitmind-mcp-server echo "Docker exec works" >/dev/null 2>&1; then
    echo "Success: Docker exec is working"
    
    # Now test the MCP server
    echo "Testing MCP server connection..."
    echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "0.1.0", "capabilities": {"tools": {}}}, "id": 1}' | \
    docker exec -i splitmind-mcp-server python /app/mcp-server-redis.py 2>&1 | head -5
else
    echo "Error: Cannot execute commands in Docker container"
    exit 1
fi