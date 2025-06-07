# A2AMCP Usage Guide for SplitMind

## Overview

A2AMCP (Agent-to-Agent Model Context Protocol) is now integrated into SplitMind, providing revolutionary multi-agent coordination capabilities. Your AI agents can now communicate, share context, and avoid conflicts automatically.

## Quick Start

### 1. Launch SplitMind with A2AMCP

```bash
./launch-with-a2amcp.sh
```

This script:
- Starts the A2AMCP server infrastructure (Docker containers)
- Configures Claude CLI for MCP communication
- Launches the SplitMind dashboard
- Shows real-time coordination status

### 2. Check Coordination Status

In the dashboard, look for the **Agent Coordination** panel on the left side:
- 🟢 **Active** - A2AMCP is running and agents can coordinate
- 🟡 **Not Available** - A2AMCP server is not running
- 🔴 **Error** - Check Docker and server logs

## What A2AMCP Provides

### 1. **Automatic Agent Registration**
When agents start, they automatically:
- Register with the coordination server
- See other active agents
- Share their task description

### 2. **File Conflict Prevention**
Before modifying any file, agents:
- Check if another agent is working on it
- Wait or negotiate access
- Prevent merge conflicts before they happen

### 3. **Shared Context**
Agents can:
- Share interfaces and type definitions
- Query each other for information
- Maintain consistency across the codebase

### 4. **Task Coordination**
- Agents share their todo lists
- Others can see progress in real-time
- Smart task distribution based on activity

## How It Works

### Agent Prompts
Every agent receives A2AMCP instructions automatically:

```
MANDATORY: You MUST use the MCP communication tools.

1. Register yourself:
   register_agent("project-id", "session-name", "task-id", "branch", "description")

2. Create todo list:
   add_todo("project-id", "session-name", "Research approach", 1)
   update_todo("project-id", "session-name", "todo-1", "completed")

3. Coordinate files:
   announce_file_change("project-id", "session-name", "src/api.ts", "modify", "Adding endpoint")
   release_file_lock("project-id", "session-name", "src/api.ts")

4. Share interfaces:
   register_interface("project-id", "session-name", "User", "interface User {...}")
   query_interface("project-id", "User")

5. Communicate:
   query_agent("project-id", "from", "to", "type", "question")
   broadcast_message("project-id", "session", "type", "message")
```

### Merge Queue Enhancement
The merge queue now:
- Checks A2AMCP file locks before merging
- Negotiates with active agents
- Prevents conflicts proactively
- Notifies agents about pending merges

### Dashboard Features
The Agent Coordination panel shows:
- Active agent count
- Task completion progress
- Shared interfaces
- Recent file changes
- Communication activity

## Example Scenarios

### Scenario 1: Parallel Frontend Development
```
Agent 1 (Components): Building Button, Card, Modal
Agent 2 (Layout): Creating Header, Footer, Sidebar
Agent 3 (Styling): Setting up design system

Result: No conflicts! Each agent knows what others are building.
```

### Scenario 2: API Development
```
Agent 1: Creates User interface, shares it immediately
Agent 2: Queries the interface, builds user endpoints
Agent 3: Uses the interface for authentication logic

Result: Consistent types across all implementations!
```

### Scenario 3: Conflict Resolution
```
Agent 1: Working on src/config.ts
Agent 2: Needs to modify src/config.ts
A2AMCP: Agent 2 waits, queries Agent 1 timeline
Agent 1: Finishes, releases lock
Agent 2: Proceeds with changes

Result: No merge conflict!
```

## Monitoring Coordination

### 1. Dashboard Metrics
- **Active Agents**: Currently working agents
- **Task Progress**: Overall completion percentage  
- **Shared Interfaces**: Number of shared types
- **Recent Changes**: File modification activity

### 2. Redis Monitoring
```bash
# Connect to Redis
docker exec -it splitmind-redis redis-cli

# See all projects
KEYS project:*

# See agents in a project
HGETALL project:myproject:agents

# See todos
LRANGE project:myproject:todos:task-001 0 -1

# See file locks
HGETALL project:myproject:locks
```

### 3. Server Logs
```bash
# View A2AMCP server logs
docker-compose -f A2AMCP/docker-compose.yml logs -f mcp-server

# View Redis logs
docker-compose -f A2AMCP/docker-compose.yml logs -f redis
```

## Best Practices

### 1. **Let Agents Register First**
- Always ensure registration succeeds
- Check for MCP tool availability
- Fail fast if coordination isn't working

### 2. **Use Descriptive Task Names**
- Other agents see these descriptions
- Clear names prevent duplicate work
- Include scope in the description

### 3. **Share Early and Often**
- Register interfaces immediately after creation
- Update todos frequently
- Broadcast major changes

### 4. **Handle Conflicts Gracefully**
- Implement retry logic for file locks
- Query other agents before waiting
- Consider alternative files if blocked

### 5. **Monitor Coordination Health**
- Check the dashboard regularly
- Watch for stuck agents
- Review communication patterns

## Troubleshooting

### A2AMCP Not Available
```bash
# Check if Docker is running
docker ps

# Start A2AMCP manually
cd A2AMCP && ./quickstart.sh

# Check server status
curl http://localhost:5000/health
```

### Agents Not Coordinating
1. Check Claude CLI config:
   ```bash
   cat ~/.config/claude-code/config.json
   ```

2. Verify MCP server in config:
   ```json
   {
     "mcpServers": {
       "splitmind-coordination": {
         "command": "docker",
         "args": ["exec", "-i", "splitmind-mcp-server", "python", "/app/mcp_server_redis.py"]
       }
     }
   }
   ```

3. Test registration manually in Claude

### File Lock Issues
```bash
# Clear all locks (use with caution!)
docker exec -it splitmind-redis redis-cli
> DEL project:myproject:locks
```

## Advanced Configuration

### Custom Conflict Strategies
In your task configuration:
```python
task.conflict_strategy = "negotiate"  # or "wait", "abort", "queue"
task.conflict_timeout = 120  # seconds
```

### Priority-Based Access
```python
task.file_priority = {
    "src/critical.ts": 10,  # High priority
    "src/normal.ts": 5,     # Normal priority
}
```

### Agent Communication Patterns
```python
# Broadcast pattern
broadcast_message(project_id, session, "announcement", "Starting refactor")

# Query-response pattern
response = query_agent(project_id, from, to, "api", "What's the User schema?")

# Event pattern
register_event_handler("file_locked", handle_file_lock)
```

## Performance Impact

- **Registration**: < 100ms
- **File lock check**: < 50ms
- **Interface query**: < 20ms
- **Message delivery**: < 200ms
- **Overall overhead**: < 5% on task completion time

## Future Enhancements

1. **Visual Communication Graph**: See agent interactions
2. **Conflict Prediction**: ML-based conflict avoidance
3. **Smart Task Distribution**: Auto-assign based on skills
4. **Cross-Project Coordination**: Share between projects
5. **Agent Specialization**: Role-based communication

## Conclusion

A2AMCP transforms SplitMind from parallel execution to true collaborative development. Your AI agents now work as a coordinated team, sharing knowledge and avoiding conflicts automatically.

For more details, see:
- [A2AMCP Documentation](https://github.com/webdevtodayjason/A2AMCP)
- [Integration Plan](./A2AMCP-INTEGRATION-PLAN.md)
- [SplitMind Documentation](./README.md)