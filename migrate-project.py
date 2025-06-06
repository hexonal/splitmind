#!/usr/bin/env python3
"""
Migrate a project to the projects folder or create a new one
"""
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def migrate_project(project_id: str, source_path: str = None):
    """Migrate or create a project in the projects folder"""
    
    # Load projects config
    projects_file = Path("projects.json")
    if projects_file.exists():
        with open(projects_file) as f:
            projects = json.load(f)
    else:
        projects = {"projects": []}
    
    # Find the project
    project = None
    for p in projects["projects"]:
        if p["id"] == project_id:
            project = p
            break
    
    if not project:
        print(f"Project {project_id} not found in projects.json")
        return False
    
    # Create projects directory
    projects_dir = Path("projects")
    projects_dir.mkdir(exist_ok=True)
    
    # New project path
    new_path = projects_dir / project_id
    
    if source_path and Path(source_path).exists():
        print(f"Copying project from {source_path} to {new_path}")
        
        # If destination exists, ask for confirmation
        if new_path.exists():
            response = input(f"Project already exists at {new_path}. Overwrite? (y/n): ")
            if response.lower() != 'y':
                print("Migration cancelled")
                return False
            shutil.rmtree(new_path)
        
        # Copy the project
        shutil.copytree(source_path, new_path)
        print(f"Project copied successfully")
    else:
        # Clone from git if it's a new setup
        if new_path.exists():
            print(f"Project already exists at {new_path}")
        else:
            print(f"Creating new project at {new_path}")
            new_path.mkdir(parents=True)
            
            # Initialize git
            subprocess.run(["git", "init"], cwd=new_path)
            
            # Create initial structure
            (new_path / ".splitmind").mkdir(exist_ok=True)
            (new_path / "worktrees").mkdir(exist_ok=True)
            
            # Create a simple README
            readme = new_path / "README.md"
            readme.write_text(f"# {project['name']}\n\n{project.get('description', '')}\n")
            
            # Initial commit
            subprocess.run(["git", "add", "."], cwd=new_path)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=new_path)
            
            print(f"New project initialized")
    
    # Update project path in projects.json
    old_path = project["path"]
    project["path"] = str(new_path.absolute())
    
    # Save updated projects.json
    with open(projects_file, 'w') as f:
        json.dump(projects, f, indent=2)
    
    print(f"Updated project path from {old_path} to {project['path']}")
    print("Migration complete!")
    
    # Also update the .splitmind folder if needed
    splitmind_dir = new_path / ".splitmind"
    splitmind_dir.mkdir(exist_ok=True)
    
    # Ensure tasks.md exists
    tasks_file = splitmind_dir / "tasks.md"
    if not tasks_file.exists():
        tasks_file.write_text("# tasks.md\n\n")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate-project.py <project_id> [source_path]")
        print("  project_id: The ID of the project to migrate")
        print("  source_path: Optional path to copy from (e.g., /Users/jasonbrashear/code/splitmind.ai)")
        sys.exit(1)
    
    project_id = sys.argv[1]
    source_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = migrate_project(project_id, source_path)
    sys.exit(0 if success else 1)