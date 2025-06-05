<p align="center">
  <img src="assets/splitmind-banner.jpg" alt="SplitMind Logo Banner" width="100%">
</p>

<h1 align="center">SplitMind</h1>
<p align="center"><i>Asynchronous AI coder orchestration using Git worktrees and tmux.</i></p>

---

## 🧱 Project Structure

```
your_project/
├── .claude/
│   └── commands/
│       └── spawn.md
├── tasks.md
├── worktrees/       # (Created dynamically)
├── .git/           # (Git repo root)
└── ...
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

## ✅ TODO's

- ✓ A script to auto-format tasks.md (see `scripts/format-tasks.py`)
- Auto-merging worktrees
- Command templates for testing, deployment, or linting

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
