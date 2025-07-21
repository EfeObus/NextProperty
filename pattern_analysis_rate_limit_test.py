#!/usr/bin/env python3
"""
Pattern Analysis Rate Limiting Test Suite
Tests the rate limiting functionality for pattern analysis operations.
"""

import time
import sys
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# Add the project root to Python path
sys.path.append('.')

from app.security.pattern_analysis_rate_limiter import (
    PatternAnalysisRateLimiter, PatternAnalysisType, AnalysisComplexity,
    AnalysisRequest, check_pattern_analysis_rate_limit, record_pattern_analysis
)


class PatternAnalysisRateLimitTester:
    """Test suite for pattern analysis rate limiting."""
    
    def __init__(self):
        self.limiter = PatternAnalysisRateLimiter()
        self.test_client_id = "test:pattern_analysis"
        
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    def test_basic_functionality(self):
        """Test basic pattern analysis rate limiting functionality."""
        self.log("🧪 Testing Basic Functionality", "TEST")
        
        try:
            # Test simple analysis
            allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                self.test_client_id, 
                PatternAnalysisType.FREQUENCY_ANALYSIS,
                1024,  # 1KB data
                {'test': True}
            )
            
            if allowed:
                self.log("✅ Simple analysis allowed")
                
                # Record the analysis
                record_pattern_analysis(
                    self.test_client_id,
                    PatternAnalysisType.FREQUENCY_ANALYSIS,
                    1024,
                    {'test': True},
                    0.1  # 100ms processing time
                )
                self.log("✅ Analysis recording works")
                
            else:
                self.log(f"❌ Unexpected rate limit: {reason}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"❌ Basic functionality test failed: {e}", "ERROR")
            return False
    
    def test_complexity_based_limiting(self):
        """Test rate limiting based on analysis complexity."""
        self.log("🎚️ Testing Complexity-Based Rate Limiting", "TEST")
        
        complexities = [
            (AnalysisComplexity.SIMPLE, PatternAnalysisType.FREQUENCY_ANALYSIS),
            (AnalysisComplexity.MODERATE, PatternAnalysisType.ENDPOINT_ANALYSIS),
            (AnalysisComplexity.COMPLEX, PatternAnalysisType.BEHAVIORAL_ANALYSIS),
            (AnalysisComplexity.INTENSIVE, PatternAnalysisType.CORRELATION_ANALYSIS)
        ]
        
        for complexity, analysis_type in complexities:
            self.log(f"Testing {complexity.name} complexity...")
            
            # Get the limit for this complexity
            limit_config = self.limiter.complexity_limits.get(complexity)
            if not limit_config:
                continue
            
            max_requests = limit_config['requests']
            allowed_count = 0
            blocked_count = 0
            
            # Try to exceed the limit
            for i in range(max_requests + 5):
                allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                    f"{self.test_client_id}_{complexity.name}",
                    analysis_type,
                    1024,
                    {}
                )
                
                if allowed:
                    allowed_count += 1
                    # Record successful analysis
                    record_pattern_analysis(
                        f"{self.test_client_id}_{complexity.name}",
                        analysis_type, 1024, {}, 0.1
                    )
                else:
                    blocked_count += 1
                
                time.sleep(0.01)  # Small delay
            
            self.log(f"  {complexity.name}: {allowed_count} allowed, {blocked_count} blocked")
            
            if allowed_count <= max_requests and blocked_count > 0:
                self.log(f"  ✅ {complexity.name} rate limiting working correctly")
            else:
                self.log(f"  ⚠️ {complexity.name} rate limiting may need adjustment", "WARN")
        
        return True
    
    def test_data_size_limiting(self):
        """Test rate limiting based on data size."""
        self.log("📊 Testing Data Size-Based Rate Limiting", "TEST")
        
        data_sizes = [
            (512, "small"),      # 512 bytes
            (5120, "medium"),    # 5KB
            (51200, "large"),    # 50KB
            (512000, "xlarge"),  # 500KB
            (2048000, "massive") # 2MB
        ]
        
        for data_size, expected_category in data_sizes:
            self.log(f"Testing {expected_category} data size ({data_size} bytes)...")
            
            category = self.limiter.determine_data_size_category(data_size)
            if category != expected_category:
                self.log(f"  ⚠️ Expected {expected_category}, got {category}", "WARN")
            
            # Test rate limiting for this size
            client_id = f"{self.test_client_id}_size_{category}"
            
            allowed_count = 0
            blocked_count = 0
            
            # Try multiple requests
            for i in range(15):
                allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                    client_id,
                    PatternAnalysisType.PARAMETER_ANALYSIS,
                    data_size,
                    {}
                )
                
                if allowed:
                    allowed_count += 1
                    record_pattern_analysis(
                        client_id, PatternAnalysisType.PARAMETER_ANALYSIS,
                        data_size, {}, 0.1
                    )
                else:
                    blocked_count += 1
                
                time.sleep(0.01)
            
            self.log(f"  {category}: {allowed_count} allowed, {blocked_count} blocked")
        
        return True
    
    def test_analysis_type_limiting(self):
        """Test rate limiting based on analysis type."""
        self.log("🔍 Testing Analysis Type-Based Rate Limiting", "TEST")
        
        # Test different analysis types
        test_types = [
            PatternAnalysisType.BEHAVIORAL_ANALYSIS,
            PatternAnalysisType.TEMPORAL_ANALYSIS,
            PatternAnalysisType.ANOMALY_DETECTION
        ]
        
        for analysis_type in test_types:
            if analysis_type not in self.limiter.type_limits:
                continue
            
            self.log(f"Testing {analysis_type.value}...")
            
            limit_config = self.limiter.type_limits[analysis_type]
            max_requests = limit_config['requests']
            
            client_id = f"{self.test_client_id}_type_{analysis_type.value}"
            allowed_count = 0
            blocked_count = 0
            
            # Try to exceed the limit
            for i in range(max_requests + 3):
                allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                    client_id, analysis_type, 1024, {}
                )
                
                if allowed:
                    allowed_count += 1
                    record_pattern_analysis(
                        client_id, analysis_type, 1024, {}, 0.1
                    )
                else:
                    blocked_count += 1
                
                time.sleep(0.01)
            
            self.log(f"  {analysis_type.value}: {allowed_count} allowed, {blocked_count} blocked")
            
            if allowed_count <= max_requests and blocked_count > 0:
                self.log(f"  ✅ {analysis_type.value} rate limiting working")
            else:
                self.log(f"  ⚠️ {analysis_type.value} rate limiting needs attention", "WARN")
        
        return True
    
    def test_client_tier_limiting(self):
        """Test rate limiting based on client tier."""
        self.log("👥 Testing Client Tier-Based Rate Limiting", "TEST")
        
        client_tiers = [
            ("ip:192.168.1.1", "default"),
            ("premium:user123", "premium"),
            ("admin:admin123", "admin"),
            ("system:service", "system")
        ]
        
        for client_id, expected_tier in client_tiers:
            tier = self.limiter.get_client_tier(client_id)
            if tier != expected_tier:
                self.log(f"  ⚠️ Expected tier {expected_tier}, got {tier}", "WARN")
            
            # Test rate limiting for this tier
            if tier in self.limiter.client_limits:
                limit_config = self.limiter.client_limits[tier]
                max_requests = min(limit_config['requests'], 20)  # Cap for testing
                
                allowed_count = 0
                blocked_count = 0
                
                for i in range(max_requests + 5):
                    allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                        f"test_{client_id}",
                        PatternAnalysisType.FREQUENCY_ANALYSIS,
                        1024, {}
                    )
                    
                    if allowed:
                        allowed_count += 1
                        record_pattern_analysis(
                            f"test_{client_id}",
                            PatternAnalysisType.FREQUENCY_ANALYSIS,
                            1024, {}, 0.1
                        )
                    else:
                        blocked_count += 1
                    
                    time.sleep(0.01)
                
                self.log(f"  {tier}: {allowed_count} allowed, {blocked_count} blocked")
        
        return True
    
    def test_concurrent_analysis_limiting(self):
        """Test concurrent analysis limiting."""
        self.log("🔄 Testing Concurrent Analysis Limiting", "TEST")
        
        def run_analysis(thread_id):
            """Run analysis in a thread."""
            client_id = f"{self.test_client_id}_concurrent_{thread_id}"
            
            allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                client_id,
                PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                10240,  # 10KB
                {'thread_id': thread_id}
            )
            
            if allowed:
                # Simulate analysis processing
                start_time = time.time()
                time.sleep(0.1)  # 100ms processing
                processing_time = time.time() - start_time
                
                record_pattern_analysis(
                    client_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                    10240, {'thread_id': thread_id}, processing_time
                )
                
                return {'thread_id': thread_id, 'allowed': True, 'processing_time': processing_time}
            else:
                return {'thread_id': thread_id, 'allowed': False, 'reason': reason}
        
        # Test with multiple concurrent threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analysis, i) for i in range(8)]
            results = [future.result() for future in as_completed(futures)]
        
        allowed_count = sum(1 for r in results if r['allowed'])
        blocked_count = len(results) - allowed_count
        
        self.log(f"Concurrent test: {allowed_count} allowed, {blocked_count} blocked")
        
        if allowed_count > 0:
            processing_times = [r['processing_time'] for r in results if r['allowed']]
            avg_time = statistics.mean(processing_times)
            self.log(f"Average processing time: {avg_time:.3f}s")
        
        return True
    
    def test_metrics_collection(self):
        """Test metrics collection functionality."""
        self.log("📈 Testing Metrics Collection", "TEST")
        
        try:
            # Perform some analyses to generate metrics
            test_client = f"{self.test_client_id}_metrics"
            
            for i in range(5):
                allowed, _, _ = check_pattern_analysis_rate_limit(
                    test_client,
                    PatternAnalysisType.FREQUENCY_ANALYSIS,
                    1024, {}
                )
                
                if allowed:
                    record_pattern_analysis(
                        test_client, PatternAnalysisType.FREQUENCY_ANALYSIS,
                        1024, {}, 0.05 + (i * 0.01)  # Varying processing times
                    )
            
            # Get metrics
            client_metrics = self.limiter.get_analysis_metrics(test_client)
            overall_metrics = self.limiter.get_analysis_metrics()
            
            self.log(f"Client metrics collected: {client_metrics['metrics']['total_requests']} requests")
            self.log(f"Overall metrics: {overall_metrics['total_clients']} clients")
            
            # Test status
            status = self.limiter.get_rate_limit_status(test_client)
            self.log(f"Status retrieved with {len(status['limits'])} limit types")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Metrics collection test failed: {e}", "ERROR")
            return False
    
    def test_cleanup_functionality(self):
        """Test data cleanup functionality."""
        self.log("🧹 Testing Cleanup Functionality", "TEST")
        
        try:
            cleanup_client = f"{self.test_client_id}_cleanup"
            
            # Generate some test data
            for i in range(3):
                allowed, _, _ = check_pattern_analysis_rate_limit(
                    cleanup_client,
                    PatternAnalysisType.ENDPOINT_ANALYSIS,
                    2048, {}
                )
                
                if allowed:
                    record_pattern_analysis(
                        cleanup_client, PatternAnalysisType.ENDPOINT_ANALYSIS,
                        2048, {}, 0.1
                    )
            
            # Check data exists
            metrics_before = self.limiter.get_analysis_metrics(cleanup_client)
            requests_before = metrics_before['metrics']['total_requests']
            
            if requests_before > 0:
                self.log(f"Data before cleanup: {requests_before} requests")
                
                # Clear the client data
                self.limiter.clear_client_data(cleanup_client)
                
                # Check data is cleared
                metrics_after = self.limiter.get_analysis_metrics(cleanup_client)
                requests_after = metrics_after['metrics']['total_requests']
                
                self.log(f"Data after cleanup: {requests_after} requests")
                
                if requests_after == 0:
                    self.log("✅ Cleanup functionality working correctly")
                    return True
                else:
                    self.log("❌ Cleanup did not remove all data", "ERROR")
                    return False
            else:
                self.log("⚠️ No data generated for cleanup test", "WARN")
                return True
                
        except Exception as e:
            self.log(f"❌ Cleanup test failed: {e}", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """Run all pattern analysis rate limiting tests."""
        self.log("🚀 Starting Pattern Analysis Rate Limiting Test Suite", "START")
        self.log("=" * 70)
        
        tests = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Complexity-Based Limiting", self.test_complexity_based_limiting),
            ("Data Size-Based Limiting", self.test_data_size_limiting),
            ("Analysis Type-Based Limiting", self.test_analysis_type_limiting),
            ("Client Tier-Based Limiting", self.test_client_tier_limiting),
            ("Concurrent Analysis Limiting", self.test_concurrent_analysis_limiting),
            ("Metrics Collection", self.test_metrics_collection),
            ("Cleanup Functionality", self.test_cleanup_functionality),
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
            
            time.sleep(1)  # Pause between tests
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        self.log("=" * 70)
        self.log("📊 PATTERN ANALYSIS RATE LIMITING TEST SUMMARY", "SUMMARY")
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
            self.log("\n🎉 Pattern analysis rate limiting system is working well!", "SUCCESS")
        elif success_rate >= 60:
            self.log("\n⚠️ Pattern analysis rate limiting system needs attention.", "WARN")
        else:
            self.log("\n🚨 Pattern analysis rate limiting system has issues!", "ERROR")
        
        return success_rate >= 80


def main():
    """Main function to run the tests."""
    print("🔍 Pattern Analysis Rate Limiting Test Suite")
    print("=" * 70)
    
    tester = PatternAnalysisRateLimitTester()
    
    # Run comprehensive tests
    success = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
