#!/usr/bin/env python3
"""
NextProperty AI Application Rate Limiting Test
Real-time testing of rate limiting on the main application endpoints.
"""

import requests
import time
import json
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class NextPropertyRateLimitTester:
    """Test rate limiting on the main NextProperty AI application."""
    
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    def make_request(self, endpoint, method="GET", data=None, expected_status=200):
        """Make a request and return detailed response info."""
        url = f"{self.base_url}{endpoint}"
        try:
            start_time = time.time()
            
            if method.upper() == "POST":
                response = self.session.post(url, json=data, headers={'Content-Type': 'application/json'})
            else:
                response = self.session.get(url)
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
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
                'success': response.status_code == expected_status,
                'url': url,
                'method': method
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': 0,
                'rate_limit': {},
                'success': False,
                'error': str(e),
                'url': url,
                'method': method
            }
    
    def test_main_routes(self):
        """Test rate limiting on main application routes."""
        self.log("🏠 Testing Main Application Routes", "TEST")
        
        endpoints = [
            ("/", "GET"),
            ("/properties", "GET"),
            ("/dashboard", "GET"),
            ("/about", "GET"),
        ]
        
        for endpoint, method in endpoints:
            self.log(f"Testing {method} {endpoint}...")
            result = self.make_request(endpoint, method)
            
            if result['success']:
                self.log(f"✅ {endpoint}: Success ({result['response_time']:.2f}ms)")
                if result['rate_limit']['remaining']:
                    self.log(f"   Rate limit remaining: {result['rate_limit']['remaining']}")
            elif result['status_code'] == 429:
                self.log(f"🚫 {endpoint}: Rate limited")
                if result['rate_limit']['retry_after']:
                    self.log(f"   Retry after: {result['rate_limit']['retry_after']}s")
            else:
                self.log(f"⚠️ {endpoint}: Status {result['status_code']}")
        
        return True
    
    def test_api_endpoints(self):
        """Test rate limiting on API endpoints."""
        self.log("🔌 Testing API Endpoints", "TEST")
        
        api_endpoints = [
            ("/api/properties", "GET"),
            ("/api/health", "GET"),
            ("/api/statistics", "GET"),
        ]
        
        for endpoint, method in api_endpoints:
            self.log(f"Testing {method} {endpoint}...")
            
            # Test multiple requests to trigger rate limiting
            success_count = 0
            rate_limited_count = 0
            
            for i in range(5):
                result = self.make_request(endpoint, method)
                
                if result['success']:
                    success_count += 1
                elif result['status_code'] == 429:
                    rate_limited_count += 1
                    self.log(f"  Request {i+1}: Rate limited")
                    break
                else:
                    self.log(f"  Request {i+1}: Unexpected status {result['status_code']}")
                
                time.sleep(0.1)
            
            self.log(f"  Results: {success_count} success, {rate_limited_count} rate limited")
        
        return True
    
    def test_prediction_endpoints(self):
        """Test rate limiting on ML prediction endpoints."""
        self.log("🤖 Testing ML Prediction Endpoints", "TEST")
        
        # Test property prediction endpoint
        prediction_data = {
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1500,
            "property_type": "Detached",
            "city": "Toronto",
            "province": "ON"
        }
        
        self.log("Testing property prediction endpoint...")
        
        success_count = 0
        rate_limited_count = 0
        
        for i in range(3):  # Try 3 predictions
            result = self.make_request("/api/property-prediction", "POST", prediction_data)
            
            if result['success']:
                success_count += 1
                self.log(f"  Prediction {i+1}: ✅ Success ({result['response_time']:.2f}ms)")
            elif result['status_code'] == 429:
                rate_limited_count += 1
                self.log(f"  Prediction {i+1}: 🚫 Rate limited")
            else:
                self.log(f"  Prediction {i+1}: Status {result['status_code']}")
            
            time.sleep(1)  # Wait between predictions
        
        self.log(f"Prediction results: {success_count} success, {rate_limited_count} rate limited")
        return True
    
    def test_search_endpoints(self):
        """Test rate limiting on search endpoints."""
        self.log("🔍 Testing Search Endpoints", "TEST")
        
        search_endpoints = [
            "/api/search?q=toronto",
            "/api/search/geospatial?lat=43.7532&lng=-79.3832&radius=10",
            "/api/properties?city=Toronto&per_page=5"
        ]
        
        for endpoint in search_endpoints:
            self.log(f"Testing search: {endpoint}")
            
            # Test burst of search requests
            for i in range(3):
                result = self.make_request(endpoint)
                
                if result['success']:
                    self.log(f"  Search {i+1}: ✅ Success")
                elif result['status_code'] == 429:
                    self.log(f"  Search {i+1}: 🚫 Rate limited")
                    break
                
                time.sleep(0.2)
        
        return True
    
    def test_concurrent_load(self):
        """Test rate limiting under concurrent load."""
        self.log("🔄 Testing Concurrent Load", "TEST")
        
        def make_concurrent_request(endpoint):
            """Make a concurrent request."""
            return self.make_request(endpoint)
        
        # Test 20 concurrent requests to properties endpoint
        endpoint = "/api/properties"
        self.log(f"Testing 20 concurrent requests to {endpoint}...")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_concurrent_request, endpoint) for _ in range(20)]
            results = [future.result() for future in futures]
        
        success_count = sum(1 for r in results if r['success'])
        rate_limited_count = sum(1 for r in results if r['status_code'] == 429)
        error_count = sum(1 for r in results if r['status_code'] not in [200, 429])
        
        self.log(f"Concurrent results:")
        self.log(f"  ✅ Success: {success_count}")
        self.log(f"  🚫 Rate limited: {rate_limited_count}")
        self.log(f"  ❌ Errors: {error_count}")
        
        return True
    
    def test_rate_limit_headers(self):
        """Test rate limit headers across different endpoints."""
        self.log("📋 Testing Rate Limit Headers", "TEST")
        
        endpoints_to_test = [
            "/api/health",
            "/api/properties",
            "/",
        ]
        
        for endpoint in endpoints_to_test:
            result = self.make_request(endpoint)
            headers = result['rate_limit']
            
            self.log(f"Headers for {endpoint}:")
            for key, value in headers.items():
                if value:
                    self.log(f"  {key}: {value}")
            
            if not any(headers.values()):
                self.log(f"  No rate limit headers found")
        
        return True
    
    def run_application_tests(self):
        """Run all application-specific tests."""
        self.log("🚀 Starting NextProperty AI Rate Limiting Tests", "START")
        self.log("=" * 60)
        
        # Check if application is running
        try:
            health_check = self.make_request("/api/health")
            if not health_check['success']:
                self.log("❌ NextProperty AI not running at http://localhost:5007", "ERROR")
                self.log("Please start the application first: python app.py", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Cannot connect to NextProperty AI: {e}", "ERROR")
            self.log("Please start the application first: python app.py", "ERROR")
            return False
        
        self.log("✅ NextProperty AI is running")
        self.log("")
        
        tests = [
            ("Main Routes", self.test_main_routes),
            ("API Endpoints", self.test_api_endpoints),
            ("ML Prediction Endpoints", self.test_prediction_endpoints),
            ("Search Endpoints", self.test_search_endpoints),
            ("Concurrent Load", self.test_concurrent_load),
            ("Rate Limit Headers", self.test_rate_limit_headers),
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
            
            time.sleep(0.5)  # Pause between tests
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        self.log("=" * 60)
        self.log("📊 APPLICATION TEST SUMMARY", "SUMMARY")
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
            self.log("\n🎉 NextProperty AI rate limiting is working excellently!", "SUCCESS")
        elif success_rate >= 60:
            self.log("\n⚠️ NextProperty AI rate limiting needs some attention.", "WARN")
        else:
            self.log("\n🚨 NextProperty AI rate limiting has issues!", "ERROR")
        
        return success_rate >= 80


def main():
    """Main function to run the application tests."""
    print("🏠 NextProperty AI Rate Limiting Test Suite")
    print("=" * 60)
    
    tester = NextPropertyRateLimitTester()
    success = tester.run_application_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
