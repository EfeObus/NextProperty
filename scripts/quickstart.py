#!/usr/bin/env python3
"""
NextProperty Auto Git Update - Quick Start Guide

This script provides a quick overview of all available commands
and features of the auto-update system.
"""

import os
from pathlib import Path

def print_header():
    """Print the header information."""
    print("🚀 NextProperty Auto Git Update System")
    print("=" * 60)
    print("Automated GitHub Integration for https://github.com/EfeObus/NextProperty")
    print("=" * 60)

def print_quick_commands():
    """Print quick start commands."""
    print("\n🎯 QUICK START COMMANDS:")
    print("─" * 40)
    print("# Setup (run this first)")
    print("./scripts/git_auto_update.sh setup")
    print()
    print("# Check for changes")
    print("./scripts/git_auto_update.sh check")
    print()
    print("# Update now (commit & push)")
    print("./scripts/git_auto_update.sh update")
    print()
    print("# Start automatic monitoring")
    print("./scripts/git_auto_update.sh watch")

def print_advanced_commands():
    """Print advanced commands."""
    print("\n🔧 ADVANCED COMMANDS:")
    print("─" * 40)
    print("# Python script directly")
    print("python scripts/auto_git_update.py --help")
    print()
    print("# One-time update")
    print("python scripts/auto_git_update.py --once")
    print()
    print("# Watch mode with custom delay")
    print("python scripts/auto_git_update.py --watch --delay 60")
    print()
    print("# Interactive mode")
    print("python scripts/auto_git_update.py")

def print_service_setup():
    """Print service setup instructions."""
    print("\n🛠️  BACKGROUND SERVICE SETUP:")
    print("─" * 40)
    print("# macOS LaunchAgent")
    print("cp scripts/com.nextproperty.autoupdate.plist ~/Library/LaunchAgents/")
    print("launchctl load ~/Library/LaunchAgents/com.nextproperty.autoupdate.plist")
    print("launchctl start com.nextproperty.autoupdate")
    print()
    print("# Linux SystemD")
    print("sudo cp scripts/nextproperty-auto-update.service /etc/systemd/system/")
    print("sudo systemctl enable nextproperty-auto-update.service")
    print("sudo systemctl start nextproperty-auto-update.service")

def print_features():
    """Print feature list."""
    print("\n✨ KEY FEATURES:")
    print("─" * 40)
    print("• 🔍 Automatic change detection")
    print("• 🧠 Intelligent commit message generation")
    print("• 🚫 Smart file filtering (ignores logs, cache, etc.)")
    print("• ⏱️  Configurable delay before auto-commit")
    print("• 📝 Comprehensive logging")
    print("• 🔄 Background service support")
    print("• 🛡️  Error handling and recovery")
    print("• 🎯 Context-aware categorization")

def print_file_structure():
    """Print the auto-update file structure."""
    print("\n📁 AUTO-UPDATE FILES:")
    print("─" * 40)
    files = [
        "scripts/auto_git_update.py          # Main Python script",
        "scripts/git_auto_update.sh          # Shell wrapper script",
        "scripts/demo_auto_update.py         # Demo and testing",
        "scripts/git_hooks.py                # Git hooks integration",
        "scripts/config_auto_update.json     # Configuration file",
        "scripts/requirements_auto_update.txt # Python dependencies",
        "scripts/com.nextproperty.autoupdate.plist # macOS service",
        "scripts/nextproperty-auto-update.service  # Linux service",
        "docs/AUTO_GIT_UPDATE_GUIDE.md       # Complete documentation"
    ]
    
    for file_desc in files:
        print(f"  {file_desc}")

def print_examples():
    """Print usage examples."""
    print("\n📚 USAGE EXAMPLES:")
    print("─" * 40)
    print("# Example 1: Basic setup and first run")
    print("./scripts/git_auto_update.sh setup")
    print("./scripts/git_auto_update.sh update")
    print()
    print("# Example 2: Start monitoring for automatic updates")
    print("./scripts/git_auto_update.sh watch")
    print("# (Leave running in background or set up as service)")
    print()
    print("# Example 3: Check what would be committed")
    print("./scripts/git_auto_update.sh status")
    print("./scripts/git_auto_update.sh check")

def print_troubleshooting():
    """Print troubleshooting tips."""
    print("\n🔧 TROUBLESHOOTING:")
    print("─" * 40)
    print("• Check logs: tail -f logs/git_auto_update.log")
    print("• Test script: python scripts/auto_git_update.py --help")
    print("• Verify Git config: git config --list")
    print("• Check permissions: ls -la scripts/")
    print("• View Git status: git status")

def print_next_steps():
    """Print next steps."""
    print("\n🎯 NEXT STEPS:")
    print("─" * 40)
    print("1. Run: ./scripts/git_auto_update.sh setup")
    print("2. Test: ./scripts/git_auto_update.sh check")
    print("3. Try: ./scripts/git_auto_update.sh update")
    print("4. Demo: python scripts/demo_auto_update.py")
    print("5. Setup service for continuous monitoring")
    print("6. Read: docs/AUTO_GIT_UPDATE_GUIDE.md")

def main():
    """Main function."""
    # Change to project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)
    
    print_header()
    print_quick_commands()
    print_advanced_commands()
    print_service_setup()
    print_features()
    print_file_structure()
    print_examples()
    print_troubleshooting()
    print_next_steps()
    
    print("\n" + "=" * 60)
    print("🎉 Happy coding! Your changes will be automatically synced to GitHub.")
    print("📖 Full documentation: docs/AUTO_GIT_UPDATE_GUIDE.md")
    print("🐛 Issues? Check logs/git_auto_update.log")
    print("=" * 60)

if __name__ == "__main__":
    main()
