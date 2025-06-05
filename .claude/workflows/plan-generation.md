# Plan Generation Workflow

This workflow is used by the SplitMind orchestrator to generate comprehensive project plans.

## Workflow Steps

### 1. Context Gathering
When a user requests plan generation:
- Project overview is provided
- Initial prompt describes desired outcome
- Integration settings (Dart, etc.) are available

### 2. Plan Generation
The orchestrator will:
1. Call `generate-plan.md` command with project context
2. Use MCP tools as needed:
   - `brave_search` for researching best practices
   - `context7_set` to store architectural decisions
   - `dart_create_task` if Dart integration is configured

### 3. Task Creation
From the generated plan:
1. Extract actionable tasks
2. Group related tasks
3. Identify dependencies
4. Create tasks in the project

### 4. Execution
After plan and tasks are created:
1. Orchestrator can be started
2. Agents claim tasks from the board
3. Each agent uses appropriate command files
4. Work progresses in parallel

## Integration Points

### Claude CLI
```bash
# Example of how the dashboard calls Claude
claude .claude/commands/generate-plan.md \
  --var project_overview="$OVERVIEW" \
  --var initial_prompt="$PROMPT" \
  --var dart_workspace="$WORKSPACE"
```

### MCP Tools Usage
Within the plan generation:
```
# Research best practices
brave_search: "best practices $TECHNOLOGY microservices architecture"

# Store decisions
context7_set: "arch_database_choice" "PostgreSQL chosen for ACID compliance"

# Create Dart tasks if configured
dart_create_task: workspace="$WORKSPACE" dartboard="$DARTBOARD" \
  title="Initialize Project" description="Set up project structure"
```

## Expected Output

The plan generation should produce:

1. **Structured Plan**
   - Project overview
   - Architecture decisions
   - Development phases
   - Risk factors
   - Success metrics

2. **Task List**
   - 10-20 initial tasks
   - Clear titles and descriptions
   - Logical grouping
   - Dependency information

3. **Context Storage**
   - Key decisions saved
   - Technology choices documented
   - Best practices noted

## Error Handling

If plan generation fails:
1. Check Claude CLI is installed
2. Verify command files exist
3. Ensure project has valid Git repo
4. Check MCP tool availability

## Customization

Users can customize plan generation by:
1. Editing `.claude/commands/generate-plan.md`
2. Adding project-specific templates
3. Configuring MCP tool preferences
4. Setting up integration credentials