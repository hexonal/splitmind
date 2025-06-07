# A2AMCP Integration Plan for SplitMind

## Overview

A2AMCP (Agent-to-Agent Model Context Protocol) will transform how SplitMind agents coordinate by providing:
- Real-time agent communication
- File conflict prevention
- Shared context management
- Task coordination

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SplitMind Dashboard                       │
├─────────────────────────────────────────────────────────────┤
│                    Orchestrator (Python)                      │
│  - Spawns agents with A2AMCP prompts                        │
│  - Monitors agent coordination via Redis                     │
│  - Manages task assignments                                  │
├─────────────────────────────────────────────────────────────┤
│                  A2AMCP Infrastructure                        │
│  ┌─────────────────┐                ┌─────────────────┐     │
│  │  MCP Server     │◄──────────────►│     Redis       │     │
│  │  (Port 5000)    │                │  (Port 6379)    │     │
│  └─────────────────┘                └─────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│              Claude Code Agents (tmux sessions)              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│  │Agent 1 │ │Agent 2 │ │Agent 3 │ │Agent 4 │ │Agent N │   │
│  │task-001│ │task-002│ │task-003│ │task-004│ │task-...│   │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Phase 1: Infrastructure Setup

1. **Install A2AMCP SDK**
   ```bash
   pip install a2amcp-sdk
   ```

2. **Deploy A2AMCP Server**
   - Add to SplitMind's launch process
   - Configure Docker Compose integration
   - Ensure Redis persistence

3. **Configure Claude Code**
   - Update Claude CLI config for MCP server
   - Create MCP configuration template

### Phase 2: Orchestrator Integration

1. **Update Agent Spawning**
   - Generate A2AMCP-aware prompts
   - Include registration instructions
   - Add heartbeat requirements

2. **Add Monitoring**
   - Monitor agent coordination via Redis
   - Track file conflicts
   - Display communication in dashboard

3. **Enhanced Task Assignment**
   - Consider agent communication patterns
   - Optimize for minimal conflicts
   - Use shared context for dependencies

### Phase 3: Agent Communication Protocol

1. **Mandatory Registration**
   ```python
   # First action for every agent
   register_agent(project_id, session_name, task_id, branch, description)
   ```

2. **Todo Sharing**
   ```python
   # Break down task into todos
   add_todo(project_id, session_name, "Research approach", 1)
   add_todo(project_id, session_name, "Implement feature", 2)
   ```

3. **File Coordination**
   ```python
   # Before modifying any file
   announce_file_change(project_id, session_name, "src/api.ts", "modify", "Adding auth endpoint")
   # After completion
   release_file_lock(project_id, session_name, "src/api.ts")
   ```

4. **Interface Sharing**
   ```python
   # When creating interfaces/types
   register_interface(project_id, session_name, "User", "interface User { id: string; ... }")
   ```

### Phase 4: Conflict Resolution

1. **Merge Queue Enhancement**
   - Check A2AMCP file locks before merging
   - Coordinate merge order based on dependencies
   - Handle interface conflicts

2. **Real-time Conflict Prevention**
   - Agents negotiate file access
   - Automatic retry with backoff
   - Priority-based resolution

### Phase 5: Dashboard Enhancement

1. **Agent Communication View**
   - Show active conversations
   - Display file locks
   - Monitor shared interfaces

2. **Coordination Metrics**
   - Track communication patterns
   - Measure conflict rates
   - Optimize task distribution

## Key Integration Points

### 1. Orchestrator (orchestrator.py)

```python
from a2amcp import A2AMCPClient, Project

class A2AMCPOrchestrator(OrchestratorManager):
    def __init__(self, ws_manager):
        super().__init__(ws_manager)
        self.a2amcp = A2AMCPClient(server_url="localhost:5000")
    
    async def spawn_agent(self, task, project_id):
        # Generate A2AMCP-aware prompt
        prompt = self.generate_a2amcp_prompt(task, project_id)
        
        # Standard agent spawning
        session_name = await super().spawn_agent(task, project_id, prompt)
        
        # Monitor via A2AMCP
        project = Project(self.a2amcp, project_id)
        await self.monitor_agent_coordination(project, session_name)
```

### 2. Prompt Generation

```python
def generate_a2amcp_prompt(self, task, project_id):
    session_name = f"task-{task.task_id}"
    
    base_prompt = task.prompt or task.description
    
    a2amcp_instructions = f"""
MANDATORY A2AMCP COORDINATION:

1. FIRST ACTION - Register yourself:
   register_agent("{project_id}", "{session_name}", "{task.task_id}", "{task.branch}", "{task.title}")

2. CREATE TODO LIST:
   Break down your task and share progress:
   - add_todo("{project_id}", "{session_name}", "task description", priority)
   - update_todo("{project_id}", "{session_name}", "todo_id", "in_progress")

3. COORDINATE FILE ACCESS:
   Before modifying ANY file:
   - announce_file_change("{project_id}", "{session_name}", "filepath", "change_type", "description")
   After completion:
   - release_file_lock("{project_id}", "{session_name}", "filepath")

4. SHARE INTERFACES:
   When creating types/interfaces:
   - register_interface("{project_id}", "{session_name}", "InterfaceName", "definition")

5. COMMUNICATE:
   - Check who's active: list_active_agents("{project_id}")
   - Query other agents: query_agent("{project_id}", "{session_name}", "target", "type", "question")
   - Send heartbeat every 30 seconds: heartbeat("{project_id}", "{session_name}")

Your task:
{base_prompt}
"""
    
    return a2amcp_instructions
```

### 3. Merge Queue Enhancement

```python
class A2AMCPMergeQueue(MergeQueue):
    async def can_merge(self, task):
        # Check traditional constraints
        if not await super().can_merge(task):
            return False
        
        # Check A2AMCP file locks
        project = Project(self.a2amcp, task.project_id)
        
        # Get files modified in this branch
        modified_files = self.get_modified_files(task.branch)
        
        # Check if any are locked by other agents
        for file_path in modified_files:
            lock_status = await project.client.call_tool(
                "check_file_lock",
                project_id=task.project_id,
                file_path=file_path
            )
            
            if lock_status.get('locked') and lock_status['locked_by'] != task.session:
                return False
        
        return True
```

### 4. Claude Configuration

```json
{
  "mcpServers": {
    "splitmind-coordination": {
      "command": "docker",
      "args": ["exec", "-i", "splitmind-mcp-server", "python", "/app/mcp_server_redis.py"],
      "env": {}
    }
  }
}
```

## Benefits

1. **Conflict Prevention**: 80%+ reduction in merge conflicts
2. **Faster Development**: Agents don't duplicate work
3. **Better Quality**: Shared interfaces ensure consistency
4. **Real-time Awareness**: Agents know what others are doing
5. **Smart Coordination**: Automatic dependency resolution

## Timeline

- **Week 1**: Infrastructure setup and basic integration
- **Week 2**: Orchestrator updates and prompt engineering
- **Week 3**: Dashboard enhancements and monitoring
- **Week 4**: Testing and optimization

## Success Metrics

1. **Conflict Rate**: < 5% of merges have conflicts
2. **Communication Usage**: > 90% of agents use coordination tools
3. **Task Completion**: 20% faster with coordination
4. **Interface Sharing**: 100% of shared types registered
5. **Agent Awareness**: < 1% duplicate work

## Next Steps

1. Start A2AMCP server with quickstart script
2. Update orchestrator with A2AMCP client
3. Modify prompt generation
4. Test with sample project
5. Monitor coordination patterns
6. Optimize based on results