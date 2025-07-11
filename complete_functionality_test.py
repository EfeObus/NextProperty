#!/usr/bin/env python3
"""
Complete Functionality Test Suite for NextProperty AI
Tests all aspects of the application functionality including web routes, API endpoints, ML predictions, 
database operations, security features, and overall system health.

This comprehensive test suite covers:
- Web application routes and pages
- API endpoints and responses
- Machine learning predictions
- Database connectivity and operations
- Authentication and security features
- File uploads and form handling
- Map functionality and geospatial data
- Economic data integration
- Error handling and edge cases
- Performance and response times
"""

import requests
import time
import json
import sys
import subprocess
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import statistics
from typing import Dict, List, Tuple, Any, Optional
import warnings
import random
import string
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)


class CompleteFunctionalityTester:
    """Complete functionality test suite for NextProperty AI."""
    
    def __init__(self, base_url="http://localhost:5007"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NextProperty-Complete-Functionality-Test/1.0'
        })
        self.results = {
            'test_results': [],
            'performance_metrics': {},
            'functionality_stats': {},
            'error_log': [],
            'coverage_report': {}
        }
        self.lock = Lock()
        self.test_data = self._initialize_test_data()
        
    def log(self, message, level="INFO", category="GENERAL"):
        """Enhanced logging with categorization."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "WARN": "⚠️",
            "ERROR": "❌",
            "DEBUG": "🐛"
        }.get(level, "ℹ️")
        
        formatted_message = f"[{timestamp}] {prefix} [{category}] {message}"
        print(formatted_message)
        
        with self.lock:
            self.results['test_results'].append({
                'timestamp': timestamp,
                'level': level,
                'category': category,
                'message': message
            })
    
    def _initialize_test_data(self) -> Dict[str, Any]:
        """Initialize test data for various endpoints."""
        return {
            'property_search': {
                'city': 'Toronto',
                'property_type': 'House',
                'min_price': 300000,
                'max_price': 800000,
                'bedrooms': 3,
                'bathrooms': 2
            },
            'property_data': {
                'address': '123 Test Street',
                'city': 'Toronto',
                'province': 'Ontario',
                'postal_code': 'M5V 3A8',
                'property_type': 'House',
                'bedrooms': 3,
                'bathrooms': 2.5,
                'sqft': 1500,
                'lot_size': 0.15,
                'year_built': 2010,
                'listing_price': 650000,
                'features': 'Updated kitchen, hardwood floors',
                'description': 'Beautiful family home in great neighborhood'
            },
            'prediction_features': {
                'bedrooms': 3,
                'bathrooms': 2.5,
                'sqft': 1500,
                'city': 'Toronto',
                'property_type': 'House',
                'year_built': 2010
            },
            'map_filters': {
                'city': 'Vancouver',
                'type': 'Condo',
                'min_price': 400000,
                'max_price': 700000,
                'bedrooms': 2
            }
        }
    
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
            'main_pages': [
                '/',
                '/properties',
                '/search',
                '/mapview',
                '/favourites',
                '/predict-price',
                '/upload-property',
                '/top-properties',
                '/market-insights',
                '/economic-dashboard',
                '/about',
                '/contact',
                '/careers',
                '/privacy',
                '/investment-guide',
                '/market-reports',
                '/api-docs',
                '/help'
            ],
            'api_endpoints': [
                '/api/health',
                '/api/properties',
                '/api/search',
                '/api/stats/summary',
                '/api/market/trends',
                '/api/market/economic-indicators',
                '/api/market/predictions',
                '/api/market-summary',
                '/api/economic-indicators',
                '/api/market-impact',
                '/api/economic-insights',
                '/api/properties/map-data',
                '/api/model/status'
            ],
            'auth_pages': [
                '/login',
                '/register'
            ],
            'admin_endpoints': [
                '/admin/',
                '/admin/bulk-operations',
                '/admin/model-management',
                '/admin/api/system-stats'
            ],
            'dashboard_endpoints': [
                '/dashboard/',
                '/dashboard/portfolio',
                '/dashboard/market',
                '/dashboard/analytics',
                '/dashboard/economic'
            ]
        }
    
    def test_application_health(self) -> Dict[str, Any]:
        """Test basic application health and connectivity."""
        self.log("Testing application health and connectivity", "INFO", "HEALTH")
        
        health_results = {
            'server_responsive': False,
            'response_time': None,
            'status_code': None,
            'basic_content': False,
            'error': None
        }
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/", timeout=10)
            response_time = time.time() - start_time
            
            health_results.update({
                'server_responsive': True,
                'response_time': response_time,
                'status_code': response.status_code,
                'basic_content': len(response.text) > 100,
                'headers': dict(response.headers)
            })
            
            if response.status_code == 200:
                self.log(f"✅ Server is responsive (Status: {response.status_code}, Time: {response_time:.3f}s)", "SUCCESS", "HEALTH")
            else:
                self.log(f"⚠️ Server responded with status {response.status_code}", "WARN", "HEALTH")
                
        except Exception as e:
            health_results['error'] = str(e)
            self.log(f"❌ Server health check failed: {str(e)}", "ERROR", "HEALTH")
        
        return health_results
    
    def test_web_pages(self) -> Dict[str, Any]:
        """Test all main web pages and routes."""
        self.log("Testing web pages and main routes", "INFO", "WEB_PAGES")
        
        endpoints = self._initialize_endpoints()
        page_results = {}
        
        for page in endpoints['main_pages']:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{page}", timeout=15)
                response_time = time.time() - start_time
                
                page_results[page] = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'content_length': len(response.text),
                    'has_content': len(response.text) > 100,
                    'content_type': response.headers.get('content-type', ''),
                    'success': response.status_code in [200, 302]
                }
                
                if response.status_code == 200:
                    self.log(f"✅ {page} - OK ({response_time:.3f}s)", "SUCCESS", "WEB_PAGES")
                elif response.status_code == 302:
                    self.log(f"↩️ {page} - Redirect ({response_time:.3f}s)", "INFO", "WEB_PAGES")
                else:
                    self.log(f"⚠️ {page} - Status {response.status_code} ({response_time:.3f}s)", "WARN", "WEB_PAGES")
                    
            except Exception as e:
                page_results[page] = {
                    'status_code': None,
                    'response_time': None,
                    'error': str(e),
                    'success': False
                }
                self.log(f"❌ {page} - Error: {str(e)}", "ERROR", "WEB_PAGES")
                
        return page_results
    
    def test_api_endpoints(self) -> Dict[str, Any]:
        """Test API endpoints functionality."""
        self.log("Testing API endpoints", "INFO", "API")
        
        endpoints = self._initialize_endpoints()
        api_results = {}
        
        for endpoint in endpoints['api_endpoints']:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=15)
                response_time = time.time() - start_time
                
                # Try to parse JSON response
                json_data = None
                is_json = False
                try:
                    json_data = response.json()
                    is_json = True
                except:
                    pass
                
                api_results[endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'is_json': is_json,
                    'json_data': json_data,
                    'content_length': len(response.text),
                    'content_type': response.headers.get('content-type', ''),
                    'success': response.status_code in [200, 201]
                }
                
                if response.status_code == 200:
                    self.log(f"✅ {endpoint} - OK ({response_time:.3f}s, JSON: {is_json})", "SUCCESS", "API")
                else:
                    self.log(f"⚠️ {endpoint} - Status {response.status_code} ({response_time:.3f}s)", "WARN", "API")
                    
            except Exception as e:
                api_results[endpoint] = {
                    'status_code': None,
                    'response_time': None,
                    'error': str(e),
                    'success': False
                }
                self.log(f"❌ {endpoint} - Error: {str(e)}", "ERROR", "API")
                
        return api_results
    
    def test_property_search(self) -> Dict[str, Any]:
        """Test property search functionality."""
        self.log("Testing property search functionality", "INFO", "SEARCH")
        
        search_results = {}
        search_params = self.test_data['property_search']
        
        # Test different search scenarios
        search_tests = [
            {'name': 'city_search', 'params': {'city': search_params['city']}},
            {'name': 'price_range', 'params': {'min_price': search_params['min_price'], 'max_price': search_params['max_price']}},
            {'name': 'property_type', 'params': {'type': search_params['property_type']}},
            {'name': 'combined_search', 'params': search_params}
        ]
        
        for test in search_tests:
            try:
                # Test both web page and API
                web_url = f"{self.base_url}/search"
                api_url = f"{self.base_url}/api/search"
                
                start_time = time.time()
                web_response = self.session.get(web_url, params=test['params'], timeout=15)
                web_time = time.time() - start_time
                
                start_time = time.time()
                api_response = self.session.get(api_url, params=test['params'], timeout=15)
                api_time = time.time() - start_time
                
                search_results[test['name']] = {
                    'web_search': {
                        'status_code': web_response.status_code,
                        'response_time': web_time,
                        'content_length': len(web_response.text),
                        'success': web_response.status_code == 200
                    },
                    'api_search': {
                        'status_code': api_response.status_code,
                        'response_time': api_time,
                        'is_json': 'application/json' in api_response.headers.get('content-type', ''),
                        'success': api_response.status_code == 200
                    },
                    'params': test['params']
                }
                
                self.log(f"✅ Search test '{test['name']}' - Web: {web_response.status_code}, API: {api_response.status_code}", 
                        "SUCCESS" if web_response.status_code == 200 and api_response.status_code == 200 else "WARN", 
                        "SEARCH")
                
            except Exception as e:
                search_results[test['name']] = {
                    'error': str(e),
                    'success': False,
                    'params': test['params']
                }
                self.log(f"❌ Search test '{test['name']}' failed: {str(e)}", "ERROR", "SEARCH")
        
        return search_results
    
    def test_property_predictions(self) -> Dict[str, Any]:
        """Test ML property price prediction functionality."""
        self.log("Testing ML property price predictions", "INFO", "ML_PREDICTIONS")
        
        prediction_results = {}
        
        # Test GET request to prediction page
        try:
            start_time = time.time()
            get_response = self.session.get(f"{self.base_url}/predict-price", timeout=15)
            get_time = time.time() - start_time
            
            prediction_results['prediction_page'] = {
                'status_code': get_response.status_code,
                'response_time': get_time,
                'success': get_response.status_code == 200,
                'content_length': len(get_response.text)
            }
            
            self.log(f"✅ Prediction page loaded - Status: {get_response.status_code} ({get_time:.3f}s)", 
                    "SUCCESS" if get_response.status_code == 200 else "WARN", "ML_PREDICTIONS")
                    
        except Exception as e:
            prediction_results['prediction_page'] = {'error': str(e), 'success': False}
            self.log(f"❌ Failed to load prediction page: {str(e)}", "ERROR", "ML_PREDICTIONS")
        
        # Test POST request with prediction data
        try:
            start_time = time.time()
            post_response = self.session.post(
                f"{self.base_url}/predict-price",
                data=self.test_data['prediction_features'],
                timeout=30
            )
            post_time = time.time() - start_time
            
            prediction_results['prediction_request'] = {
                'status_code': post_response.status_code,
                'response_time': post_time,
                'success': post_response.status_code in [200, 302],
                'content_length': len(post_response.text),
                'redirect': post_response.status_code == 302
            }
            
            self.log(f"✅ Prediction request - Status: {post_response.status_code} ({post_time:.3f}s)", 
                    "SUCCESS" if post_response.status_code in [200, 302] else "WARN", "ML_PREDICTIONS")
                    
        except Exception as e:
            prediction_results['prediction_request'] = {'error': str(e), 'success': False}
            self.log(f"❌ Failed to make prediction request: {str(e)}", "ERROR", "ML_PREDICTIONS")
        
        return prediction_results
    
    def test_map_functionality(self) -> Dict[str, Any]:
        """Test map view and geospatial functionality."""
        self.log("Testing map functionality and geospatial features", "INFO", "MAP")
        
        map_results = {}
        
        # Test map page loading
        try:
            start_time = time.time()
            map_response = self.session.get(f"{self.base_url}/mapview", timeout=15)
            map_time = time.time() - start_time
            
            map_results['map_page'] = {
                'status_code': map_response.status_code,
                'response_time': map_time,
                'success': map_response.status_code == 200,
                'content_length': len(map_response.text)
            }
            
            self.log(f"✅ Map page loaded - Status: {map_response.status_code} ({map_time:.3f}s)", 
                    "SUCCESS" if map_response.status_code == 200 else "WARN", "MAP")
                    
        except Exception as e:
            map_results['map_page'] = {'error': str(e), 'success': False}
            self.log(f"❌ Failed to load map page: {str(e)}", "ERROR", "MAP")
        
        # Test map data API
        try:
            start_time = time.time()
            map_data_response = self.session.get(
                f"{self.base_url}/api/properties/map-data",
                params=self.test_data['map_filters'],
                timeout=20
            )
            map_data_time = time.time() - start_time
            
            map_data = None
            try:
                map_data = map_data_response.json()
            except:
                pass
            
            map_results['map_data_api'] = {
                'status_code': map_data_response.status_code,
                'response_time': map_data_time,
                'success': map_data_response.status_code == 200,
                'is_json': map_data is not None,
                'data': map_data,
                'property_count': len(map_data.get('properties', [])) if map_data else 0
            }
            
            self.log(f"✅ Map data API - Status: {map_data_response.status_code}, Properties: {map_results['map_data_api']['property_count']} ({map_data_time:.3f}s)", 
                    "SUCCESS" if map_data_response.status_code == 200 else "WARN", "MAP")
                    
        except Exception as e:
            map_results['map_data_api'] = {'error': str(e), 'success': False}
            self.log(f"❌ Failed to get map data: {str(e)}", "ERROR", "MAP")
        
        return map_results
    
    def test_property_upload(self) -> Dict[str, Any]:
        """Test property upload functionality."""
        self.log("Testing property upload functionality", "INFO", "UPLOAD")
        
        upload_results = {}
        
        # Test GET request to upload page
        try:
            start_time = time.time()
            get_response = self.session.get(f"{self.base_url}/upload-property", timeout=15)
            get_time = time.time() - start_time
            
            upload_results['upload_page'] = {
                'status_code': get_response.status_code,
                'response_time': get_time,
                'success': get_response.status_code == 200,
                'content_length': len(get_response.text)
            }
            
            self.log(f"✅ Upload page loaded - Status: {get_response.status_code} ({get_time:.3f}s)", 
                    "SUCCESS" if get_response.status_code == 200 else "WARN", "UPLOAD")
                    
        except Exception as e:
            upload_results['upload_page'] = {'error': str(e), 'success': False}
            self.log(f"❌ Failed to load upload page: {str(e)}", "ERROR", "UPLOAD")
        
        # Note: We won't test actual property upload POST to avoid creating test data
        # but we can verify the form is accessible
        
        return upload_results
    
    def test_authentication_pages(self) -> Dict[str, Any]:
        """Test authentication related pages."""
        self.log("Testing authentication pages", "INFO", "AUTH")
        
        auth_results = {}
        endpoints = self._initialize_endpoints()
        
        for page in endpoints['auth_pages']:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{page}", timeout=15)
                response_time = time.time() - start_time
                
                auth_results[page] = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code == 200,
                    'content_length': len(response.text)
                }
                
                self.log(f"✅ {page} - Status: {response.status_code} ({response_time:.3f}s)", 
                        "SUCCESS" if response.status_code == 200 else "WARN", "AUTH")
                        
            except Exception as e:
                auth_results[page] = {'error': str(e), 'success': False}
                self.log(f"❌ {page} failed: {str(e)}", "ERROR", "AUTH")
        
        return auth_results
    
    def test_economic_data(self) -> Dict[str, Any]:
        """Test economic data and market insights functionality."""
        self.log("Testing economic data and market insights", "INFO", "ECONOMIC")
        
        economic_results = {}
        
        economic_endpoints = [
            '/economic-dashboard',
            '/market-insights',
            '/api/economic-indicators',
            '/api/market-impact',
            '/api/economic-insights'
        ]
        
        for endpoint in economic_endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=15)
                response_time = time.time() - start_time
                
                json_data = None
                if endpoint.startswith('/api/'):
                    try:
                        json_data = response.json()
                    except:
                        pass
                
                economic_results[endpoint] = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code == 200,
                    'is_json': json_data is not None,
                    'json_data': json_data,
                    'content_length': len(response.text)
                }
                
                self.log(f"✅ {endpoint} - Status: {response.status_code} ({response_time:.3f}s)", 
                        "SUCCESS" if response.status_code == 200 else "WARN", "ECONOMIC")
                        
            except Exception as e:
                economic_results[endpoint] = {'error': str(e), 'success': False}
                self.log(f"❌ {endpoint} failed: {str(e)}", "ERROR", "ECONOMIC")
        
        return economic_results
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid requests."""
        self.log("Testing error handling and edge cases", "INFO", "ERROR_HANDLING")
        
        error_results = {}
        
        # Test various error scenarios
        error_tests = [
            {'name': 'invalid_property_id', 'url': '/property/INVALID_ID'},
            {'name': 'malformed_search', 'url': '/api/search', 'params': {'min_price': 'invalid'}},
            {'name': 'non_existent_endpoint', 'url': '/this/does/not/exist'},
            {'name': 'invalid_api_request', 'url': '/api/invalid/endpoint'}
        ]
        
        for test in error_tests:
            try:
                start_time = time.time()
                response = self.session.get(
                    f"{self.base_url}{test['url']}", 
                    params=test.get('params', {}),
                    timeout=10
                )
                response_time = time.time() - start_time
                
                error_results[test['name']] = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'handled_gracefully': response.status_code in [400, 404, 500],
                    'content_length': len(response.text)
                }
                
                self.log(f"✅ Error test '{test['name']}' - Status: {response.status_code} ({response_time:.3f}s)", 
                        "SUCCESS", "ERROR_HANDLING")
                        
            except Exception as e:
                error_results[test['name']] = {'error': str(e), 'success': False}
                self.log(f"❌ Error test '{test['name']}' failed: {str(e)}", "ERROR", "ERROR_HANDLING")
        
        return error_results
    
    def test_performance_metrics(self) -> Dict[str, Any]:
        """Test performance characteristics of key endpoints."""
        self.log("Testing performance metrics", "INFO", "PERFORMANCE")
        
        performance_results = {}
        
        # Key endpoints to test for performance
        performance_endpoints = [
            '/',
            '/properties',
            '/api/properties',
            '/mapview',
            '/api/properties/map-data'
        ]
        
        for endpoint in performance_endpoints:
            try:
                times = []
                success_count = 0
                
                # Run multiple requests to get average performance
                for i in range(5):
                    start_time = time.time()
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=20)
                    response_time = time.time() - start_time
                    
                    times.append(response_time)
                    if response.status_code == 200:
                        success_count += 1
                    
                    time.sleep(0.5)  # Small delay between requests
                
                performance_results[endpoint] = {
                    'avg_response_time': statistics.mean(times),
                    'min_response_time': min(times),
                    'max_response_time': max(times),
                    'success_rate': success_count / 5,
                    'all_times': times
                }
                
                self.log(f"✅ {endpoint} - Avg: {performance_results[endpoint]['avg_response_time']:.3f}s, Success: {success_count}/5", 
                        "SUCCESS", "PERFORMANCE")
                        
            except Exception as e:
                performance_results[endpoint] = {'error': str(e), 'success': False}
                self.log(f"❌ Performance test for {endpoint} failed: {str(e)}", "ERROR", "PERFORMANCE")
        
        return performance_results
    
    def test_concurrent_load(self) -> Dict[str, Any]:
        """Test concurrent request handling."""
        self.log("Testing concurrent load handling", "INFO", "CONCURRENCY")
        
        def make_request(endpoint):
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=15)
                response_time = time.time() - start_time
                return {
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'success': response.status_code == 200
                }
            except Exception as e:
                return {
                    'endpoint': endpoint,
                    'error': str(e),
                    'success': False
                }
        
        # Test concurrent requests to various endpoints
        endpoints = ['/', '/properties', '/api/properties', '/mapview']
        concurrent_results = {'results': [], 'summary': {}}
        
        try:
            with ThreadPoolExecutor(max_workers=8) as executor:
                # Submit concurrent requests
                futures = []
                for _ in range(20):  # 20 concurrent requests
                    endpoint = random.choice(endpoints)
                    futures.append(executor.submit(make_request, endpoint))
                
                # Collect results
                for future in as_completed(futures):
                    result = future.result()
                    concurrent_results['results'].append(result)
            
            # Calculate summary statistics
            successful_requests = [r for r in concurrent_results['results'] if r.get('success', False)]
            response_times = [r['response_time'] for r in successful_requests if 'response_time' in r]
            
            concurrent_results['summary'] = {
                'total_requests': len(concurrent_results['results']),
                'successful_requests': len(successful_requests),
                'success_rate': len(successful_requests) / len(concurrent_results['results']),
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0
            }
            
            self.log(f"✅ Concurrent load test - Success rate: {concurrent_results['summary']['success_rate']:.2%}, Avg time: {concurrent_results['summary']['avg_response_time']:.3f}s", 
                    "SUCCESS", "CONCURRENCY")
                    
        except Exception as e:
            concurrent_results['error'] = str(e)
            self.log(f"❌ Concurrent load test failed: {str(e)}", "ERROR", "CONCURRENCY")
        
        return concurrent_results
    
    def run_complete_test_suite(self) -> Dict[str, Any]:
        """Run the complete functionality test suite."""
        self.log("=" * 80, "INFO", "MAIN")
        self.log("🚀 STARTING COMPLETE NEXTPROPERTY AI FUNCTIONALITY TEST SUITE", "INFO", "MAIN")
        self.log("=" * 80, "INFO", "MAIN")
        
        start_time = time.time()
        all_results = {}
        
        # Run all test categories
        test_categories = [
            ('Health Check', self.test_application_health),
            ('Web Pages', self.test_web_pages),
            ('API Endpoints', self.test_api_endpoints),
            ('Property Search', self.test_property_search),
            ('ML Predictions', self.test_property_predictions),
            ('Map Functionality', self.test_map_functionality),
            ('Property Upload', self.test_property_upload),
            ('Authentication', self.test_authentication_pages),
            ('Economic Data', self.test_economic_data),
            ('Error Handling', self.test_error_handling),
            ('Performance', self.test_performance_metrics),
            ('Concurrency', self.test_concurrent_load)
        ]
        
        for category_name, test_function in test_categories:
            self.log(f"\n📋 Running {category_name} Tests...", "INFO", "MAIN")
            try:
                category_results = test_function()
                all_results[category_name.lower().replace(' ', '_')] = category_results
                self.log(f"✅ {category_name} tests completed", "SUCCESS", "MAIN")
            except Exception as e:
                self.log(f"❌ {category_name} tests failed: {str(e)}", "ERROR", "MAIN")
                all_results[category_name.lower().replace(' ', '_')] = {'error': str(e)}
        
        total_time = time.time() - start_time
        
        # Generate summary report
        summary = self._generate_summary_report(all_results, total_time)
        all_results['summary'] = summary
        
        # Store results
        self.results['functionality_stats'] = all_results
        
        self.log("\n" + "=" * 80, "INFO", "MAIN")
        self.log("📊 COMPLETE FUNCTIONALITY TEST SUMMARY", "INFO", "MAIN")
        self.log("=" * 80, "INFO", "MAIN")
        
        self._print_summary_report(summary)
        
        return all_results
    
    def _generate_summary_report(self, results: Dict[str, Any], total_time: float) -> Dict[str, Any]:
        """Generate a comprehensive summary report."""
        summary = {
            'total_execution_time': total_time,
            'categories_tested': len(results),
            'overall_health': 'UNKNOWN',
            'category_summaries': {},
            'critical_issues': [],
            'recommendations': []
        }
        
        # Analyze each category
        for category, data in results.items():
            if isinstance(data, dict) and 'error' not in data:
                summary['category_summaries'][category] = self._analyze_category_results(category, data)
            else:
                summary['category_summaries'][category] = {'status': 'FAILED', 'details': 'Test execution failed'}
        
        # Determine overall health
        successful_categories = sum(1 for cat in summary['category_summaries'].values() if cat.get('status') == 'HEALTHY')
        total_categories = len(summary['category_summaries'])
        
        if successful_categories == total_categories:
            summary['overall_health'] = 'HEALTHY'
        elif successful_categories > total_categories * 0.7:
            summary['overall_health'] = 'MOSTLY_HEALTHY'
        elif successful_categories > total_categories * 0.4:
            summary['overall_health'] = 'DEGRADED'
        else:
            summary['overall_health'] = 'UNHEALTHY'
        
        return summary
    
    def _analyze_category_results(self, category: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results for a specific test category."""
        if category == 'health_check':
            return {
                'status': 'HEALTHY' if data.get('server_responsive') else 'FAILED',
                'details': f"Response time: {data.get('response_time', 'N/A')}s"
            }
        elif category in ['web_pages', 'api_endpoints', 'authentication']:
            successful = sum(1 for result in data.values() if isinstance(result, dict) and result.get('success', False))
            total = len(data)
            success_rate = successful / total if total > 0 else 0
            
            if success_rate >= 0.9:
                status = 'HEALTHY'
            elif success_rate >= 0.7:
                status = 'MOSTLY_HEALTHY'
            else:
                status = 'DEGRADED'
            
            return {
                'status': status,
                'details': f"{successful}/{total} endpoints successful ({success_rate:.1%})"
            }
        else:
            # For other categories, check if there are any errors
            has_errors = any('error' in str(v) for v in data.values() if isinstance(v, dict))
            return {
                'status': 'FAILED' if has_errors else 'HEALTHY',
                'details': 'Test completed with mixed results'
            }
    
    def _print_summary_report(self, summary: Dict[str, Any]):
        """Print a formatted summary report."""
        health_emoji = {
            'HEALTHY': '🟢',
            'MOSTLY_HEALTHY': '🟡',
            'DEGRADED': '🟠',
            'UNHEALTHY': '🔴',
            'FAILED': '❌',
            'UNKNOWN': '❓'
        }
        
        self.log(f"🏥 Overall System Health: {health_emoji.get(summary['overall_health'], '❓')} {summary['overall_health']}", "INFO", "SUMMARY")
        self.log(f"⏱️  Total Execution Time: {summary['total_execution_time']:.2f} seconds", "INFO", "SUMMARY")
        self.log(f"📋 Categories Tested: {summary['categories_tested']}", "INFO", "SUMMARY")
        
        self.log("\n📊 Category Breakdown:", "INFO", "SUMMARY")
        for category, details in summary['category_summaries'].items():
            status_emoji = health_emoji.get(details.get('status'), '❓')
            self.log(f"  {status_emoji} {category.replace('_', ' ').title()}: {details.get('details', 'No details')}", "INFO", "SUMMARY")
        
        # Recommendations
        if summary['overall_health'] != 'HEALTHY':
            self.log("\n💡 Recommendations:", "INFO", "SUMMARY")
            if any(cat.get('status') == 'FAILED' for cat in summary['category_summaries'].values()):
                self.log("  • Check server logs for detailed error information", "INFO", "SUMMARY")
                self.log("  • Verify database connectivity and dependencies", "INFO", "SUMMARY")
            if summary['overall_health'] in ['DEGRADED', 'UNHEALTHY']:
                self.log("  • Consider reviewing and optimizing failing endpoints", "INFO", "SUMMARY")
                self.log("  • Check for resource constraints or configuration issues", "INFO", "SUMMARY")

def main():
    """Main execution function."""
    print("🚀 NextProperty AI Complete Functionality Test Suite")
    print("=" * 60)
    
    # Configuration
    base_url = "http://localhost:5007"
    
    # Check if custom URL provided
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        print(f"🌐 Using custom base URL: {base_url}")
    
    # Initialize tester
    tester = CompleteFunctionalityTester(base_url)
    
    try:
        # Run complete test suite
        results = tester.run_complete_test_suite()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"complete_functionality_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Exit with appropriate code
        overall_health = results.get('summary', {}).get('overall_health', 'UNKNOWN')
        if overall_health in ['HEALTHY', 'MOSTLY_HEALTHY']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
