#!/usr/bin/env python3
"""
Simple Security Test Runner

This script runs security tests with proper path handling and can work
with or without the actual security modules installed.
"""

import sys
import os
from pathlib import Path
import subprocess
import importlib.util

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check which dependencies are available."""
    available = {}
    
    # Check for pytest
    try:
        import pytest
        available['pytest'] = True
    except ImportError:
        available['pytest'] = False
    
    # Check for security modules
    try:
        spec = importlib.util.find_spec('app.security.advanced_validation')
        available['security_modules'] = spec is not None
    except ImportError:
        available['security_modules'] = False
    
    return available

def install_pytest():
    """Install pytest if not available."""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pytest'])
        return True
    except subprocess.CalledProcessError:
        return False

def run_tests(test_file=None, verbose=True):
    """Run security tests."""
    deps = check_dependencies()
    
    # Install pytest if not available
    if not deps['pytest']:
        print("pytest not found. Installing...")
        if install_pytest():
            print("✅ pytest installed successfully")
        else:
            print("❌ Failed to install pytest")
            return False
    
    # Determine which tests to run
    if test_file:
        test_files = [test_file]
    else:
        test_files = [
            'tests/test_security_comprehensive.py',
            'tests/test_security_performance.py',
            'tests/test_security_attacks.py'
        ]
    
    # Check if test files exist
    existing_files = []
    for file in test_files:
        file_path = project_root / file
        if file_path.exists():
            existing_files.append(str(file_path))
        else:
            print(f"⚠️  Test file not found: {file}")
    
    if not existing_files:
        print("❌ No test files found")
        return False
    
    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest'] + existing_files
    
    if verbose:
        cmd.append('-v')
    
    # Add basic options
    cmd.extend(['--tb=short', '-x'])  # Stop on first failure
    
    print(f"🔒 Running Security Tests")
    print(f"Files: {len(existing_files)}")
    if not deps['security_modules']:
        print("⚠️  Security modules not found - running with mocks")
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run NextProperty AI security tests')
    parser.add_argument('--file', '-f', help='Run specific test file')
    parser.add_argument('--quiet', '-q', action='store_true', help='Less verbose output')
    
    args = parser.parse_args()
    
    print("🔒 NextProperty AI Security Test Runner")
    print("=" * 50)
    
    # Check environment
    deps = check_dependencies()
    print(f"Python version: {sys.version}")
    print(f"Working directory: {project_root}")
    print(f"pytest available: {'✅' if deps['pytest'] else '❌'}")
    print(f"Security modules: {'✅' if deps['security_modules'] else '⚠️  (will use mocks)'}")
    print()
    
    # Run tests
    success = run_tests(args.file, not args.quiet)
    
    if success:
        print("\n🎉 Security tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed or couldn't run")
        return 1

if __name__ == '__main__':
    sys.exit(main())
