# MCP (Model Context Protocol) Tools Available

This document describes the tools available to Claude through MCP servers.

## Available Tools

### 🔍 Brave Search
Search the web using Brave Search API for up-to-date information.

**Usage:**
```
brave_search: "your search query"
```

**Example:**
```
brave_search: "latest React 18 features"
```

### 📄 Context7
Access and manage contextual information across your project.

**Usage:**
```
context7_get: "context_key"
context7_set: "context_key" "value"
context7_list: 
```

**Examples:**
```
context7_set: "project_tech_stack" "React, TypeScript, FastAPI, SQLite"
context7_get: "project_tech_stack"
```

### 🎯 Dart
Update and manage projects in Dart workspace.

**Usage:**
```
dart_update: workspace="<workspace_id>" dartboard="<dartboard_id>" content="<update>"
dart_create_task: workspace="<workspace_id>" dartboard="<dartboard_id>" title="<title>" description="<description>"
```

**Examples:**
```
dart_update: workspace="ws_123" dartboard="db_456" content="Completed API integration"
dart_create_task: workspace="ws_123" dartboard="db_456" title="Add authentication" description="Implement JWT auth"
```

## Project-Specific Configuration

You can set project-specific MCP configurations in your project's `.splitmind/mcp-config.md`:

```markdown
# MCP Configuration for [Your Project]

## Dart Settings
- Workspace ID: ws_123456
- Dartboard ID: db_789012

## Context7 Namespaces
- Technical: tech_
- Business: biz_
- Architecture: arch_

## Search Preferences
- Include domains: developer.mozilla.org, react.dev
- Exclude domains: w3schools.com
```

## Using MCP Tools in Commands

In your command files (`.claude/commands/*.md`), you can reference these tools:

```markdown
# Example Command: research.md

You are a research assistant. Your task is to:

1. Use brave_search to find the latest best practices for the requested topic
2. Store key findings in context7 with appropriate namespaces
3. Update the Dart project board with research summary
4. Generate a comprehensive report

Available project settings:
- Dart Workspace: {{dart_workspace}}
- Dart Dartboard: {{dart_dartboard}}
```