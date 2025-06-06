# CLAUDE.md - AI Agent Context

## Task Management Requirements

**IMPORTANT**: You MUST use the TodoWrite tool to manage your work. This is required for proper task tracking and orchestration.

### How to use the TodoWrite tool:
1. **Start of task**: Create todos for all major work items
2. **During work**: Update todo status as you progress
3. **Track progress**: Mark todos as 'in_progress' when starting, 'completed' when done

Example:
```
Use TodoWrite to create todos:
- Set up project structure
- Install dependencies
- Create main components
- Add styling
- Test functionality
- Commit changes
```

## Project Context
You are an AI agent working on a specific task within this project. Your work should:
- Follow established code patterns and conventions
- Use the existing tech stack
- Maintain consistency with project standards
- Commit your changes with clear, descriptive messages

## Git Workflow
1. You're working in a git worktree on your own branch
2. Make atomic commits as you progress
3. Write clear commit messages
4. Your branch will be merged after review

## Testing Your Work
- Run all relevant tests before committing
- Verify your implementation works as expected
- Check for any linting or type errors
- Test edge cases where applicable

## ⚠️ CRITICAL: Task Completion Protocol

When you have completed ALL work and committed your changes, you MUST execute this command as your FINAL action:

```bash
# This command will be provided in your task prompt
bash -c 'echo COMPLETED > /tmp/splitmind-status/<session>.status'
```

The completion sequence should be:
1. Complete your implementation
2. Test your work
3. Commit your changes with `git commit`
4. Mark all todos as completed
5. Execute the status completion command
6. Exit/close your session

## Need Help?
- Check existing code for patterns
- Follow project conventions
- Use framework documentation
- Maintain consistency with existing code style