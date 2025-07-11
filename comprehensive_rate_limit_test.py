#!/usr/bin/env python3
"""
Comprehensive Rate Limiting Test Suite for NextProperty AI
Tests all aspects of rate limiting functionality across the entire application.

This script combines and enhances all individual rate limiting tests to provide:
- Complete endpoint coverage
- Performance analysis
- Concurrent load testing
- Header validation
- CLI command testing
- Real-world scenario simulation
"""

import requests
import time
import json
import sys
import subprocess
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import statistics
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


class ComprehensiveRateLimitTester:
    """Comprehensive rate limiting test suite for NextProperty AI."""
    
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'test_results': [],
            'performance_metrics': {},
            'rate_limit_stats': {},
            'error_log': []
        }
        self.lock = Lock()
        
    def log(self, message, level="INFO", category="GENERAL"):
        """Enhanced logging with categorization."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARN": "⚠️",
            "ERROR": "❌",
            "TEST": "🧪",
            "PERFORMANCE": "📊",
            "SUMMARY": "📋"
        }.get(level, "•")
        
        print(f"[{timestamp}] {prefix} [{category}] {message}")
        
        if level in ["ERROR", "WARN"]:
            with self.lock:
                self.results['error_log'].append({
                    'timestamp': timestamp,
                    'level': level,
                    'category': category,
                    'message': message
                })
    
    def make_request(self, endpoint, method="GET", data=None, headers=None, timeout=10):
        """Enhanced request method with detailed metrics."""
        url = f"{self.base_url}{endpoint}"
        request_headers = headers or {}
        
        try:
            start_time = time.time()
            
            if method.upper() == "POST":
                response = self.session.post(
                    url, 
                    json=data, 
                    headers={**request_headers, 'Content-Type': 'application/json'},
                    timeout=timeout
                )
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=request_headers, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers, timeout=timeout)
            else:
                response = self.session.get(url, headers=request_headers, timeout=timeout)
                
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            # Extract all relevant headers
            rate_limit_headers = {
                'limit': response.headers.get('X-RateLimit-Limit'),
                'remaining': response.headers.get('X-RateLimit-Remaining'),
                'reset': response.headers.get('X-RateLimit-Reset'),
                'retry_after': response.headers.get('Retry-After'),
                'window': response.headers.get('X-RateLimit-Window'),
                'burst_limit': response.headers.get('X-RateLimit-Burst'),
                'rate_limit_type': response.headers.get('X-RateLimit-Type')
            }
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'rate_limit_headers': rate_limit_headers,
                'headers': dict(response.headers),
                'success': 200 <= response.status_code < 300,
                'rate_limited': response.status_code == 429,
                'url': url,
                'method': method,
                'timestamp': datetime.now().isoformat(),
                'content_length': len(response.content) if response.content else 0
            }
        except requests.exceptions.Timeout:
            return {
                'status_code': 0,
                'response_time': timeout * 1000,
                'rate_limit_headers': {},
                'headers': {},
                'success': False,
                'rate_limited': False,
                'error': 'Request timeout',
                'url': url,
                'method': method,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status_code': 0,
                'response_time': 0,
                'rate_limit_headers': {},
                'headers': {},
                'success': False,
                'rate_limited': False,
                'error': str(e),
                'url': url,
                'method': method,
                'timestamp': datetime.now().isoformat()
            }
    
    def test_application_health(self):
        """Test if the NextProperty AI application is running and healthy."""
        self.log("Testing Application Health", "TEST", "HEALTH")
        
        health_endpoints = [
            "/api/health",
            "/health", 
            "/",
            "/api/status"
        ]
        
        healthy_endpoints = []
        
        for endpoint in health_endpoints:
            result = self.make_request(endpoint)
            if result['success']:
                healthy_endpoints.append(endpoint)
                self.log(f"✅ {endpoint}: Healthy ({result['response_time']:.2f}ms)", "SUCCESS", "HEALTH")
            else:
                self.log(f"❌ {endpoint}: Unhealthy (Status: {result['status_code']})", "ERROR", "HEALTH")
        
        if not healthy_endpoints:
            self.log("Application is not responding to any health checks", "ERROR", "HEALTH")
            return False
        
        self.log(f"Application is healthy ({len(healthy_endpoints)}/{len(health_endpoints)} endpoints responding)", "SUCCESS", "HEALTH")
        return True
    
    def test_rate_limit_headers(self):
        """Comprehensive test of rate limit headers across all endpoints."""
        self.log("Testing Rate Limit Headers", "TEST", "HEADERS")
        
        test_endpoints = [
            "/",
            "/api/health",
            "/api/properties",
            "/api/statistics",
            "/properties",
            "/dashboard",
            "/about",
            "/login"
        ]
        
        header_results = {}
        
        for endpoint in test_endpoints:
            result = self.make_request(endpoint)
            headers = result['rate_limit_headers']
            
            # Count non-empty headers
            present_headers = {k: v for k, v in headers.items() if v is not None}
            header_results[endpoint] = {
                'present_count': len(present_headers),
                'headers': present_headers,
                'status': result['status_code']
            }
            
            if present_headers:
                self.log(f"✅ {endpoint}: {len(present_headers)} rate limit headers found", "SUCCESS", "HEADERS")
                for key, value in present_headers.items():
                    self.log(f"   {key}: {value}", "INFO", "HEADERS")
            else:
                self.log(f"⚠️ {endpoint}: No rate limit headers found", "WARN", "HEADERS")
        
        # Summary
        total_endpoints = len(test_endpoints)
        endpoints_with_headers = sum(1 for r in header_results.values() if r['present_count'] > 0)
        
        self.log(f"Headers summary: {endpoints_with_headers}/{total_endpoints} endpoints have rate limit headers", "SUMMARY", "HEADERS")
        
        with self.lock:
            self.results['rate_limit_stats']['header_coverage'] = header_results
        
        return endpoints_with_headers > 0
    
    def test_web_routes(self):
        """Test rate limiting on main web routes."""
        self.log("Testing Web Routes", "TEST", "WEB")
        
        web_routes = [
            ("/", "Home Page"),
            ("/properties", "Properties Listing"),
            ("/dashboard", "Dashboard"),
            ("/about", "About Page"),
            ("/contact", "Contact Page"),
            ("/login", "Login Page"),
            ("/register", "Register Page")
        ]
        
        results = []
        
        for route, description in web_routes:
            self.log(f"Testing {description}: {route}", "INFO", "WEB")
            
            # Test multiple requests to check rate limiting
            route_results = []
            for i in range(5):
                result = self.make_request(route)
                route_results.append(result)
                
                if result['success']:
                    self.log(f"  Request {i+1}: ✅ Success ({result['response_time']:.2f}ms)", "SUCCESS", "WEB")
                elif result['rate_limited']:
                    self.log(f"  Request {i+1}: 🚫 Rate Limited", "WARN", "WEB")
                    break
                else:
                    self.log(f"  Request {i+1}: Status {result['status_code']}", "WARN", "WEB")
                
                time.sleep(0.1)
            
            success_count = sum(1 for r in route_results if r['success'])
            rate_limited_count = sum(1 for r in route_results if r['rate_limited'])
            
            results.append({
                'route': route,
                'description': description,
                'success_count': success_count,
                'rate_limited_count': rate_limited_count,
                'total_requests': len(route_results)
            })
            
            self.log(f"  Results: {success_count} success, {rate_limited_count} rate limited", "SUMMARY", "WEB")
        
        with self.lock:
            self.results['test_results'].append({
                'test_name': 'web_routes',
                'results': results
            })
        
        return True
    
    def test_api_endpoints(self):
        """Test rate limiting on API endpoints."""
        self.log("Testing API Endpoints", "TEST", "API")
        
        api_endpoints = [
            ("/api/health", "GET", "Health Check"),
            ("/api/properties", "GET", "Properties List"),
            ("/api/statistics", "GET", "Statistics"),
            ("/api/search", "GET", "Search"),
            ("/api/agents", "GET", "Agents List"),
            ("/api/cities", "GET", "Cities List"),
            ("/api/market-data", "GET", "Market Data")
        ]
        
        results = []
        
        for endpoint, method, description in api_endpoints:
            self.log(f"Testing {description}: {method} {endpoint}", "INFO", "API")
            
            # Test burst requests
            endpoint_results = []
            for i in range(8):
                result = self.make_request(endpoint, method)
                endpoint_results.append(result)
                
                if result['success']:
                    remaining = result['rate_limit_headers'].get('remaining', 'N/A')
                    self.log(f"  Request {i+1}: ✅ Success (Remaining: {remaining})", "SUCCESS", "API")
                elif result['rate_limited']:
                    retry_after = result['rate_limit_headers'].get('retry_after', 'N/A')
                    self.log(f"  Request {i+1}: 🚫 Rate Limited (Retry After: {retry_after}s)", "WARN", "API")
                    break
                else:
                    self.log(f"  Request {i+1}: Status {result['status_code']}", "WARN", "API")
                
                time.sleep(0.05)  # Very short delay for burst testing
            
            success_count = sum(1 for r in endpoint_results if r['success'])
            rate_limited_count = sum(1 for r in endpoint_results if r['rate_limited'])
            avg_response_time = statistics.mean([r['response_time'] for r in endpoint_results if r['response_time'] > 0])
            
            results.append({
                'endpoint': endpoint,
                'method': method,
                'description': description,
                'success_count': success_count,
                'rate_limited_count': rate_limited_count,
                'avg_response_time': avg_response_time,
                'total_requests': len(endpoint_results)
            })
            
            self.log(f"  Results: {success_count} success, {rate_limited_count} rate limited, {avg_response_time:.2f}ms avg", "SUMMARY", "API")
        
        with self.lock:
            self.results['test_results'].append({
                'test_name': 'api_endpoints',
                'results': results
            })
        
        return True
    
    def test_ml_prediction_endpoints(self):
        """Test rate limiting on ML prediction endpoints."""
        self.log("Testing ML Prediction Endpoints", "TEST", "ML")
        
        # Sample property data for predictions
        property_data = {
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1500,
            "property_type": "Detached",
            "city": "Toronto",
            "province": "ON",
            "postal_code": "M5V",
            "year_built": 2010,
            "garage": 1,
            "basement": True
        }
        
        ml_endpoints = [
            ("/api/property-prediction", "POST", property_data, "Property Price Prediction"),
            ("/api/market-analysis", "POST", {"city": "Toronto", "property_type": "Condo"}, "Market Analysis"),
            ("/predict-price", "POST", property_data, "Price Prediction (Legacy)"),
            ("/api/valuation", "POST", property_data, "Property Valuation")
        ]
        
        results = []
        
        for endpoint, method, data, description in ml_endpoints:
            self.log(f"Testing {description}: {method} {endpoint}", "INFO", "ML")
            
            # Test ML prediction requests (typically more expensive)
            ml_results = []
            for i in range(3):
                result = self.make_request(endpoint, method, data)
                ml_results.append(result)
                
                if result['success']:
                    self.log(f"  Prediction {i+1}: ✅ Success ({result['response_time']:.2f}ms)", "SUCCESS", "ML")
                elif result['rate_limited']:
                    self.log(f"  Prediction {i+1}: 🚫 Rate Limited", "WARN", "ML")
                    break
                elif result['status_code'] == 404:
                    self.log(f"  Prediction {i+1}: Endpoint not available", "INFO", "ML")
                    break
                else:
                    self.log(f"  Prediction {i+1}: Status {result['status_code']}", "WARN", "ML")
                
                time.sleep(1)  # Longer delay for ML endpoints
            
            success_count = sum(1 for r in ml_results if r['success'])
            rate_limited_count = sum(1 for r in ml_results if r['rate_limited'])
            
            if ml_results:
                avg_response_time = statistics.mean([r['response_time'] for r in ml_results if r['response_time'] > 0])
            else:
                avg_response_time = 0
                
            results.append({
                'endpoint': endpoint,
                'description': description,
                'success_count': success_count,
                'rate_limited_count': rate_limited_count,
                'avg_response_time': avg_response_time,
                'total_requests': len(ml_results)
            })
            
            self.log(f"  Results: {success_count} success, {rate_limited_count} rate limited", "SUMMARY", "ML")
        
        with self.lock:
            self.results['test_results'].append({
                'test_name': 'ml_prediction_endpoints',
                'results': results
            })
        
        return True
    
    def test_search_functionality(self):
        """Test rate limiting on search endpoints."""
        self.log("Testing Search Functionality", "TEST", "SEARCH")
        
        search_tests = [
            ("/api/search?q=toronto", "Text Search"),
            ("/api/search?q=condo&city=Toronto", "Filtered Text Search"),
            ("/api/search/geospatial?lat=43.7532&lng=-79.3832&radius=10", "Geospatial Search"),
            ("/api/properties?city=Toronto&per_page=5", "Property Search"),
            ("/api/properties?min_price=500000&max_price=1000000", "Price Range Search"),
            ("/api/properties?bedrooms=3&bathrooms=2", "Feature Search")
        ]
        
        results = []
        
        for endpoint, description in search_tests:
            self.log(f"Testing {description}: {endpoint}", "INFO", "SEARCH")
            
            # Test search burst
            search_results = []
            for i in range(4):
                result = self.make_request(endpoint)
                search_results.append(result)
                
                if result['success']:
                    self.log(f"  Search {i+1}: ✅ Success ({result['response_time']:.2f}ms)", "SUCCESS", "SEARCH")
                elif result['rate_limited']:
                    self.log(f"  Search {i+1}: 🚫 Rate Limited", "WARN", "SEARCH")
                    break
                else:
                    self.log(f"  Search {i+1}: Status {result['status_code']}", "WARN", "SEARCH")
                
                time.sleep(0.2)
            
            success_count = sum(1 for r in search_results if r['success'])
            rate_limited_count = sum(1 for r in search_results if r['rate_limited'])
            
            results.append({
                'endpoint': endpoint,
                'description': description,
                'success_count': success_count,
                'rate_limited_count': rate_limited_count,
                'total_requests': len(search_results)
            })
            
            self.log(f"  Results: {success_count} success, {rate_limited_count} rate limited", "SUMMARY", "SEARCH")
        
        with self.lock:
            self.results['test_results'].append({
                'test_name': 'search_functionality',
                'results': results
            })
        
        return True
    
    def test_concurrent_load(self):
        """Test rate limiting under concurrent load."""
        self.log("Testing Concurrent Load", "TEST", "CONCURRENT")
        
        def make_concurrent_request(endpoint, thread_id):
            """Make a request from a specific thread."""
            result = self.make_request(endpoint)
            result['thread_id'] = thread_id
            return result
        
        # Test different concurrency levels
        concurrency_tests = [
            ("/api/health", 10, "Low Concurrency Health Check"),
            ("/api/properties", 20, "Medium Concurrency Properties"),
            ("/", 30, "High Concurrency Home Page")
        ]
        
        concurrent_results = []
        
        for endpoint, worker_count, description in concurrency_tests:
            self.log(f"Testing {description}: {worker_count} concurrent requests to {endpoint}", "INFO", "CONCURRENT")
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                futures = [
                    executor.submit(make_concurrent_request, endpoint, i) 
                    for i in range(worker_count)
                ]
                results = []
                
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=30)
                        results.append(result)
                    except Exception as e:
                        self.log(f"Concurrent request failed: {e}", "ERROR", "CONCURRENT")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            success_count = sum(1 for r in results if r['success'])
            rate_limited_count = sum(1 for r in results if r['rate_limited'])
            error_count = sum(1 for r in results if not r['success'] and not r['rate_limited'])
            
            if results:
                avg_response_time = statistics.mean([r['response_time'] for r in results if r['response_time'] > 0])
                min_response_time = min([r['response_time'] for r in results if r['response_time'] > 0], default=0)
                max_response_time = max([r['response_time'] for r in results if r['response_time'] > 0], default=0)
            else:
                avg_response_time = min_response_time = max_response_time = 0
            
            concurrent_result = {
                'endpoint': endpoint,
                'description': description,
                'worker_count': worker_count,
                'total_time': total_time,
                'success_count': success_count,
                'rate_limited_count': rate_limited_count,
                'error_count': error_count,
                'avg_response_time': avg_response_time,
                'min_response_time': min_response_time,
                'max_response_time': max_response_time,
                'throughput': len(results) / total_time if total_time > 0 else 0
            }
            
            concurrent_results.append(concurrent_result)
            
            self.log(f"  Completed in {total_time:.2f}s", "PERFORMANCE", "CONCURRENT")
            self.log(f"  Success: {success_count}, Rate Limited: {rate_limited_count}, Errors: {error_count}", "SUMMARY", "CONCURRENT")
            self.log(f"  Avg Response: {avg_response_time:.2f}ms, Throughput: {concurrent_result['throughput']:.2f} req/s", "PERFORMANCE", "CONCURRENT")
        
        with self.lock:
            self.results['test_results'].append({
                'test_name': 'concurrent_load',
                'results': concurrent_results
            })
            self.results['performance_metrics']['concurrent_load'] = concurrent_results
        
        return True
    
    def test_cli_commands(self):
        """Test rate limiting CLI commands."""
        self.log("Testing CLI Commands", "TEST", "CLI")
        
        cli_commands = [
            "flask rate-limit health",
            "flask rate-limit status", 
            "flask rate-limit clear",
            "flask rate-limit stats"
        ]
        
        cli_results = []
        
        for command in cli_commands:
            self.log(f"Testing CLI: {command}", "INFO", "CLI")
            
            try:
                start_time = time.time()
                result = subprocess.run(
                    command.split(), 
                    capture_output=True, 
                    text=True, 
                    timeout=30,
                    cwd="/Users/efeobukohwo/Desktop/Nextproperty Real Estate"
                )
                end_time = time.time()
                
                execution_time = end_time - start_time
                
                if result.returncode == 0:
                    self.log(f"  ✅ Command executed successfully ({execution_time:.2f}s)", "SUCCESS", "CLI")
                    if result.stdout.strip():
                        output_preview = result.stdout[:200].replace('\n', ' ')
                        self.log(f"  Output: {output_preview}...", "INFO", "CLI")
                else:
                    self.log(f"  ❌ Command failed: {result.stderr}", "ERROR", "CLI")
                
                cli_results.append({
                    'command': command,
                    'returncode': result.returncode,
                    'execution_time': execution_time,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'success': result.returncode == 0
                })
                
            except subprocess.TimeoutExpired:
                self.log(f"  ⏰ Command timed out", "ERROR", "CLI")
                cli_results.append({
                    'command': command,
                    'returncode': -1,
                    'execution_time': 30,
                    'error': 'Timeout',
                    'success': False
                })
            except Exception as e:
                self.log(f"  ❌ Command error: {e}", "ERROR", "CLI")
                cli_results.append({
                    'command': command,
                    'returncode': -1,
                    'execution_time': 0,
                    'error': str(e),
                    'success': False
                })
        
        successful_commands = sum(1 for r in cli_results if r['success'])
        self.log(f"CLI Results: {successful_commands}/{len(cli_commands)} commands successful", "SUMMARY", "CLI")
        
        with self.lock:
            self.results['test_results'].append({
                'test_name': 'cli_commands',
                'results': cli_results
            })
        
        return successful_commands > 0
    
    def test_sustained_load(self):
        """Test rate limiting under sustained load over time."""
        self.log("Testing Sustained Load (30 seconds)", "TEST", "SUSTAINED")
        
        endpoint = "/api/health"
        duration = 30  # seconds
        request_interval = 0.5  # seconds between requests
        
        start_time = time.time()
        sustained_results = []
        request_count = 0
        
        while time.time() - start_time < duration:
            result = self.make_request(endpoint)
            result['elapsed_time'] = time.time() - start_time
            result['request_number'] = request_count + 1
            sustained_results.append(result)
            request_count += 1
            
            if result['success']:
                remaining = result['rate_limit_headers'].get('remaining', 'N/A')
                if request_count % 10 == 0:  # Log every 10th request
                    self.log(f"  Request {request_count}: ✅ Success (Remaining: {remaining})", "INFO", "SUSTAINED")
            elif result['rate_limited']:
                self.log(f"  Request {request_count}: 🚫 Rate Limited", "WARN", "SUSTAINED")
            
            time.sleep(request_interval)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Analyze sustained load results
        success_count = sum(1 for r in sustained_results if r['success'])
        rate_limited_count = sum(1 for r in sustained_results if r['rate_limited'])
        total_requests = len(sustained_results)
        success_rate = (success_count / total_requests) * 100 if total_requests > 0 else 0
        avg_response_time = statistics.mean([r['response_time'] for r in sustained_results if r['response_time'] > 0])
        
        sustained_summary = {
            'duration': actual_duration,
            'total_requests': total_requests,
            'success_count': success_count,
            'rate_limited_count': rate_limited_count,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'requests_per_second': total_requests / actual_duration
        }
        
        self.log(f"Sustained Load Results:", "SUMMARY", "SUSTAINED")
        self.log(f"  Duration: {actual_duration:.2f}s, Total Requests: {total_requests}", "PERFORMANCE", "SUSTAINED")
        self.log(f"  Success Rate: {success_rate:.1f}%, Avg Response: {avg_response_time:.2f}ms", "PERFORMANCE", "SUSTAINED")
        self.log(f"  Rate Limited: {rate_limited_count}, RPS: {sustained_summary['requests_per_second']:.2f}", "PERFORMANCE", "SUSTAINED")
        
        with self.lock:
            self.results['test_results'].append({
                'test_name': 'sustained_load',
                'results': sustained_summary
            })
            self.results['performance_metrics']['sustained_load'] = sustained_summary
        
        return True
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive test report."""
        self.log("Generating Comprehensive Report", "SUMMARY", "REPORT")
        
        print("\n" + "=" * 80)
        print("🏠 NEXTPROPERTY AI - COMPREHENSIVE RATE LIMITING TEST REPORT")
        print("=" * 80)
        
        # Test execution summary
        total_tests = len(self.results['test_results'])
        print(f"\n📊 EXECUTION SUMMARY")
        print(f"   Total Test Suites: {total_tests}")
        print(f"   Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Individual test results
        print(f"\n🧪 DETAILED TEST RESULTS")
        print("-" * 50)
        
        for test_result in self.results['test_results']:
            test_name = test_result['test_name'].replace('_', ' ').title()
            print(f"\n{test_name}:")
            
            if test_name == "Web Routes":
                for result in test_result['results']:
                    status = "✅" if result['success_count'] > 0 else "❌"
                    print(f"   {status} {result['route']}: {result['success_count']}/{result['total_requests']} successful")
            
            elif test_name == "Api Endpoints":
                for result in test_result['results']:
                    status = "✅" if result['success_count'] > 0 else "❌"
                    print(f"   {status} {result['endpoint']}: {result['success_count']}/{result['total_requests']} successful ({result['avg_response_time']:.2f}ms avg)")
            
            elif test_name == "Concurrent Load":
                for result in test_result['results']:
                    print(f"   📊 {result['description']}: {result['success_count']}/{result['worker_count']} successful")
                    print(f"      Throughput: {result['throughput']:.2f} req/s, Avg Response: {result['avg_response_time']:.2f}ms")
            
            elif test_name == "Cli Commands":
                successful = sum(1 for r in test_result['results'] if r['success'])
                total = len(test_result['results'])
                print(f"   ⚙️ CLI Commands: {successful}/{total} successful")
        
        # Performance metrics
        if 'performance_metrics' in self.results and self.results['performance_metrics']:
            print(f"\n⚡ PERFORMANCE METRICS")
            print("-" * 30)
            
            if 'sustained_load' in self.results['performance_metrics']:
                sustained = self.results['performance_metrics']['sustained_load']
                print(f"   Sustained Load Test:")
                print(f"   • Success Rate: {sustained['success_rate']:.1f}%")
                print(f"   • Average Response Time: {sustained['avg_response_time']:.2f}ms")
                print(f"   • Requests per Second: {sustained['requests_per_second']:.2f}")
            
            if 'concurrent_load' in self.results['performance_metrics']:
                concurrent = self.results['performance_metrics']['concurrent_load']
                print(f"   Concurrent Load Tests:")
                for test in concurrent:
                    print(f"   • {test['description']}: {test['throughput']:.2f} req/s")
        
        # Rate limiting effectiveness
        print(f"\n🛡️ RATE LIMITING EFFECTIVENESS")
        print("-" * 40)
        
        if 'rate_limit_stats' in self.results and 'header_coverage' in self.results['rate_limit_stats']:
            header_stats = self.results['rate_limit_stats']['header_coverage']
            endpoints_with_headers = sum(1 for stats in header_stats.values() if stats['present_count'] > 0)
            total_endpoints = len(header_stats)
            header_coverage = (endpoints_with_headers / total_endpoints) * 100 if total_endpoints > 0 else 0
            
            print(f"   Header Coverage: {endpoints_with_headers}/{total_endpoints} endpoints ({header_coverage:.1f}%)")
        
        # Count rate limited requests across all tests
        total_rate_limited = 0
        total_requests = 0
        
        for test_result in self.results['test_results']:
            if isinstance(test_result['results'], list):
                for result in test_result['results']:
                    if isinstance(result, dict):
                        if 'rate_limited_count' in result:
                            total_rate_limited += result.get('rate_limited_count', 0)
                            total_requests += result.get('total_requests', 0)
        
        if total_requests > 0:
            rate_limit_effectiveness = (total_rate_limited / total_requests) * 100
            print(f"   Rate Limiting Triggered: {total_rate_limited}/{total_requests} requests ({rate_limit_effectiveness:.1f}%)")
        
        # Error summary
        if self.results['error_log']:
            print(f"\n⚠️ ERRORS AND WARNINGS")
            print("-" * 25)
            error_count = sum(1 for log in self.results['error_log'] if log['level'] == 'ERROR')
            warn_count = sum(1 for log in self.results['error_log'] if log['level'] == 'WARN')
            print(f"   Errors: {error_count}, Warnings: {warn_count}")
            
            # Show recent errors
            recent_errors = [log for log in self.results['error_log'] if log['level'] == 'ERROR'][-5:]
            for error in recent_errors:
                print(f"   ❌ [{error['category']}] {error['message']}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT")
        print("-" * 22)
        
        # Calculate overall success rate
        all_successful_tests = 0
        all_total_tests = 0
        
        for test_result in self.results['test_results']:
            if test_result['test_name'] in ['web_routes', 'api_endpoints', 'ml_prediction_endpoints', 'search_functionality']:
                for result in test_result['results']:
                    all_successful_tests += 1 if result.get('success_count', 0) > 0 else 0
                    all_total_tests += 1
        
        if all_total_tests > 0:
            overall_success_rate = (all_successful_tests / all_total_tests) * 100
            print(f"   Overall Success Rate: {overall_success_rate:.1f}%")
            
            if overall_success_rate >= 90:
                print("   🏆 EXCELLENT: Rate limiting system is performing excellently!")
            elif overall_success_rate >= 75:
                print("   ✅ GOOD: Rate limiting system is working well!")
            elif overall_success_rate >= 50:
                print("   ⚠️ FAIR: Rate limiting system needs attention!")
            else:
                print("   🚨 POOR: Rate limiting system has significant issues!")
        
        print("\n" + "=" * 80)
        print("📋 Test completed successfully! Check the detailed logs above for specific findings.")
        print("=" * 80)
        
        return True
    
    def run_comprehensive_tests(self):
        """Run all comprehensive rate limiting tests."""
        start_time = time.time()
        
        print("🚀 STARTING COMPREHENSIVE RATE LIMITING TEST SUITE")
        print("=" * 60)
        print(f"Target Application: {self.base_url}")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check application health first
        if not self.test_application_health():
            self.log("Application health check failed. Cannot proceed with tests.", "ERROR", "HEALTH")
            return False
        
        # Define test sequence
        test_sequence = [
            ("Rate Limit Headers", self.test_rate_limit_headers),
            ("Web Routes", self.test_web_routes),
            ("API Endpoints", self.test_api_endpoints),
            ("ML Prediction Endpoints", self.test_ml_prediction_endpoints),
            ("Search Functionality", self.test_search_functionality),
            ("Concurrent Load", self.test_concurrent_load),
            ("CLI Commands", self.test_cli_commands),
            ("Sustained Load", self.test_sustained_load)
        ]
        
        successful_tests = 0
        failed_tests = 0
        
        # Execute test sequence
        for test_name, test_function in test_sequence:
            self.log("-" * 60, "INFO", "SEPARATOR")
            try:
                result = test_function()
                if result:
                    successful_tests += 1
                    self.log(f"✅ {test_name}: PASSED", "SUCCESS", "TEST_RESULT")
                else:
                    failed_tests += 1
                    self.log(f"❌ {test_name}: FAILED", "ERROR", "TEST_RESULT")
            except Exception as e:
                failed_tests += 1
                self.log(f"❌ {test_name}: FAILED with exception: {str(e)}", "ERROR", "TEST_RESULT")
            
            # Short pause between tests
            time.sleep(1)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Test execution summary
        self.log("-" * 60, "INFO", "SEPARATOR")
        self.log(f"TEST EXECUTION COMPLETED", "SUMMARY", "FINAL")
        self.log(f"Duration: {total_duration:.2f} seconds", "SUMMARY", "FINAL")
        self.log(f"Successful Tests: {successful_tests}", "SUMMARY", "FINAL")
        self.log(f"Failed Tests: {failed_tests}", "SUMMARY", "FINAL")
        self.log(f"Success Rate: {(successful_tests / len(test_sequence)) * 100:.1f}%", "SUMMARY", "FINAL")
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
        
        return successful_tests > failed_tests


def main():
    """Main function to run the comprehensive rate limiting tests."""
    print("🏠 NextProperty AI - Comprehensive Rate Limiting Test Suite")
    print("=" * 70)
    print("This script will test all aspects of rate limiting functionality.")
    print("Ensure the NextProperty AI application is running on localhost:5007")
    print()
    
    # Initialize tester
    tester = ComprehensiveRateLimitTester()
    
    # Run comprehensive tests
    success = tester.run_comprehensive_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
