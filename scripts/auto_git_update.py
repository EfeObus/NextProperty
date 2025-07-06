#!/usr/bin/env python3
"""
Auto Git Update Script for NextProperty AI

This script automatically commits and pushes changes to the GitHub repository
when modifications are detected in the project.
"""

import os
import subprocess
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Optional, Dict, Any
import json
import hashlib
import signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class GitAutoUpdater:
    """Handles automatic Git operations for the NextProperty project."""
    
    def __init__(self, repo_path: str = None, remote_url: str = None, branch: str = "main"):
        """
        Initialize the Git auto-updater.
        
        Args:
            repo_path: Path to the Git repository
            remote_url: GitHub repository URL
            branch: Git branch to work with
        """
        self.repo_path = Path(repo_path or os.getcwd())
        self.remote_url = remote_url or "https://github.com/EfeObus/NextProperty.git"
        self.branch = branch
        self.last_commit_hash = None
        self.ignored_patterns = {
            '__pycache__/', '*.pyc', '*.pyo', '*.pyd', '.Python',
            'env/', 'venv/', '.venv/', '.env',
            'instance/', 'logs/', '.git/',
            '*.log', '*.log.*', '.DS_Store',
            'node_modules/', '.npm/', '.cache/',
            '*.tmp', '*.temp', '.pytest_cache/',
            '.coverage', 'htmlcov/', '.tox/',
            '.mypy_cache/', '.idea/', '.vscode/',
            '*.db', '*.sqlite', '*.sqlite3'
        }
        
        # Setup logging
        self.setup_logging()
        
        # Validate repository
        self.validate_repository()
        
    def setup_logging(self):
        """Setup logging configuration."""
        log_dir = self.repo_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "git_auto_update.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def validate_repository(self):
        """Validate that we're in a Git repository."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            self.logger.error(f"Not a Git repository: {self.repo_path}")
            raise ValueError(f"Directory {self.repo_path} is not a Git repository")
            
        self.logger.info(f"Git repository validated: {self.repo_path}")
        
    def run_git_command(self, command: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """
        Run a Git command and return the result.
        
        Args:
            command: Git command as list of strings
            capture_output: Whether to capture command output
            
        Returns:
            CompletedProcess object
        """
        full_command = ["git"] + command
        self.logger.debug(f"Running command: {' '.join(full_command)}")
        
        try:
            result = subprocess.run(
                full_command,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.logger.error(f"Git command failed: {' '.join(full_command)}")
                self.logger.error(f"Error output: {result.stderr}")
                
            return result
            
        except subprocess.SubprocessError as e:
            self.logger.error(f"Failed to run Git command: {e}")
            raise
            
    def check_for_changes(self) -> bool:
        """
        Check if there are any uncommitted changes.
        
        Returns:
            True if there are changes, False otherwise
        """
        # Check for unstaged changes
        result = self.run_git_command(["diff", "--quiet"])
        has_unstaged = result.returncode != 0
        
        # Check for staged changes
        result = self.run_git_command(["diff", "--cached", "--quiet"])
        has_staged = result.returncode != 0
        
        # Check for untracked files
        result = self.run_git_command(["ls-files", "--others", "--exclude-standard"])
        has_untracked = bool(result.stdout.strip())
        
        return has_unstaged or has_staged or has_untracked
        
    def get_changed_files(self) -> Dict[str, List[str]]:
        """
        Get lists of changed files by type.
        
        Returns:
            Dictionary with lists of modified, added, and deleted files
        """
        changes = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": []
        }
        
        # Get modified and deleted files
        result = self.run_git_command(["diff", "--name-status"])
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    status, filename = line.split('\t', 1)
                    if status == 'M':
                        changes["modified"].append(filename)
                    elif status == 'D':
                        changes["deleted"].append(filename)
                        
        # Get staged changes
        result = self.run_git_command(["diff", "--cached", "--name-status"])
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line:
                    status, filename = line.split('\t', 1)
                    if status == 'A':
                        changes["added"].append(filename)
                    elif status == 'M' and filename not in changes["modified"]:
                        changes["modified"].append(filename)
                        
        # Get untracked files
        result = self.run_git_command(["ls-files", "--others", "--exclude-standard"])
        if result.stdout:
            changes["untracked"] = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
        return changes
        
    def should_ignore_file(self, filepath: str) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if file should be ignored
        """
        for pattern in self.ignored_patterns:
            if pattern.endswith('/'):
                if filepath.startswith(pattern) or f"/{pattern}" in filepath:
                    return True
            elif pattern.startswith('*.'):
                if filepath.endswith(pattern[1:]):
                    return True
            elif pattern in filepath:
                return True
                
        return False
        
    def generate_commit_message(self, changes: Dict[str, List[str]]) -> str:
        """
        Generate an intelligent commit message based on changes.
        
        Args:
            changes: Dictionary of changed files by type
            
        Returns:
            Generated commit message
        """
        total_files = sum(len(files) for files in changes.values())
        
        if total_files == 0:
            return "Update: Minor changes"
            
        # Categorize changes by file type/purpose
        categories = {
            "security": [],
            "models": [],
            "routes": [],
            "templates": [],
            "static": [],
            "config": [],
            "docs": [],
            "tests": [],
            "scripts": [],
            "other": []
        }
        
        all_files = []
        for file_list in changes.values():
            all_files.extend(file_list)
            
        for filepath in all_files:
            if self.should_ignore_file(filepath):
                continue
                
            filepath_lower = filepath.lower()
            
            if "security" in filepath_lower or "auth" in filepath_lower:
                categories["security"].append(filepath)
            elif "model" in filepath_lower or filepath.startswith("models/"):
                categories["models"].append(filepath)
            elif "route" in filepath_lower or filepath.startswith("app/routes/"):
                categories["routes"].append(filepath)
            elif "template" in filepath_lower or filepath.startswith("app/templates/"):
                categories["templates"].append(filepath)
            elif "static" in filepath_lower or filepath.startswith("app/static/"):
                categories["static"].append(filepath)
            elif "config" in filepath_lower or filepath.startswith("config/"):
                categories["config"].append(filepath)
            elif "doc" in filepath_lower or filepath.startswith("docs/"):
                categories["docs"].append(filepath)
            elif "test" in filepath_lower or filepath.startswith("tests/"):
                categories["tests"].append(filepath)
            elif "script" in filepath_lower or filepath.startswith("scripts/"):
                categories["scripts"].append(filepath)
            else:
                categories["other"].append(filepath)
                
        # Generate message based on primary category
        primary_category = max(categories.keys(), key=lambda k: len(categories[k]))
        primary_count = len(categories[primary_category])
        
        if primary_count == 0:
            return f"Update: {total_files} file(s) modified"
            
        category_messages = {
            "security": "Enhanced security features and XSS protection",
            "models": "Updated data models and database schema",
            "routes": "Modified API routes and endpoints",
            "templates": "Updated UI templates and views",
            "static": "Updated static assets (CSS, JS, images)",
            "config": "Configuration updates and settings",
            "docs": "Documentation updates and improvements",
            "tests": "Test updates and new test cases",
            "scripts": "Utility scripts and automation updates",
            "other": "General updates and improvements"
        }
        
        base_message = category_messages.get(primary_category, "General updates")
        
        # Add file count details
        if total_files == 1:
            return f"{base_message} - 1 file updated"
        elif total_files <= 5:
            return f"{base_message} - {total_files} files updated"
        else:
            return f"{base_message} - {total_files} files updated (bulk update)"
            
    def stage_changes(self, changes: Dict[str, List[str]]) -> bool:
        """
        Stage all relevant changes for commit.
        
        Args:
            changes: Dictionary of changed files
            
        Returns:
            True if staging was successful
        """
        files_to_stage = []
        
        # Collect files that should be staged
        for file_list in [changes["modified"], changes["untracked"]]:
            for filepath in file_list:
                if not self.should_ignore_file(filepath):
                    files_to_stage.append(filepath)
                    
        if not files_to_stage:
            self.logger.info("No files to stage")
            return False
            
        # Stage files
        for filepath in files_to_stage:
            result = self.run_git_command(["add", filepath])
            if result.returncode == 0:
                self.logger.info(f"Staged: {filepath}")
            else:
                self.logger.error(f"Failed to stage: {filepath}")
                return False
                
        return True
        
    def commit_changes(self, message: str) -> bool:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            
        Returns:
            True if commit was successful
        """
        result = self.run_git_command(["commit", "-m", message])
        
        if result.returncode == 0:
            self.logger.info(f"Successfully committed: {message}")
            return True
        else:
            self.logger.error(f"Failed to commit changes: {result.stderr}")
            return False
            
    def push_changes(self) -> bool:
        """
        Push committed changes to remote repository.
        
        Returns:
            True if push was successful
        """
        # First, try to pull any remote changes
        self.logger.info("Pulling latest changes from remote...")
        pull_result = self.run_git_command(["pull", "origin", self.branch])
        
        if pull_result.returncode != 0:
            self.logger.warning("Failed to pull changes, attempting to push anyway")
            
        # Push changes
        self.logger.info(f"Pushing changes to origin/{self.branch}...")
        push_result = self.run_git_command(["push", "origin", self.branch])
        
        if push_result.returncode == 0:
            self.logger.info("Successfully pushed changes to GitHub")
            return True
        else:
            self.logger.error(f"Failed to push changes: {push_result.stderr}")
            return False
            
    def auto_update(self) -> bool:
        """
        Perform a complete auto-update cycle.
        
        Returns:
            True if update was successful
        """
        self.logger.info("Starting auto-update cycle...")
        
        # Check for changes
        if not self.check_for_changes():
            self.logger.info("No changes detected")
            return True
            
        # Get changed files
        changes = self.get_changed_files()
        self.logger.info(f"Changes detected: {changes}")
        
        # Stage changes
        if not self.stage_changes(changes):
            self.logger.error("Failed to stage changes")
            return False
            
        # Generate commit message
        commit_message = self.generate_commit_message(changes)
        self.logger.info(f"Generated commit message: {commit_message}")
        
        # Commit changes
        if not self.commit_changes(commit_message):
            return False
            
        # Push changes
        if not self.push_changes():
            return False
            
        self.logger.info("Auto-update cycle completed successfully")
        return True


class FileChangeHandler(FileSystemEventHandler):
    """File system event handler for watching file changes."""
    
    def __init__(self, git_updater: GitAutoUpdater, delay: int = 30):
        """
        Initialize the file change handler.
        
        Args:
            git_updater: GitAutoUpdater instance
            delay: Delay in seconds before triggering update
        """
        self.git_updater = git_updater
        self.delay = delay
        self.last_change_time = 0
        self.pending_update = False
        
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            self.trigger_update()
            
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            self.trigger_update()
            
    def on_deleted(self, event):
        """Handle file deletion events."""
        if not event.is_directory:
            self.trigger_update()
            
    def trigger_update(self):
        """Trigger an update after a delay."""
        current_time = time.time()
        self.last_change_time = current_time
        
        if not self.pending_update:
            self.pending_update = True
            # Schedule update after delay
            import threading
            timer = threading.Timer(self.delay, self.perform_update)
            timer.start()
            
    def perform_update(self):
        """Perform the actual update if no recent changes."""
        current_time = time.time()
        
        # Check if there were more recent changes
        if current_time - self.last_change_time >= self.delay:
            self.git_updater.logger.info("File changes detected, performing auto-update...")
            self.git_updater.auto_update()
            
        self.pending_update = False


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Auto Git Update for NextProperty AI")
    parser.add_argument("--repo-path", default=None, help="Path to Git repository")
    parser.add_argument("--remote-url", default="https://github.com/EfeObus/NextProperty.git", 
                       help="GitHub repository URL")
    parser.add_argument("--branch", default="main", help="Git branch to use")
    parser.add_argument("--watch", action="store_true", help="Watch for file changes")
    parser.add_argument("--delay", type=int, default=30, 
                       help="Delay in seconds before auto-update (watch mode)")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    
    args = parser.parse_args()
    
    try:
        # Initialize Git updater
        updater = GitAutoUpdater(
            repo_path=args.repo_path,
            remote_url=args.remote_url,
            branch=args.branch
        )
        
        if args.once:
            # Run once and exit
            success = updater.auto_update()
            sys.exit(0 if success else 1)
            
        elif args.watch:
            # Watch mode
            print(f"Watching for changes in {updater.repo_path}")
            print(f"Will auto-update to {args.remote_url} on branch {args.branch}")
            print("Press Ctrl+C to stop")
            
            # Setup file watcher
            event_handler = FileChangeHandler(updater, args.delay)
            observer = Observer()
            observer.schedule(event_handler, str(updater.repo_path), recursive=True)
            
            def signal_handler(signum, frame):
                print("\nShutting down...")
                observer.stop()
                observer.join()
                sys.exit(0)
                
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            observer.start()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                observer.join()
                
        else:
            # Interactive mode
            while True:
                print("\nNextProperty Auto Git Update")
                print("1. Check for changes")
                print("2. Auto-update now")
                print("3. Start watching for changes")
                print("4. Exit")
                
                choice = input("Enter your choice (1-4): ").strip()
                
                if choice == "1":
                    if updater.check_for_changes():
                        changes = updater.get_changed_files()
                        print(f"Changes detected: {changes}")
                    else:
                        print("No changes detected")
                        
                elif choice == "2":
                    updater.auto_update()
                    
                elif choice == "3":
                    print("Starting watch mode... Press Ctrl+C to stop")
                    event_handler = FileChangeHandler(updater, args.delay)
                    observer = Observer()
                    observer.schedule(event_handler, str(updater.repo_path), recursive=True)
                    observer.start()
                    
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        observer.stop()
                        observer.join()
                        print("Stopped watching")
                        
                elif choice == "4":
                    break
                    
                else:
                    print("Invalid choice")
                    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
