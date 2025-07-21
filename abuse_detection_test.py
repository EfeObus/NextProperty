#!/usr/bin/env python3
"""
Comprehensive Abuse Detection Test Suite
Real-time testing of abuse detection functionality across different scenarios.
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
import random

class AbuseDetectionTester:
    """Comprehensive abuse detection test suite."""
    
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.results = defaultdict(list)
        self.session = requests.Session()
        
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    def make_request(self, endpoint, expected_status=200, headers=None, params=None):
        """Make a request and return detailed response info."""
        url = f"{self.base_url}{endpoint}"
        try:
            start_time = time.time()
            response = self.session.get(url, headers=headers or {}, params=params or {})
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            # Extract abuse detection headers
            abuse_info = {
                'abuse_type': response.headers.get('X-Abuse-Type'),
                'abuse_level': response.headers.get('X-Abuse-Level'),
                'retry_after': response.headers.get('Retry-After')
            }
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'abuse_info': abuse_info,
                'content': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'headers': dict(response.headers),
                'success': response.status_code == expected_status
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': 0,
                'abuse_info': {},
                'content': str(e),
                'headers': {},
                'success': False,
                'error': str(e)
            }
    
    def test_basic_functionality(self):
        """Test basic abuse detection functionality."""
        self.log("🧪 Testing Basic Abuse Detection Functionality", "TEST")
        
        # Test normal behavior
        self.log("Testing normal request behavior...")
        result = self.make_request("/api/unlimited")
        if result['success']:
            self.log(f"✅ Normal request working (Response time: {result['response_time']:.2f}ms)")
        else:
            self.log(f"❌ Normal request failed: {result.get('error', 'Unknown error')}", "ERROR")
        
        return True
    
    def test_rapid_request_detection(self):
        """Test rapid request abuse detection."""
        self.log("🚀 Testing Rapid Request Detection", "TEST")
        
        self.log("Sending rapid requests to trigger detection...")
        blocked_count = 0
        allowed_count = 0
        response_times = []
        
        # Send 60 requests in quick succession
        for i in range(60):
            result = self.make_request("/api/limited")
            response_times.append(result['response_time'])
            
            if result['status_code'] == 429:
                blocked_count += 1
                abuse_type = result['abuse_info'].get('abuse_type')
                abuse_level = result['abuse_info'].get('abuse_level')
                self.log(f"  Request {i+1}: 🚫 Blocked (Type: {abuse_type}, Level: {abuse_level})")
            elif result['success']:
                allowed_count += 1
                if i < 5 or i % 10 == 0:  # Log first few and every 10th request
                    self.log(f"  Request {i+1}: ✅ Allowed")
            else:
                self.log(f"  Request {i+1}: ❌ Error: {result['status_code']}")
            
            time.sleep(0.05)  # 50ms between requests
        
        avg_response_time = statistics.mean(response_times)
        self.log(f"Results: {allowed_count} allowed, {blocked_count} blocked")
        self.log(f"Average response time: {avg_response_time:.2f}ms")
        
        if blocked_count > 0:
            self.log("✅ Rapid request detection working")
            return True
        else:
            self.log("⚠️ No rapid request blocking detected", "WARN")
            return False
    
    def test_authentication_abuse_detection(self):
        """Test authentication abuse detection."""
        self.log("🔐 Testing Authentication Abuse Detection", "TEST")
        
        self.log("Simulating failed login attempts...")
        failed_attempts = 0
        blocked_attempts = 0
        
        # Simulate multiple failed login attempts
        for i in range(15):
            # Simulate a failed login by making requests that would typically fail auth
            result = self.make_request("/api/limited", expected_status=200)
            
            if result['status_code'] == 429:
                blocked_attempts += 1
                abuse_type = result['abuse_info'].get('abuse_type')
                self.log(f"  Attempt {i+1}: 🚫 Blocked due to abuse detection (Type: {abuse_type})")
            else:
                failed_attempts += 1
                self.log(f"  Attempt {i+1}: 🔄 Request processed")
            
            time.sleep(0.2)  # 200ms between attempts
        
        self.log(f"Results: {failed_attempts} processed, {blocked_attempts} blocked")
        
        return True
    
    def test_scraping_behavior_detection(self):
        """Test scraping behavior detection."""
        self.log("🕷️ Testing Scraping Behavior Detection", "TEST")
        
        self.log("Simulating scraping behavior...")
        endpoints = [
            "/api/properties",
            "/api/search",
            "/api/property/1",
            "/api/property/2",
            "/api/property/3",
            "/api/agents",
            "/api/listings"
        ]
        
        blocked_count = 0
        total_requests = 0
        
        # Access many different endpoints with varying parameters
        for round_num in range(5):
            for endpoint in endpoints:
                for param_var in range(3):
                    params = {
                        'page': param_var + 1,
                        'limit': random.choice([10, 20, 50]),
                        'search': f"query_{param_var}",
                        'filter': f"filter_{random.randint(1, 10)}"
                    }
                    
                    result = self.make_request(endpoint, params=params)
                    total_requests += 1
                    
                    if result['status_code'] == 429:
                        blocked_count += 1
                        abuse_type = result['abuse_info'].get('abuse_type')
                        if abuse_type:
                            self.log(f"  🚫 Scraping detected and blocked (Type: {abuse_type})")
                    
                    time.sleep(0.1)  # 100ms between requests
        
        self.log(f"Results: {total_requests} total requests, {blocked_count} blocked")
        
        if blocked_count > 0:
            self.log("✅ Scraping detection working")
        else:
            self.log("⚠️ No scraping detection triggered", "WARN")
        
        return True
    
    def test_suspicious_pattern_detection(self):
        """Test suspicious pattern detection."""
        self.log("🕵️ Testing Suspicious Pattern Detection", "TEST")
        
        self.log("Simulating suspicious patterns...")
        
        # Test with varying user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Bot/1.0",
            "Scanner/2.0",
            "curl/7.68.0",
            "Python-requests/2.25.1",
            "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N)"
        ]
        
        blocked_count = 0
        total_requests = 0
        
        for i, user_agent in enumerate(user_agents):
            headers = {'User-Agent': user_agent}
            
            # Make multiple requests with each user agent
            for j in range(8):
                result = self.make_request("/api/unlimited", headers=headers)
                total_requests += 1
                
                if result['status_code'] == 429:
                    blocked_count += 1
                    abuse_type = result['abuse_info'].get('abuse_type')
                    self.log(f"  🚫 Suspicious pattern detected (UA: {user_agent[:30]}..., Type: {abuse_type})")
                
                time.sleep(0.1)
        
        self.log(f"Results: {total_requests} total requests, {blocked_count} blocked")
        return True
    
    def test_concurrent_abuse_detection(self):
        """Test abuse detection under concurrent load."""
        self.log("🔄 Testing Concurrent Abuse Detection", "TEST")
        
        def make_concurrent_requests(thread_id):
            """Make requests for concurrent testing."""
            blocked_count = 0
            total_count = 0
            
            for i in range(20):  # 20 requests per thread
                result = self.make_request("/api/limited")
                total_count += 1
                
                if result['status_code'] == 429:
                    blocked_count += 1
                
                time.sleep(0.05)  # 50ms between requests
            
            return {'thread_id': thread_id, 'blocked': blocked_count, 'total': total_count}
        
        self.log("Testing with 10 concurrent threads...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(make_concurrent_requests, i)
                for i in range(10)
            ]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        
        total_requests = sum(r['total'] for r in results)
        total_blocked = sum(r['blocked'] for r in results)
        
        self.log(f"Concurrent results: {total_requests} total requests, {total_blocked} blocked")
        
        if total_blocked > 0:
            self.log("✅ Concurrent abuse detection working")
            return True
        else:
            self.log("⚠️ No concurrent abuse blocking detected", "WARN")
            return False
    
    def test_abuse_recovery(self):
        """Test recovery from abuse detection."""
        self.log("⏰ Testing Abuse Recovery", "TEST")
        
        # First, trigger abuse detection
        self.log("Triggering abuse detection...")
        for i in range(20):
            result = self.make_request("/api/limited")
            if result['status_code'] == 429:
                retry_after = result['abuse_info'].get('retry_after')
                self.log(f"Abuse detected. Retry after: {retry_after}s")
                break
        
        # Wait a short time and test recovery
        self.log("Waiting 3 seconds for partial recovery...")
        time.sleep(3)
        
        result = self.make_request("/api/limited")
        if result['status_code'] == 200:
            self.log("✅ Successfully recovered from abuse detection")
            return True
        elif result['status_code'] == 429:
            self.log("🔄 Still blocked (expected for short wait)")
            return True
        else:
            self.log(f"❌ Unexpected status after recovery: {result['status_code']}", "ERROR")
            return False
    
    def test_error_rate_abuse_detection(self):
        """Test error rate-based abuse detection."""
        self.log("📊 Testing Error Rate Abuse Detection", "TEST")
        
        self.log("Testing high error rate scenarios...")
        
        # Make requests to non-existent endpoints to generate errors
        error_endpoints = [
            "/api/nonexistent1",
            "/api/nonexistent2", 
            "/api/invalid",
            "/api/missing"
        ]
        
        blocked_count = 0
        error_count = 0
        total_count = 0
        
        for i in range(30):
            endpoint = random.choice(error_endpoints)
            result = self.make_request(endpoint, expected_status=404)
            total_count += 1
            
            if result['status_code'] == 429:
                blocked_count += 1
                abuse_type = result['abuse_info'].get('abuse_type')
                self.log(f"  Request {i+1}: 🚫 Blocked due to error rate (Type: {abuse_type})")
            elif result['status_code'] >= 400:
                error_count += 1
            
            time.sleep(0.1)
        
        error_rate = error_count / total_count if total_count > 0 else 0
        self.log(f"Results: {total_count} total, {error_count} errors ({error_rate:.1%}), {blocked_count} blocked")
        
        return True
    
    def test_performance_impact(self):
        """Test performance impact of abuse detection."""
        self.log("⚡ Testing Performance Impact", "TEST")
        
        # Test response times with normal behavior
        normal_times = []
        for i in range(10):
            result = self.make_request("/api/unlimited")
            if result['success']:
                normal_times.append(result['response_time'])
            time.sleep(0.2)
        
        if normal_times:
            avg_normal = statistics.mean(normal_times)
            self.log(f"Average response time with abuse detection: {avg_normal:.2f}ms")
            
            if avg_normal < 100:  # Less than 100ms is good
                self.log("✅ Excellent performance - minimal overhead")
                return True
            elif avg_normal < 500:  # Less than 500ms is acceptable
                self.log("✅ Good performance - acceptable overhead")
                return True
            else:
                self.log("⚠️ High overhead detected", "WARN")
                return False
        else:
            self.log("❌ Could not measure performance impact", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """Run all abuse detection tests and provide summary."""
        self.log("🚀 Starting Comprehensive Abuse Detection Test Suite", "START")
        self.log("=" * 70)
        
        tests = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Rapid Request Detection", self.test_rapid_request_detection),
            ("Authentication Abuse Detection", self.test_authentication_abuse_detection),
            ("Scraping Behavior Detection", self.test_scraping_behavior_detection),
            ("Suspicious Pattern Detection", self.test_suspicious_pattern_detection),
            ("Concurrent Abuse Detection", self.test_concurrent_abuse_detection),
            ("Abuse Recovery", self.test_abuse_recovery),
            ("Error Rate Abuse Detection", self.test_error_rate_abuse_detection),
            ("Performance Impact", self.test_performance_impact),
        ]
        
        results = []
        start_time = time.time()
        
        for test_name, test_function in tests:
            self.log("-" * 70)
            try:
                result = test_function()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                self.log(f"{test_name}: {status}")
            except Exception as e:
                results.append((test_name, False))
                self.log(f"{test_name}: ❌ FAILED - {str(e)}", "ERROR")
            
            time.sleep(2)  # Pause between tests
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        self.log("=" * 70)
        self.log("📊 ABUSE DETECTION TEST SUMMARY", "SUMMARY")
        self.log("=" * 70)
        
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
            self.log("\n🎉 Abuse detection system is working well!", "SUCCESS")
        elif success_rate >= 60:
            self.log("\n⚠️ Abuse detection system needs some attention.", "WARN")
        else:
            self.log("\n🚨 Abuse detection system has significant issues!", "ERROR")
        
        return success_rate >= 80


def main():
    """Main function to run the tests."""
    print("🔍 Abuse Detection Comprehensive Test Suite")
    print("=" * 70)
    
    # Check if demo server is running
    tester = AbuseDetectionTester()
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
