# Task: Generate Project Plan and Tasks

You are tasked with generating a comprehensive project plan and creating actionable tasks for a software project.

## Project Information

**Project Name**: {{project_name}}
**Project Overview**: {{project_overview}}
**Initial Prompt**: {{initial_prompt}}

## Instructions

Please create a detailed project plan that includes:

1. **Project Analysis**
   - Understand the requirements from the overview and prompt
   - Identify key features and functionality needed
   - Consider technical constraints and best practices

2. **Architecture Decisions**
   - Choose appropriate technologies
   - Design system architecture
   - Plan data models and API structure

3. **Development Phases**
   - Break down the project into logical phases
   - Each phase should have clear goals
   - Include time estimates if possible

4. **Task Generation**
   - Create 10-15 specific, actionable tasks
   - Each task should be self-contained
   - Include clear acceptance criteria

## Output Format

Please provide your response in the following format:

### Project Plan
```markdown
# Project Plan: [Project Name]

## Overview
[Brief summary]

## Architecture Decisions
- [Decision 1]
- [Decision 2]
...

## Development Phases
[Detailed phases with tasks]
```

### Suggested Tasks
For each task, provide in this exact format:
```
- **Task Title** - Brief description of what needs to be done
```

Make sure tasks are specific and actionable. For example:
- **Initialize Git Repository** - Set up Git repo with .gitignore and initial README
- **Create Database Schema** - Design and implement database tables for user management
- **Build Authentication API** - Implement JWT-based auth endpoints for login/register

Generate tasks that are appropriate for the specific project described in the overview and prompt.