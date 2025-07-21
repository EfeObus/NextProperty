"""
Comprehensive Test Suite for Geographic Rate Limiting System
Tests Canadian provincial, city, and timezone-based rate limiting.
"""

import time
import json
import requests
import subprocess
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import threading


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class GeographicLimitingTest:
    """Comprehensive test suite for geographic rate limiting."""
    
    def __init__(self, base_url: str = "http://localhost:5007"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {
            'country_limits': [],
            'timezone_restrictions': [],
            'regional_quotas': [],
            'geo_blocking': [],
            'performance_metrics': {},
            'errors': []
        }
        self.start_time = time.time()
    
    def log(self, message: str, level: str = "INFO") -> None:
        """Enhanced logging with color coding."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": Colors.OKBLUE,
            "SUCCESS": Colors.OKGREEN,
            "WARNING": Colors.WARNING,
            "ERROR": Colors.FAIL,
            "HEADER": Colors.HEADER
        }
        color = colors.get(level, Colors.ENDC)
        print(f"{color}[{timestamp}] {message}{Colors.ENDC}")
    
    def test_country_limits(self) -> bool:
        """Test country-based limiting (Canada only)."""
        self.log("🇨🇦 Testing Country Limits (Canada Only)", "HEADER")
        self.log("=" * 60, "INFO")
        
        test_cases = [
            {
                'name': 'Canadian IP - Toronto',
                'client_id': 'test_canadian_user_toronto',
                'ip_address': '99.252.1.100',  # Mock Canadian IP
                'expected_allowed': True,
                'expected_location': 'Canada'
            },
            {
                'name': 'Canadian IP - Vancouver',
                'client_id': 'test_canadian_user_vancouver',
                'ip_address': '24.108.1.200',  # Mock Canadian IP
                'expected_allowed': True,
                'expected_location': 'Canada'
            },
            {
                'name': 'Non-Canadian IP - US',
                'client_id': 'test_us_user',
                'ip_address': '8.8.8.8',  # Google DNS (US)
                'expected_allowed': False,
                'expected_reason': 'geo_blocked'
            },
            {
                'name': 'Non-Canadian IP - International',
                'client_id': 'test_intl_user',
                'ip_address': '1.1.1.1',  # Cloudflare DNS (International)
                'expected_allowed': False,
                'expected_reason': 'geo_blocked'
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            self.log(f"\n{i}. Testing: {test_case['name']}", "INFO")
            
            try:
                # Test using CLI command
                result = subprocess.run([
                    "python", "-m", "flask", "geographic-limiting", "test-client",
                    test_case['client_id'], test_case['ip_address']
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    output = result.stdout
                    
                    if test_case['expected_allowed']:
                        if "Request ALLOWED" in output:
                            self.log(f"  ✅ PASS: Canadian IP correctly allowed", "SUCCESS")
                            self.test_results['country_limits'].append({
                                'test': test_case['name'],
                                'status': 'PASS',
                                'ip': test_case['ip_address']
                            })
                        else:
                            self.log(f"  ❌ FAIL: Canadian IP incorrectly blocked", "ERROR")
                            all_passed = False
                    else:
                        if "Request BLOCKED" in output and test_case['expected_reason'] in output:
                            self.log(f"  ✅ PASS: Non-Canadian IP correctly blocked", "SUCCESS")
                            self.test_results['country_limits'].append({
                                'test': test_case['name'],
                                'status': 'PASS',
                                'ip': test_case['ip_address'],
                                'reason': test_case['expected_reason']
                            })
                        else:
                            self.log(f"  ❌ FAIL: Non-Canadian IP incorrectly allowed", "ERROR")
                            all_passed = False
                else:
                    self.log(f"  ❌ ERROR: CLI command failed: {result.stderr}", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"  ❌ ERROR: {str(e)}", "ERROR")
                all_passed = False
        
        return all_passed
    
    def test_timezone_restrictions(self) -> bool:
        """Test timezone-based restrictions."""
        self.log("\n🕐 Testing Timezone Restrictions", "HEADER")
        self.log("=" * 60, "INFO")
        
        # Test timezone status CLI command
        self.log("1. Testing timezone status command", "INFO")
        
        try:
            result = subprocess.run([
                "python", "-m", "flask", "geographic-limiting", "timezone-status"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                output = result.stdout
                if "Canadian Timezone Status" in output:
                    self.log("  ✅ PASS: Timezone status command working", "SUCCESS")
                    
                    # Count active vs restricted timezones
                    active_count = output.count("🟢")
                    restricted_count = output.count("🔴")
                    
                    self.log(f"  Active timezones: {active_count}", "INFO")
                    self.log(f"  Restricted timezones: {restricted_count}", "INFO")
                    
                    self.test_results['timezone_restrictions'].append({
                        'test': 'timezone_status_command',
                        'status': 'PASS',
                        'active_timezones': active_count,
                        'restricted_timezones': restricted_count
                    })
                    
                    return True
                else:
                    self.log("  ❌ FAIL: Timezone status command output invalid", "ERROR")
                    return False
            else:
                self.log(f"  ❌ ERROR: CLI command failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"  ❌ ERROR: {str(e)}", "ERROR")
            return False
    
    def test_regional_quotas(self) -> bool:
        """Test regional quota system."""
        self.log("\n📊 Testing Regional Quotas", "HEADER")
        self.log("=" * 60, "INFO")
        
        test_cases = [
            {
                'name': 'Province Quota Report',
                'command': ['python', '-m', 'flask', 'geographic-limiting', 'quota-report', '--region-type', 'province'],
                'expected_content': ['Ontario', 'Quebec', 'British Columbia']
            },
            {
                'name': 'City Quota Report',
                'command': ['python', '-m', 'flask', 'geographic-limiting', 'quota-report', '--region-type', 'city'],
                'expected_content': ['Toronto', 'Montreal', 'Vancouver']
            },
            {
                'name': 'All Regions Report',
                'command': ['python', '-m', 'flask', 'geographic-limiting', 'quota-report'],
                'expected_content': ['province_', 'city_', 'Usage']
            }
        ]
        
        all_passed = True
        
        for i, test_case in enumerate(test_cases, 1):
            self.log(f"\n{i}. Testing: {test_case['name']}", "INFO")
            
            try:
                result = subprocess.run(
                    test_case['command'],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    output = result.stdout
                    
                    # Check for expected content
                    found_content = []
                    for expected in test_case['expected_content']:
                        if expected in output:
                            found_content.append(expected)
                    
                    if len(found_content) >= len(test_case['expected_content']) * 0.7:  # At least 70% match
                        self.log(f"  ✅ PASS: Report generated successfully", "SUCCESS")
                        self.test_results['regional_quotas'].append({
                            'test': test_case['name'],
                            'status': 'PASS',
                            'found_content': found_content
                        })
                    else:
                        self.log(f"  ⚠️ PARTIAL: Some expected content missing", "WARNING")
                        self.log(f"    Expected: {test_case['expected_content']}", "INFO")
                        self.log(f"    Found: {found_content}", "INFO")
                        all_passed = False
                else:
                    self.log(f"  ❌ ERROR: Command failed: {result.stderr}", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"  ❌ ERROR: {str(e)}", "ERROR")
                all_passed = False
        
        return all_passed
    
    def test_geo_blocking(self) -> bool:
        """Test IP range blocking functionality."""
        self.log("\n🚫 Testing Geo-blocking (IP Range Blocking)", "HEADER")
        self.log("=" * 60, "INFO")
        
        test_ip_range = "192.168.100.0/24"
        test_client_id = "test_blocked_client"
        test_ip = "192.168.100.50"
        
        try:
            # 1. Test blocking an IP range
            self.log("1. Testing IP range blocking", "INFO")
            result = subprocess.run([
                "python", "-m", "flask", "geographic-limiting", "block-ip",
                test_ip_range, "--reason", "Test blocking"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "blocked successfully" in result.stdout:
                self.log("  ✅ PASS: IP range blocking command works", "SUCCESS")
                
                # 2. Test that blocked IP is rejected
                self.log("2. Testing blocked IP rejection", "INFO")
                test_result = subprocess.run([
                    "python", "-m", "flask", "geographic-limiting", "test-client",
                    test_client_id, test_ip
                ], capture_output=True, text=True, timeout=10)
                
                if test_result.returncode == 0:
                    if "Request BLOCKED" in test_result.stdout and "ip_blocked" in test_result.stdout:
                        self.log("  ✅ PASS: Blocked IP correctly rejected", "SUCCESS")
                        blocked_test_passed = True
                    else:
                        self.log("  ❌ FAIL: Blocked IP not rejected properly", "ERROR")
                        blocked_test_passed = False
                else:
                    self.log("  ⚠️ WARNING: Could not test blocked IP", "WARNING")
                    blocked_test_passed = False
                
                # 3. Test unblocking
                self.log("3. Testing IP range unblocking", "INFO")
                unblock_result = subprocess.run([
                    "python", "-m", "flask", "geographic-limiting", "unblock-ip",
                    test_ip_range
                ], capture_output=True, text=True, timeout=10)
                
                if unblock_result.returncode == 0 and "unblocked successfully" in unblock_result.stdout:
                    self.log("  ✅ PASS: IP range unblocking command works", "SUCCESS")
                    unblock_test_passed = True
                else:
                    self.log("  ❌ FAIL: IP range unblocking failed", "ERROR")
                    unblock_test_passed = False
                
                # Overall result
                overall_passed = blocked_test_passed and unblock_test_passed
                
                self.test_results['geo_blocking'].append({
                    'test': 'ip_range_blocking',
                    'status': 'PASS' if overall_passed else 'PARTIAL',
                    'blocked_test': blocked_test_passed,
                    'unblock_test': unblock_test_passed
                })
                
                return overall_passed
            else:
                self.log(f"  ❌ FAIL: IP blocking command failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"  ❌ ERROR: {str(e)}", "ERROR")
            return False
    
    def test_province_limits(self) -> bool:
        """Test province-based rate limits."""
        self.log("\n🏛️ Testing Province Limits", "HEADER")
        self.log("=" * 60, "INFO")
        
        provinces_to_test = ['ON', 'QC', 'BC', 'AB', 'MB']
        
        try:
            # Test province limits command
            self.log("1. Testing province limits display", "INFO")
            result = subprocess.run([
                "python", "-m", "flask", "geographic-limiting", "province-limits"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Check if major provinces are listed
                found_provinces = []
                for province in provinces_to_test:
                    if province in output:
                        found_provinces.append(province)
                
                if len(found_provinces) >= 3:
                    self.log(f"  ✅ PASS: Province limits displayed ({len(found_provinces)}/{len(provinces_to_test)} found)", "SUCCESS")
                    
                    # Test specific province
                    self.log("2. Testing specific province details", "INFO")
                    specific_result = subprocess.run([
                        "python", "-m", "flask", "geographic-limiting", "province-limits",
                        "--province", "ON"
                    ], capture_output=True, text=True, timeout=10)
                    
                    if specific_result.returncode == 0 and "Ontario" in specific_result.stdout:
                        self.log("  ✅ PASS: Specific province details working", "SUCCESS")
                        return True
                    else:
                        self.log("  ⚠️ WARNING: Specific province details not working properly", "WARNING")
                        return False
                else:
                    self.log(f"  ❌ FAIL: Not enough provinces found in output", "ERROR")
                    return False
            else:
                self.log(f"  ❌ ERROR: Province limits command failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"  ❌ ERROR: {str(e)}", "ERROR")
            return False
    
    def test_city_limits(self) -> bool:
        """Test city-based rate limits."""
        self.log("\n🏙️ Testing City Limits", "HEADER")
        self.log("=" * 60, "INFO")
        
        major_cities = ['Toronto', 'Montreal', 'Vancouver', 'Calgary', 'Edmonton']
        
        try:
            # Test city limits command
            self.log("1. Testing city limits display", "INFO")
            result = subprocess.run([
                "python", "-m", "flask", "geographic-limiting", "city-limits"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Check if major cities are listed
                found_cities = []
                for city in major_cities:
                    if city in output:
                        found_cities.append(city)
                
                if len(found_cities) >= 3:
                    self.log(f"  ✅ PASS: City limits displayed ({len(found_cities)}/{len(major_cities)} found)", "SUCCESS")
                    
                    # Test specific city
                    self.log("2. Testing specific city details", "INFO")
                    specific_result = subprocess.run([
                        "python", "-m", "flask", "geographic-limiting", "city-limits",
                        "--city", "Toronto"
                    ], capture_output=True, text=True, timeout=10)
                    
                    if specific_result.returncode == 0 and ("Toronto" in specific_result.stdout or "Province:" in specific_result.stdout):
                        self.log("  ✅ PASS: Specific city details working", "SUCCESS")
                        return True
                    else:
                        self.log("  ⚠️ WARNING: Specific city details not working properly", "WARNING")
                        return False
                else:
                    self.log(f"  ❌ FAIL: Not enough cities found in output", "ERROR")
                    return False
            else:
                self.log(f"  ❌ ERROR: City limits command failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"  ❌ ERROR: {str(e)}", "ERROR")
            return False
    
    def test_performance_and_integration(self) -> Dict[str, Any]:
        """Test performance and integration with other systems."""
        self.log("\n⚡ Testing Performance and Integration", "HEADER")
        self.log("=" * 60, "INFO")
        
        performance_metrics = {
            'cli_response_times': {},
            'status_check_time': 0,
            'integration_status': {}
        }
        
        # Test CLI command response times
        cli_commands = [
            (['python', '-m', 'flask', 'geographic-limiting', 'status'], 'status'),
            (['python', '-m', 'flask', 'geographic-limiting', 'timezone-status'], 'timezone_status'),
            (['python', '-m', 'flask', 'geographic-limiting', 'province-limits'], 'province_limits'),
            (['python', '-m', 'flask', 'geographic-limiting', 'quota-report'], 'quota_report')
        ]
        
        for command, name in cli_commands:
            try:
                start_time = time.time()
                result = subprocess.run(command, capture_output=True, text=True, timeout=20)
                end_time = time.time()
                
                response_time = end_time - start_time
                performance_metrics['cli_response_times'][name] = response_time
                
                if result.returncode == 0:
                    status_icon = "🟢" if response_time < 5 else "🟡" if response_time < 10 else "🔴"
                    self.log(f"  {status_icon} {name}: {response_time:.2f}s", "INFO")
                else:
                    self.log(f"  ❌ {name}: Command failed", "ERROR")
                    
            except Exception as e:
                self.log(f"  ❌ {name}: Error - {str(e)}", "ERROR")
        
        # Overall status check
        start_time = time.time()
        try:
            result = subprocess.run([
                'python', '-m', 'flask', 'geographic-limiting', 'status', '--format', 'json'
            ], capture_output=True, text=True, timeout=15)
            
            end_time = time.time()
            performance_metrics['status_check_time'] = end_time - start_time
            
            if result.returncode == 0:
                try:
                    status_data = json.loads(result.stdout)
                    performance_metrics['integration_status'] = {
                        'json_parse': True,
                        'has_data': len(status_data) > 0,
                        'total_clients': status_data.get('total_clients', 0)
                    }
                    self.log(f"  ✅ Status check successful: {performance_metrics['status_check_time']:.2f}s", "SUCCESS")
                except json.JSONDecodeError:
                    self.log("  ⚠️ Status check returned non-JSON data", "WARNING")
                    performance_metrics['integration_status']['json_parse'] = False
            else:
                self.log("  ❌ Status check failed", "ERROR")
                
        except Exception as e:
            self.log(f"  ❌ Status check error: {str(e)}", "ERROR")
        
        self.test_results['performance_metrics'] = performance_metrics
        return performance_metrics
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all geographic limiting tests."""
        self.log("🌍 STARTING COMPREHENSIVE GEOGRAPHIC RATE LIMITING TESTS", "HEADER")
        self.log("=" * 80, "INFO")
        self.log(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        
        test_functions = [
            ('Country Limits', self.test_country_limits),
            ('Timezone Restrictions', self.test_timezone_restrictions),
            ('Regional Quotas', self.test_regional_quotas),
            ('Geo-blocking', self.test_geo_blocking),
            ('Province Limits', self.test_province_limits),
            ('City Limits', self.test_city_limits)
        ]
        
        results = {}
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_name, test_function in test_functions:
            try:
                result = test_function()
                results[test_name] = result
                if result:
                    passed_tests += 1
                    self.log(f"✅ {test_name}: PASSED", "SUCCESS")
                else:
                    self.log(f"❌ {test_name}: FAILED", "ERROR")
            except Exception as e:
                results[test_name] = False
                self.log(f"❌ {test_name}: ERROR - {str(e)}", "ERROR")
                self.test_results['errors'].append(f"{test_name}: {str(e)}")
        
        # Performance tests
        self.log("\n" + "=" * 50, "INFO")
        performance_results = self.test_performance_and_integration()
        
        # Final summary
        self.log("\n🎯 GEOGRAPHIC LIMITING TEST SUMMARY", "HEADER")
        self.log("=" * 80, "INFO")
        
        success_rate = (passed_tests / total_tests) * 100
        self.log(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)", "INFO")
        
        if success_rate >= 80:
            self.log("🎉 OVERALL STATUS: EXCELLENT - Geographic limiting system is working well!", "SUCCESS")
        elif success_rate >= 60:
            self.log("⚠️ OVERALL STATUS: GOOD - Most features working, some need attention", "WARNING")
        else:
            self.log("❌ OVERALL STATUS: NEEDS WORK - Significant issues detected", "ERROR")
        
        # Feature breakdown
        self.log("\n📋 Feature Implementation Status:", "INFO")
        feature_status = {
            '🇨🇦 Country Limits': '✅ IMPLEMENTED' if results.get('Country Limits') else '❌ NEEDS WORK',
            '🕐 Timezone Restrictions': '✅ IMPLEMENTED' if results.get('Timezone Restrictions') else '❌ NEEDS WORK',
            '📊 Regional Quotas': '✅ IMPLEMENTED' if results.get('Regional Quotas') else '❌ NEEDS WORK',
            '🚫 Geo-blocking': '✅ IMPLEMENTED' if results.get('Geo-blocking') else '❌ NEEDS WORK'
        }
        
        for feature, status in feature_status.items():
            self.log(f"  {feature}: {status}", "INFO")
        
        # Performance summary
        self.log("\n⚡ Performance Summary:", "INFO")
        avg_response_time = sum(performance_results['cli_response_times'].values()) / len(performance_results['cli_response_times'])
        self.log(f"  Average CLI Response Time: {avg_response_time:.2f}s", "INFO")
        self.log(f"  Status Check Time: {performance_results['status_check_time']:.2f}s", "INFO")
        
        # Test duration
        total_duration = time.time() - self.start_time
        self.log(f"\n⏱️ Total Test Duration: {total_duration:.2f} seconds", "INFO")
        
        # Save results
        final_results = {
            'summary': {
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'success_rate': success_rate,
                'test_duration': total_duration
            },
            'individual_results': results,
            'performance_metrics': performance_results,
            'feature_status': feature_status,
            'detailed_results': self.test_results
        }
        
        # Save to file
        try:
            with open('geographic_limiting_test_results.json', 'w') as f:
                json.dump(final_results, f, indent=2, default=str)
            self.log("💾 Results saved to: geographic_limiting_test_results.json", "INFO")
        except Exception as e:
            self.log(f"⚠️ Could not save results to file: {e}", "WARNING")
        
        self.log("🎯 Geographic Limiting Test COMPLETED", "HEADER")
        
        return final_results


def main():
    """Main function to run geographic limiting tests."""
    tester = GeographicLimitingTest()
    return tester.run_all_tests()


if __name__ == "__main__":
    try:
        results = main()
        # Exit with appropriate code
        success_rate = results['summary']['success_rate']
        if success_rate >= 80:
            exit(0)  # Success
        else:
            exit(1)  # Needs attention
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️ Test interrupted by user{Colors.ENDC}")
        exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Test failed with error: {str(e)}{Colors.ENDC}")
        exit(1)
