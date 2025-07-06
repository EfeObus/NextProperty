#!/usr/bin/env python3
"""
Demo script for NextProperty Auto Git Update System

This script demonstrates the capabilities of the auto-update system.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.auto_git_update import GitAutoUpdater

def demo_threat_analysis():
    """Demonstrate the threat analysis capabilities."""
    print("🔒 NextProperty Auto Git Update System Demo")
    print("=" * 50)
    
    updater = GitAutoUpdater(repo_path=project_root)
    
    print("\n1. Repository Information:")
    print(f"   📁 Repository Path: {updater.repo_path}")
    print(f"   🌐 Remote URL: {updater.remote_url}")
    print(f"   🌿 Branch: {updater.branch}")
    
    print("\n2. Checking for Changes:")
    has_changes = updater.check_for_changes()
    print(f"   📝 Changes Detected: {'Yes' if has_changes else 'No'}")
    
    if has_changes:
        changes = updater.get_changed_files()
        print(f"   📊 Change Summary:")
        for change_type, files in changes.items():
            if files:
                print(f"      {change_type.title()}: {len(files)} files")
                for file in files[:3]:  # Show first 3 files
                    print(f"        - {file}")
                if len(files) > 3:
                    print(f"        ... and {len(files) - 3} more")
    
    print("\n3. Commit Message Generation:")
    if has_changes:
        changes = updater.get_changed_files()
        message = updater.generate_commit_message(changes)
        print(f"   💬 Generated Message: \"{message}\"")
    else:
        print("   💬 No changes to commit")
    
    print("\n4. File Filtering Demo:")
    test_files = [
        "app/routes/main.py",
        "__pycache__/test.pyc",
        "logs/app.log",
        "instance/config.py",
        "requirements.txt",
        ".DS_Store"
    ]
    
    for file in test_files:
        ignored = updater.should_ignore_file(file)
        status = "🚫 Ignored" if ignored else "✅ Included"
        print(f"   {status}: {file}")

def demo_auto_update():
    """Demonstrate auto-update functionality."""
    print("\n" + "=" * 50)
    print("🚀 Auto-Update Demo")
    print("=" * 50)
    
    updater = GitAutoUpdater(repo_path=project_root)
    
    print("\n⚠️  This will perform actual Git operations!")
    response = input("Continue with demo? (y/N): ")
    
    if response.lower() != 'y':
        print("Demo cancelled.")
        return
    
    print("\n🔄 Running auto-update cycle...")
    success = updater.auto_update()
    
    if success:
        print("✅ Auto-update completed successfully!")
    else:
        print("❌ Auto-update failed. Check logs for details.")

def demo_watch_mode():
    """Demonstrate watch mode (simulation)."""
    print("\n" + "=" * 50)
    print("👀 Watch Mode Demo (Simulation)")
    print("=" * 50)
    
    print("\n📱 In watch mode, the system would:")
    print("   1. Monitor file system for changes")
    print("   2. Wait for a quiet period (30 seconds by default)")
    print("   3. Automatically commit and push changes")
    print("   4. Generate intelligent commit messages")
    print("   5. Log all activities")
    
    print("\n🔧 To start actual watch mode, run:")
    print("   ./scripts/git_auto_update.sh watch")
    print("   or")
    print("   python scripts/auto_git_update.py --watch")

def main():
    """Main demo function."""
    print("🎯 NextProperty Auto Git Update System")
    print("   Automated GitHub Integration Demo")
    print("   Repository: https://github.com/EfeObus/NextProperty")
    
    try:
        demo_threat_analysis()
        
        print("\n" + "=" * 50)
        print("What would you like to demo?")
        print("1. Auto-update functionality (actual Git operations)")
        print("2. Watch mode explanation")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            demo_auto_update()
        elif choice == "2":
            demo_watch_mode()
        elif choice == "3":
            print("Demo complete!")
        else:
            print("Invalid choice.")
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n🎉 Thank you for trying the NextProperty Auto Git Update System!")
    print("📚 For more information, see: docs/AUTO_GIT_UPDATE_GUIDE.md")

if __name__ == "__main__":
    main()
