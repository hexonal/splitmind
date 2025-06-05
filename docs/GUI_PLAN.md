# 🎮 SplitMind Command Center - Implementation Plan

## 📋 Requirements Analysis

**Core Features:**
1. **Orchestrator Control** - Launch/stop the orchestrator
2. **Task Management** - View, add, edit, delete tasks with live status
3. **Agent Monitoring** - Real-time agent status, resource usage
4. **Session Control** - Launch iTerm to specific tmux sessions
5. **Configuration** - Set max concurrent agents
6. **Command Center Aesthetic** - Deep indigo, electric cyan, black color scheme

## 🏗️ Architecture & Tech Stack

**Frontend:**
- **React** with TypeScript for type safety
- **Tailwind CSS** for utility-first styling
- **shadcn/ui** for beautiful, accessible components
- **Framer Motion** for smooth animations
- **React Query** for data fetching and caching
- **Recharts** for agent metrics visualization (works great with shadcn/ui)
- **Lucide React** for consistent icons

**Backend:**
- **FastAPI** (Python) - Integrates well with existing Python scripts
- **WebSockets** for real-time updates
- **SQLite** for task persistence (optional, can also use tasks.md)

**Single Port Solution:**
- FastAPI will serve both the API and the static frontend files
- Default port: 8000
- Frontend built files served from `/` 
- API endpoints at `/api/*`
- WebSocket at `/ws/*`

**Launch Method:**
```bash
# Single command to launch from project root
python launch-dashboard.py

# Or with custom port
python launch-dashboard.py --port 8080
```

**Structure:**
```
splitmind/                    # Project root
├── launch-dashboard.py       # Main entry point (in root for easy access)
├── dashboard/               # All dashboard files
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── TaskBoard.tsx
│   │   │   │   ├── AgentMonitor.tsx
│   │   │   │   ├── OrchestratorControl.tsx
│   │   │   │   └── CommandCenter.tsx
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── styles/
│   │   ├── dist/              # Built frontend files
│   │   └── public/
│   │       └── splitmind-logo-200x190.png
│   └── backend/
│       ├── __init__.py
│       ├── api.py            # FastAPI main app
│       ├── orchestrator.py   # Orchestrator integration
│       ├── task_manager.py   # Task CRUD operations
│       └── agent_monitor.py  # Agent monitoring
├── scripts/                  # Existing scripts
│   ├── format-tasks.py
│   └── auto-merge.py
├── .claude/                  # Claude commands
├── assets/                   # Project assets
├── worktrees/               # Git worktrees
└── tasks.md                 # Task definitions
```

## 🎨 UI Design Concepts

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ [Logo] SplitMind Command Center          [Dark Mode]│
├─────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────────────────────────┐ │
│ │ Orchestrator│ │         Task Board                │ │
│ │   Control   │ │  [Add Task] [Refresh]             │ │
│ │             │ │  ┌─────┬─────┬─────┬─────┐       │ │
│ │ [▶ Launch]  │ │  │TODO │CLAIM│WORK │DONE │       │ │
│ │ [■ Stop]    │ │  │     │     │     │     │       │ │
│ │             │ │  │Task1│Task2│Task3│Task4│       │ │
│ │ Max Agents: │ │  │     │     │     │     │       │ │
│ │    [5]      │ │  └─────┴─────┴─────┴─────┘       │ │
│ └─────────────┘ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────┐ │
│ │              Agent Monitor                       │ │
│ │  Agent 1: auth-feature    [█████░░] 75%  [iTerm]│ │
│ │  Agent 2: api-endpoints   [███░░░░] 45%  [iTerm]│ │
│ │  Agent 3: ui-components   [██████░] 90%  [iTerm]│ │
│ │  ┌──────────────────────────────────────┐       │ │
│ │  │ Live Metrics Graph                    │       │ │
│ │  └──────────────────────────────────────┘       │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

**Color Scheme with shadcn/ui:**
```typescript
// tailwind.config.ts custom colors
colors: {
  'deep-indigo': '#1a1f3a',
  'electric-cyan': '#00ffff',
  'dark-bg': '#0a0e1a',
  
  // shadcn/ui theme extensions
  primary: {
    DEFAULT: '#00ffff',  // electric-cyan
    foreground: '#0a0e1a',
  },
  secondary: {
    DEFAULT: '#1a1f3a',  // deep-indigo
    foreground: '#00ffff',
  },
  accent: {
    DEFAULT: '#3b82f6',
    foreground: '#ffffff',
  },
}
```

**Key shadcn/ui Components to Use:**
- `Card` - For task cards and agent panels
- `Button` - With custom variants for command center feel
- `Dialog` - For task editing and configuration
- `Tabs` - For different dashboard views
- `Progress` - For agent progress indicators
- `Badge` - For task status labels
- `ScrollArea` - For task lists
- `Separator` - For visual organization
- `Alert` - For notifications
- `Command` - For keyboard shortcuts
- `DropdownMenu` - For task actions
- `Sheet` - For side panels
- `Switch` - For dark mode toggle
- `Toaster` - For notifications

## 📝 Implementation Steps

1. **Phase 1: Backend Foundation**
   - FastAPI server with endpoints for tasks, agents, orchestrator
   - WebSocket support for real-time updates
   - Integration with existing Python scripts
   - Static file serving for frontend

2. **Phase 2: Frontend Core**
   - React app setup with TypeScript
   - Tailwind CSS configuration with custom colors
   - shadcn/ui setup and component installation
   - Dark mode setup with next-themes
   - Basic layout with shadcn/ui components

3. **Phase 3: Feature Implementation**
   - Task board with drag-and-drop
   - Real-time agent monitoring
   - Orchestrator controls
   - iTerm launcher integration

4. **Phase 4: Polish**
   - Animations and transitions
   - Dark/light mode toggle
   - Error handling and notifications
   - Performance optimization

## 🚀 Key Features Detail

**1. Task Management:**
- Kanban-style board with columns: TODO, CLAIMED, IN_PROGRESS, DONE, MERGED
- Modal for adding/editing tasks
- Quick actions: delete, clone, move

**2. Agent Monitor:**
- Real-time status updates via WebSocket
- Progress bars showing task completion
- CPU/memory usage graphs
- One-click iTerm launch to tmux session

**3. Orchestrator Control:**
- Start/stop orchestrator with visual feedback
- Configure max concurrent agents
- View orchestrator logs in modal

**4. Command Center Feel with shadcn/ui:**
- Custom CSS classes for neon glow effects
- Gradient backgrounds using Tailwind utilities
- shadcn/ui components with custom variants
- Framer Motion for smooth transitions
- Custom hover states with electric-cyan highlights
- Glass morphism effects on cards
- Sound effects for actions (optional)

**Example Component Styling:**
```tsx
// Custom Button variant
<Button 
  variant="outline" 
  className="border-electric-cyan hover:bg-electric-cyan/10 hover:shadow-[0_0_15px_rgba(0,255,255,0.5)] transition-all"
>
  Launch Agent
</Button>

// Glowing Card
<Card className="bg-deep-indigo/50 backdrop-blur border-electric-cyan/20 hover:border-electric-cyan/50 hover:shadow-[0_0_30px_rgba(0,255,255,0.3)] transition-all">
  {/* Agent status */}
</Card>
```

## 🔧 Technical Implementation Details

**Backend API Endpoints:**
```
GET    /api/tasks           - List all tasks
POST   /api/tasks           - Create task
PUT    /api/tasks/{id}      - Update task
DELETE /api/tasks/{id}      - Delete task
GET    /api/agents          - List running agents
POST   /api/orchestrator/start - Start orchestrator
POST   /api/orchestrator/stop  - Stop orchestrator
GET    /api/config          - Get configuration
PUT    /api/config          - Update configuration
WS     /ws/updates          - Real-time updates
```

**iTerm Integration:**
```python
# Launch iTerm to tmux session
def launch_iterm_session(session_name):
    applescript = f'''
    tell application "iTerm"
        create window with default profile
        tell current session of current window
            write text "tmux attach -t {session_name}"
        end tell
    end tell
    '''
    subprocess.run(['osascript', '-e', applescript])
```

**Frontend Service Integration:**
```typescript
// Single API base URL
const API_URL = window.location.origin;

// WebSocket connection
const ws = new WebSocket(`ws://${window.location.host}/ws/updates`);
```

## 🚀 Launch Script

The `launch-dashboard.py` script (in project root) will:
1. Check dependencies
2. Build frontend if needed
3. Start FastAPI server
4. Open browser automatically
5. Handle graceful shutdown

```python
#!/usr/bin/env python3
"""
SplitMind Dashboard Launcher
Launch the command center with a single command from project root
"""
import uvicorn
import webbrowser
import argparse
import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required = ['fastapi', 'uvicorn', 'websockets']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install fastapi uvicorn websockets")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Launch SplitMind Command Center')
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    args = parser.parse_args()
    
    check_dependencies()
    
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    print(f"🚀 Launching SplitMind Command Center on port {args.port}...")
    
    if not args.no_browser:
        webbrowser.open(f'http://localhost:{args.port}')
    
    uvicorn.run(
        "dashboard.backend.api:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.dev
    )

if __name__ == "__main__":
    main()
```