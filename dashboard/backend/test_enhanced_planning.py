#!/usr/bin/env python3
"""
Test script to verify the enhanced plan generation with dependencies and priorities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.anthropic_client import AnthropicClient

def test_parse_response():
    """Test the parsing of tasks with dependencies and priorities"""
    
    # Create a sample response that matches our expected format
    sample_response = """
## Project Plan

Here's a comprehensive plan for building a web application:

### Architecture
- Frontend: React with TypeScript
- Backend: FastAPI
- Database: PostgreSQL

### Tasks

- **Set up project structure** - Initialize Git repo and create basic folder structure | Dependencies: [none] | Priority: 1
- **Create database schema** - Design and implement PostgreSQL database models | Dependencies: [Set up project structure] | Priority: 2
- **Implement user authentication** - Build JWT-based auth system | Dependencies: [Create database schema] | Priority: 3
- **Create API endpoints** - Build REST API for user management | Dependencies: [Create database schema, Implement user authentication] | Priority: 3
- **Build frontend components** - Create React components for UI | Dependencies: [Set up project structure] | Priority: 4
- **Integrate frontend with API** - Connect React app to backend | Dependencies: [Create API endpoints, Build frontend components] | Priority: 5
- **Write unit tests** - Add comprehensive test coverage | Dependencies: [Create API endpoints] | Priority: 6
- **Add CI/CD pipeline** - Set up GitHub Actions for automated testing | Dependencies: [Write unit tests] | Priority: 7
- **Deploy to production** - Deploy app to cloud platform | Dependencies: [Add CI/CD pipeline] | Priority: 8
"""
    
    # Test the parsing function
    client = AnthropicClient()
    result = client._parse_response(sample_response)
    
    print("🧪 Testing Enhanced Plan Parsing")
    print("=" * 60)
    
    # Check if parsing was successful
    assert result["success"] == True
    assert len(result["suggested_tasks"]) == 9
    
    print(f"✅ Successfully parsed {len(result['suggested_tasks'])} tasks")
    print()
    
    # Verify each task has the expected fields
    for i, task in enumerate(result["suggested_tasks"]):
        print(f"Task {i+1}: {task['title']}")
        print(f"  Description: {task['description']}")
        print(f"  Dependencies: {task['dependencies']}")
        print(f"  Priority: {task['priority']}")
        print()
        
        # Verify fields exist
        assert "title" in task
        assert "description" in task
        assert "dependencies" in task
        assert "priority" in task
        assert isinstance(task["dependencies"], list)
        assert isinstance(task["priority"], int)
    
    # Check specific task dependencies
    task_map = {t["title"]: t for t in result["suggested_tasks"]}
    
    # First task should have no dependencies
    assert task_map["Set up project structure"]["dependencies"] == []
    assert task_map["Set up project structure"]["priority"] == 1
    
    # Database schema should depend on project structure
    assert "Set up project structure" in task_map["Create database schema"]["dependencies"]
    assert task_map["Create database schema"]["priority"] == 2
    
    # API endpoints should have multiple dependencies
    api_task = task_map["Create API endpoints"]
    assert "Create database schema" in api_task["dependencies"]
    assert "Implement user authentication" in api_task["dependencies"]
    assert len(api_task["dependencies"]) == 2
    
    print("✅ All dependency relationships verified correctly!")
    print("✅ All priority values parsed correctly!")
    
    # Test fallback parsing (without proper format)
    print("\n" + "=" * 60)
    print("🧪 Testing Fallback Parsing")
    
    fallback_response = """
Here are the tasks:
- Set up the project
- Create database models
- Build the API
"""
    
    fallback_result = client._parse_response(fallback_response)
    print(f"✅ Fallback parsing found {len(fallback_result['suggested_tasks'])} tasks")
    
    # Check fallback tasks have default values
    for task in fallback_result["suggested_tasks"]:
        assert task["dependencies"] == []
        assert task["priority"] == 5
        print(f"  - {task['title']} (default priority: {task['priority']})")
    
    print("\n🎉 All tests passed successfully!")


if __name__ == "__main__":
    test_parse_response()