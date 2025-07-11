"""
Test script for rate limiting functionality.
Verifies that rate limits are working correctly.
"""

import requests
import time
import sys
from datetime import datetime


def test_rate_limiting():
    """Test the rate limiting functionality."""
    base_url = "http://localhost:5007"
    
    print("🧪 Testing Rate Limiting Implementation")
    print("=" * 50)
    
    # Test basic endpoint
    endpoint = f"{base_url}/api/properties"
    
    print(f"Testing endpoint: {endpoint}")
    print("Making requests to test rate limiting...")
    
    successful_requests = 0
    rate_limited_requests = 0
    
    # Make multiple requests quickly
    for i in range(15):  # Should trigger rate limit after 10 requests/minute
        try:
            response = requests.get(endpoint, timeout=5)
            
            print(f"Request {i+1}: Status {response.status_code}", end="")
            
            # Check rate limit headers
            if 'X-RateLimit-Remaining' in response.headers:
                remaining = response.headers.get('X-RateLimit-Remaining')
                limit = response.headers.get('X-RateLimit-Limit')
                print(f" | Remaining: {remaining}/{limit}")
            else:
                print()
            
            if response.status_code == 200:
                successful_requests += 1
            elif response.status_code == 429:
                rate_limited_requests += 1
                print(f"  ⚠️  Rate limited! Retry-After: {response.headers.get('Retry-After', 'N/A')} seconds")
                break
            else:
                print(f"  ❌ Unexpected status: {response.status_code}")
            
            # Small delay between requests
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")
            break
    
    print("\n📊 Test Results:")
    print(f"✅ Successful requests: {successful_requests}")
    print(f"⚠️  Rate limited requests: {rate_limited_requests}")
    
    if rate_limited_requests > 0:
        print("✅ Rate limiting is working correctly!")
    elif successful_requests > 10:
        print("⚠️  Rate limiting may not be working as expected")
    else:
        print("ℹ️  Need more requests to test rate limiting")


def test_different_endpoints():
    """Test rate limiting on different endpoint categories."""
    base_url = "http://localhost:5007"
    
    endpoints = [
        ("/api/properties", "API - Properties"),
        ("/login", "Auth - Login"),
        ("/predict-price", "ML - Prediction"),
    ]
    
    print("\n🎯 Testing Different Endpoint Categories")
    print("=" * 50)
    
    for endpoint, description in endpoints:
        print(f"\nTesting {description}: {endpoint}")
        
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"  Status: {response.status_code}")
            
            # Check for rate limit headers
            headers = ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Window']
            for header in headers:
                if header in response.headers:
                    print(f"  {header}: {response.headers[header]}")
                    
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")


def test_cli_commands():
    """Test CLI commands for rate limit management."""
    print("\n🔧 Testing CLI Commands")
    print("=" * 30)
    
    commands = [
        "flask rate-limit health",
        "flask rate-limit status",
    ]
    
    for cmd in commands:
        print(f"\nTesting: {cmd}")
        try:
            import subprocess
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Command executed successfully")
                if result.stdout:
                    print(f"Output: {result.stdout[:200]}...")
            else:
                print(f"❌ Command failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error running command: {e}")


if __name__ == "__main__":
    print(f"🚀 Rate Limiting Test - {datetime.now()}")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5007/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            
            # Run tests
            test_rate_limiting()
            test_different_endpoints()
            test_cli_commands()
            
        else:
            print(f"❌ Server not responding correctly: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        print("\n💡 To run this test:")
        print("1. Start the server: python app.py")
        print("2. Run this test: python test_rate_limiting.py")
    
    print(f"\n🏁 Test completed - {datetime.now()}")
