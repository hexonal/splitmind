# Testing the Onboarding Modal and MCP Diagnostics

## Features Implemented

### 1. Onboarding Modal (`OnboardingModal.tsx`)
- ✅ Updated with specific MCP examples as requested:
  - Dart with token example
  - Context7 with SSE transport
  - Playwright
  - BrowserMCP
  - Copy from Claude Desktop command
- ✅ Multi-step modal with tabs for:
  - Anthropic API setup
  - Git & GitHub setup
  - Dart integration
  - MCP setup
- ✅ Copy-to-clipboard buttons for all commands
- ✅ Progress tracking with localStorage

### 2. MCP Diagnostics Component (`MCPDiagnostics.tsx`)
- ✅ Shows Claude CLI installation status
- ✅ Lists installed MCPs using `claude mcp list`
- ✅ Provides installation commands for recommended MCPs
- ✅ Copy-to-clipboard functionality
- ✅ Real-time status updates with refresh

### 3. Backend API Updates
- ✅ `/api/mcp/check-cli` - Check Claude CLI installation
- ✅ `/api/mcp/list` - List installed MCPs
- ✅ `/api/mcp/install` - Install MCP tools (optional)

### 4. UI Integration
- ✅ Help button in header opens onboarding modal
- ✅ "Need help getting started?" button on welcome screen
- ✅ MCP Status tab in Settings
- ✅ Auto-show onboarding on first visit

## Testing Steps

1. **Start the backend**:
   ```bash
   cd /Users/jasonbrashear/code/cctg
   python launch-dashboard.py
   ```

2. **Test Onboarding Modal**:
   - Click the "Help" button in the header
   - Navigate through all tabs
   - Test copy-to-clipboard buttons
   - Mark steps as complete

3. **Test MCP Diagnostics**:
   - Go to any project → Settings → MCP Status tab
   - Check Claude CLI status
   - View installed MCPs
   - Test copy buttons for installation commands

4. **First Visit Experience**:
   - Clear localStorage: `localStorage.clear()`
   - Refresh page
   - Onboarding should auto-open

## MCP Commands Included

```bash
# Dart (with token)
claude mcp add-json dart '{"command":"npx","args":["-y","dart-mcp-server"],"env":{"DART_TOKEN":"dsa_9aa6........."}}'

# Context7
claude mcp add --transport sse context7 https://mcp.context7.com/sse

# Playwright
claude mcp add-json playwright '{"command":"npx","args":["@playwright/mcp"]}'

# BrowserMCP
claude mcp add-json browsermcp '{"command":"npx","args":["@browsermcp/mcp@latest"]}'

# Copy from Claude Desktop
claude mcp add-from-claude-desktop
```

## Design System Used
- Dark theme with electric cyan accents
- ShadCN UI components
- Framer Motion animations
- Consistent with existing SplitMind design