#!/usr/bin/env python3
"""
Setup script for abuse detection system.
Ensures proper configuration and initializes necessary components.
"""

import sys
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'flask',
        'redis',
        'numpy',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_file_structure():
    """Check if abuse detection files are in place."""
    required_files = [
        'app/security/abuse_detection.py',
        'app/security/abuse_detection_config.py',
        'app/cli/abuse_detection_commands.py',
        'abuse_detection_test.py',
        'demo_abuse_detection.py',
        'docs/ABUSE_DETECTION_DOCUMENTATION.md'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} is missing")
    
    if missing_files:
        print(f"\nMissing files need to be created:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    return True

def test_imports():
    """Test if abuse detection modules can be imported."""
    try:
        sys.path.append('.')
        from app.security.abuse_detection import AbuseDetectionRateLimiter, AbuseDetectionMiddleware
        from app.security.abuse_detection_config import ABUSE_DETECTION_CONFIG
        print("✅ Abuse detection modules can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_redis_connection():
    """Check Redis connection (optional)."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is available and accessible")
        return True
    except Exception as e:
        print(f"⚠️ Redis not available: {e}")
        print("   Abuse detection will use in-memory storage")
        return True  # Not a critical failure

def run_basic_test():
    """Run a basic functionality test."""
    try:
        sys.path.append('.')
        from app.security.abuse_detection import AbuseDetectionRateLimiter
        
        # Create test instance
        detector = AbuseDetectionRateLimiter()
        
        # Test basic functionality
        test_client_id = "test:127.0.0.1"
        test_request_data = {
            'endpoint': '/test',
            'method': 'GET',
            'status_code': 200,
            'response_time': 50,
            'user_agent': 'TestAgent/1.0',
            'parameters': {},
            'ip_address': '127.0.0.1'
        }
        
        # Record a request
        detector.record_request(test_client_id, test_request_data)
        
        # Analyze patterns
        metrics = detector.analyze_request_patterns(test_client_id)
        
        # Check rate limit
        allowed, retry_after, incident = detector.check_abuse_rate_limit(test_client_id)
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🔧 Abuse Detection System Setup")
    print("=" * 50)
    
    checks = [
        ("Checking dependencies", check_dependencies),
        ("Checking file structure", check_file_structure),
        ("Testing imports", test_imports),
        ("Checking Redis connection", check_redis_connection),
        ("Running basic test", run_basic_test)
    ]
    
    all_passed = True
    
    for check_name, check_function in checks:
        print(f"\n{check_name}...")
        if not check_function():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the demo server: python demo_abuse_detection.py")
        print("2. Run the test suite: python abuse_detection_test.py")
        print("3. Use CLI commands: flask abuse-detection status")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
