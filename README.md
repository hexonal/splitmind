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

## 🖥️ Dashboard Usage & Workflow

The SplitMind Dashboard provides a complete command center for AI-orchestrated development. Here's how to use it effectively:

### 🚀 Getting Started with the Dashboard

#### 1. **First Launch**
When you first open the dashboard, you'll see the welcome screen:
- Click **"Create New Project"** or the `+` button
- Enter project details:
  - **Name**: Your project's display name
  - **Path**: Select or enter the path to your Git repository
  - **Description**: Brief project description
  - **Max Agents**: Maximum concurrent AI agents (default: 5)

#### 2. **Project Overview**
Once a project is created, you'll see four main tabs:

##### 📊 **Dashboard Tab**
The main control center showing:
- **Task Board**: All project tasks organized by status
  - `Unclaimed`: Ready for AI agents
  - `Claimed`: Assigned to an agent
  - `In Progress`: Currently being worked on
  - `Completed`: Work finished
  - `Merged`: Successfully merged to main
- **Quick Actions**: Add tasks, refresh status
- **Task Management**: Click tasks to edit/delete

##### 🤖 **Agents Tab**
Monitor active AI agents:
- See which agents are working on which tasks
- View real-time progress
- Launch iTerm to connect to agent sessions
- Monitor agent logs and status

##### 📈 **Statistics Tab**
Project metrics and insights:
- Total tasks breakdown by status
- Active agents count
- Completion rates
- Historical agent activity

##### ⚙️ **Settings Tab**
Configure project and generate plans:
- **Overview Section**:
  - Project Overview: Detailed description for AI context
  - Initial Prompt: What you want to build
  - Save Settings: Persist your configuration
  - Generate Plan & Tasks: AI creates development plan
- **Plan Section**: View generated project plan
- **Integrations Section**: Configure external tools (Dart)

### 🎯 Complete Workflow Example

#### Step 1: Create and Configure Project
1. Launch dashboard: `python launch-dashboard.py`
2. Create new project pointing to your Git repo
3. Go to Settings tab
4. Add project overview:
   ```
   E-commerce platform for handmade crafts. Built with React and Node.js.
   Needs user authentication, product catalog, shopping cart, and payment.
   Target audience: craft sellers and buyers. Mobile-first design.
   ```
5. Add initial prompt:
   ```
   Build a modern e-commerce platform with user registration, product listings,
   shopping cart, and Stripe payment integration. Include seller dashboards.
   ```
6. Click "Generate Plan & Tasks"

#### Step 2: Review Generated Plan
The AI will create:
- Comprehensive development plan
- Phased approach (Foundation → Features → Polish)
- Initial task set with clear objectives

#### Step 3: Start Development
1. Review tasks in Dashboard tab
2. Configure Orchestrator in left sidebar:
   - Max Concurrent Agents: 3
   - Auto-merge: Off (manual review)
   - Click "Start Orchestrator"
3. AI agents automatically:
   - Claim tasks from the board
   - Create git worktrees
   - Start implementation
   - Update task status

#### Step 4: Monitor Progress
- **Dashboard**: Watch tasks move through statuses
- **Agents Tab**: See active agents and their work
- **Use iTerm**: Click agent to open terminal session
- **Real-time Updates**: WebSocket provides live status

#### Step 5: Review and Merge
1. When tasks show "Completed"
2. Review changes in agent's worktree
3. Use merge controls or CLI commands
4. Merged work appears in main branch

### 💡 Pro Tips

#### Effective Task Creation
- **Be Specific**: "Add user authentication with JWT" not "Add auth"
- **Include Context**: Reference files, APIs, or designs
- **Set Dependencies**: Note which tasks must complete first
- **Size Appropriately**: 2-4 hour chunks work best

#### Using Command Files
Create custom workflows in `.claude/commands/`:
```markdown
# Custom Test Runner
You are a test specialist. When assigned a testing task:
1. Identify test framework: `context7_get: "test_framework"`
2. Write comprehensive tests
3. Ensure 80% coverage minimum
4. Update Dart board with results
```

#### MCP Tool Integration
In Settings → Integrations:
- Add Dart Workspace ID for project sync
- Configure Context7 namespaces
- Set Brave Search preferences

#### Orchestrator Best Practices
- Start with fewer agents (2-3) to avoid conflicts
- Enable auto-merge only after testing manual merges
- Use "squash" merge strategy for cleaner history
- Monitor agent logs for issues

### 🔧 Troubleshooting Dashboard Issues

#### Tasks Not Being Claimed
- Check orchestrator is running (green status)
- Verify tasks.md exists in project
- Ensure Claude CLI is configured
- Check agent limit hasn't been reached

#### WebSocket Disconnections
- Check browser console for errors
- Ensure backend is running
- Try refreshing the page
- Check firewall/proxy settings

#### Can't See Projects
- Verify projects.json has correct paths
- Check Git repositories exist
- Ensure proper file permissions
- Try "Reset Configuration" in settings

---

## 🔄 How It Works

SplitMind enables parallel AI development by:

1. **Task Definition** - Define tasks in `tasks.md` with clear objectives
2. **Agent Spawning** - Claude orchestrator creates isolated Git worktrees and launches AI agents
3. **Parallel Execution** - Multiple AI coders work simultaneously in tmux sessions
4. **Smart Merging** - Completed work is reviewed and merged back to main
5. **Continuous Flow** - New tasks can be added while others are in progress

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  tasks.md   │────▶│   Claude    │────▶│  Worktrees  │
│             │     │ Orchestrator│     │  + Agents   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │    Merge    │◀────│  Completed  │
                    │   to Main   │     │    Work     │
                    └─────────────┘     └─────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- tmux
- Claude CLI (optional, for AI agents)

---

## 🧱 Project Structure

```
splitmind/                   # SplitMind installation directory
├── config.json             # Global configuration
├── projects.json           # Registered projects list
├── dashboard/              # Web dashboard
│   ├── backend/           # FastAPI backend
│   └── frontend/          # React frontend
├── scripts/               # Utility scripts
└── launch-dashboard.py    # Dashboard launcher

your_project/               # Individual project directory
├── .splitmind/            # Project-specific SplitMind data
│   └── tasks.md          # Project tasks
├── .claude/              # Claude command files
│   └── commands/
│       └── spawn.md
├── worktrees/            # Git worktrees (created dynamically)
└── .git/                # Git repository
```

---

## ✅ 1. Create .claude/commands/spawn.md

```markdown
You are an agent spawner and orchestrator. You read the tasks file and then find one or multiple tasks that can be solved by one agent and assign them to a new agent by first creating a new worktree, then building a prompt, and then launching the agent.

### What to do

1. **READ:** `tasks.md`
2. **Select** one or multiple tasks that can be solved by one agent.  
   **Convention:** If multiple tasks are dependent on each other, they should be solved by the same agent. If a task is independent, it should be solved by a separate agent.
3. For each selected task to be assigned:
   - RUN: `git worktree add "worktrees/$FEATURE" -b "$FEATURE"`
   - Build the agent prompt (substitute `$TASK_TEXT`):  
     `"Create a plan, review your plan and choose the best option, then accomplish $TASK_TEXT and commit the changes."`
   - RUN:  
     `tmux new-session -d -s "$SLUG" claude "$PROMPT" --allowedTools "Edit,Write,Bash,Replace"`

### Output

For every agent you launch, update `tasks.md`:

- Set `status` to `claimed`
- Record the `tmux` session name
```

---

## ✅ 2. Example tasks.md

```markdown
# tasks.md

## Task: Create light theme

- status: unclaimed
- branch: light-theme
- session: null

## Task: Add filter to dropdown

- status: unclaimed
- branch: add-filter
- session: null
```

Keep this format. Claude will read, parse, and update it.

---

## ✅ 3. Setup Commands

Make sure you’re in a Git repo:

```bash
git init
```

Create your worktrees directory:

```bash
mkdir worktrees
```

Launch Claude and run the `.claude/commands/spawn.md` command. It will:

- Read tasks.md
- Create worktrees for unclaimed tasks
- Spawn agents in tmux sessions with task-specific prompts
- Update tasks.md with status and session name

---

## ✅ 4. Monitor Sessions

```bash
tmux ls                      # list all sessions
tmux attach -t session-name  # connect to a session
ctrl+b then d               # detach from a session
```

---

## 🎯 Project Planning & AI Orchestration

SplitMind now includes powerful project planning capabilities:

### Project Settings
In the dashboard, navigate to the Settings tab to:
- **Project Overview**: Provide detailed context about your project
- **Initial Prompt**: Describe what you want to build
- **Generate Plan**: AI creates a comprehensive development plan with tasks

### MCP Tool Integration
SplitMind supports Model Context Protocol (MCP) tools:
- **Brave Search**: Research best practices and solutions
- **Context7**: Store and retrieve project context
- **Dart**: Sync with external project management

### Custom Command Files
Create your own AI workflows in `.claude/commands/`:
- `generate-plan.md` - Project planning and task generation
- `research.md` - Automated research assistant
- `implement-feature.md` - Feature implementation workflow
- See `.claude/commands/README.md` for full documentation

### Example Workflow
1. Add project overview and initial prompt in Settings
2. Click "Generate Plan & Tasks" to create initial tasks
3. AI orchestrator uses command files to execute tasks
4. Agents work in parallel using git worktrees
5. Completed work is merged back automatically

## ✅ TODO's

- ✓ A script to auto-format tasks.md (see `scripts/format-tasks.py`)
- ✓ Auto-merging worktrees (see `scripts/auto-merge.py` and `.claude/commands/merge.md`)
- ✓ Project planning with AI-generated tasks
- ✓ MCP tool integration (Brave Search, Context7, Dart)
- ✓ Custom command file system

## 📝 Scripts

### Auto-format tasks.md

Use the provided Python script to automatically format your tasks.md file:

```bash
python scripts/format-tasks.py
```

This script will:

- Standardize task structure
- Generate branch names from task titles if missing
- Ensure consistent formatting
- Validate required fields (status, branch, session)

### Auto-merge Worktrees

Safely merge completed worktree branches back to main:

```bash
# Merge a specific branch
python scripts/auto-merge.py feature-branch

# Merge all worktree branches
python scripts/auto-merge.py --all

# Dry run to see what would happen
python scripts/auto-merge.py --all --dry-run

# Use different merge strategies
python scripts/auto-merge.py feature-branch --strategy squash
```

The script provides:

- Automatic safety checks (uncommitted changes, unpushed commits)
- Multiple merge strategies (merge, squash, fast-forward)
- Cleanup of merged branches and worktrees
- JSON output for integration with Claude orchestrator

## 🤖 Claude Commands

### `.claude/commands/spawn.md`

Spawns new AI agents for unclaimed tasks in isolated worktrees.

### `.claude/commands/merge.md`

Intelligently reviews and merges completed work from agents back to main.

---

## 🚀 Usage Examples

### For Human Operators

1. **Setup and Initialize**

```bash
# Initialize your project
git init
mkdir worktrees
echo "# tasks.md" > tasks.md

# Add some tasks
cat >> tasks.md << EOF
## Task: Add user authentication

- status: unclaimed
- branch: add-auth
- session: null

## Task: Create API endpoints

- status: unclaimed
- branch: api-endpoints
- session: null
EOF
```

2. **Format Tasks**

```bash
# Auto-format your tasks file
python scripts/format-tasks.py
```

3. **Manual Worktree Management**

```bash
# Create a worktree manually
git worktree add worktrees/feature-x -b feature-x

# Work in the worktree
cd worktrees/feature-x
# ... make changes ...
git add . && git commit -m "Complete feature X"
git push -u origin feature-x

# Merge when done
cd ../..
python scripts/auto-merge.py feature-x --strategy squash
```

4. **Monitor AI Agents**

```bash
# See running agents
tmux ls

# Attach to an agent's session
tmux attach -t add-auth

# Check worktree status
git worktree list
```

### For Claude Orchestrator

1. **Spawn Agents** (run `.claude/commands/spawn.md`)

```bash
# Claude will:
# 1. Read tasks.md
# 2. Find unclaimed tasks
# 3. Create worktrees for each
# 4. Launch AI agents in tmux sessions
# 5. Update task status to "claimed"
```

2. **Merge Completed Work** (run `.claude/commands/merge.md`)

```bash
# Claude will:
# 1. Check for completed tasks
# 2. Review changes in each branch
# 3. Choose appropriate merge strategy
# 4. Execute merges safely
# 5. Update tasks.md with "merged" status
```

### Complete Workflow Example

**Step 1: Human creates tasks**

```bash
vim tasks.md  # Add your tasks
python scripts/format-tasks.py  # Format them
```

**Step 2: Claude spawns agents**

```bash
claude /claude/commands/spawn.md
# Multiple AI agents now working in parallel
```

**Step 3: Human monitors progress**

```bash
tmux ls  # See active agents
git worktree list  # See active branches
tail -f worktrees/*/claude.log  # Watch agent logs (if available)
```

**Step 4: Claude merges completed work**

```bash
claude /claude/commands/merge.md
# Completed work is merged back to main
```

**Step 5: Human reviews and deploys**

```bash
git log --oneline  # Review merged commits
git push origin main  # Deploy changes
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. **Server won't start - JSON parsing error**
```
❌ Error: Expecting value: line X column Y (char Z)
```

**Solution:** Reset corrupted configuration files
```bash
# Reset projects file
echo '{"projects": []}' > ~/.splitmind/projects.json

# Or completely reset all settings
rm -rf ~/.splitmind
python launch-dashboard.py  # Will recreate with defaults
```

#### 2. **Frontend not built error**
```
⚠️  Frontend not built yet.
```

**Solution:** Build the frontend
```bash
cd dashboard/frontend
npm install
npm run build
cd ../..
python launch-dashboard.py
```

#### 3. **Shutdown errors with Ctrl+C**
```
ERROR: Exception in ASGI application
asyncio.exceptions.CancelledError
```

**Solution:** This is cosmetic and doesn't affect functionality. Use Ctrl+C once and wait a moment for clean shutdown.

#### 4. **Can't create project - nothing happens**

**Check:**
- Browser console (F12) for errors
- Terminal for Python exceptions
- Ensure the project path exists and is a Git repository
- Check file permissions on the project directory

#### 5. **Missing dependencies**
```
Missing dependencies: fastapi, uvicorn
```

**Solution:** Install Python dependencies
```bash
pip install fastapi[all] uvicorn[standard] websockets aiofiles
```

#### 6. **tmux sessions not found**
```
no server running on /tmp/tmux-501/default
```

**Solution:** Install tmux
```bash
# macOS
brew install tmux

# Ubuntu/Debian
sudo apt-get install tmux
```

#### 7. **Claude CLI not working**

**Solution:** Claude CLI is optional. SplitMind works without it for task management. To use AI agents:
1. Install Claude CLI from https://docs.anthropic.com/en/docs/claude-cli
2. Configure API keys
3. Test with: `claude --version`

#### 8. **Port already in use**
```
[Errno 48] Address already in use
```

**Solution:** Use a different port
```bash
python launch-dashboard.py --port 8080
```

#### 9. **Can't access dashboard from browser**

**Check:**
- Firewall settings
- Correct URL: http://localhost:8000
- Try: http://127.0.0.1:8000
- Check if port is blocked

#### 10. **Project creation fails silently**

**Debug steps:**
1. Check browser DevTools Console (F12)
2. Check terminal for Python errors
3. Verify project path is absolute (not relative)
4. Ensure you have write permissions
5. Check if path is already a Git repo

### 📝 Debug Mode

Run in development mode for more detailed logging:
```bash
python launch-dashboard.py --dev
```

### 🗑️ Clean Reset

If all else fails, perform a clean reset:
```bash
# 1. Stop all tmux sessions
tmux kill-server

# 2. Reset configuration
rm -rf ~/.splitmind

# 3. Clean and rebuild frontend
cd dashboard/frontend
rm -rf node_modules dist
npm install
npm run build
cd ../..

# 4. Restart
python launch-dashboard.py
```

### 📞 Getting Help

1. Check the [GitHub Issues](https://github.com/yourusername/splitmind/issues)
2. Review error messages in both terminal and browser console
3. Run in dev mode for detailed logs
4. Include full error traceback when reporting issues
