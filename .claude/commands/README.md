# SplitMind Command Files

Command files allow you to create custom AI workflows and control how the orchestrator handles different types of tasks.

## Overview

Each `.md` file in this directory represents a command that can be executed by the AI orchestrator. Commands can:
- Use MCP tools (Brave Search, Context7, Dart)
- Access project context through variables
- Follow specific workflows you define
- Generate structured outputs

## Command Structure

```markdown
# Command Name

Brief description of what this command does.

## Instructions
Step-by-step instructions for the AI to follow.

## Variables
- `{{variable_name}}` - Description of the variable

## Output Format
Expected output structure.
```

## Available Commands

### 📋 generate-plan.md
Generates a comprehensive project plan based on overview and initial prompt.
- Analyzes project requirements
- Creates development phases
- Suggests specific tasks
- Stores architectural decisions

### 🔍 research.md
Conducts research on specific topics using web search.
- Searches for best practices
- Stores findings in Context7
- Creates research reports
- Updates project boards

### ⚡ implement-feature.md
Implements a specific feature following project conventions.
- Retrieves project context
- Follows coding standards
- Writes tests
- Updates documentation

### 🧪 spawn.md
Original agent spawner for parallel task execution.
- Reads tasks.md
- Creates git worktrees
- Launches AI agents in tmux

### 🔀 merge.md
Handles merging completed work back to main branch.
- Reviews agent changes
- Resolves conflicts
- Updates task status

## Creating Custom Commands

1. Create a new `.md` file in this directory
2. Define clear instructions
3. Use variables for dynamic content
4. Specify expected output format
5. Reference MCP tools as needed

### Example: Custom Test Command

```markdown
# Run Tests

You are a testing specialist. Run comprehensive tests for the project.

## Instructions

1. Check test framework: `context7_get: "test_framework"`
2. Run unit tests
3. Run integration tests
4. Generate coverage report
5. Update Dart board with results

## Variables
- `{{test_scope}}` - Specific area to test (or "all")
- `{{coverage_threshold}}` - Minimum coverage percentage

## Output Format
- Test results summary
- Coverage statistics
- Failed test details
- Recommendations
```

## Variable System

Variables are replaced when commands are executed:
- Project variables: `{{project_name}}`, `{{project_path}}`
- Custom variables: Passed when invoking commands
- Context variables: Retrieved from Context7
- Integration variables: `{{dart_workspace}}`, `{{dart_dartboard}}`

## MCP Tool Integration

Commands can use MCP tools directly:

```markdown
# Search for solution
brave_search: "React performance optimization techniques"

# Store finding
context7_set: "perf_react_tips" "Use React.memo for expensive components..."

# Update project board
dart_update: workspace="{{dart_workspace}}" dartboard="{{dart_dartboard}}" content="Researched performance optimizations"
```

## Best Practices

1. **Be Specific**: Clear, detailed instructions produce better results
2. **Use Context**: Store and retrieve project context for consistency
3. **Structure Output**: Define clear output formats for predictability
4. **Handle Errors**: Include error handling instructions
5. **Document Variables**: List all variables and their purposes

## Tips

- Test commands with small tasks first
- Iterate on instructions based on results
- Share useful commands with the community
- Keep commands focused on single responsibilities
- Use research commands before implementation commands