#!/bin/bash
# Setup script for Hello SplitMind test project

PROJECT_NAME="hello-splitmind"
PROJECT_PATH="/Users/jasonbrashear/code/$PROJECT_NAME"

echo "🚀 Setting up test project: $PROJECT_NAME"
echo "=" * 60

# Create project directory
echo "📁 Creating project directory..."
mkdir -p "$PROJECT_PATH"
cd "$PROJECT_PATH"

# Initialize git
echo "🔧 Initializing Git repository..."
git init
git checkout -b main

# Create initial README
echo "# Hello SplitMind Test Project" > README.md
echo "" >> README.md
echo "A simple test project for demonstrating SplitMind's agent coordination system." >> README.md
echo "" >> README.md
echo "## Purpose" >> README.md
echo "This project tests parallel AI agent execution with:" >> README.md
echo "- File conflict prevention" >> README.md
echo "- Dependency management" >> README.md
echo "- Automated merging" >> README.md
echo "- Task prioritization" >> README.md

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Dependencies
node_modules/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# SplitMind
.splitmind/cache/
worktrees/
EOF

# Initial commit
git add README.md .gitignore
git commit -m "Initial commit"

# Create directories
echo "📁 Creating project structure..."
mkdir -p .splitmind
mkdir -p components
mkdir -p data
mkdir -p tests

# Create tasks.md
echo "📝 Creating tasks.md..."
cat > .splitmind/tasks.md << 'EOF'
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
EOF

# Create CLAUDE.md
echo "📝 Creating CLAUDE.md..."
cat > CLAUDE.md << 'EOF'
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

## Task-Specific Instructions

### Base HTML
Create a simple HTML5 structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello SplitMind</title>
</head>
<body>
    <!-- Components will be added here -->
</body>
</html>
```

### Base CSS
Create a minimal CSS reset:
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
}
```

### Header Component
Add a header element inside body:
```html
<!-- Header Component -->
<header id="main-header">
    <h1>Hello SplitMind</h1>
    <nav>
        <a href="#home">Home</a>
        <a href="#about">About</a>
    </nav>
</header>
```

### Footer Component
Add a footer element at the end of body:
```html
<!-- Footer Component -->
<footer id="main-footer">
    <p>&copy; 2024 SplitMind Test</p>
</footer>
```

### Other Tasks
Follow similar patterns - keep it simple and focused.

## Important
- If your task modifies a shared file (like index.html), make changes only in your designated section
- Add a comment with your task name when modifying shared files
- Keep code simple - this is for testing coordination, not production
EOF

# Create settings.json for Claude
echo "📝 Creating Claude settings..."
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Edit(**)",
      "Write(**)",
      "Bash(**)"
    ]
  },
  "preferences": {
    "autoCommit": false,
    "testBeforeCommit": false
  }
}
EOF

echo ""
echo "✅ Test project created successfully!"
echo "📍 Location: $PROJECT_PATH"
echo ""
echo "Next steps:"
echo "1. Add project to dashboard:"
echo "   curl -X POST http://localhost:8000/api/projects -H \"Content-Type: application/json\" -d '{\"id\": \"hello-splitmind\", \"name\": \"Hello SplitMind Test\", \"path\": \"$PROJECT_PATH\", \"description\": \"Quick test project\", \"max_agents\": 5}'"
echo ""
echo "2. Start orchestrator:"
echo "   curl -X POST http://localhost:8000/api/orchestrator/start -H \"Content-Type: application/json\" -d '{\"project_id\": \"hello-splitmind\"}'"
echo ""
echo "3. Monitor progress in the dashboard or with:"
echo "   python monitor-test.py"