# A2AMCP Integration Test Plan for SplitMind

## Overview
This document provides a comprehensive test plan for verifying the A2AMCP (Agent-to-Agent Model Context Protocol) integration with SplitMind. The tests ensure that multiple AI agents can coordinate effectively, share context, and avoid conflicts while working on parallel tasks.

## Prerequisites

### 1. System Requirements
- Docker Desktop installed and running
- Node.js (v18+) and npm
- Python 3.8+
- Git
- Anthropic API key
- At least 8GB free RAM (for Docker containers)

### 2. Setup Steps
```bash
# 1. Ensure Docker is running
docker --version

# 2. Clone A2AMCP if not already present
git clone https://github.com/webdevtodayjason/A2AMCP.git

# 3. Launch SplitMind with A2AMCP
./launch-with-a2amcp.sh

# 4. Verify services are running
docker ps --filter name=splitmind
```

## Test Scenarios

### Test 1: Basic Agent Registration and Communication

**Objective**: Verify agents can register with A2AMCP and see each other

**Setup**:
1. Create a new project called "test-coordination"
2. Generate these simple tasks:
   ```
   - Task 1: Create a User interface in types/user.ts
   - Task 2: Create a Product interface in types/product.ts
   - Task 3: Create API endpoints in api/users.ts
   ```

**Expected Results**:
- [ ] Agents register successfully (check Redis: `docker exec -it splitmind-redis redis-cli`)
- [ ] Agent Coordination panel shows 3 active agents
- [ ] Agents can query each other's status
- [ ] No "Cannot access MCP coordination tools" errors in agent logs

**Verification Commands**:
```bash
# Check registered agents
docker exec -it splitmind-redis redis-cli HGETALL project:test-coordination:agents

# Check agent todos
docker exec -it splitmind-redis redis-cli LRANGE project:test-coordination:todos:task-001 0 -1
```

### Test 2: File Conflict Prevention

**Objective**: Verify agents coordinate when working on shared files

**Setup**:
1. Create tasks that intentionally overlap:
   ```
   - Task 1: Update config.ts with API settings
   - Task 2: Update config.ts with database settings
   - Task 3: Update config.ts with auth settings
   ```

**Expected Results**:
- [ ] First agent locks config.ts
- [ ] Other agents detect the lock and wait
- [ ] Agents negotiate access order
- [ ] No merge conflicts occur
- [ ] All changes are successfully integrated

**Monitoring**:
```bash
# Watch file locks in real-time
watch -n 2 'docker exec -it splitmind-redis redis-cli HGETALL project:test-coordination:locks'

# Check agent messages
docker exec -it splitmind-redis redis-cli LRANGE project:test-coordination:messages 0 -1
```

### Test 3: Interface Sharing

**Objective**: Verify agents can share and query interfaces

**Setup**:
1. Create interdependent tasks:
   ```
   - Task 1: Create User and Role interfaces
   - Task 2: Create authentication service using User interface
   - Task 3: Create user API endpoints using User interface
   ```

**Expected Results**:
- [ ] Task 1 agent registers User and Role interfaces
- [ ] Task 2 and 3 agents query and use shared interfaces
- [ ] All implementations use consistent types
- [ ] No TypeScript errors in final merged code

**Verification**:
```bash
# List shared interfaces
docker exec -it splitmind-redis redis-cli HKEYS project:test-coordination:interfaces

# Get interface definition
docker exec -it splitmind-redis redis-cli HGET project:test-coordination:interfaces User
```

### Test 4: Dependency Chain Coordination

**Objective**: Test complex dependency handling with coordination

**Setup**:
1. Create a dependency chain:
   ```
   - Task 1: Set up database models (priority: 1)
   - Task 2: Create API service layer (priority: 2, depends on Task 1)
   - Task 3: Create REST endpoints (priority: 3, depends on Task 2)
   - Task 4: Create frontend components (priority: 4, depends on Task 3)
   ```

**Expected Results**:
- [ ] Tasks start in correct order
- [ ] Later tasks query earlier agents for schemas
- [ ] Each agent marks todos as completed
- [ ] Merge queue respects dependencies
- [ ] Final code has no missing dependencies

### Test 5: Conflict Resolution During Merge

**Objective**: Test A2AMCP-aware merge conflict handling

**Setup**:
1. Create tasks that will cause merge conflicts:
   ```
   - Task 1: Refactor authentication module
   - Task 2: Add new auth features (slight delay)
   - Task 3: Update auth tests
   ```

**Expected Results**:
- [ ] Merge queue detects active file locks
- [ ] Queue negotiates with active agents before merging
- [ ] Agents receive merge notifications
- [ ] Conflicts are prevented or auto-resolved
- [ ] No manual intervention required

### Test 6: Multi-File Coordination

**Objective**: Test coordination across multiple files

**Setup**:
1. Create a feature that spans multiple files:
   ```
   - Task 1: Create shopping cart backend (models, services)
   - Task 2: Create cart API endpoints
   - Task 3: Create cart UI components
   - Task 4: Create cart state management
   ```

**Expected Results**:
- [ ] Agents coordinate file ownership
- [ ] Shared files are properly locked/released
- [ ] All agents complete successfully
- [ ] Feature works end-to-end after merging

### Test 7: Agent Communication Patterns

**Objective**: Test different communication patterns

**Setup**:
1. Create tasks that require communication:
   ```
   - Task 1: Design system architect (creates design tokens)
   - Task 2: Component builder (queries design system)
   - Task 3: Documentation writer (queries all agents)
   ```

**Expected Results**:
- [ ] Broadcast messages reach all agents
- [ ] Query-response patterns work correctly
- [ ] Agents update status based on messages
- [ ] Communication log shows all interactions

### Test 8: Performance and Scale

**Objective**: Test system under load

**Setup**:
1. Create 10+ simultaneous tasks:
   ```
   - Multiple feature implementations
   - Multiple bug fixes
   - Multiple test additions
   ```

**Expected Results**:
- [ ] All agents register successfully
- [ ] Coordination overhead < 5% task time
- [ ] No deadlocks or race conditions
- [ ] Redis performance remains stable
- [ ] Dashboard remains responsive

## Monitoring Tools

### 1. Real-time Coordination Monitor
```bash
# Create monitoring script
cat > monitor-coordination.sh << 'EOF'
#!/bin/bash
while true; do
  clear
  echo "=== ACTIVE AGENTS ==="
  docker exec -it splitmind-redis redis-cli HGETALL project:$1:agents
  echo -e "\n=== FILE LOCKS ==="
  docker exec -it splitmind-redis redis-cli HGETALL project:$1:locks
  echo -e "\n=== RECENT MESSAGES ==="
  docker exec -it splitmind-redis redis-cli LRANGE project:$1:messages -10 -1
  sleep 2
done
EOF

chmod +x monitor-coordination.sh
./monitor-coordination.sh test-coordination
```

### 2. A2AMCP Server Logs
```bash
# Follow MCP server logs
docker-compose -f A2AMCP/docker-compose.yml logs -f mcp-server

# Follow Redis logs
docker-compose -f A2AMCP/docker-compose.yml logs -f redis
```

### 3. Agent Session Monitoring
```bash
# List all tmux sessions
tmux ls

# Attach to specific agent session
tmux attach -t 1-test-coordination

# Monitor all agent outputs
for session in $(tmux ls | cut -d: -f1); do
  echo "=== $session ==="
  tmux capture-pane -t $session -p | tail -20
done
```

## Troubleshooting Guide

### Issue: Agents can't register
**Solution**:
1. Check Docker containers: `docker ps`
2. Verify Claude config: `cat ~/.config/claude-code/config.json`
3. Test MCP server: `docker exec -it splitmind-mcp-server python -m mcp_server_redis`

### Issue: File locks not working
**Solution**:
1. Check Redis connectivity: `docker exec -it splitmind-redis redis-cli PING`
2. Verify project ID matches: Check agent prompts
3. Clear stale locks: `docker exec -it splitmind-redis redis-cli DEL project:PROJECT_ID:locks`

### Issue: Agents not communicating
**Solution**:
1. Check agent registration first
2. Verify MCP tools in Claude output
3. Check for error messages in agent sessions
4. Review A2AMCP server logs

### Issue: Merge conflicts despite coordination
**Solution**:
1. Check timing of file modifications
2. Verify agents are releasing locks
3. Check merge queue logs
4. Review git history for actual changes

## Success Metrics

### Quantitative Metrics
- Agent registration success rate: 100%
- File conflict prevention rate: > 95%
- Auto-merge success rate: > 90%
- Communication latency: < 200ms
- Coordination overhead: < 5%

### Qualitative Metrics
- No manual merge conflict resolution needed
- Agents demonstrate awareness of each other
- Shared interfaces used consistently
- Complex features built successfully
- System remains stable under load

## Test Automation

### Create Test Project Script
```bash
cat > create-test-project.sh << 'EOF'
#!/bin/bash
PROJECT_ID="test-coordination-$(date +%s)"

# Create project via API
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "id": "'$PROJECT_ID'",
    "name": "A2AMCP Test Project",
    "path": "/tmp/'$PROJECT_ID'",
    "project_scope": "Test A2AMCP coordination features",
    "initial_prompt": "Build a simple web API with user management"
  }'

echo "Created project: $PROJECT_ID"
EOF

chmod +x create-test-project.sh
```

### Automated Test Runner
```python
# test_a2amcp_integration.py
import asyncio
import httpx
import time
from datetime import datetime

async def test_coordination():
    """Run automated A2AMCP coordination tests"""
    
    async with httpx.AsyncClient() as client:
        # Create test project
        project_data = {
            "id": f"test-auto-{int(time.time())}",
            "name": "Automated A2AMCP Test",
            "path": f"/tmp/test-auto-{int(time.time())}",
            "project_scope": "Test coordination",
            "initial_prompt": "Create user management system"
        }
        
        # Create project
        response = await client.post(
            "http://localhost:8000/api/projects",
            json=project_data
        )
        project = response.json()
        
        # Generate tasks with AI
        await client.post(
            f"http://localhost:8000/api/projects/{project['id']}/generate_plan",
            json={"prompt": project['initial_prompt']}
        )
        
        # Start orchestrator
        await client.post(
            f"http://localhost:8000/api/orchestrator/start/{project['id']}"
        )
        
        # Monitor coordination
        for _ in range(60):  # Monitor for 10 minutes
            stats = await client.get(
                f"http://localhost:8000/api/orchestrator/coordination_stats/{project['id']}"
            )
            print(f"[{datetime.now()}] Coordination stats: {stats.json()}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(test_coordination())
```

## Reporting

### Test Report Template
```markdown
# A2AMCP Integration Test Report

**Date**: [DATE]
**Tester**: [NAME]
**Environment**: [LOCAL/STAGING/PROD]

## Test Summary
- Total Tests Run: X
- Passed: X
- Failed: X
- Skipped: X

## Test Results

### Test 1: Basic Registration
- Status: [PASS/FAIL]
- Notes: [Details]
- Evidence: [Screenshots/Logs]

[Continue for each test...]

## Issues Found
1. [Issue description]
   - Severity: [HIGH/MEDIUM/LOW]
   - Reproduction steps
   - Suggested fix

## Recommendations
- [Improvement suggestions]
- [Performance optimizations]
- [Feature requests]

## Conclusion
[Overall assessment of A2AMCP integration]
```

## Next Steps

After completing these tests:

1. **Document Results**: Create test report with findings
2. **Fix Issues**: Address any coordination failures
3. **Optimize Performance**: Tune Redis and message passing
4. **Enhance Features**: Add missing coordination capabilities
5. **Create Demos**: Record successful multi-agent coordination
6. **Update Documentation**: Incorporate test findings

Remember: The goal is to prove that A2AMCP enables truly collaborative AI development where agents work together as a team, not just in parallel.