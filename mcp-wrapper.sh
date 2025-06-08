#!/bin/bash
# MCP wrapper script for A2AMCP
# This script runs the MCP server command properly from any context

docker exec -i splitmind-mcp-server python /app/mcp-server-redis.py "$@"