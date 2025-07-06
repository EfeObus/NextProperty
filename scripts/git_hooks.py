#!/usr/bin/env python3
"""
Git Hooks Integration for NextProperty Auto Update

This script can be used as a Git hook to automatically update
the repository when changes are detected.
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.auto_git_update import GitAutoUpdater

def pre_commit_hook():
    """Pre-commit hook to validate changes before commit."""
    print("Running pre-commit validation...")
    
    updater = GitAutoUpdater(repo_path=project_root)
    
    # Check if there are any changes
    if not updater.check_for_changes():
        print("No changes to commit")
        return 0
    
    # Get changed files
    changes = updater.get_changed_files()
    
    # Basic validation
    total_files = sum(len(files) for files in changes.values())
    if total_files > 100:
        print(f"Warning: Large number of files changed ({total_files})")
        response = input("Continue with commit? (y/N): ")
        if response.lower() != 'y':
            return 1
    
    print("Pre-commit validation passed")
    return 0

def post_commit_hook():
    """Post-commit hook to push changes after commit."""
    print("Running post-commit auto-push...")
    
    updater = GitAutoUpdater(repo_path=project_root)
    
    # Push the changes
    if updater.push_changes():
        print("Changes pushed successfully")
        return 0
    else:
        print("Failed to push changes")
        return 1

def install_hooks():
    """Install Git hooks for automatic updates."""
    hooks_dir = project_root / ".git" / "hooks"
    
    if not hooks_dir.exists():
        print("Error: Not in a Git repository")
        return 1
    
    # Create pre-commit hook
    pre_commit_path = hooks_dir / "pre-commit"
    with open(pre_commit_path, 'w') as f:
        f.write(f"""#!/bin/bash
# Auto-generated pre-commit hook for NextProperty
cd "{project_root}"
python "{__file__}" pre-commit
""")
    os.chmod(pre_commit_path, 0o755)
    
    # Create post-commit hook
    post_commit_path = hooks_dir / "post-commit"
    with open(post_commit_path, 'w') as f:
        f.write(f"""#!/bin/bash
# Auto-generated post-commit hook for NextProperty
cd "{project_root}"
python "{__file__}" post-commit
""")
    os.chmod(post_commit_path, 0o755)
    
    print("Git hooks installed successfully")
    print(f"Pre-commit hook: {pre_commit_path}")
    print(f"Post-commit hook: {post_commit_path}")
    return 0

def main():
    """Main function for hook execution."""
    if len(sys.argv) < 2:
        print("Usage: git_hooks.py [pre-commit|post-commit|install]")
        return 1
    
    command = sys.argv[1]
    
    if command == "pre-commit":
        return pre_commit_hook()
    elif command == "post-commit":
        return post_commit_hook()
    elif command == "install":
        return install_hooks()
    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
