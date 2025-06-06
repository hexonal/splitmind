"""
Task configuration with file ownership and dependencies
"""

TASK_DEFINITIONS = {
    # Test project tasks
    "base-html": {
        "title": "Base HTML",
        "priority": 10,
        "merge_order": 1,
        "exclusive_files": ["index.html"],
        "shared_files": [],
        "initialization_deps": [],
        "setup_commands": [],
    },
    
    "base-css": {
        "title": "Base CSS",
        "priority": 10,
        "merge_order": 2,
        "exclusive_files": ["styles.css"],
        "shared_files": [],
        "initialization_deps": [],
        "setup_commands": [],
    },
    
    "header-component": {
        "title": "Header Component",
        "priority": 8,
        "merge_order": 5,
        "exclusive_files": ["components/header.css"],
        "shared_files": ["index.html"],
        "initialization_deps": ["base-html"],
        "setup_commands": [],
    },
    
    "footer-component": {
        "title": "Footer Component",
        "priority": 8,
        "merge_order": 6,
        "exclusive_files": ["components/footer.css"],
        "shared_files": ["index.html"],
        "initialization_deps": ["base-html"],
        "setup_commands": [],
    },
    
    "theme-styles": {
        "title": "Theme Styles",
        "priority": 7,
        "merge_order": 7,
        "exclusive_files": ["components/theme.css"],
        "shared_files": ["styles.css"],
        "initialization_deps": ["base-css"],
        "setup_commands": [],
    },
    
    "javascript-base": {
        "title": "JavaScript Base",
        "priority": 9,
        "merge_order": 3,
        "exclusive_files": ["script.js"],
        "shared_files": [],
        "initialization_deps": [],
        "setup_commands": [],
    },
    
    "data-file": {
        "title": "Data File",
        "priority": 9,
        "merge_order": 4,
        "exclusive_files": ["data/content.json"],
        "shared_files": [],
        "initialization_deps": [],
        "setup_commands": [],
    },
    
    "main-content": {
        "title": "Main Content",
        "priority": 6,
        "merge_order": 8,
        "exclusive_files": ["components/main.css"],
        "shared_files": ["index.html"],
        "initialization_deps": ["header-component", "footer-component"],
        "setup_commands": [],
    },
    
    "interactive-features": {
        "title": "Interactive Features",
        "priority": 5,
        "merge_order": 9,
        "exclusive_files": ["components/interactive.js"],
        "shared_files": ["script.js"],
        "initialization_deps": ["javascript-base", "main-content"],
        "setup_commands": [],
    },
    
    "final-integration": {
        "title": "Final Integration",
        "priority": 4,
        "merge_order": 10,
        "exclusive_files": [],
        "shared_files": ["index.html"],
        "initialization_deps": ["main-content", "interactive-features"],
        "setup_commands": [],
    },
    
    # Original project tasks
    "framework": {
        "title": "Next.js 14 Framework Setup",
        "priority": 10,
        "merge_order": 1,
        "exclusive_files": [
            "next.config.ts",
            "next.config.js",
            "tsconfig.json",
            "src/app/layout.tsx",
            "src/app/page.tsx",
            "src/app/*.tsx",
            "src/app/*.ts",
            "public/",
        ],
        "shared_files": ["package.json", "README.md", ".gitignore"],
        "initialization_deps": [],
        "setup_commands": ["pnpm install", "pnpm next telemetry disable"],
    },
    
    "styling": {
        "title": "TailwindCSS Configuration",
        "priority": 9,
        "merge_order": 2,
        "exclusive_files": [
            "tailwind.config.ts",
            "tailwind.config.js",
            "postcss.config.mjs",
            "postcss.config.js",
            "src/styles/",
            "src/app/globals.css",
        ],
        "shared_files": ["package.json"],
        "initialization_deps": ["framework"],
        "setup_commands": ["pnpm install"],
    },
    
    "ui-components": {
        "title": "ShadCN/UI Components",
        "priority": 8,
        "merge_order": 3,
        "exclusive_files": [
            "src/components/",
            "components/",
            "components.json",
            "lib/utils.ts",
        ],
        "shared_files": ["package.json"],
        "initialization_deps": ["framework", "styling"],
        "setup_commands": ["pnpm install", "pnpx shadcn-ui@latest init -y"],
    },
    
    "package-manager": {
        "title": "Package Manager Setup",
        "priority": 10,
        "merge_order": 0,  # Should merge first
        "exclusive_files": [
            ".npmrc",
            ".nvmrc",
            "pnpm-workspace.yaml",
        ],
        "shared_files": ["package.json", ".gitignore"],
        "initialization_deps": [],
        "setup_commands": [],
    },
    
    "code-quality": {
        "title": "ESLint + Prettier",
        "priority": 7,
        "merge_order": 4,
        "exclusive_files": [
            "eslint.config.mjs",
            "eslint.config.js",
            ".eslintrc.js",
            ".eslintrc.json",
            ".prettierrc",
            ".prettierrc.json",
            ".editorconfig",
        ],
        "shared_files": ["package.json"],
        "initialization_deps": ["framework"],
        "setup_commands": ["pnpm install"],
    },
    
    "type-safety": {
        "title": "TypeScript Configuration",
        "priority": 8,
        "merge_order": 5,
        "exclusive_files": [
            "src/types/",
            "types/",
            "global.d.ts",
        ],
        "shared_files": ["tsconfig.json", "package.json"],
        "initialization_deps": ["framework"],
        "setup_commands": ["pnpm install"],
    },
}


def can_tasks_run_concurrently(task1_id: str, task2_id: str) -> bool:
    """
    Check if two tasks can run concurrently without file conflicts
    """
    if task1_id not in TASK_DEFINITIONS or task2_id not in TASK_DEFINITIONS:
        return True  # Unknown tasks, assume they can run
    
    task1 = TASK_DEFINITIONS[task1_id]
    task2 = TASK_DEFINITIONS[task2_id]
    
    # Check for exclusive file conflicts
    exclusive1 = set(task1.get("exclusive_files", []))
    exclusive2 = set(task2.get("exclusive_files", []))
    
    # Check if any exclusive files overlap
    if exclusive1.intersection(exclusive2):
        return False
    
    # Check if one task's exclusive files conflict with another's shared files
    shared1 = set(task1.get("shared_files", []))
    shared2 = set(task2.get("shared_files", []))
    
    if exclusive1.intersection(shared2) or exclusive2.intersection(shared1):
        return False
    
    return True


def get_task_config(task_id: str) -> dict:
    """
    Get configuration for a specific task
    """
    # Normalize task ID (remove project prefix if present)
    if "-" in task_id:
        parts = task_id.split("-")
        if len(parts) > 2:
            task_id = "-".join(parts[2:])  # Remove project prefix
    
    return TASK_DEFINITIONS.get(task_id, {})


def get_initialization_script(task_id: str, worktree_path: str) -> str:
    """
    Generate initialization script for a task's worktree
    """
    config = get_task_config(task_id)
    
    script_lines = [
        "#!/bin/bash",
        f"cd {worktree_path}",
        "echo '🔧 Initializing worktree...'",
    ]
    
    # Add setup commands
    for cmd in config.get("setup_commands", []):
        script_lines.append(f"echo '  Running: {cmd}'")
        script_lines.append(cmd)
    
    script_lines.append("echo '✅ Worktree initialized!'")
    
    return "\n".join(script_lines)