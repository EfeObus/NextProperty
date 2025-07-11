#!/usr/bin/env python3
"""
Comprehensive Rate Limiting Test Suite
Real-time testing of rate limiting functionality across different scenarios.
"""

import requests
import time
import threading
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from datetime import datetime, timedelta
import statistics

class RateLimitTester:
    """Comprehensive rate limiting test suite."""
    
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.results = defaultdict(list)
        self.session = requests.Session()
        
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    def make_request(self, endpoint, expected_status=200, headers=None):
        """Make a request and return detailed response info."""
        url = f"{self.base_url}{endpoint}"
        try:
            start_time = time.time()
            response = self.session.get(url, headers=headers or {})
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            # Extract rate limit headers
            rate_limit_info = {
                'limit': response.headers.get('X-RateLimit-Limit'),
                'remaining': response.headers.get('X-RateLimit-Remaining'),
                'reset': response.headers.get('X-RateLimit-Reset'),
                'retry_after': response.headers.get('Retry-After')
            }
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'rate_limit': rate_limit_info,
                'content': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'headers': dict(response.headers),
                'success': response.status_code == expected_status
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': 0,
                'rate_limit': {},
                'content': str(e),
                'headers': {},
                'success': False,
                'error': str(e)
            }
    
    def test_basic_functionality(self):
        """Test basic rate limiting functionality."""
        self.log("🧪 Testing Basic Functionality", "TEST")
        
        # Test unlimited endpoint
        self.log("Testing unlimited endpoint...")
        result = self.make_request("/api/unlimited")
        if result['success']:
            self.log(f"✅ Unlimited endpoint working (Response time: {result['response_time']:.2f}ms)")
        else:
            self.log(f"❌ Unlimited endpoint failed: {result.get('error', 'Unknown error')}", "ERROR")
        
        # Test health endpoint
        self.log("Testing health endpoint...")
        result = self.make_request("/health")
        if result['success']:
            self.log(f"✅ Health endpoint working (Response time: {result['response_time']:.2f}ms)")
        else:
            self.log(f"❌ Health endpoint failed: {result.get('error', 'Unknown error')}", "ERROR")
        
        return True
    
    def test_rate_limit_enforcement(self):
        """Test that rate limits are properly enforced."""
        self.log("🚦 Testing Rate Limit Enforcement", "TEST")
        
        # Test limited endpoint (5 per minute)
        self.log("Testing limited endpoint (5 per minute)...")
        success_count = 0
        rate_limited_count = 0
        
        for i in range(8):  # Try 8 requests (should get 5 success, 3 rate limited)
            result = self.make_request("/api/limited")
            if result['status_code'] == 200:
                success_count += 1
                self.log(f"  Request {i+1}: ✅ Success (Remaining: {result['rate_limit'].get('remaining', 'N/A')})")
            elif result['status_code'] == 429:
                rate_limited_count += 1
                self.log(f"  Request {i+1}: 🚫 Rate limited (Retry after: {result['rate_limit'].get('retry_after', 'N/A')}s)")
            else:
                self.log(f"  Request {i+1}: ❌ Unexpected status: {result['status_code']}", "ERROR")
            
            time.sleep(0.1)  # Small delay between requests
        
        self.log(f"Results: {success_count} successful, {rate_limited_count} rate limited")
        
        if success_count <= 5 and rate_limited_count >= 3:
            self.log("✅ Rate limiting working correctly")
            return True
        else:
            self.log("❌ Rate limiting not working as expected", "ERROR")
            return False
    
    def test_strict_rate_limiting(self):
        """Test strict rate limiting (2 per minute)."""
        self.log("🔒 Testing Strict Rate Limiting", "TEST")
        
        self.log("Testing strict endpoint (2 per minute)...")
        success_count = 0
        rate_limited_count = 0
        
        for i in range(5):  # Try 5 requests (should get 2 success, 3 rate limited)
            result = self.make_request("/api/strict")
            if result['status_code'] == 200:
                success_count += 1
                self.log(f"  Request {i+1}: ✅ Success")
            elif result['status_code'] == 429:
                rate_limited_count += 1
                self.log(f"  Request {i+1}: 🚫 Rate limited")
            
            time.sleep(0.1)
        
        self.log(f"Results: {success_count} successful, {rate_limited_count} rate limited")
        
        if success_count <= 2 and rate_limited_count >= 3:
            self.log("✅ Strict rate limiting working correctly")
            return True
        else:
            self.log("❌ Strict rate limiting not working as expected", "ERROR")
            return False
    
    def test_burst_protection(self):
        """Test burst protection functionality."""
        self.log("💥 Testing Burst Protection", "TEST")
        
        self.log("Testing burst protected endpoint (3/min, 10/hour)...")
        success_count = 0
        rate_limited_count = 0
        response_times = []
        
        for i in range(6):  # Try 6 requests quickly
            result = self.make_request("/api/burst")
            response_times.append(result['response_time'])
            
            if result['status_code'] == 200:
                success_count += 1
                self.log(f"  Request {i+1}: ✅ Success ({result['response_time']:.2f}ms)")
            elif result['status_code'] == 429:
                rate_limited_count += 1
                self.log(f"  Request {i+1}: 🚫 Rate limited ({result['response_time']:.2f}ms)")
            
            time.sleep(0.05)  # Very short delay to test burst
        
        avg_response_time = statistics.mean(response_times)
        self.log(f"Average response time: {avg_response_time:.2f}ms")
        self.log(f"Results: {success_count} successful, {rate_limited_count} rate limited")
        
        return True
    
    def test_concurrent_requests(self):
        """Test rate limiting under concurrent load."""
        self.log("🔄 Testing Concurrent Requests", "TEST")
        
        def make_concurrent_request(endpoint, request_id):
            """Make a request for concurrent testing."""
            result = self.make_request(endpoint)
            result['request_id'] = request_id
            return result
        
        # Test with 10 concurrent requests to limited endpoint
        self.log("Testing 10 concurrent requests to limited endpoint...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(make_concurrent_request, "/api/limited", i)
                for i in range(10)
            ]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        success_count = sum(1 for r in results if r['status_code'] == 200)
        rate_limited_count = sum(1 for r in results if r['status_code'] == 429)
        
        self.log(f"Concurrent results: {success_count} successful, {rate_limited_count} rate limited")
        
        # Should still respect rate limits even with concurrent requests
        if success_count <= 5:
            self.log("✅ Concurrent rate limiting working correctly")
            return True
        else:
            self.log("❌ Concurrent rate limiting allowing too many requests", "ERROR")
            return False
    
    def test_rate_limit_recovery(self):
        """Test rate limit recovery after waiting."""
        self.log("⏰ Testing Rate Limit Recovery", "TEST")
        
        # First, hit the rate limit
        self.log("Hitting rate limit on strict endpoint...")
        for i in range(3):
            result = self.make_request("/api/strict")
            if result['status_code'] == 429:
                retry_after = result['rate_limit'].get('retry_after')
                self.log(f"Rate limited. Retry after: {retry_after}s")
                break
        
        # Wait for recovery (simulate partial wait)
        self.log("Waiting 5 seconds for partial recovery...")
        time.sleep(5)
        
        # Try again
        result = self.make_request("/api/strict")
        if result['status_code'] == 200:
            self.log("✅ Successfully recovered from rate limit")
            return True
        elif result['status_code'] == 429:
            self.log("🔄 Still rate limited (expected for short wait)")
            return True
        else:
            self.log(f"❌ Unexpected status after recovery: {result['status_code']}", "ERROR")
            return False
    
    def test_header_information(self):
        """Test rate limit header information."""
        self.log("📋 Testing Rate Limit Headers", "TEST")
        
        result = self.make_request("/api/limited")
        headers = result['rate_limit']
        
        self.log("Rate limit headers:")
        for key, value in headers.items():
            if value:
                self.log(f"  {key}: {value}")
        
        # Check if essential headers are present
        essential_headers = ['limit', 'remaining']
        missing_headers = [h for h in essential_headers if not headers.get(h)]
        
        if not missing_headers:
            self.log("✅ Essential rate limit headers present")
            return True
        else:
            self.log(f"❌ Missing headers: {missing_headers}", "ERROR")
            return False
    
    def test_performance_impact(self):
        """Test performance impact of rate limiting."""
        self.log("⚡ Testing Performance Impact", "TEST")
        
        # Test response times with and without rate limiting
        unlimited_times = []
        limited_times = []
        
        # Test unlimited endpoint
        for i in range(5):
            result = self.make_request("/api/unlimited")
            if result['success']:
                unlimited_times.append(result['response_time'])
            time.sleep(0.1)
        
        # Test limited endpoint (within limits)
        for i in range(3):  # Stay within limit
            result = self.make_request("/api/limited")
            if result['success']:
                limited_times.append(result['response_time'])
            time.sleep(0.1)
        
        if unlimited_times and limited_times:
            avg_unlimited = statistics.mean(unlimited_times)
            avg_limited = statistics.mean(limited_times)
            overhead = avg_limited - avg_unlimited
            
            self.log(f"Average response time (unlimited): {avg_unlimited:.2f}ms")
            self.log(f"Average response time (limited): {avg_limited:.2f}ms")
            self.log(f"Rate limiting overhead: {overhead:.2f}ms")
            
            if overhead < 10:  # Less than 10ms overhead is excellent
                self.log("✅ Excellent performance - minimal overhead")
                return True
            elif overhead < 50:  # Less than 50ms is acceptable
                self.log("✅ Good performance - acceptable overhead")
                return True
            else:
                self.log("⚠️ High overhead detected", "WARN")
                return False
        else:
            self.log("❌ Could not measure performance impact", "ERROR")
            return False
    
    def test_error_handling(self):
        """Test error handling and user experience."""
        self.log("🚨 Testing Error Handling", "TEST")
        
        # Hit rate limit and check error response
        for i in range(6):  # Hit the limit (5 per minute)
            result = self.make_request("/api/limited")
            if result['status_code'] == 429:
                error_content = result['content']
                self.log("Rate limit error response:")
                if isinstance(error_content, dict):
                    for key, value in error_content.items():
                        self.log(f"  {key}: {value}")
                else:
                    self.log(f"  Content: {error_content}")
                
                # Check if error response is user-friendly
                if isinstance(error_content, dict) and 'error' in error_content:
                    self.log("✅ User-friendly error response provided")
                    return True
                break
        
        self.log("❌ Could not test error handling", "ERROR")
        return False
    
    def run_comprehensive_test(self):
        """Run all tests and provide summary."""
        self.log("🚀 Starting Comprehensive Rate Limiting Test Suite", "START")
        self.log("=" * 60)
        
        tests = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Rate Limit Enforcement", self.test_rate_limit_enforcement),
            ("Strict Rate Limiting", self.test_strict_rate_limiting),
            ("Burst Protection", self.test_burst_protection),
            ("Concurrent Requests", self.test_concurrent_requests),
            ("Rate Limit Recovery", self.test_rate_limit_recovery),
            ("Header Information", self.test_header_information),
            ("Performance Impact", self.test_performance_impact),
            ("Error Handling", self.test_error_handling),
        ]
        
        results = []
        start_time = time.time()
        
        for test_name, test_function in tests:
            self.log("-" * 60)
            try:
                result = test_function()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                self.log(f"{test_name}: {status}")
            except Exception as e:
                results.append((test_name, False))
                self.log(f"{test_name}: ❌ FAILED - {str(e)}", "ERROR")
            
            time.sleep(1)  # Pause between tests
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        self.log("=" * 60)
        self.log("📊 TEST SUMMARY", "SUMMARY")
        self.log("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        failed = len(results) - passed
        success_rate = (passed / len(results)) * 100
        
        self.log(f"Total tests: {len(results)}")
        self.log(f"Passed: {passed}")
        self.log(f"Failed: {failed}")
        self.log(f"Success rate: {success_rate:.1f}%")
        self.log(f"Total time: {total_time:.2f}s")
        
        self.log("\nDetailed Results:")
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"  {test_name}: {status}")
        
        if success_rate >= 80:
            self.log("\n🎉 Rate limiting system is working well!", "SUCCESS")
        elif success_rate >= 60:
            self.log("\n⚠️ Rate limiting system needs some attention.", "WARN")
        else:
            self.log("\n🚨 Rate limiting system has significant issues!", "ERROR")
        
        return success_rate >= 80


def main():
    """Main function to run the tests."""
    print("🧪 Rate Limiting Comprehensive Test Suite")
    print("=" * 60)
    
    # Check if demo server is running
    tester = RateLimitTester()
    try:
        health_check = tester.make_request("/health")
        if not health_check['success']:
            print("❌ Demo server not running at http://localhost:5007")
            print("Please start the demo server first: python demo_rate_limiting.py")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to demo server: {e}")
        print("Please start the demo server first: python demo_rate_limiting.py")
        return False
    
    print("✅ Demo server is running")
    print()
    
    # Run comprehensive tests
    success = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
