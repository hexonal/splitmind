# SplitMind Agent Coordination Test Plan

## Overview
Create a simple test project with quick tasks that agents can complete in 1-2 minutes each, allowing rapid testing of the coordination system.

## Test Project: "Hello SplitMind"
A minimal web project where each agent adds a specific feature to demonstrate coordination.

### Project Structure
```
hello-splitmind/
├── index.html
├── styles.css
├── script.js
├── components/
├── data/
└── tests/
```

## Test Tasks Definition

### 1. Base HTML (Priority: 10, No dependencies)
**Description**: Create basic HTML structure
**Duration**: ~1 minute
**Files**: index.html
**Test**: Creates index.html with basic structure

### 2. Base CSS (Priority: 10, No dependencies)
**Description**: Create basic CSS file
**Duration**: ~1 minute
**Files**: styles.css
**Test**: Creates styles.css with reset and base styles

### 3. Header Component (Priority: 8, Depends on: base-html)
**Description**: Add header section to HTML
**Duration**: ~1 minute
**Files**: index.html (shared), components/header.css
**Test**: Adds header element to body

### 4. Footer Component (Priority: 8, Depends on: base-html)
**Description**: Add footer section to HTML
**Duration**: ~1 minute
**Files**: index.html (shared), components/footer.css
**Test**: Adds footer element to body

### 5. Theme Styles (Priority: 7, Depends on: base-css)
**Description**: Add dark theme CSS variables
**Duration**: ~1 minute
**Files**: styles.css (shared), components/theme.css
**Test**: Adds CSS variables for theming

### 6. JavaScript Base (Priority: 9, No dependencies)
**Description**: Create main JavaScript file
**Duration**: ~1 minute
**Files**: script.js
**Test**: Creates script.js with DOMContentLoaded

### 7. Data File (Priority: 9, No dependencies)
**Description**: Create JSON data file
**Duration**: ~30 seconds
**Files**: data/content.json
**Test**: Creates simple JSON structure

### 8. Main Content (Priority: 6, Depends on: header-component, footer-component)
**Description**: Add main content section
**Duration**: ~1 minute
**Files**: index.html (shared), components/main.css
**Test**: Adds main element between header and footer

### 9. Interactive Features (Priority: 5, Depends on: javascript-base, main-content)
**Description**: Add click handlers and interactivity
**Duration**: ~1 minute
**Files**: script.js (shared), components/interactive.js
**Test**: Adds event listeners

### 10. Final Integration (Priority: 4, Depends on: all above)
**Description**: Link all files together
**Duration**: ~1 minute
**Files**: index.html (shared)
**Test**: Ensures all CSS/JS files are linked

## Expected Behavior

### Parallel Execution Groups:
1. **First Wave** (can run simultaneously):
   - Base HTML
   - Base CSS
   - JavaScript Base
   - Data File

2. **Second Wave** (after dependencies met):
   - Header Component (after base-html)
   - Footer Component (after base-html)
   - Theme Styles (after base-css)

3. **Third Wave**:
   - Main Content (after header & footer)

4. **Fourth Wave**:
   - Interactive Features (after javascript-base & main-content)

5. **Final Wave**:
   - Final Integration (after all)

### Merge Order:
1. Base HTML (merge_order: 1)
2. Base CSS (merge_order: 2)
3. JavaScript Base (merge_order: 3)
4. Data File (merge_order: 4)
5. Header Component (merge_order: 5)
6. Footer Component (merge_order: 6)
7. Theme Styles (merge_order: 7)
8. Main Content (merge_order: 8)
9. Interactive Features (merge_order: 9)
10. Final Integration (merge_order: 10)

## Test Metrics

### Success Criteria:
1. **No File Conflicts**: Tasks modifying same files don't run simultaneously
2. **Dependency Respect**: Tasks wait for dependencies
3. **Parallel Execution**: Independent tasks run in parallel
4. **Merge Success**: All tasks merge without conflicts
5. **Completion Time**: All tasks complete in < 10 minutes

### Monitoring Points:
1. Agent spawn order
2. Concurrent agent count
3. File conflict detection logs
4. Merge queue processing
5. Task state transitions

## Implementation Files

### 1. Test Project Setup Script
```bash
#!/bin/bash
# setup-test-project.sh

PROJECT_NAME="hello-splitmind"
PROJECT_PATH="/Users/jasonbrashear/code/$PROJECT_NAME"

# Create project directory
mkdir -p "$PROJECT_PATH"
cd "$PROJECT_PATH"

# Initialize git
git init
git checkout -b main
echo "# Hello SplitMind Test Project" > README.md
git add README.md
git commit -m "Initial commit"

# Create .splitmind directory
mkdir -p .splitmind

echo "✅ Test project created at $PROJECT_PATH"
```

### 2. Test Tasks File
```markdown
# tasks.md

## Task: Base HTML
- status: unclaimed
- branch: base-html
- session: null
- description: Create basic HTML structure with doctype, head, and body
- priority: 10
- merge_order: 1
- exclusive_files: [index.html]
- shared_files: []

## Task: Base CSS
- status: unclaimed
- branch: base-css
- session: null
- description: Create basic CSS file with reset and root styles
- priority: 10
- merge_order: 2
- exclusive_files: [styles.css]
- shared_files: []

## Task: Header Component
- status: unclaimed
- branch: header-component
- session: null
- description: Add header section with navigation
- dependencies: [base-html]
- priority: 8
- merge_order: 5
- exclusive_files: [components/header.css]
- shared_files: [index.html]
- initialization_deps: [base-html]

## Task: Footer Component
- status: unclaimed
- branch: footer-component
- session: null
- description: Add footer section with copyright
- dependencies: [base-html]
- priority: 8
- merge_order: 6
- exclusive_files: [components/footer.css]
- shared_files: [index.html]
- initialization_deps: [base-html]

## Task: Theme Styles
- status: unclaimed
- branch: theme-styles
- session: null
- description: Add CSS variables for dark theme
- dependencies: [base-css]
- priority: 7
- merge_order: 7
- exclusive_files: [components/theme.css]
- shared_files: [styles.css]
- initialization_deps: [base-css]

## Task: JavaScript Base
- status: unclaimed
- branch: javascript-base
- session: null
- description: Create main JavaScript file with DOMContentLoaded
- priority: 9
- merge_order: 3
- exclusive_files: [script.js]
- shared_files: []

## Task: Data File
- status: unclaimed
- branch: data-file
- session: null
- description: Create JSON data file with sample content
- priority: 9
- merge_order: 4
- exclusive_files: [data/content.json]
- shared_files: []

## Task: Main Content
- status: unclaimed
- branch: main-content
- session: null
- description: Add main content section between header and footer
- dependencies: [header-component, footer-component]
- priority: 6
- merge_order: 8
- exclusive_files: [components/main.css]
- shared_files: [index.html]
- initialization_deps: [header-component, footer-component]

## Task: Interactive Features
- status: unclaimed
- branch: interactive-features
- session: null
- description: Add JavaScript interactivity and event handlers
- dependencies: [javascript-base, main-content]
- priority: 5
- merge_order: 9
- exclusive_files: [components/interactive.js]
- shared_files: [script.js]
- initialization_deps: [javascript-base, main-content]

## Task: Final Integration
- status: unclaimed
- branch: final-integration
- session: null
- description: Link all CSS and JS files in HTML
- dependencies: [base-html, base-css, javascript-base, header-component, footer-component, theme-styles, main-content, interactive-features]
- priority: 4
- merge_order: 10
- exclusive_files: []
- shared_files: [index.html]
- initialization_deps: [main-content, interactive-features]
```

### 3. CLAUDE.md for Test Project
```markdown
# CLAUDE.md - Hello SplitMind Test Project

## Overview
You are working on a simple test project to demonstrate the SplitMind coordination system. Each task should be completed quickly (1-2 minutes).

## Task Guidelines
1. Keep changes minimal and focused
2. Add clear comments in your code
3. Commit with descriptive messages
4. Complete your specific task only

## File Structure
- `index.html` - Main HTML file
- `styles.css` - Base styles
- `script.js` - Main JavaScript
- `components/` - Component-specific files
- `data/` - Data files

## Important
- If your task modifies a shared file (like index.html), make changes only in your designated section
- Add a comment with your task name when modifying shared files
- Keep code simple - this is for testing coordination, not production
```

### 4. Test Monitoring Script
```python
#!/usr/bin/env python3
# monitor-test.py

import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

class TestMonitor:
    def __init__(self, project_id):
        self.project_id = project_id
        self.start_time = datetime.now()
        self.events = []
        
    def log_event(self, event_type, data):
        self.events.append({
            "time": (datetime.now() - self.start_time).total_seconds(),
            "type": event_type,
            "data": data
        })
        print(f"[{self.events[-1]['time']:.1f}s] {event_type}: {data}")
    
    def check_status(self):
        # Get project stats
        result = subprocess.run([
            "curl", "-s", 
            f"http://localhost:8000/api/projects/{self.project_id}/stats"
        ], capture_output=True, text=True)
        
        stats = json.loads(result.stdout)
        return stats
    
    def check_agents(self):
        # Get running agents
        result = subprocess.run([
            "curl", "-s",
            f"http://localhost:8000/api/projects/{self.project_id}/agents"
        ], capture_output=True, text=True)
        
        agents = json.loads(result.stdout)
        return agents
    
    def monitor(self):
        print(f"Starting test monitor for project: {self.project_id}")
        print("=" * 60)
        
        last_stats = None
        while True:
            # Check current status
            stats = self.check_status()
            agents = self.check_agents()
            
            # Log changes
            if last_stats != stats:
                self.log_event("STATS_CHANGE", {
                    "unclaimed": stats["unclaimed_tasks"],
                    "claimed": stats["claimed_tasks"],
                    "in_progress": stats["in_progress_tasks"],
                    "completed": stats["completed_tasks"],
                    "merged": stats["merged_tasks"],
                    "active_agents": len(agents)
                })
                last_stats = stats
            
            # Check for completion
            if stats["merged_tasks"] == stats["total_tasks"]:
                self.log_event("TEST_COMPLETE", {
                    "total_time": (datetime.now() - self.start_time).total_seconds(),
                    "total_tasks": stats["total_tasks"]
                })
                break
            
            # Show running agents
            if agents:
                agent_info = [f"{a['task_title']} ({a['status']})" for a in agents]
                self.log_event("AGENTS", agent_info)
            
            time.sleep(5)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        print("\n" + "=" * 60)
        print("TEST REPORT")
        print("=" * 60)
        
        # Calculate metrics
        total_time = self.events[-1]["time"]
        spawn_events = [e for e in self.events if e["type"] == "STATS_CHANGE"]
        max_concurrent = max(e["data"]["active_agents"] for e in spawn_events)
        
        print(f"Total Time: {total_time:.1f} seconds")
        print(f"Max Concurrent Agents: {max_concurrent}")
        print(f"Total Events: {len(self.events)}")
        
        # Save detailed log
        with open("test-report.json", "w") as f:
            json.dump({
                "project_id": self.project_id,
                "total_time": total_time,
                "max_concurrent": max_concurrent,
                "events": self.events
            }, f, indent=2)
        
        print("\nDetailed report saved to test-report.json")

if __name__ == "__main__":
    monitor = TestMonitor("hello-splitmind")
    monitor.monitor()
```

## Test Execution Steps

1. **Create Test Project**:
   ```bash
   ./setup-test-project.sh
   ```

2. **Add to Dashboard**:
   ```bash
   curl -X POST http://localhost:8000/api/projects \
     -H "Content-Type: application/json" \
     -d '{
       "id": "hello-splitmind",
       "name": "Hello SplitMind Test",
       "path": "/Users/jasonbrashear/code/hello-splitmind",
       "description": "Quick test project for agent coordination",
       "max_agents": 5
     }'
   ```

3. **Copy Test Files**:
   - Copy tasks.md to project
   - Copy CLAUDE.md to project

4. **Configure Orchestrator**:
   ```bash
   curl -X PUT http://localhost:8000/api/orchestrator/config \
     -H "Content-Type: application/json" \
     -d '{
       "max_concurrent_agents": 4,
       "auto_merge": true,
       "auto_spawn_interval": 10,
       "enabled": true
     }'
   ```

5. **Start Orchestrator**:
   ```bash
   curl -X POST http://localhost:8000/api/orchestrator/start \
     -H "Content-Type: application/json" \
     -d '{"project_id": "hello-splitmind"}'
   ```

6. **Monitor Test**:
   ```bash
   python monitor-test.py
   ```

## Expected Results

### Timeline:
- 0-30s: First wave spawns (4 agents)
- 1-2min: First wave completes
- 2-3min: Second wave spawns (3 agents)
- 3-4min: Second wave completes
- 4-5min: Third wave spawns (1 agent)
- 5-6min: Third wave completes
- 6-7min: Fourth wave spawns (1 agent)
- 7-8min: Fourth wave completes
- 8-9min: Final wave spawns (1 agent)
- 9-10min: All tasks complete and merged

### Success Indicators:
1. No merge conflicts
2. All tasks complete successfully
3. Dependencies respected
4. Parallel execution where possible
5. Total time < 10 minutes