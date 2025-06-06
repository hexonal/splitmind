# SplitMind Agent Coordination Plan

## Overview
This plan addresses the coordination challenges when running multiple AI agents in parallel using git worktrees. While worktrees provide file isolation during work, merge conflicts arise when multiple agents modify shared files.

## Current Issues
1. **Shared File Conflicts**: Multiple agents modifying README.md, package.json, .gitignore
2. **Initialization Dependencies**: Later tasks depend on earlier tasks' setup (e.g., UI Components needs Framework's Next.js setup)
3. **Environment Setup**: Each worktree needs proper initialization (npm/pnpm install)
4. **Merge Order**: Tasks should merge in dependency order to avoid conflicts

## Proposed Solution Architecture

### 1. Enhanced Task Dependency System

```python
# Enhanced Task Model
class Task:
    id: str
    title: str
    dependencies: List[str]  # Task IDs that must complete first
    priority: int  # 0-10, higher = more important
    exclusive_files: List[str]  # Files only this task should modify
    shared_files: List[str]  # Files that might be modified (requires coordination)
    initialization_deps: List[str]  # Tasks whose output is needed for setup
    merge_order: int  # Explicit merge sequence
```

### 2. Smart Task Scheduling Algorithm

```python
def get_next_tasks(tasks, max_concurrent=3):
    """
    Select tasks that can run in parallel without conflicts
    """
    eligible = []
    
    for task in tasks:
        if task.status != TaskStatus.UNCLAIMED:
            continue
            
        # Check dependencies are met
        deps_met = all(
            dep_task.status in [TaskStatus.COMPLETED, TaskStatus.MERGED]
            for dep_task in task.dependencies
        )
        
        if not deps_met:
            continue
            
        # Check for file conflicts with running tasks
        running_tasks = [t for t in tasks if t.status == TaskStatus.IN_PROGRESS]
        has_conflict = any(
            set(task.exclusive_files).intersection(set(rt.exclusive_files)) or
            set(task.exclusive_files).intersection(set(rt.shared_files))
            for rt in running_tasks
        )
        
        if not has_conflict:
            eligible.append(task)
    
    # Sort by priority and return top N
    eligible.sort(key=lambda t: (t.priority, -t.merge_order), reverse=True)
    return eligible[:max_concurrent]
```

### 3. Worktree Initialization System

```python
class WorktreeInitializer:
    """
    Handles proper worktree setup based on task dependencies
    """
    
    def initialize_worktree(self, task, project_path):
        worktree_path = project_path / "worktrees" / task.branch
        
        # Create worktree from the latest merged state
        base_branch = self.get_base_branch(task)
        subprocess.run([
            "git", "worktree", "add", 
            str(worktree_path), 
            "-b", task.branch,
            base_branch  # Start from latest relevant merge
        ])
        
        # Copy initialization files from completed dependencies
        for dep_id in task.initialization_deps:
            self.copy_initialization_files(dep_id, worktree_path)
        
        # Run setup commands
        self.run_setup_commands(task, worktree_path)
    
    def get_base_branch(self, task):
        """
        Determine the best starting point for this task
        """
        if task.initialization_deps:
            # Start from the latest dependency merge
            return f"merge-{task.initialization_deps[-1]}"
        return "main"
    
    def run_setup_commands(self, task, worktree_path):
        """
        Run necessary setup based on task type
        """
        os.chdir(worktree_path)
        
        # Install dependencies if package.json exists
        if (worktree_path / "package.json").exists():
            subprocess.run(["pnpm", "install"])
        
        # Type-specific setup
        if "framework" in task.dependencies:
            # Ensure Next.js is properly initialized
            subprocess.run(["pnpm", "next", "telemetry", "disable"])
```

### 4. File Ownership Registry

```python
# File ownership configuration
FILE_OWNERSHIP = {
    "framework": {
        "exclusive": [
            "next.config.ts",
            "tsconfig.json",
            "src/app/layout.tsx",
            "src/app/page.tsx"
        ],
        "shared": ["package.json", "README.md"]
    },
    "styling": {
        "exclusive": [
            "tailwind.config.ts",
            "src/styles/",
            "postcss.config.mjs"
        ],
        "shared": ["package.json"]
    },
    "ui-components": {
        "exclusive": [
            "src/components/",
            "components.json"
        ],
        "shared": ["package.json"]
    }
}
```

### 5. Merge Queue System

```python
class MergeQueue:
    """
    Manages orderly merging of completed tasks
    """
    
    def __init__(self):
        self.queue = []
        self.merge_lock = asyncio.Lock()
    
    async def add_to_queue(self, task):
        """
        Add completed task to merge queue
        """
        self.queue.append(task)
        self.queue.sort(key=lambda t: t.merge_order)
        
        # Try to process queue
        await self.process_queue()
    
    async def process_queue(self):
        """
        Process tasks in order, respecting dependencies
        """
        async with self.merge_lock:
            while self.queue:
                task = self.queue[0]
                
                # Check if dependencies are merged
                deps_merged = all(
                    dep.status == TaskStatus.MERGED
                    for dep in task.dependencies
                )
                
                if deps_merged:
                    success = await self.merge_task(task)
                    if success:
                        self.queue.pop(0)
                        task.status = TaskStatus.MERGED
                    else:
                        # Handle merge conflict
                        await self.resolve_conflict(task)
                else:
                    # Can't merge yet, try next task
                    break
    
    async def resolve_conflict(self, task):
        """
        Automated conflict resolution strategies
        """
        # Strategy 1: Rebase on latest main
        # Strategy 2: Auto-resolve known patterns
        # Strategy 3: Queue for manual review
        pass
```

### 6. Enhanced Task Configuration

```yaml
# tasks.yaml - Enhanced task definitions
tasks:
  - id: framework
    title: "Next.js 14 Framework Setup"
    priority: 10
    merge_order: 1
    dependencies: []
    initialization_deps: []
    exclusive_files:
      - "next.config.ts"
      - "tsconfig.json"
      - "src/app/"
    shared_files:
      - "package.json"
      - "README.md"
    setup_commands:
      - "pnpm create next-app . --typescript --tailwind --app"
    
  - id: styling
    title: "TailwindCSS Configuration"
    priority: 9
    merge_order: 2
    dependencies: []
    initialization_deps: ["framework"]  # Needs Next.js structure
    exclusive_files:
      - "tailwind.config.ts"
      - "src/styles/"
    shared_files:
      - "package.json"
    
  - id: ui-components
    title: "ShadCN/UI Setup"
    priority: 8
    merge_order: 3
    dependencies: ["framework", "styling"]
    initialization_deps: ["framework", "styling"]
    exclusive_files:
      - "src/components/"
      - "components.json"
    shared_files:
      - "package.json"
```

### 7. Conflict Resolution Strategies

```python
class ConflictResolver:
    """
    Automated conflict resolution for common patterns
    """
    
    def resolve_package_json(self, ours, theirs):
        """
        Merge package.json intelligently
        """
        our_json = json.loads(ours)
        their_json = json.loads(theirs)
        
        # Merge dependencies
        merged = our_json.copy()
        merged['dependencies'] = {
            **our_json.get('dependencies', {}),
            **their_json.get('dependencies', {})
        }
        merged['devDependencies'] = {
            **our_json.get('devDependencies', {}),
            **their_json.get('devDependencies', {})
        }
        
        # Merge scripts (prefer theirs for new scripts)
        merged['scripts'] = {
            **our_json.get('scripts', {}),
            **their_json.get('scripts', {})
        }
        
        return json.dumps(merged, indent=2)
    
    def resolve_readme(self, ours, theirs):
        """
        Merge README.md by section
        """
        # Parse sections and merge intelligently
        # Keep both versions of different sections
        pass
```

## Implementation Steps

### Phase 1: Enhanced Task System (Week 1)
1. Update Task model with new fields
2. Implement file ownership registry
3. Create task scheduling algorithm
4. Update orchestrator to use smart scheduling

### Phase 2: Worktree Management (Week 2)
1. Implement WorktreeInitializer
2. Add proper environment setup for each worktree
3. Create base branch selection logic
4. Test with various task combinations

### Phase 3: Merge Queue (Week 3)
1. Implement MergeQueue class
2. Add automated conflict resolution
3. Create merge order optimization
4. Add manual conflict resolution UI

### Phase 4: Monitoring & Optimization (Week 4)
1. Add metrics for merge success rate
2. Track agent productivity
3. Optimize task scheduling
4. Create conflict prediction system

## Key Benefits

1. **Reduced Conflicts**: File ownership prevents most conflicts
2. **Faster Development**: Parallel work without interference
3. **Automated Merging**: Smart merge queue handles most cases
4. **Better Dependencies**: Proper initialization ensures tasks have what they need
5. **Scalability**: Can run many agents without coordination issues

## Configuration Example

```python
# orchestrator_config.py
ORCHESTRATOR_CONFIG = {
    "max_concurrent_agents": 5,
    "scheduling_strategy": "smart",  # vs "simple"
    "conflict_resolution": "auto",   # vs "manual"
    "merge_strategy": "queue",       # vs "immediate"
    "initialization_strategy": "dependency-based",
    "file_locking": True,
    "auto_rebase": True,
}
```

## Monitoring Dashboard Updates

Add new metrics:
- Conflicts per task
- Merge success rate
- Agent utilization
- Dependency wait time
- File contention heat map

## Future Enhancements

1. **ML-based Conflict Prediction**: Predict which tasks will conflict
2. **Dynamic Task Splitting**: Break large tasks into non-conflicting subtasks
3. **Cross-Project Coordination**: Manage agents across multiple projects
4. **Intelligent Caching**: Share build artifacts between worktrees
5. **Rollback System**: Automatic rollback on merge failure