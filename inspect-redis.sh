#!/bin/bash
# Quick Redis inspection for A2AMCP debugging

echo "🔍 A2AMCP Redis Inspector"
echo "========================"
echo ""

echo "📋 All Projects:"
docker exec splitmind-redis redis-cli KEYS "project:*" | grep -v "project:.*:.*"
echo ""

echo "🔑 All Keys:"
docker exec splitmind-redis redis-cli KEYS "*"
echo ""

if [ "$1" ]; then
    PROJECT_ID="$1"
    echo "📊 Details for project: $PROJECT_ID"
    echo "-----------------------------------"
    
    echo -e "\n🤖 Agents:"
    docker exec splitmind-redis redis-cli HGETALL "project:$PROJECT_ID:agents"
    
    echo -e "\n🔒 File Locks:"
    docker exec splitmind-redis redis-cli HGETALL "project:$PROJECT_ID:locks"
    
    echo -e "\n🔗 Interfaces:"
    docker exec splitmind-redis redis-cli HKEYS "project:$PROJECT_ID:interfaces"
    
    echo -e "\n📝 Todo Lists:"
    for key in $(docker exec splitmind-redis redis-cli KEYS "project:$PROJECT_ID:todos:*"); do
        echo -e "\n$key:"
        docker exec splitmind-redis redis-cli LRANGE "$key" 0 -1
    done
    
    echo -e "\n💬 Messages:"
    docker exec splitmind-redis redis-cli LRANGE "project:$PROJECT_ID:messages" 0 -1
else
    echo "Usage: $0 [project-id]"
    echo "Example: $0 simple-coord-demo"
fi