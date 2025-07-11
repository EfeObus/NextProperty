#!/usr/bin/env python3
"""
NextProperty AI - Ultimate Rate Limiting Functionality Test Suite
================================================================

This comprehensive test suite combines and enhances all existing rate limiting tests
to provide complete coverage of the NextProperty AI application's rate limiting functionality.

Test Coverage:
- Application Health & Status
- Web Route Rate Limiting
- API Endpoint Rate Limiting
- ML Prediction Rate Limiting
- Search Functionality Rate Limiting
- Authentication Rate Limiting
- Concurrent Load Testing
- Sustained Load Testing
- CLI Command Testing
- Error Handling & Recovery
- Performance Metrics
- Header Validation
- Rate Limit Configuration Testing

Author: NextProperty AI Team
Date: July 11, 2025
"""

import requests
import time
import json
import threading
import subprocess
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter
from datetime import datetime
import sys
import os
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class Colors:
    """ANSI color codes for enhanced terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class UltimateRateLimitTester:
    """
    Ultimate Rate Limiting Test Suite for NextProperty AI
    
    This class provides comprehensive testing of all rate limiting functionality
    including web routes, API endpoints, ML predictions, search, authentication,
    concurrent access, sustained load, CLI commands, and performance metrics.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NextProperty-RateLimit-Tester/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Test results storage
        self.results = {
            'health_checks': [],
            'web_routes': [],
            'api_endpoints': [],
            'ml_predictions': [],
            'search_tests': [],
            'auth_tests': [],
            'concurrent_tests': [],
            'sustained_tests': [],
            'cli_tests': [],
            'header_tests': [],
            'performance_metrics': {},
            'error_summary': defaultdict(int),
            'rate_limit_triggers': 0,
            'total_requests': 0,
            'test_duration': 0
        }
        
        # Test configuration
        self.test_config = {
            'request_timeout': 10,
            'burst_size': 25,
            'concurrent_threads': 30,
            'sustained_duration': 45,
            'rate_limit_expected_codes': [429, 503],
            'success_codes': [200, 201, 202, 302, 304],
            'client_error_codes': [400, 401, 403, 404, 422],
            'server_error_codes': [500, 502, 503, 504]
        }
        
        # Endpoint definitions
        self.endpoints = self._initialize_endpoints()
        
    def _initialize_endpoints(self) -> Dict[str, List[str]]:
        """Initialize all endpoints to be tested"""
        return {
            'health': [
                '/api/health',
                '/health',
                '/api/status',
                '/status',
                '/',
                '/ping'
            ],
            'web_routes': [
                '/',
                '/properties',
                '/dashboard',
                '/about',
                '/contact',
                '/login',
                '/register',
                '/profile',
                '/settings',
                '/map',
                '/favorites',
                '/search'
            ],
            'api_routes': [
                '/api/health',
                '/api/properties',
                '/api/properties/search',
                '/api/statistics',
                '/api/market-data',
                '/api/agents',
                '/api/cities',
                '/api/neighborhoods',
                '/api/property-types',
                '/api/price-ranges',
                '/api/features'
            ],
            'ml_routes': [
                '/api/predict',
                '/api/predict/price',
                '/api/predict/market',
                '/api/predict/valuation',
                '/api/predict/trends',
                '/api/ml/analyze',
                '/api/ml/recommend'
            ],
            'search_routes': [
                '/api/search',
                '/api/search/properties',
                '/api/search/location',
                '/api/search/advanced',
                '/api/search/suggestions',
                '/api/geocode',
                '/api/nearby'
            ],
            'auth_routes': [
                '/api/auth/login',
                '/api/auth/register',
                '/api/auth/logout',
                '/api/auth/refresh',
                '/api/auth/verify',
                '/api/auth/reset-password'
            ]
        }

    def print_header(self, text: str, color: str = Colors.HEADER):
        """Print formatted header"""
        print(f"\n{color}{'=' * 80}")
        print(f"{text.center(80)}")
        print(f"{'=' * 80}{Colors.ENDC}\n")

    def print_status(self, text: str, status: str = "INFO", color: str = Colors.OKBLUE):
        """Print formatted status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] [{status}] {text}{Colors.ENDC}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with comprehensive error handling and metrics collection
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Dictionary containing response data, metrics, and status
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            kwargs.setdefault('timeout', self.test_config['request_timeout'])
            kwargs.setdefault('verify', False)
            
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            # Extract rate limiting headers
            rate_limit_headers = {
                key: value for key, value in response.headers.items()
                if 'rate' in key.lower() or 'limit' in key.lower() or 'retry' in key.lower()
            }
            
            # Track rate limiting
            if response.status_code in self.test_config['rate_limit_expected_codes']:
                self.results['rate_limit_triggers'] += 1
                
            self.results['total_requests'] += 1
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response_time': response_time,
                'headers': dict(response.headers),
                'rate_limit_headers': rate_limit_headers,
                'content_length': len(response.content) if response.content else 0,
                'url': url,
                'method': method,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            self.results['error_summary']['timeout'] += 1
            return {
                'success': False,
                'error': 'timeout',
                'response_time': time.time() - start_time,
                'url': url,
                'method': method,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.ConnectionError:
            self.results['error_summary']['connection'] += 1
            return {
                'success': False,
                'error': 'connection',
                'response_time': time.time() - start_time,
                'url': url,
                'method': method,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.results['error_summary']['other'] += 1
            return {
                'success': False,
                'error': str(e),
                'response_time': time.time() - start_time,
                'url': url,
                'method': method,
                'timestamp': datetime.now().isoformat()
            }

    def test_application_health(self) -> bool:
        """
        Test application health and connectivity
        
        Returns:
            True if application is healthy, False otherwise
        """
        self.print_header("🏥 APPLICATION HEALTH CHECK", Colors.OKGREEN)
        
        health_status = True
        
        for endpoint in self.endpoints['health']:
            self.print_status(f"Testing health endpoint: {endpoint}")
            
            result = self.make_request('GET', endpoint)
            self.results['health_checks'].append(result)
            
            if result['success'] and result['status_code'] in self.test_config['success_codes']:
                self.print_status(f"✅ {endpoint} - OK ({result['status_code']}) - {result['response_time']:.3f}s", "SUCCESS", Colors.OKGREEN)
            else:
                self.print_status(f"❌ {endpoint} - FAILED ({result.get('status_code', 'N/A')}) - {result.get('error', 'Unknown')}", "ERROR", Colors.FAIL)
                health_status = False
                
            time.sleep(0.1)  # Brief pause between requests
            
        return health_status

    def test_rate_limit_headers(self):
        """Test rate limiting header presence and validity"""
        self.print_header("📋 RATE LIMIT HEADERS VALIDATION", Colors.OKCYAN)
        
        expected_headers = [
            'x-ratelimit-limit',
            'x-ratelimit-remaining', 
            'x-ratelimit-reset',
            'retry-after'
        ]
        
        header_coverage = defaultdict(int)
        total_tests = 0
        
        # Test headers across different endpoint types
        test_endpoints = [
            '/api/health',
            '/api/properties', 
            '/api/predict',
            '/',
            '/properties'
        ]
        
        for endpoint in test_endpoints:
            self.print_status(f"Testing headers for: {endpoint}")
            
            result = self.make_request('GET', endpoint)
            total_tests += 1
            
            if result['success']:
                headers = {k.lower(): v for k, v in result['headers'].items()}
                
                for expected_header in expected_headers:
                    if expected_header in headers:
                        header_coverage[expected_header] += 1
                        
                rate_limit_found = len(result['rate_limit_headers'])
                self.print_status(f"Found {rate_limit_found} rate limiting headers", "INFO", Colors.OKBLUE)
                
            self.results['header_tests'].append(result)
            time.sleep(0.1)
            
        # Calculate header coverage percentage
        if total_tests > 0:
            coverage_stats = {}
            for header in expected_headers:
                coverage_pct = (header_coverage[header] / total_tests) * 100
                coverage_stats[header] = coverage_pct
                self.print_status(f"Header '{header}' coverage: {coverage_pct:.1f}%")
                
            self.results['performance_metrics']['header_coverage'] = coverage_stats

    def test_web_routes_rate_limiting(self):
        """Test rate limiting on web routes"""
        self.print_header("🌐 WEB ROUTES RATE LIMITING", Colors.WARNING)
        
        for route in self.endpoints['web_routes']:
            self.print_status(f"Testing web route: {route}")
            
            # Make burst requests to trigger rate limiting
            for i in range(self.test_config['burst_size']):
                result = self.make_request('GET', route)
                self.results['web_routes'].append(result)
                
                if result['success']:
                    status_code = result['status_code']
                    if status_code in self.test_config['rate_limit_expected_codes']:
                        self.print_status(f"🚦 Rate limit triggered on request {i+1} ({status_code})", "RATE_LIMIT", Colors.WARNING)
                        break
                    elif status_code in self.test_config['success_codes']:
                        continue
                    else:
                        self.print_status(f"⚠️ Unexpected status code: {status_code}", "WARNING", Colors.WARNING)
                else:
                    self.print_status(f"❌ Request failed: {result.get('error', 'Unknown')}", "ERROR", Colors.FAIL)
                    
                time.sleep(0.05)  # Small delay between requests
                
            time.sleep(0.5)  # Pause between routes

    def test_api_endpoints_rate_limiting(self):
        """Test rate limiting on API endpoints"""
        self.print_header("🔌 API ENDPOINTS RATE LIMITING", Colors.OKBLUE)
        
        for route in self.endpoints['api_routes']:
            self.print_status(f"Testing API route: {route}")
            
            response_times = []
            status_codes = []
            
            # Make burst requests to measure response and trigger rate limiting
            for i in range(self.test_config['burst_size']):
                result = self.make_request('GET', route)
                self.results['api_endpoints'].append(result)
                
                if result['success']:
                    response_times.append(result['response_time'])
                    status_codes.append(result['status_code'])
                    
                    if result['status_code'] in self.test_config['rate_limit_expected_codes']:
                        self.print_status(f"🚦 API rate limit triggered on request {i+1}", "RATE_LIMIT", Colors.WARNING)
                        break
                        
                time.sleep(0.05)
                
            # Calculate metrics for this route
            if response_times:
                avg_response = statistics.mean(response_times)
                self.print_status(f"Average response time: {avg_response:.3f}s ({len(response_times)} requests)")
                
            time.sleep(0.5)

    def test_ml_prediction_rate_limiting(self):
        """Test rate limiting on ML prediction endpoints"""
        self.print_header("🤖 ML PREDICTION RATE LIMITING", Colors.HEADER)
        
        # Sample property data for ML predictions
        sample_property_data = {
            "bedrooms": 3,
            "bathrooms": 2,
            "sqft": 1500,
            "location": "Toronto",
            "property_type": "House",
            "year_built": 2000
        }
        
        for route in self.endpoints['ml_routes']:
            self.print_status(f"Testing ML route: {route}")
            
            # Test both GET and POST requests for ML endpoints
            for method in ['GET', 'POST']:
                for i in range(10):  # Smaller burst for ML endpoints
                    if method == 'POST':
                        result = self.make_request(method, route, json=sample_property_data)
                    else:
                        result = self.make_request(method, route)
                        
                    self.results['ml_predictions'].append(result)
                    
                    if result['success'] and result['status_code'] in self.test_config['rate_limit_expected_codes']:
                        self.print_status(f"🚦 ML rate limit triggered ({method}) on request {i+1}", "RATE_LIMIT", Colors.WARNING)
                        break
                        
                    time.sleep(0.1)
                    
            time.sleep(0.5)

    def test_search_functionality_rate_limiting(self):
        """Test rate limiting on search endpoints"""
        self.print_header("🔍 SEARCH FUNCTIONALITY RATE LIMITING", Colors.OKCYAN)
        
        search_queries = [
            {"q": "Toronto condos"},
            {"location": "Vancouver", "price_min": 500000},
            {"bedrooms": 3, "bathrooms": 2},
            {"property_type": "House", "sqft_min": 1000}
        ]
        
        for route in self.endpoints['search_routes']:
            self.print_status(f"Testing search route: {route}")
            
            for query_data in search_queries:
                for i in range(8):  # Moderate burst for search
                    # Test both GET with params and POST with JSON
                    if i % 2 == 0:
                        result = self.make_request('GET', route, params=query_data)
                    else:
                        result = self.make_request('POST', route, json=query_data)
                        
                    self.results['search_tests'].append(result)
                    
                    if result['success'] and result['status_code'] in self.test_config['rate_limit_expected_codes']:
                        self.print_status(f"🚦 Search rate limit triggered", "RATE_LIMIT", Colors.WARNING)
                        break
                        
                    time.sleep(0.1)
                    
            time.sleep(0.3)

    def test_authentication_rate_limiting(self):
        """Test rate limiting on authentication endpoints"""
        self.print_header("🔐 AUTHENTICATION RATE LIMITING", Colors.FAIL)
        
        # Sample authentication data
        auth_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        register_data = {
            "name": "Test User",
            "email": "newuser@example.com", 
            "password": "newpassword123"
        }
        
        for route in self.endpoints['auth_routes']:
            self.print_status(f"Testing auth route: {route}")
            
            # Use appropriate data based on endpoint
            if 'register' in route:
                test_data = register_data
            else:
                test_data = auth_data
                
            # Authentication endpoints should have stricter rate limiting
            for i in range(15):
                result = self.make_request('POST', route, json=test_data)
                self.results['auth_tests'].append(result)
                
                if result['success'] and result['status_code'] in self.test_config['rate_limit_expected_codes']:
                    self.print_status(f"🚦 Auth rate limit triggered on request {i+1}", "RATE_LIMIT", Colors.WARNING)
                    break
                    
                time.sleep(0.2)  # Slightly longer delay for auth endpoints
                
            time.sleep(1)  # Longer pause between auth routes

    def test_concurrent_access(self):
        """Test rate limiting under concurrent access"""
        self.print_header("⚡ CONCURRENT ACCESS TESTING", Colors.BOLD)
        
        def make_concurrent_request(endpoint: str) -> Dict[str, Any]:
            """Make a single concurrent request"""
            return self.make_request('GET', endpoint)
            
        # Test different levels of concurrency
        concurrency_levels = [10, 20, 30]
        test_endpoint = '/api/health'
        
        for concurrency in concurrency_levels:
            self.print_status(f"Testing {concurrency} concurrent requests to {test_endpoint}")
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                # Submit all requests
                futures = [
                    executor.submit(make_concurrent_request, test_endpoint)
                    for _ in range(concurrency)
                ]
                
                # Collect results
                concurrent_results = []
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=self.test_config['request_timeout'])
                        concurrent_results.append(result)
                        self.results['concurrent_tests'].append(result)
                    except Exception as e:
                        self.print_status(f"Concurrent request failed: {e}", "ERROR", Colors.FAIL)
                        
            duration = time.time() - start_time
            
            # Analyze concurrent results
            successful_requests = sum(1 for r in concurrent_results if r['success'])
            rate_limited = sum(1 for r in concurrent_results if r['success'] and r['status_code'] in self.test_config['rate_limit_expected_codes'])
            
            throughput = len(concurrent_results) / duration if duration > 0 else 0
            
            self.print_status(f"Concurrency {concurrency}: {successful_requests}/{concurrency} successful, {rate_limited} rate limited")
            self.print_status(f"Duration: {duration:.2f}s, Throughput: {throughput:.2f} req/s")
            
            time.sleep(2)  # Pause between concurrency tests

    def test_sustained_load(self):
        """Test rate limiting under sustained load"""
        self.print_header("🔄 SUSTAINED LOAD TESTING", Colors.WARNING)
        
        test_endpoint = '/api/health'
        duration = self.test_config['sustained_duration']
        
        self.print_status(f"Running sustained load test for {duration} seconds on {test_endpoint}")
        
        start_time = time.time()
        sustained_results = []
        request_count = 0
        rate_limit_count = 0
        
        while time.time() - start_time < duration:
            result = self.make_request('GET', test_endpoint)
            sustained_results.append(result)
            self.results['sustained_tests'].append(result)
            
            request_count += 1
            
            if result['success'] and result['status_code'] in self.test_config['rate_limit_expected_codes']:
                rate_limit_count += 1
                
            # Brief pause to avoid overwhelming
            time.sleep(0.1)
            
            # Progress update every 10 seconds
            elapsed = time.time() - start_time
            if request_count % 50 == 0:
                self.print_status(f"Progress: {elapsed:.1f}s, {request_count} requests, {rate_limit_count} rate limited")
                
        total_duration = time.time() - start_time
        
        # Calculate sustained load metrics
        successful_requests = sum(1 for r in sustained_results if r['success'])
        avg_response_time = statistics.mean([r['response_time'] for r in sustained_results if 'response_time' in r])
        throughput = request_count / total_duration
        rate_limit_percentage = (rate_limit_count / request_count) * 100 if request_count > 0 else 0
        
        self.print_status(f"Sustained load results:")
        self.print_status(f"  Total requests: {request_count}")
        self.print_status(f"  Successful: {successful_requests}")
        self.print_status(f"  Rate limited: {rate_limit_count} ({rate_limit_percentage:.1f}%)")
        self.print_status(f"  Average response time: {avg_response_time:.3f}s")
        self.print_status(f"  Throughput: {throughput:.2f} req/s")
        
        # Store sustained load metrics
        self.results['performance_metrics']['sustained_load'] = {
            'total_requests': request_count,
            'successful_requests': successful_requests,
            'rate_limited_requests': rate_limit_count,
            'rate_limit_percentage': rate_limit_percentage,
            'average_response_time': avg_response_time,
            'throughput': throughput,
            'duration': total_duration
        }

    def test_cli_commands(self):
        """Test CLI rate limiting commands"""
        self.print_header("⚙️ CLI COMMANDS TESTING", Colors.OKGREEN)
        
        cli_commands = [
            'flask rate-limit health',
            'flask rate-limit status', 
            'flask rate-limit stats',
            'flask rate-limit clear',
            'flask --help'
        ]
        
        for cmd in cli_commands:
            self.print_status(f"Testing CLI command: {cmd}")
            
            try:
                start_time = time.time()
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=os.getcwd()
                )
                
                execution_time = time.time() - start_time
                
                cli_result = {
                    'command': cmd,
                    'return_code': result.returncode,
                    'execution_time': execution_time,
                    'stdout_length': len(result.stdout) if result.stdout else 0,
                    'stderr_length': len(result.stderr) if result.stderr else 0,
                    'success': result.returncode == 0,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.results['cli_tests'].append(cli_result)
                
                if result.returncode == 0:
                    self.print_status(f"✅ CLI command successful ({execution_time:.2f}s)", "SUCCESS", Colors.OKGREEN)
                else:
                    self.print_status(f"❌ CLI command failed (code: {result.returncode})", "ERROR", Colors.FAIL)
                    if result.stderr:
                        self.print_status(f"Error: {result.stderr[:100]}...", "ERROR", Colors.FAIL)
                        
            except subprocess.TimeoutExpired:
                self.print_status(f"⏰ CLI command timed out", "TIMEOUT", Colors.WARNING)
                self.results['cli_tests'].append({
                    'command': cmd,
                    'success': False,
                    'error': 'timeout',
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self.print_status(f"❌ CLI command error: {e}", "ERROR", Colors.FAIL)
                self.results['cli_tests'].append({
                    'command': cmd,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
            time.sleep(1)

    def analyze_performance_metrics(self):
        """Analyze and calculate comprehensive performance metrics"""
        self.print_header("📊 PERFORMANCE ANALYSIS", Colors.HEADER)
        
        # Collect all response times
        all_response_times = []
        status_code_distribution = Counter()
        endpoint_performance = defaultdict(list)
        
        # Aggregate data from all test categories
        all_results = (
            self.results['health_checks'] +
            self.results['web_routes'] +
            self.results['api_endpoints'] +
            self.results['ml_predictions'] +
            self.results['search_tests'] +
            self.results['auth_tests'] +
            self.results['concurrent_tests'] +
            self.results['sustained_tests']
        )
        
        for result in all_results:
            if result['success'] and 'response_time' in result:
                response_time = result['response_time']
                all_response_times.append(response_time)
                
                status_code = result['status_code']
                status_code_distribution[status_code] += 1
                
                url = result.get('url', '')
                endpoint_performance[url].append(response_time)
                
        # Calculate comprehensive metrics
        if all_response_times:
            metrics = {
                'total_requests': len(all_results),
                'successful_requests': len(all_response_times),
                'response_time_stats': {
                    'min': min(all_response_times),
                    'max': max(all_response_times),
                    'mean': statistics.mean(all_response_times),
                    'median': statistics.median(all_response_times),
                    'std_dev': statistics.stdev(all_response_times) if len(all_response_times) > 1 else 0
                },
                'status_code_distribution': dict(status_code_distribution),
                'rate_limit_effectiveness': {
                    'total_rate_limits': self.results['rate_limit_triggers'],
                    'rate_limit_percentage': (self.results['rate_limit_triggers'] / self.results['total_requests'] * 100) if self.results['total_requests'] > 0 else 0
                },
                'error_summary': dict(self.results['error_summary'])
            }
            
            self.results['performance_metrics'].update(metrics)
            
            # Display key metrics
            self.print_status(f"Total Requests: {metrics['total_requests']}")
            self.print_status(f"Successful Requests: {metrics['successful_requests']}")
            self.print_status(f"Rate Limits Triggered: {self.results['rate_limit_triggers']}")
            self.print_status(f"Rate Limit Percentage: {metrics['rate_limit_effectiveness']['rate_limit_percentage']:.2f}%")
            
            resp_stats = metrics['response_time_stats']
            self.print_status(f"Response Time - Min: {resp_stats['min']:.3f}s, Max: {resp_stats['max']:.3f}s, Avg: {resp_stats['mean']:.3f}s")
            
            # Top status codes
            top_status_codes = status_code_distribution.most_common(5)
            self.print_status("Top Status Codes:")
            for code, count in top_status_codes:
                percentage = (count / len(all_results)) * 100
                self.print_status(f"  {code}: {count} ({percentage:.1f}%)")

    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        self.print_header("📋 COMPREHENSIVE TEST REPORT", Colors.BOLD)
        
        # Test summary
        test_categories = {
            'Health Checks': len(self.results['health_checks']),
            'Web Routes': len(self.results['web_routes']), 
            'API Endpoints': len(self.results['api_endpoints']),
            'ML Predictions': len(self.results['ml_predictions']),
            'Search Tests': len(self.results['search_tests']),
            'Auth Tests': len(self.results['auth_tests']),
            'Concurrent Tests': len(self.results['concurrent_tests']),
            'Sustained Tests': len(self.results['sustained_tests']),
            'CLI Tests': len(self.results['cli_tests']),
            'Header Tests': len(self.results['header_tests'])
        }
        
        print(f"{Colors.OKGREEN}📊 Test Execution Summary:{Colors.ENDC}")
        for category, count in test_categories.items():
            print(f"  {category}: {count} tests")
            
        # Overall assessment
        total_tests = sum(test_categories.values())
        success_rate = ((self.results['total_requests'] - sum(self.results['error_summary'].values())) / self.results['total_requests'] * 100) if self.results['total_requests'] > 0 else 0
        
        print(f"\n{Colors.OKBLUE}🎯 Overall Assessment:{Colors.ENDC}")
        print(f"  Total Tests Executed: {total_tests}")
        print(f"  Total HTTP Requests: {self.results['total_requests']}")
        print(f"  Success Rate: {success_rate:.2f}%")
        print(f"  Rate Limiting Effectiveness: {self.results['rate_limit_triggers']} triggers")
        
        # Performance metrics summary
        if 'response_time_stats' in self.results['performance_metrics']:
            resp_stats = self.results['performance_metrics']['response_time_stats']
            print(f"\n{Colors.OKCYAN}⚡ Performance Summary:{Colors.ENDC}")
            print(f"  Average Response Time: {resp_stats['mean']:.3f}s")
            print(f"  Response Time Range: {resp_stats['min']:.3f}s - {resp_stats['max']:.3f}s")
            
        # Error summary
        if any(self.results['error_summary'].values()):
            print(f"\n{Colors.WARNING}⚠️ Error Summary:{Colors.ENDC}")
            for error_type, count in self.results['error_summary'].items():
                if count > 0:
                    print(f"  {error_type.title()}: {count}")
                    
        # Rate limiting effectiveness
        rate_limit_pct = (self.results['rate_limit_triggers'] / self.results['total_requests'] * 100) if self.results['total_requests'] > 0 else 0
        
        print(f"\n{Colors.HEADER}🛡️ Rate Limiting Assessment:{Colors.ENDC}")
        if rate_limit_pct > 10:
            print(f"  {Colors.OKGREEN}✅ Excellent - Rate limiting is actively protecting the application ({rate_limit_pct:.1f}%){Colors.ENDC}")
        elif rate_limit_pct > 5:
            print(f"  {Colors.WARNING}⚠️ Good - Rate limiting is working ({rate_limit_pct:.1f}%){Colors.ENDC}")
        elif rate_limit_pct > 0:
            print(f"  {Colors.OKCYAN}ℹ️ Moderate - Some rate limiting detected ({rate_limit_pct:.1f}%){Colors.ENDC}")
        else:
            print(f"  {Colors.FAIL}❌ Concern - No rate limiting detected{Colors.ENDC}")
            
        # Test duration
        print(f"\n{Colors.OKBLUE}⏱️ Test Duration: {self.results['test_duration']:.2f} seconds{Colors.ENDC}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}💡 Recommendations:{Colors.ENDC}")
        
        if rate_limit_pct == 0:
            print("  • Verify rate limiting configuration is enabled")
            print("  • Check rate limiting middleware implementation")
            
        if any(count > 0 for count in self.results['error_summary'].values()):
            print("  • Investigate connection and timeout errors")
            print("  • Consider implementing retry logic with exponential backoff")
            
        if 'response_time_stats' in self.results['performance_metrics']:
            avg_time = self.results['performance_metrics']['response_time_stats']['mean']
            if avg_time > 1.0:
                print("  • Consider performance optimization for slower endpoints")
                print("  • Implement caching for frequently accessed data")

    def run_ultimate_test_suite(self):
        """Run the complete ultimate rate limiting test suite"""
        print(f"{Colors.BOLD}{Colors.HEADER}")
        print("🚀" * 30)
        print("NextProperty AI - Ultimate Rate Limiting Test Suite".center(90))
        print("🚀" * 30)
        print(f"{Colors.ENDC}")
        
        start_time = time.time()
        
        try:
            # 1. Application Health Check
            if not self.test_application_health():
                self.print_status("❌ Application health check failed. Some tests may not work correctly.", "WARNING", Colors.WARNING)
                
            # 2. Rate Limit Headers Validation
            self.test_rate_limit_headers()
            
            # 3. Web Routes Testing
            self.test_web_routes_rate_limiting()
            
            # 4. API Endpoints Testing  
            self.test_api_endpoints_rate_limiting()
            
            # 5. ML Prediction Testing
            self.test_ml_prediction_rate_limiting()
            
            # 6. Search Functionality Testing
            self.test_search_functionality_rate_limiting()
            
            # 7. Authentication Testing
            self.test_authentication_rate_limiting()
            
            # 8. Concurrent Access Testing
            self.test_concurrent_access()
            
            # 9. Sustained Load Testing
            self.test_sustained_load()
            
            # 10. CLI Commands Testing
            self.test_cli_commands()
            
            # 11. Performance Analysis
            self.analyze_performance_metrics()
            
            # Calculate total test duration
            self.results['test_duration'] = time.time() - start_time
            
            # 12. Generate Comprehensive Report
            self.generate_comprehensive_report()
            
        except KeyboardInterrupt:
            self.print_status("❌ Test suite interrupted by user", "INTERRUPTED", Colors.WARNING)
            
        except Exception as e:
            self.print_status(f"❌ Test suite failed with error: {e}", "ERROR", Colors.FAIL)
            
        finally:
            self.print_header("🏁 ULTIMATE TEST SUITE COMPLETED", Colors.OKGREEN)
            
    def save_results_to_file(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ultimate_rate_limit_test_results_{timestamp}.json"
            
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            self.print_status(f"✅ Test results saved to: {filename}", "SUCCESS", Colors.OKGREEN)
        except Exception as e:
            self.print_status(f"❌ Failed to save results: {e}", "ERROR", Colors.FAIL)

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NextProperty AI Ultimate Rate Limiting Test Suite')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL of the application')
    parser.add_argument('--save-results', action='store_true', help='Save test results to JSON file')
    parser.add_argument('--quick', action='store_true', help='Run quick test suite (reduced load)')
    
    args = parser.parse_args()
    
    # Create and configure tester
    tester = UltimateRateLimitTester(base_url=args.url)
    
    # Adjust configuration for quick test
    if args.quick:
        tester.test_config.update({
            'burst_size': 10,
            'concurrent_threads': 10,
            'sustained_duration': 15
        })
        tester.print_status("🏃 Running in quick test mode", "INFO", Colors.OKCYAN)
    
    # Run the test suite
    tester.run_ultimate_test_suite()
    
    # Save results if requested
    if args.save_results:
        tester.save_results_to_file()

if __name__ == "__main__":
    main()
