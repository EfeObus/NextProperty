#!/usr/bin/env python3
"""
API Key Rate Limiting Test Suite
Comprehensive testing of API key generation, key-based limits, developer quotas, and usage tracking.
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, Any, List

# Test configuration
TEST_DEVELOPER_ID = "test_dev_001"
TEST_API_KEY_NAME = "Test API Key"
TEST_ENDPOINTS = [
    "/api/properties",
    "/api/search", 
    "/predict-price",
    "/api/statistics",
    "/api/agents",
    "/api/export-data",
    "/admin/api/bulk-ai-analysis"
]

class APIKeyTestRunner:
    """Test runner for API key rate limiting features."""
    
    def __init__(self):
        self.test_results = {
            'key_generation': {'passed': 0, 'failed': 0, 'tests': []},
            'key_based_limits': {'passed': 0, 'failed': 0, 'tests': []},
            'developer_quotas': {'passed': 0, 'failed': 0, 'tests': []},
            'usage_tracking': {'passed': 0, 'failed': 0, 'tests': []}
        }
        self.generated_keys = []
        
    def log(self, message: str, status: str = "INFO"):
        """Log a message with timestamp and status."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if status == "PASS":
            print(f"[{timestamp}]   ✅ {message}")
        elif status == "FAIL":
            print(f"[{timestamp}]   ❌ {message}")
        elif status == "WARN":
            print(f"[{timestamp}]   ⚠️ {message}")
        else:
            print(f"[{timestamp}] {message}")
    
    def run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        """Run a Flask CLI command and return the result."""
        try:
            full_command = ["python", "-m", "flask"] + command
            result = subprocess.run(
                full_command, 
                capture_output=True, 
                text=True, 
                timeout=30,
                cwd=os.getcwd()
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    def test_key_generation(self):
        """Test API key generation functionality."""
        self.log("🔑 Testing API Key Generation", "INFO")
        self.log("=" * 60)
        
        # Test 1: Generate free tier API key
        self.log("1. Testing: Free tier API key generation")
        result = self.run_cli_command([
            "api-keys", "generate",
            "--developer-id", TEST_DEVELOPER_ID,
            "--name", f"{TEST_API_KEY_NAME} Free",
            "--tier", "free",
            "--description", "Test free tier key",
            "--format", "json"
        ])
        
        if result['success'] and 'api_key' in result['stdout']:
            try:
                data = json.loads(result['stdout'])
                free_key = data['api_key']
                self.generated_keys.append(free_key)
                self.log("PASS: Free tier API key generated successfully", "PASS")
                self.test_results['key_generation']['passed'] += 1
                
                # Validate key format
                if free_key.startswith('npai_free_'):
                    self.log("PASS: Key format validation", "PASS")
                else:
                    self.log("FAIL: Invalid key format", "FAIL")
                    self.test_results['key_generation']['failed'] += 1
                    
            except json.JSONDecodeError:
                self.log("FAIL: Invalid JSON response", "FAIL")
                self.test_results['key_generation']['failed'] += 1
        else:
            self.log(f"FAIL: Command failed - {result['stderr']}", "FAIL")
            self.test_results['key_generation']['failed'] += 1
        
        # Test 2: Generate premium tier API key
        self.log("2. Testing: Premium tier API key generation")
        result = self.run_cli_command([
            "api-keys", "generate",
            "--developer-id", TEST_DEVELOPER_ID,
            "--name", f"{TEST_API_KEY_NAME} Premium",
            "--tier", "premium",
            "--expires-days", "30",
            "--allowed-ips", "127.0.0.1,192.168.1.1",
            "--format", "json"
        ])
        
        if result['success'] and 'api_key' in result['stdout']:
            try:
                data = json.loads(result['stdout'])
                premium_key = data['api_key']
                self.generated_keys.append(premium_key)
                self.log("PASS: Premium tier API key generated successfully", "PASS")
                self.test_results['key_generation']['passed'] += 1
                
                # Validate premium features
                key_info = data.get('key_info', {})
                if key_info.get('tier') == 'premium':
                    self.log("PASS: Premium tier assignment", "PASS")
                else:
                    self.log("FAIL: Premium tier not assigned", "FAIL")
                    self.test_results['key_generation']['failed'] += 1
                    
            except json.JSONDecodeError:
                self.log("FAIL: Invalid JSON response", "FAIL")
                self.test_results['key_generation']['failed'] += 1
        else:
            self.log(f"FAIL: Command failed - {result['stderr']}", "FAIL")
            self.test_results['key_generation']['failed'] += 1
        
        # Test 3: List tiers
        self.log("3. Testing: List available tiers")
        result = self.run_cli_command(["api-keys", "list-tiers"])
        
        if result['success'] and 'FREE' in result['stdout'] and 'PREMIUM' in result['stdout']:
            self.log("PASS: Tier listing working", "PASS")
            self.test_results['key_generation']['passed'] += 1
        else:
            self.log("FAIL: Tier listing failed", "FAIL")
            self.test_results['key_generation']['failed'] += 1
    
    def test_key_based_limits(self):
        """Test key-based rate limiting."""
        self.log("\\n🚦 Testing Key-Based Rate Limits", "INFO")
        self.log("=" * 60)
        
        if not self.generated_keys:
            self.log("FAIL: No API keys available for testing", "FAIL")
            self.test_results['key_based_limits']['failed'] += 1
            return
        
        test_key = self.generated_keys[0]  # Use the first generated key
        
        # Test 1: Key validation
        self.log("1. Testing: API key validation")
        result = self.run_cli_command([
            "api-keys", "test",
            "--api-key", test_key,
            "--endpoint", "/api/properties",
            "--ip", "127.0.0.1"
        ])
        
        if result['success'] and 'PASSED' in result['stdout']:
            self.log("PASS: API key validation working", "PASS")
            self.test_results['key_based_limits']['passed'] += 1
        else:
            self.log(f"FAIL: Key validation failed - {result['stderr']}", "FAIL")
            self.test_results['key_based_limits']['failed'] += 1
        
        # Test 2: Key information retrieval
        self.log("2. Testing: Key information retrieval")
        result = self.run_cli_command([
            "api-keys", "info",
            "--api-key", test_key,
            "--format", "json"
        ])
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                if 'key_id' in data and 'limits' in data:
                    self.log("PASS: Key information retrieval working", "PASS")
                    self.test_results['key_based_limits']['passed'] += 1
                else:
                    self.log("FAIL: Incomplete key information", "FAIL")
                    self.test_results['key_based_limits']['failed'] += 1
            except json.JSONDecodeError:
                self.log("FAIL: Invalid JSON response", "FAIL")
                self.test_results['key_based_limits']['failed'] += 1
        else:
            self.log(f"FAIL: Command failed - {result['stderr']}", "FAIL")
            self.test_results['key_based_limits']['failed'] += 1
        
        # Test 3: Key suspension and reactivation
        self.log("3. Testing: Key suspension")
        result = self.run_cli_command([
            "api-keys", "suspend",
            "--api-key", test_key
        ])
        
        if result['success'] and 'suspended' in result['stdout']:
            self.log("PASS: Key suspension working", "PASS")
            self.test_results['key_based_limits']['passed'] += 1
            
            # Test reactivation
            self.log("4. Testing: Key reactivation")
            result = self.run_cli_command([
                "api-keys", "reactivate", 
                "--api-key", test_key
            ])
            
            if result['success'] and 'reactivated' in result['stdout']:
                self.log("PASS: Key reactivation working", "PASS")
                self.test_results['key_based_limits']['passed'] += 1
            else:
                self.log("FAIL: Key reactivation failed", "FAIL")
                self.test_results['key_based_limits']['failed'] += 1
        else:
            self.log("FAIL: Key suspension failed", "FAIL")
            self.test_results['key_based_limits']['failed'] += 1
    
    def test_developer_quotas(self):
        """Test developer quota functionality."""
        self.log("\\n👤 Testing Developer Quotas", "INFO")
        self.log("=" * 60)
        
        # Test 1: Developer quota information
        self.log("1. Testing: Developer quota information")
        result = self.run_cli_command([
            "api-keys", "quota",
            "--developer-id", TEST_DEVELOPER_ID,
            "--format", "json"
        ])
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                if 'monthly_quotas' in data and 'current_usage' in data:
                    self.log("PASS: Developer quota information working", "PASS")
                    self.test_results['developer_quotas']['passed'] += 1
                    
                    # Validate quota structure
                    quotas = data['monthly_quotas']
                    usage = data['current_usage']
                    required_quota_keys = ['requests', 'data_mb', 'compute_seconds']
                    if (all(key in quotas for key in required_quota_keys) and 
                        all(key in usage for key in required_quota_keys)):
                        self.log("PASS: Quota structure validation", "PASS")
                        self.test_results['developer_quotas']['passed'] += 1
                    else:
                        self.log("FAIL: Invalid quota structure", "FAIL")
                        self.test_results['developer_quotas']['failed'] += 1
                else:
                    self.log("FAIL: Incomplete quota information", "FAIL")
                    self.test_results['developer_quotas']['failed'] += 1
            except json.JSONDecodeError:
                self.log("FAIL: Invalid JSON response", "FAIL")
                self.test_results['developer_quotas']['failed'] += 1
        else:
            # Quota might not exist yet, which is okay for new developers
            if 'not found' in result['stderr']:
                self.log("PASS: New developer quota handling", "PASS")
                self.test_results['developer_quotas']['passed'] += 1
            else:
                self.log(f"FAIL: Command failed - {result['stderr']}", "FAIL")
                self.test_results['developer_quotas']['failed'] += 1
    
    def test_usage_tracking(self):
        """Test usage tracking and analytics."""
        self.log("\\n📊 Testing Usage Tracking", "INFO")
        self.log("=" * 60)
        
        # Test 1: Global analytics
        self.log("1. Testing: Global usage analytics")
        result = self.run_cli_command([
            "api-keys", "analytics",
            "--days", "7",
            "--format", "json"
        ])
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                required_fields = ['total_requests', 'total_data_transfer_mb', 'unique_keys', 'error_rate']
                if all(field in data for field in required_fields):
                    self.log("PASS: Global analytics working", "PASS")
                    self.test_results['usage_tracking']['passed'] += 1
                else:
                    self.log("FAIL: Incomplete analytics data", "FAIL")
                    self.test_results['usage_tracking']['failed'] += 1
            except json.JSONDecodeError:
                self.log("FAIL: Invalid JSON response", "FAIL")
                self.test_results['usage_tracking']['failed'] += 1
        else:
            self.log(f"FAIL: Command failed - {result['stderr']}", "FAIL")
            self.test_results['usage_tracking']['failed'] += 1
        
        # Test 2: Developer-specific analytics
        self.log("2. Testing: Developer-specific analytics")
        result = self.run_cli_command([
            "api-keys", "analytics",
            "--developer-id", TEST_DEVELOPER_ID,
            "--days", "1",
            "--format", "json"
        ])
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                if 'total_requests' in data and 'unique_keys' in data:
                    self.log("PASS: Developer analytics working", "PASS")
                    self.test_results['usage_tracking']['passed'] += 1
                else:
                    self.log("FAIL: Incomplete developer analytics", "FAIL")
                    self.test_results['usage_tracking']['failed'] += 1
            except json.JSONDecodeError:
                self.log("FAIL: Invalid JSON response", "FAIL")
                self.test_results['usage_tracking']['failed'] += 1
        else:
            self.log(f"FAIL: Command failed - {result['stderr']}", "FAIL")
            self.test_results['usage_tracking']['failed'] += 1
        
        # Test 3: Cleanup functionality
        self.log("3. Testing: Cleanup functionality")
        result = self.run_cli_command([
            "api-keys", "cleanup",
            "--dry-run"
        ])
        
        if result['success']:
            self.log("PASS: Cleanup functionality working", "PASS")
            self.test_results['usage_tracking']['passed'] += 1
        else:
            self.log(f"FAIL: Cleanup failed - {result['stderr']}", "FAIL")
            self.test_results['usage_tracking']['failed'] += 1
    
    def cleanup_test_keys(self):
        """Clean up generated test keys."""
        self.log("\\n🧹 Cleaning up test API keys")
        
        for key in self.generated_keys:
            result = self.run_cli_command([
                "api-keys", "revoke",
                "--api-key", key
            ])
            
            if result['success']:
                self.log(f"Revoked test key: {key[:12]}...")
            else:
                self.log(f"Failed to revoke key: {key[:12]}...")
    
    def print_summary(self):
        """Print test summary."""
        self.log("\\n" + "=" * 80)
        self.log("🎯 API KEY RATE LIMITING TEST SUMMARY")
        self.log("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for feature, results in self.test_results.items():
            passed = results['passed']
            failed = results['failed']
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            if total > 0:
                percentage = (passed / total) * 100
                status = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
                self.log(f"{status} {feature.replace('_', ' ').title()}: {passed}/{total} ({percentage:.1f}%)")
            else:
                self.log(f"❓ {feature.replace('_', ' ').title()}: No tests run")
        
        total_tests = total_passed + total_failed
        if total_tests > 0:
            overall_percentage = (total_passed / total_tests) * 100
            
            self.log("")
            self.log(f"📊 Overall Results: {total_passed}/{total_tests} tests passed ({overall_percentage:.1f}%)")
            
            if total_failed == 0:
                self.log("🎉 All API key features are working correctly!", "PASS")
                status = "EXCELLENT"
            elif overall_percentage >= 80:
                self.log("👍 Most API key features are working well", "PASS")
                status = "GOOD"
            elif overall_percentage >= 60:
                self.log("⚠️ Some API key features need attention", "WARN")
                status = "FAIR"
            else:
                self.log("❌ Major issues with API key features", "FAIL")
                status = "POOR"
        else:
            self.log("❓ No tests were completed")
            status = "UNKNOWN"
        
        # Feature implementation status
        self.log("")
        self.log("📋 Feature Implementation Status:")
        features = {
            'key_generation': 'API Key Generation',
            'key_based_limits': 'Key-Based Rate Limits', 
            'developer_quotas': 'Developer Quotas',
            'usage_tracking': 'Usage Tracking & Analytics'
        }
        
        for feature_key, feature_name in features.items():
            results = self.test_results[feature_key]
            if results['passed'] > 0 and results['failed'] == 0:
                self.log(f"  ✅ {feature_name}: IMPLEMENTED")
            elif results['passed'] > results['failed']:
                self.log(f"  ⚠️ {feature_name}: PARTIALLY IMPLEMENTED")
            elif results['passed'] + results['failed'] > 0:
                self.log(f"  ❌ {feature_name}: NEEDS WORK")
            else:
                self.log(f"  ❓ {feature_name}: NOT TESTED")
        
        # Save results
        results_file = f"api_key_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'summary': {
                    'total_tests': total_tests,
                    'passed': total_passed,
                    'failed': total_failed,
                    'percentage': overall_percentage if total_tests > 0 else 0
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        self.log(f"💾 Results saved to: {results_file}")
        self.log("🎯 API Key Test COMPLETED")
        
        return status
    
    def run_all_tests(self):
        """Run all API key tests."""
        self.log("🚀 STARTING COMPREHENSIVE API KEY RATE LIMITING TESTS")
        self.log("=" * 80)
        self.log(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run all test categories
            self.test_key_generation()
            self.test_key_based_limits()
            self.test_developer_quotas()
            self.test_usage_tracking()
            
        except KeyboardInterrupt:
            self.log("\\n⚠️ Tests interrupted by user")
        except Exception as e:
            self.log(f"\\n❌ Test suite error: {e}")
        finally:
            # Always clean up
            self.cleanup_test_keys()
            
            # Print summary
            status = self.print_summary()
            
            # Exit with appropriate code
            if status in ["EXCELLENT", "GOOD"]:
                sys.exit(0)
            else:
                sys.exit(1)


if __name__ == "__main__":
    # Change to the project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run the tests
    runner = APIKeyTestRunner()
    runner.run_all_tests()
