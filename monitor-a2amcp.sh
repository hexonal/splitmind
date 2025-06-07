#!/bin/bash
# Monitor A2AMCP coordination in real-time

PROJECT_ID="${1:-test-coordination}"

while true; do
  clear
  echo "🔍 A2AMCP Coordination Monitor - Project: $PROJECT_ID"
  echo "=================================================="
  echo ""
  
  echo "📊 ACTIVE AGENTS:"
  echo "----------------"
  docker exec splitmind-redis redis-cli HGETALL "project:$PROJECT_ID:agents" 2>/dev/null || echo "No agents registered"
  
  echo ""
  echo "🔒 FILE LOCKS:"
  echo "--------------"
  docker exec splitmind-redis redis-cli HGETALL "project:$PROJECT_ID:locks" 2>/dev/null || echo "No file locks"
  
  echo ""
  echo "📝 RECENT TODOS (last 5):"
  echo "-------------------------"
  for agent in $(docker exec splitmind-redis redis-cli KEYS "project:$PROJECT_ID:todos:*" 2>/dev/null); do
    echo "Agent: ${agent##*:}"
    docker exec splitmind-redis redis-cli LRANGE "$agent" -5 -1 2>/dev/null
  done
  
  echo ""
  echo "🔗 SHARED INTERFACES:"
  echo "--------------------"
  docker exec splitmind-redis redis-cli HKEYS "project:$PROJECT_ID:interfaces" 2>/dev/null || echo "No shared interfaces"
  
  echo ""
  echo "💬 RECENT MESSAGES (last 5):"
  echo "---------------------------"
  docker exec splitmind-redis redis-cli LRANGE "project:$PROJECT_ID:messages" -5 -1 2>/dev/null || echo "No messages"
  
  echo ""
  echo "🕐 Last update: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Press Ctrl+C to exit"
  
  sleep 3
done