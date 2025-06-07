#!/bin/bash
# Launch SplitMind with A2AMCP coordination

set -e

echo "🚀 Starting SplitMind with A2AMCP Agent Coordination"
echo "==================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if A2AMCP is cloned
if [ ! -d "A2AMCP" ]; then
    echo -e "${YELLOW}📥 A2AMCP not found. Cloning repository...${NC}"
    git clone https://github.com/webdevtodayjason/A2AMCP.git
fi

# Start A2AMCP server
echo -e "${GREEN}🏗️  Starting A2AMCP server...${NC}"
cd A2AMCP

# Make scripts executable
chmod +x quickstart.sh entrypoint.sh

# Start A2AMCP infrastructure
./quickstart.sh

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for A2AMCP services to be ready...${NC}"
sleep 10

# Check if MCP server is running
if docker ps | grep -q splitmind-mcp-server; then
    echo -e "${GREEN}✅ A2AMCP MCP server is running${NC}"
else
    echo -e "${RED}❌ A2AMCP MCP server failed to start${NC}"
    exit 1
fi

# Check if Redis is running
if docker ps | grep -q splitmind-redis; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis failed to start${NC}"
    exit 1
fi

# Go back to main directory
cd ..

# Configure Claude CLI for A2AMCP
echo -e "${GREEN}🔧 Configuring Claude CLI for A2AMCP...${NC}"
mkdir -p ~/.config/claude-code

# Create/update Claude config
cat > ~/.config/claude-code/a2amcp-config.json << 'EOF'
{
  "mcpServers": {
    "splitmind-coordination": {
      "command": "docker",
      "args": ["exec", "-i", "splitmind-mcp-server", "python", "/app/mcp_server_redis.py"],
      "env": {}
    }
  }
}
EOF

echo -e "${GREEN}📝 Created A2AMCP config at ~/.config/claude-code/a2amcp-config.json${NC}"

# Launch SplitMind Dashboard
echo -e "${GREEN}🎯 Launching SplitMind Dashboard...${NC}"
python launch-dashboard.py &
DASHBOARD_PID=$!

# Wait for dashboard to start
sleep 5

# Show status
echo ""
echo -e "${GREEN}🎉 SplitMind with A2AMCP is ready!${NC}"
echo ""
echo "📍 Service URLs:"
echo "   - SplitMind Dashboard: http://localhost:3000"
echo "   - A2AMCP MCP Server: localhost:5000"
echo "   - Redis: localhost:6379"
echo ""
echo "📊 Service Status:"
docker ps --filter name=splitmind --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "🔌 Next Steps:"
echo "   1. Set your Anthropic API key in Orchestrator Settings"
echo "   2. Create a new project with the setup wizard"
echo "   3. Watch agents coordinate in real-time!"
echo ""
echo "📝 Useful commands:"
echo "   - View A2AMCP logs: docker-compose -f A2AMCP/docker-compose.yml logs -f"
echo "   - Redis CLI: docker exec -it splitmind-redis redis-cli"
echo "   - Stop all: pkill -f launch-dashboard.py && docker-compose -f A2AMCP/docker-compose.yml down"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
wait $DASHBOARD_PID

# Cleanup on exit
echo -e "${YELLOW}🛑 Stopping services...${NC}"
docker-compose -f A2AMCP/docker-compose.yml down
echo -e "${GREEN}✅ All services stopped${NC}"