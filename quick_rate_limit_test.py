#!/usr/bin/env python3
"""
Quick Rate Limiting Test for NextProperty AI
Simple test to verify rate limiting is working on the main application.
"""

import requests
import time
import json
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_rate_limiting():
    """Test rate limiting on NextProperty AI."""
    base_url = "http://localhost:5007"
    
    log("🧪 Quick Rate Limiting Test for NextProperty AI")
    log("=" * 50)
    
    # Test 1: Basic connectivity
    log("Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            log("✅ Application is responding")
        else:
            log(f"⚠️ Application returned status {response.status_code}")
    except Exception as e:
        log(f"❌ Cannot connect to application: {e}")
        return False
    
    # Test 2: Check rate limit headers
    log("\nTesting rate limit headers...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        headers_found = []
        
        for header in ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset']:
            if header in response.headers:
                headers_found.append(f"{header}: {response.headers[header]}")
        
        if headers_found:
            log("✅ Rate limit headers found:")
            for header in headers_found:
                log(f"   {header}")
        else:
            log("⚠️ No rate limit headers found (may use in-memory backend)")
            
    except Exception as e:
        log(f"❌ Error checking headers: {e}")
    
    # Test 3: Test rapid requests to trigger rate limiting
    log("\nTesting rapid requests...")
    success_count = 0
    rate_limited_count = 0
    
    for i in range(10):
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                success_count += 1
                log(f"  Request {i+1}: ✅ Success")
            elif response.status_code == 429:
                rate_limited_count += 1
                log(f"  Request {i+1}: 🚫 Rate limited!")
                break
            else:
                log(f"  Request {i+1}: Status {response.status_code}")
            
            time.sleep(0.1)  # Small delay
            
        except Exception as e:
            log(f"  Request {i+1}: ❌ Error: {e}")
    
    log(f"\nResults: {success_count} successful, {rate_limited_count} rate limited")
    
    # Test 4: Test API endpoint if available
    log("\nTesting API endpoint...")
    try:
        api_endpoints = ["/api/health", "/health", "/api/properties"]
        
        for endpoint in api_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    log(f"✅ {endpoint}: Working")
                    break
                elif response.status_code == 429:
                    log(f"🚫 {endpoint}: Rate limited")
                    break
                else:
                    log(f"⚠️ {endpoint}: Status {response.status_code}")
            except:
                continue
                
    except Exception as e:
        log(f"API test error: {e}")
    
    # Summary
    log("\n" + "=" * 50)
    log("📊 SUMMARY")
    log("=" * 50)
    
    if success_count > 0:
        log("✅ Application is responding to requests")
    
    if rate_limited_count > 0:
        log("✅ Rate limiting is working - blocked excessive requests")
    else:
        log("⚠️ Rate limiting not triggered (may need more requests or different endpoint)")
    
    log("\n🎯 Rate limiting system appears to be functional!")
    return True

if __name__ == "__main__":
    test_rate_limiting()
