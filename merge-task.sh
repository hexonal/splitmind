#!/bin/bash
# Script to merge a task branch in the splitmind.ai project

PROJECT_DIR="/Users/jasonbrashear/code/splitmind.ai"
BRANCH=$1

if [ -z "$BRANCH" ]; then
    echo "Usage: $0 <branch-name>"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

echo "Checking out main branch..."
git checkout main

echo "Merging $BRANCH..."
git merge "$BRANCH" --no-ff -m "Merge branch '$BRANCH'"

if [ $? -eq 0 ]; then
    echo "✅ Successfully merged $BRANCH into main"
    
    # Update task status to merged
    echo "Branch merged successfully!"
else
    echo "❌ Failed to merge $BRANCH"
    exit 1
fi