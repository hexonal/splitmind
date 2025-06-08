# Register with A2AMCP

Registers this agent with the coordination system.

## Usage
```
/register
```

## What it does
1. Registers your session with the A2AMCP coordination server
2. Announces your presence to other agents
3. Sets up file lock monitoring
4. Enables inter-agent communication

## Example
```
/register
```

This will execute:
```javascript
register_agent("{{PROJECT_ID}}", "{{SESSION_NAME}}", "{{TASK_ID}}", "{{BRANCH}}", "{{TASK_TITLE}}")
```