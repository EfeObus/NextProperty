#!/usr/bin/env python3
"""
Enhanced Rate Limit Error Handling Test Suite
Tests all rate limiting features and error responses for NextProperty AI
"""

import os
import sys
import time
import requests
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.security.enhanced_rate_limit_error_handler import enhanced_rate_limit_handler
from app.security.abuse_detection_handler import simulate_abuse_detection_error


class RateLimitErrorHandlingTester:
    """Comprehensive tester for rate limit error handling."""
    
    def __init__(self):
        self.app = create_app()
        self.client = None
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        colored_message = f"[{timestamp}] {level}: {message}"
        print(colored_message)
        
        self.test_results.append({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })
    
    def setup_test_client(self):
        """Set up Flask test client."""
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        self.log("Test client initialized", "SUCCESS")
    
    def test_abuse_detection_web_response(self):
        """Test web-based abuse detection error page."""
        self.log("Testing abuse detection web response...")
        
        try:
            with self.app.test_request_context('/', headers={'User-Agent': 'Mozilla/5.0'}):
                test_data = {
                    "abuse_type": "resource_exhaustion",
                    "error": "Request blocked due to abuse detection",
                    "incident_id": 1753105363.67304,
                    "level": 4,
                    "retry_after": 504,
                    "type": "abuse_rate_limit"
                }
                
                response = enhanced_rate_limit_handler.handle_abuse_detection_error(test_data)
                
                if response.status_code == 429:
                    self.log("✅ Web response status code correct (429)", "SUCCESS")
                else:
                    self.log(f"❌ Wrong status code: {response.status_code}", "ERROR")
                    return False
                
                # Check headers
                if 'X-RateLimit-Type' in response.headers:
                    self.log("✅ Rate limit headers present", "SUCCESS")
                else:
                    self.log("❌ Missing rate limit headers", "ERROR")
                    return False
                
                # Check if HTML content is present
                response_data = response.get_data(as_text=True)
                if 'NextProperty AI' in response_data and 'resource_exhaustion' in response_data:
                    self.log("✅ Web template rendered correctly", "SUCCESS")
                    return True
                else:
                    self.log("❌ Web template rendering failed", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Error in web response test: {str(e)}", "ERROR")
            return False
    
    def test_abuse_detection_api_response(self):
        """Test API-based abuse detection error response."""
        self.log("Testing abuse detection API response...")
        
        try:
            with self.app.test_request_context('/api/test', 
                                             headers={'Content-Type': 'application/json', 'Accept': 'application/json'}):
                test_data = {
                    "abuse_type": "rapid_requests",
                    "error": "Request blocked due to abuse detection",
                    "incident_id": 1753105363.67304,
                    "level": 3,
                    "retry_after": 300,
                    "type": "abuse_rate_limit"
                }
                
                response = enhanced_rate_limit_handler.handle_abuse_detection_error(test_data)
                
                if response.status_code == 429:
                    self.log("✅ API response status code correct (429)", "SUCCESS")
                else:
                    self.log(f"❌ Wrong status code: {response.status_code}", "ERROR")
                    return False
                
                # Check if response is JSON
                if response.is_json:
                    response_json = response.get_json()
                    
                    # Check required fields
                    required_fields = ['error', 'error_code', 'type', 'abuse_type', 'retry_after', 'guidance']
                    for field in required_fields:
                        if field in response_json:
                            self.log(f"✅ API field '{field}' present", "SUCCESS")
                        else:
                            self.log(f"❌ API field '{field}' missing", "ERROR")
                            return False
                    
                    # Check specific values
                    if response_json.get('type') == 'abuse_rate_limit':
                        self.log("✅ API response type correct", "SUCCESS")
                    else:
                        self.log("❌ API response type incorrect", "ERROR")
                        return False
                    
                    return True
                else:
                    self.log("❌ API response is not JSON", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Error in API response test: {str(e)}", "ERROR")
            return False
    
    def test_different_abuse_types(self):
        """Test different abuse types for proper handling."""
        self.log("Testing different abuse types...")
        
        abuse_types = [
            'resource_exhaustion',
            'rapid_requests',
            'brute_force',
            'scraping',
            'api_abuse',
            'suspicious_patterns'
        ]
        
        for abuse_type in abuse_types:
            try:
                with self.app.test_request_context('/'):
                    test_data = {
                        "abuse_type": abuse_type,
                        "error": f"Request blocked due to {abuse_type}",
                        "incident_id": int(time.time()),
                        "level": 2,
                        "retry_after": 180,
                        "type": "abuse_rate_limit"
                    }
                    
                    response = enhanced_rate_limit_handler.handle_abuse_detection_error(test_data)
                    
                    if response.status_code == 429:
                        self.log(f"✅ Abuse type '{abuse_type}' handled correctly", "SUCCESS")
                    else:
                        self.log(f"❌ Abuse type '{abuse_type}' failed", "ERROR")
                        return False
                        
            except Exception as e:
                self.log(f"❌ Error testing abuse type '{abuse_type}': {str(e)}", "ERROR")
                return False
        
        return True
    
    def test_severity_levels(self):
        """Test different severity levels."""
        self.log("Testing severity levels...")
        
        for level in range(1, 6):
            try:
                with self.app.test_request_context('/'):
                    test_data = {
                        "abuse_type": "resource_exhaustion",
                        "error": "Request blocked due to abuse detection",
                        "incident_id": int(time.time()),
                        "level": level,
                        "retry_after": level * 100,  # Scale retry time with level
                        "type": "abuse_rate_limit"
                    }
                    
                    response = enhanced_rate_limit_handler.handle_abuse_detection_error(test_data)
                    
                    if response.status_code == 429:
                        self.log(f"✅ Severity level {level} handled correctly", "SUCCESS")
                    else:
                        self.log(f"❌ Severity level {level} failed", "ERROR")
                        return False
                        
            except Exception as e:
                self.log(f"❌ Error testing severity level {level}: {str(e)}", "ERROR")
                return False
        
        return True
    
    def test_template_rendering(self):
        """Test template rendering capabilities."""
        self.log("Testing template rendering...")
        
        try:
            with self.app.app_context():
                # Test enhanced template exists
                template_path = os.path.join(
                    self.app.template_folder, 
                    'errors', 
                    'enhanced_rate_limit.html'
                )
                
                if os.path.exists(template_path):
                    self.log("✅ Enhanced rate limit template exists", "SUCCESS")
                else:
                    self.log("❌ Enhanced rate limit template missing", "ERROR")
                    return False
                
                # Test template can be rendered
                from flask import render_template
                
                rendered = render_template(
                    'errors/enhanced_rate_limit.html',
                    abuse_type='resource_exhaustion',
                    title='System Resources Overloaded',
                    message='Test message',
                    icon='⚡',
                    color='#ff6b6b',
                    guidance='Test guidance',
                    retry_after=300,
                    retry_after_human='5 minutes',
                    level=4,
                    incident_id=123456,
                    timestamp='2025-01-21 12:00:00',
                    severity_description='High severity test',
                    next_action='Test action'
                )
                
                if rendered and len(rendered) > 1000:  # Template should be substantial
                    self.log("✅ Template renders correctly", "SUCCESS")
                    return True
                else:
                    self.log("❌ Template rendering failed or too short", "ERROR")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Error in template rendering test: {str(e)}", "ERROR")
            return False
    
    def test_error_handler_registration(self):
        """Test that error handlers are properly registered."""
        self.log("Testing error handler registration...")
        
        try:
            # Check if the enhanced error handler is initialized
            if hasattr(enhanced_rate_limit_handler, 'app') and enhanced_rate_limit_handler.app:
                self.log("✅ Enhanced error handler is initialized", "SUCCESS")
            else:
                self.log("❌ Enhanced error handler not initialized", "ERROR")
                return False
            
            # Check if error handlers are registered
            error_handlers = self.app.error_handler_spec.get(None, {})
            if 429 in error_handlers:
                self.log("✅ 429 error handler registered", "SUCCESS")
            else:
                self.log("❌ 429 error handler not registered", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error in handler registration test: {str(e)}", "ERROR")
            return False
    
    def test_response_headers(self):
        """Test that proper headers are set in responses."""
        self.log("Testing response headers...")
        
        try:
            with self.app.test_request_context('/'):
                test_data = {
                    "abuse_type": "resource_exhaustion",
                    "error": "Request blocked due to abuse detection",
                    "incident_id": 1753105363.67304,
                    "level": 4,
                    "retry_after": 504,
                    "type": "abuse_rate_limit"
                }
                
                response = enhanced_rate_limit_handler.handle_abuse_detection_error(test_data)
                
                # Check required headers
                required_headers = [
                    'Retry-After',
                    'X-RateLimit-Type',
                    'X-RateLimit-Abuse-Type',
                    'X-RateLimit-Level',
                    'X-Incident-ID'
                ]
                
                for header in required_headers:
                    if header in response.headers:
                        self.log(f"✅ Header '{header}' present: {response.headers[header]}", "SUCCESS")
                    else:
                        self.log(f"❌ Header '{header}' missing", "ERROR")
                        return False
                
                return True
                
        except Exception as e:
            self.log(f"❌ Error in headers test: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests and provide a summary."""
        self.log("🚀 Starting Enhanced Rate Limit Error Handling Tests", "INFO")
        self.log("=" * 60, "INFO")
        
        start_time = time.time()
        
        # Setup
        self.setup_test_client()
        
        # Run tests
        tests = [
            ("Error Handler Registration", self.test_error_handler_registration),
            ("Template Rendering", self.test_template_rendering),
            ("Web Response", self.test_abuse_detection_web_response),
            ("API Response", self.test_abuse_detection_api_response),
            ("Different Abuse Types", self.test_different_abuse_types),
            ("Severity Levels", self.test_severity_levels),
            ("Response Headers", self.test_response_headers),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Running test: {test_name}", "INFO")
            try:
                if test_func():
                    passed_tests += 1
                    self.log(f"✅ Test '{test_name}' PASSED", "SUCCESS")
                else:
                    self.log(f"❌ Test '{test_name}' FAILED", "ERROR")
            except Exception as e:
                self.log(f"❌ Test '{test_name}' CRASHED: {str(e)}", "ERROR")
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("\n" + "=" * 60, "INFO")
        self.log("📊 TEST SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        self.log(f"Total Tests: {total_tests}", "INFO")
        self.log(f"Passed: {passed_tests}", "SUCCESS" if passed_tests == total_tests else "INFO")
        self.log(f"Failed: {total_tests - passed_tests}", "ERROR" if passed_tests != total_tests else "INFO")
        self.log(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%", "INFO")
        self.log(f"Duration: {duration:.2f}s", "INFO")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED! Enhanced error handling is working correctly.", "SUCCESS")
        else:
            self.log("⚠️  Some tests failed. Please review the errors above.", "ERROR")
        
        return passed_tests == total_tests


def main():
    """Main function to run the tests."""
    tester = RateLimitErrorHandlingTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
