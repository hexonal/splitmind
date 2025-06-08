# Claude Agent Instructions for SplitMind

## IMPORTANT: Multi-Agent Coordination

You are part of a multi-agent system. Other AI agents are working on related tasks in parallel.

### 🚀 FIRST ACTION - Register Yourself

Before doing ANYTHING else, you MUST use the MCP tools to register:

```
register_agent(project_id, session_name, task_id, branch, description)
```

Use the values from your environment:
- project_id: The project you're working on
- session_name: Your tmux session name (visible in terminal)
- task_id: Your task number
- branch: Your git branch
- description: Your task title

### 📝 During Your Work

1. **Track Progress**: Use `add_todo()` to track subtasks
2. **File Coordination**: Before modifying any file, use `announce_file_change()`
3. **Share Interfaces**: Use `register_interface()` when creating types/interfaces
4. **Query Others**: Use `query_interface()` to get shared types
5. **Heartbeat**: Send `heartbeat()` every 30-60 seconds

### 🏁 Task Completion

When you've completed all work and committed changes:

1. Mark all todos as completed
2. Release all file locks with `release_file_lock()`
3. Mark task completed: `mark_task_completed(project_id, session_name, task_id)`
4. Unregister: `unregister_agent()`
5. Signal completion: `bash -c 'echo COMPLETED > /tmp/splitmind-status/SESSION_NAME.status'`

## Available MCP Tools

The following coordination tools are available via MCP:

- `register_agent` - Register yourself with the system
- `unregister_agent` - Unregister when done
- `heartbeat` - Send periodic heartbeat
- `add_todo` - Add a todo item
- `update_todo` - Update todo status
- `complete_todo` - Mark todo as done
- `get_todos` - Get your todo list
- `announce_file_change` - Lock a file before editing
- `release_file_lock` - Release file lock
- `check_file_lock` - Check if file is locked
- `list_file_locks` - List all locked files
- `register_interface` - Share a type/interface
- `query_interface` - Get a shared interface
- `list_interfaces` - List all shared interfaces
- `send_message` - Send message to another agent
- `broadcast_message` - Broadcast to all agents
- `check_messages` - Check your messages
- `list_active_agents` - See other active agents

## Git Workflow

1. All work happens in your feature branch
2. Commit frequently with clear messages
3. The orchestrator will handle merging to main
4. Never switch branches or merge manually

## Quality Standards

1. Write clean, maintainable code
2. Follow existing patterns and conventions
3. Add appropriate error handling
4. Test your changes before marking complete
5. Document complex logic

Remember: You're part of a team. Coordinate, communicate, and help build something great together!