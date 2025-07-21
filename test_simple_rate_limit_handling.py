#!/usr/bin/env python3
"""
Simple Rate Limit Error Handling Test
Tests the enhanced error handling components independently
"""

import os
import sys
import time
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class SimpleRateLimitTest:
    """Simple test for rate limit error handling components."""
    
    def __init__(self):
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
    
    def test_enhanced_error_handler_import(self):
        """Test that the enhanced error handler can be imported."""
        self.log("Testing enhanced error handler import...")
        
        try:
            from app.security.enhanced_rate_limit_error_handler import EnhancedRateLimitErrorHandler
            self.log("✅ Enhanced error handler imported successfully", "SUCCESS")
            
            # Test initialization
            handler = EnhancedRateLimitErrorHandler()
            if hasattr(handler, 'abuse_type_messages'):
                self.log("✅ Error handler initialized with abuse type messages", "SUCCESS")
            else:
                self.log("❌ Error handler missing abuse type messages", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error importing enhanced error handler: {str(e)}", "ERROR")
            return False
    
    def test_abuse_detection_handler_import(self):
        """Test that the abuse detection handler can be imported."""
        self.log("Testing abuse detection handler import...")
        
        try:
            from app.security.abuse_detection_handler import handle_abuse_detection_response
            self.log("✅ Abuse detection handler imported successfully", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Error importing abuse detection handler: {str(e)}", "ERROR")
            return False
    
    def test_template_exists(self):
        """Test that the enhanced template exists."""
        self.log("Testing enhanced template existence...")
        
        template_path = os.path.join(
            os.path.dirname(__file__), 
            'app', 'templates', 'errors', 'enhanced_rate_limit.html'
        )
        
        if os.path.exists(template_path):
            self.log("✅ Enhanced rate limit template exists", "SUCCESS")
            
            # Check template size (should be substantial)
            file_size = os.path.getsize(template_path)
            if file_size > 5000:  # Should be at least 5KB
                self.log(f"✅ Template size is adequate ({file_size} bytes)", "SUCCESS")
                return True
            else:
                self.log(f"❌ Template size too small ({file_size} bytes)", "ERROR")
                return False
        else:
            self.log("❌ Enhanced rate limit template missing", "ERROR")
            return False
    
    def test_abuse_type_configurations(self):
        """Test that abuse type configurations are complete."""
        self.log("Testing abuse type configurations...")
        
        try:
            from app.security.enhanced_rate_limit_error_handler import EnhancedRateLimitErrorHandler
            
            handler = EnhancedRateLimitErrorHandler()
            
            # Check that all expected abuse types are configured
            expected_abuse_types = [
                'resource_exhaustion',
                'rapid_requests',
                'brute_force',
                'scraping',
                'api_abuse',
                'suspicious_patterns'
            ]
            
            for abuse_type in expected_abuse_types:
                if abuse_type in handler.abuse_type_messages:
                    config = handler.abuse_type_messages[abuse_type]
                    
                    # Check required fields
                    required_fields = ['title', 'message', 'icon', 'color', 'guidance']
                    for field in required_fields:
                        if field in config:
                            self.log(f"✅ Abuse type '{abuse_type}' has field '{field}'", "SUCCESS")
                        else:
                            self.log(f"❌ Abuse type '{abuse_type}' missing field '{field}'", "ERROR")
                            return False
                else:
                    self.log(f"❌ Abuse type '{abuse_type}' not configured", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error testing abuse type configurations: {str(e)}", "ERROR")
            return False
    
    def test_time_formatting(self):
        """Test time formatting functionality."""
        self.log("Testing time formatting...")
        
        try:
            from app.security.enhanced_rate_limit_error_handler import EnhancedRateLimitErrorHandler
            
            handler = EnhancedRateLimitErrorHandler()
            
            # Test various time formats
            test_cases = [
                (30, "30 seconds"),
                (90, "1 minutes and 30 seconds"),
                (3600, "1 hours"),
                (3660, "1 hours and 1 minutes"),
                (7200, "2 hours")
            ]
            
            for seconds, expected_contains in test_cases:
                result = handler._format_time_duration(seconds)
                if expected_contains.split()[0] in result:  # Check if the number is in the result
                    self.log(f"✅ Time formatting for {seconds}s: {result}", "SUCCESS")
                else:
                    self.log(f"❌ Time formatting for {seconds}s failed: {result}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error testing time formatting: {str(e)}", "ERROR")
            return False
    
    def test_severity_descriptions(self):
        """Test severity level descriptions."""
        self.log("Testing severity descriptions...")
        
        try:
            from app.security.enhanced_rate_limit_error_handler import EnhancedRateLimitErrorHandler
            
            handler = EnhancedRateLimitErrorHandler()
            
            for level in range(1, 6):
                description = handler._get_severity_description(level)
                if description and len(description) > 10:  # Should be a meaningful description
                    self.log(f"✅ Severity level {level}: {description}", "SUCCESS")
                else:
                    self.log(f"❌ Severity level {level} description inadequate", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error testing severity descriptions: {str(e)}", "ERROR")
            return False
    
    def test_file_structure(self):
        """Test that all required files exist."""
        self.log("Testing file structure...")
        
        required_files = [
            'app/security/enhanced_rate_limit_error_handler.py',
            'app/security/abuse_detection_handler.py',
            'app/templates/errors/enhanced_rate_limit.html'
        ]
        
        base_path = os.path.dirname(__file__)
        
        for file_path in required_files:
            full_path = os.path.join(base_path, file_path)
            if os.path.exists(full_path):
                self.log(f"✅ File exists: {file_path}", "SUCCESS")
            else:
                self.log(f"❌ File missing: {file_path}", "ERROR")
                return False
        
        return True
    
    def run_all_tests(self):
        """Run all tests and provide a summary."""
        self.log("🚀 Starting Simple Rate Limit Error Handling Tests", "INFO")
        self.log("=" * 60, "INFO")
        
        start_time = time.time()
        
        # Run tests
        tests = [
            ("File Structure", self.test_file_structure),
            ("Enhanced Error Handler Import", self.test_enhanced_error_handler_import),
            ("Abuse Detection Handler Import", self.test_abuse_detection_handler_import),
            ("Template Exists", self.test_template_exists),
            ("Abuse Type Configurations", self.test_abuse_type_configurations),
            ("Time Formatting", self.test_time_formatting),
            ("Severity Descriptions", self.test_severity_descriptions),
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
            self.log("🎉 ALL TESTS PASSED! Enhanced error handling components are ready.", "SUCCESS")
            self.log("\n📋 Next Steps:", "INFO")
            self.log("1. Start your Flask application", "INFO")
            self.log("2. Test the error pages by visiting:", "INFO")
            self.log("   - /test/abuse-detection (if DEBUG=True)", "INFO")
            self.log("   - /test/abuse-detection/api (for API response)", "INFO")
            self.log("3. Trigger real rate limits to test the integration", "INFO")
        else:
            self.log("⚠️  Some tests failed. Please review the errors above.", "ERROR")
        
        return passed_tests == total_tests


def main():
    """Main function to run the tests."""
    tester = SimpleRateLimitTest()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
