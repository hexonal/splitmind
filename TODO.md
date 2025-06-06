# SplitMind TODO List

## Critical Setup Required
- [ ] **IMPORTANT**: Claude CLI permissions must be accepted before using orchestrator
  - Run in terminal: `claude --dangerously-skip-permissions "test"`
  - Select "Yes, I accept" when prompted
  - This is a one-time setup requirement
  - Without this, all agents will fail to spawn

## Current Issues
- [ ] Fix Ink raw mode error when launching agents in tmux
  - Status: Fixed - using echo pipe instead of stdin redirection
  - Test: Need to verify agents start properly with new command
- [ ] Fix blank screen after Generate Plan & Tasks
  - Status: Fixed - improved cache update logic in ProjectSettings
  - Test: Need to verify screen doesn't go blank after plan generation

## Agent System Enhancements

### Phase 1: Multi-Agent Architecture
- [ ] Design agent type system
  - [ ] Define agent roles (Coder, Reviewer, Tester, Planner, Documenter)
  - [ ] Create agent capabilities and constraints
  - [ ] Design inter-agent communication protocol

### Phase 2: Agent Types Implementation
- [ ] **Code Review Agent**
  - [ ] Reviews PR/branch before merge
  - [ ] Checks code quality, patterns, best practices
  - [ ] Suggests improvements
  - [ ] Can request changes from Coder agent

- [ ] **Planning Agent**
  - [ ] Breaks down complex tasks into subtasks
  - [ ] Analyzes dependencies
  - [ ] Estimates complexity and time
  - [ ] Suggests task ordering

- [ ] **Testing Agent**
  - [ ] Writes unit tests
  - [ ] Runs test suites
  - [ ] Reports coverage
  - [ ] Creates integration tests

- [ ] **Documentation Agent**
  - [ ] Updates README files
  - [ ] Writes API documentation
  - [ ] Creates code comments
  - [ ] Maintains changelog

- [ ] **DevOps Agent**
  - [ ] Sets up CI/CD pipelines
  - [ ] Configures deployment
  - [ ] Manages environment configs
  - [ ] Monitors performance

### Phase 3: Orchestrator Enhancements
- [ ] Agent assignment logic
  - [ ] Match agent types to task types
  - [ ] Load balancing across agents
  - [ ] Priority-based assignment

- [ ] Task routing
  - [ ] Route tasks to appropriate agent types
  - [ ] Handle agent specialization
  - [ ] Implement fallback strategies

- [ ] Agent coordination
  - [ ] Manage agent dependencies
  - [ ] Handle inter-agent communication
  - [ ] Resolve conflicts between agents

### Phase 4: UI/UX Improvements
- [ ] Agent type indicators in dashboard
  - [ ] Show agent type badges
  - [ ] Color coding by agent role
  - [ ] Agent capability display

- [ ] Agent assignment UI
  - [ ] Manual agent type selection
  - [ ] Auto-assignment preferences
  - [ ] Agent workload visualization

### Phase 5: Advanced Features
- [ ] Agent learning/memory
  - [ ] Project-specific knowledge base
  - [ ] Learn from code review feedback
  - [ ] Improve over time

- [ ] Agent collaboration
  - [ ] Pair programming between agents
  - [ ] Knowledge sharing
  - [ ] Consensus mechanisms

- [ ] Performance optimization
  - [ ] Parallel agent execution
  - [ ] Resource management
  - [ ] Cost optimization

## Project Management Features
- [ ] **Project Rename**
  - [ ] Add rename functionality in project settings
  - [ ] Update all references to project name
  - [ ] Handle file system implications
  - [ ] Update git repository name if applicable

- [ ] **Project Delete (Soft)**
  - [ ] Add delete button with confirmation dialog
  - [ ] Move project to "archived" status
  - [ ] Hide from main project list
  - [ ] Add "Show Archived" toggle

- [ ] **Project Nuclear Delete**
  - [ ] Complete removal from database
  - [ ] Delete project directory (with multiple confirmations)
  - [ ] Remove all git branches and worktrees
  - [ ] Clean up all related data

- [ ] **Project Management UI**
  - [ ] Add project actions dropdown menu
  - [ ] Implement rename dialog
  - [ ] Create delete confirmation flow
  - [ ] Add project archiving/unarchiving

## Technical Debt
- [ ] Add comprehensive logging for agent lifecycle
- [ ] Implement proper error handling for agent failures
- [ ] Create agent health monitoring system
- [ ] Add metrics and analytics for agent performance

## Future Ideas
- [ ] Natural language task creation from user stories
- [ ] AI-powered project estimation
- [ ] Automated tech debt identification
- [ ] Smart merge conflict resolution
- [ ] Cross-project knowledge transfer