<p align="center">
  <img src="assets/splitmind-banner.png" alt="SplitMind Logo Banner" width="100%">
</p>

<h1 align="center">SplitMind With Claude Code</h1>
<p align="center"><i>Asynchronous AI coder orchestration using Git worktrees and tmux.</i></p>

---

## 🚀 Quick Start

### First-Time Setup

Run the automated setup script:

```bash
python setup.py
```

This will:
- ✅ Check prerequisites (Python, Node.js, Git, tmux)
- ✅ Install all dependencies
- ✅ Build the dashboard frontend
- ✅ Create necessary directories
- ✅ Generate example files

### Launch Dashboard

After setup, start the command center:

```bash
python launch-dashboard.py
```

Then open http://localhost:8000 in your browser.

---

## 🎯 Key Features

### 🤖 AI Task Master (NEW!)
- **Wave-Based Task Generation**: Automatically creates structured, parallel-executable tasks
- **Custom AI Prompts**: Each task gets tailored instructions for optimal results
- **Smart Dependencies**: Tasks organized by development phases (Foundation → Features → Deploy)

### 📊 Enhanced Dashboard
- **Real-Time Monitoring**: Live updates via WebSocket
- **Task Status Workflow**: `UNCLAIMED` → `UP_NEXT` → `IN_PROGRESS` → `COMPLETED` → `MERGED`
- **Drag & Drop Task Board**: Organize tasks visually
- **Agent Monitoring**: See start times, running duration, and live status

### ⚙️ Powerful Orchestration
- **Smart Queue Management**: Maintains optimal task queue based on max agents
- **Manual & Auto Merge**: Choose between automatic merging or manual review
- **Custom Prompts**: Edit AI instructions for each task individually
- **Plan Editing**: Modify generated plans to guide development

---

## 🖥️ Dashboard Usage & Workflow

### 🚀 Getting Started

#### 1. **First Launch**
When you first open the dashboard, you'll see the welcome screen:
- Click **"Create New Project"** or the `+` button
- Enter project details:
  - **Name**: Your project's display name
  - **Path**: Select or enter the path to your Git repository
  - **Description**: Brief project description
  - **Max Agents**: Maximum concurrent AI agents (default: 5)

⚠️ **Important**: Make sure your project path is a Git repository!

#### 2. **Project Setup**
Navigate to the Settings tab:

##### Overview Tab
1. **Project Overview**: Provide detailed context about your project
2. **Initial Prompt**: Describe what you want to build
3. Choose generation method:
   - **Basic Plan Generation**: Simple plan with basic tasks
   - **🚀 AI Task Master (Recommended)**: Comprehensive plan + structured tasks

##### Plan Tab
- View and edit the generated project plan
- Plans created by AI Task Master include architecture decisions and tech stack

### 🎯 Complete Workflow Example

#### Step 1: Configure Your Project
```
Project Overview:
Modern task management SaaS platform for remote teams. Built with Next.js 14, 
TypeScript, and Supabase. Features include real-time collaboration, project 
templates, time tracking, and team analytics. Target audience: distributed teams 
and digital agencies. Focus on performance and intuitive UX.

Initial Prompt:
Build a collaborative task management platform with user authentication, 
real-time updates, project workspaces, kanban boards, time tracking, 
team member invitations, and analytics dashboard. Include Stripe integration 
for subscriptions.
```

#### Step 2: Generate with AI Task Master
1. Click **"🚀 AI Task Master (Plan + Tasks)"**
2. Watch the beautiful loading animation
3. AI creates:
   - Comprehensive project plan
   - Wave-based task breakdown
   - 15-20 structured tasks with custom prompts

#### Step 3: Review Generated Tasks
Tasks are automatically organized by:
- **Priority**: Lower numbers = higher priority
- **Wave**: Foundation tasks before features
- **Dependencies**: Implicit in wave structure

Each task includes:
- Clear title and description
- Custom AI prompt
- Git branch name
- Priority assignment

#### Step 4: Start Development
1. Configure Orchestrator in left sidebar:
   - Max Concurrent Agents: 3-5
   - Auto-merge: Off (for manual review)
   - Click "Start Orchestrator"
2. Orchestrator automatically:
   - Promotes tasks to UP_NEXT queue
   - Spawns AI agents for available tasks
   - Manages parallel execution
   - Updates status in real-time

#### Step 5: Monitor Progress
- **Task Board**: Watch tasks flow through statuses
- **Agent Monitor**: 
  - See exact start times
  - Watch live duration counters
  - Monitor agent status (running/completed)
- **Click on Tasks**: 
  - View/edit task details
  - See full AI prompt
  - Update branch names
  - Manual status changes

#### Step 6: Review and Merge
When tasks show "Completed":
1. Click the task card
2. Review the changes
3. Click the merge button (appears for completed tasks)
4. Or use auto-merge if enabled

### 💡 Advanced Features

#### Custom Task Prompts
Click any task to:
- View the exact prompt sent to AI agents
- Edit prompts for specific requirements
- Add technical specifications
- Include context about dependencies

#### Manual Plan Editing
In Settings → Plan tab:
- Click "Edit Plan" to modify the generated plan
- Update architecture decisions
- Add implementation notes
- Guide the overall project direction

#### Task Management
- **Add Tasks**: Click "+" to create custom tasks
- **Edit Tasks**: Click any task card to modify
- **Branch Names**: Edit branch names (avoid `/`, `&`, `\`)
- **Reset Tasks**: Return tasks to UNCLAIMED status
- **Delete Tasks**: Remove unwanted tasks

### 🔧 Troubleshooting Common Issues

#### Tasks Stuck in UP_NEXT
- Verify orchestrator is running (green status)
- Check max agents setting vs running agents
- Look for file conflicts between tasks
- Review agent logs for errors

#### "Method Not Allowed" Error
- Clear browser cache
- Rebuild frontend: `npm run build`
- Check for special characters in task IDs

#### WebSocket Disconnections
- Status indicator shows connection state
- Auto-reconnects every 5 seconds
- Check backend is running

---

## 🔄 How It Works

SplitMind enables parallel AI development through intelligent orchestration:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Project   │────▶│ AI Task     │────▶│   Wave-     │
│  Settings   │     │  Master     │     │   Based     │
└─────────────┘     └─────────────┘     │   Tasks     │
                                        └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │Orchestrator │────▶│ AI Agents   │
                    │   Queue     │     │ (Parallel)  │
                    └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   Review    │◀────│ Completed   │
                    │  & Merge    │     │   Work      │
                    └─────────────┘     └─────────────┘
```

### Key Concepts

1. **Wave-Based Execution**: Tasks organized by dependencies
2. **UP_NEXT Queue**: Maintains ready tasks equal to max agents
3. **Smart Spawning**: Agents get custom prompts and isolated worktrees
4. **Real-Time Monitoring**: WebSocket updates for live status
5. **Flexible Merging**: Manual review or automatic integration

---

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- tmux
- Claude CLI (for AI agents)
- Anthropic API key (for plan generation)

---

## 🧱 Project Structure

```
cctg/                       # SplitMind installation directory
├── config.json            # Global configuration
├── projects.json          # Registered projects list
├── dashboard/             # Web dashboard
│   ├── backend/          # FastAPI backend
│   │   ├── api.py       # REST endpoints
│   │   ├── orchestrator.py # Agent orchestration
│   │   ├── anthropic_client.py # AI integration
│   │   └── models.py    # Data models
│   └── frontend/         # React frontend
│       ├── components/   # UI components
│       └── services/     # API services
├── scripts/              # Utility scripts
└── launch-dashboard.py   # Dashboard launcher

your_project/             # Individual project directory
├── .splitmind/          # Project-specific data
│   ├── tasks.md        # Task definitions
│   └── plans/          # Generated plans
├── worktrees/          # Git worktrees (auto-created)
└── .git/               # Git repository
```

---

## 📝 Task Definition Format

Tasks are stored in `.splitmind/tasks.md`:

```markdown
# tasks.md

## Task: Initialize Next.js project with TypeScript

- task_id: 1
- status: unclaimed
- branch: initialize-nextjs-project
- session: null
- description: Set up Next.js 14 with App Router, TypeScript, and TailwindCSS
- prompt: null
- dependencies: []
- priority: 1

## Task: Create authentication system

- task_id: 2
- status: unclaimed
- branch: create-authentication-system
- session: null
- description: Implement JWT-based auth with login, register, and protected routes
- prompt: null
- dependencies: [initialize-nextjs-project]
- priority: 2
```

---

## 🛠️ Configuration

### Orchestrator Settings
Configure in the dashboard's left sidebar:
- **Max Concurrent Agents**: Number of parallel AI agents
- **Auto-merge**: Enable/disable automatic merging
- **Merge Strategy**: merge, squash, or fast-forward
- **API Key**: Anthropic API key for plan generation

### Project Settings
Set in each project's Settings tab:
- **Project Overview**: Detailed project context
- **Initial Prompt**: What to build
- **Max Agents**: Project-specific agent limit

---

## 📚 API Reference

### REST Endpoints

#### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

#### Tasks
- `GET /api/projects/{id}/tasks` - Get project tasks
- `POST /api/projects/{id}/tasks` - Create task
- `PUT /api/projects/{id}/tasks/{task_id}` - Update task
- `DELETE /api/projects/{id}/tasks/{task_id}` - Delete task
- `POST /api/projects/{id}/tasks/{task_id}/merge` - Merge task

#### Plan Generation
- `POST /api/projects/{id}/generate-plan` - Basic plan generation
- `POST /api/projects/{id}/generate-task-breakdown` - AI Task Master

#### Orchestrator
- `POST /api/orchestrator/start` - Start orchestrator
- `POST /api/orchestrator/stop` - Stop orchestrator
- `GET /api/orchestrator/status` - Get status

### WebSocket Events

Connect to `ws://localhost:8000/ws` for real-time updates:

- `task_created` - New task added
- `task_updated` - Task modified
- `task_status_changed` - Status update
- `agent_spawned` - New agent started
- `agent_status_update` - Agent progress
- `orchestrator_started/stopped` - Orchestrator state

---

## 🚨 Troubleshooting

### Common Issues

#### 1. **Task Update Fails - "Method Not Allowed"**
- **Cause**: Special characters in task IDs
- **Fix**: Run `python fix-task-ids.py <project-id>`

#### 2. **Tasks Not Being Claimed**
- Check orchestrator is running
- Verify Claude CLI is configured
- Check agent limit settings
- Review task dependencies

#### 3. **Plan Generation Timeout**
- Use simpler project descriptions
- Try claude-3-5-haiku model (faster)
- Check API key is valid

#### 4. **Frontend Build Errors**
```bash
cd dashboard/frontend
rm -rf node_modules
npm install
npm run build
```

#### 5. **WebSocket Disconnections**
- Check backend is running
- Clear browser cache
- Try different browser

### Debug Mode

Run with verbose logging:
```bash
python launch-dashboard.py --dev
```

### Clean Reset

Complete reset:
```bash
# Stop everything
tmux kill-server

# Reset config
rm -rf config.json projects.json

# Rebuild frontend
cd dashboard/frontend
rm -rf node_modules dist
npm install
npm run build
cd ../..

# Restart
python launch-dashboard.py
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- Built for use with [Claude](https://claude.ai)
- Inspired by the need for parallel AI development
- Thanks to all contributors and early adopters

---

## 📞 Support

- 📧 Email: support@splitmind.ai
- 💬 Discord: [Join our community](https://discord.gg/splitmind)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/splitmind/issues)