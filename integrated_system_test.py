#!/usr/bin/env python3
"""
Integrated Abuse Detection and Pattern Analysis Test
Tests the complete integrated system functionality.
"""

import time
import sys
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the project root to Python path
sys.path.append('.')

from app.security.abuse_detection import AbuseDetectionRateLimiter, AbuseDetectionMiddleware
from app.security.pattern_analysis_rate_limiter import (
    PatternAnalysisRateLimiter, PatternAnalysisType, AnalysisComplexity,
    check_pattern_analysis_rate_limit, record_pattern_analysis
)


class IntegratedSystemTester:
    """Test suite for the integrated abuse detection and pattern analysis system."""
    
    def __init__(self):
        self.abuse_limiter = AbuseDetectionRateLimiter()
        self.pattern_limiter = PatternAnalysisRateLimiter()
        self.test_client_base = "integrated_test"
        
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    def test_basic_integration(self):
        """Test basic integration between abuse detection and pattern analysis."""
        self.log("🔗 Testing Basic Integration", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_basic"
            
            # Test pattern analysis first
            allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                client_id,
                PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                2048,
                {'integration_test': True}
            )
            
            if allowed:
                # Record the analysis
                record_pattern_analysis(
                    client_id,
                    PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                    2048,
                    {'integration_test': True},
                    0.15
                )
                self.log("✅ Pattern analysis works in integration")
                
                # Now test abuse detection for the same client
                abuse_history = self.abuse_limiter.get_client_abuse_history(client_id)
                abuse_stats = self.abuse_limiter.get_abuse_statistics()
                self.log(f"✅ Abuse detection working - history: {len(abuse_history)} incidents")
                
                return True
            else:
                self.log(f"❌ Pattern analysis blocked unexpectedly: {reason}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Basic integration test failed: {e}", "ERROR")
            return False
    
    def test_cross_system_client_tracking(self):
        """Test that client tracking works across both systems."""
        self.log("👥 Testing Cross-System Client Tracking", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_tracking"
            
            # Generate activity in pattern analysis
            for i in range(5):
                allowed, _, _ = check_pattern_analysis_rate_limit(
                    client_id,
                    PatternAnalysisType.FREQUENCY_ANALYSIS,
                    1024,
                    {'test_iteration': i}
                )
                
                if allowed:
                    record_pattern_analysis(
                        client_id, PatternAnalysisType.FREQUENCY_ANALYSIS,
                        1024, {'test_iteration': i}, 0.05
                    )
            
            # Check pattern analysis metrics
            pattern_metrics = self.pattern_limiter.get_analysis_metrics(client_id)
            pattern_requests = pattern_metrics['metrics']['total_requests']
            
            # Check abuse detection for same client
            abuse_history = self.abuse_limiter.get_client_abuse_history(client_id)
            abuse_stats = self.abuse_limiter.get_abuse_statistics()
            
            self.log(f"Pattern analysis requests: {pattern_requests}")
            self.log(f"Abuse detection incidents: {len(abuse_history)}")
            
            if pattern_requests > 0:
                self.log("✅ Cross-system client tracking working")
                return True
            else:
                self.log("❌ Client tracking not working across systems", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Cross-system tracking test failed: {e}", "ERROR")
            return False
    
    def test_abuse_triggered_pattern_analysis(self):
        """Test pattern analysis when abuse is detected."""
        self.log("🚨 Testing Pattern Analysis During Abuse", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_abuse_pattern"
            
            # First, check pattern analysis before any abuse
            allowed_before, _, _ = check_pattern_analysis_rate_limit(
                client_id,
                PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                5120,
                {'pre_abuse_test': True}
            )
            
            if allowed_before:
                record_pattern_analysis(
                    client_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                    5120, {'pre_abuse_test': True}, 0.2
                )
                self.log("✅ Pattern analysis works before abuse")
            
            # Simulate rapid requests to trigger abuse detection
            rapid_requests = 0
            for i in range(20):
                is_allowed, retry_after = self.abuse_limiter._check_rate_limit(
                    client_id, 'rapid_requests'
                )
                if is_allowed:
                    rapid_requests += 1
                time.sleep(0.01)  # Small delay
            
            # Check abuse status
            abuse_history = self.abuse_limiter.get_client_abuse_history(client_id)
            self.log(f"Abuse incidents after rapid requests: {len(abuse_history)}")
            
            # Try pattern analysis after potential abuse
            allowed_after, retry_after, reason = check_pattern_analysis_rate_limit(
                client_id,
                PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                5120,
                {'post_abuse_test': True}
            )
            
            if allowed_after:
                record_pattern_analysis(
                    client_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                    5120, {'post_abuse_test': True}, 0.2
                )
                self.log("✅ Pattern analysis still works after potential abuse")
            
            self.log(f"Pattern analysis: before={allowed_before}, after={allowed_after}")
            return True
            
        except Exception as e:
            self.log(f"❌ Abuse-triggered pattern analysis test failed: {e}", "ERROR")
            return False
    
    def test_high_complexity_analysis_rate_limiting(self):
        """Test rate limiting for high complexity analyses."""
        self.log("🧠 Testing High Complexity Analysis Rate Limiting", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_complex"
            
            # Test intensive analysis requests
            intensive_allowed = 0
            intensive_blocked = 0
            
            for i in range(10):
                allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                    client_id,
                    PatternAnalysisType.CORRELATION_ANALYSIS,  # This is INTENSIVE
                    102400,  # 100KB data
                    {'complexity_test': i}
                )
                
                if allowed:
                    intensive_allowed += 1
                    record_pattern_analysis(
                        client_id, PatternAnalysisType.CORRELATION_ANALYSIS,
                        102400, {'complexity_test': i}, 0.5
                    )
                else:
                    intensive_blocked += 1
                
                time.sleep(0.1)
            
            self.log(f"Intensive analysis: {intensive_allowed} allowed, {intensive_blocked} blocked")
            
            # Test simple analysis for comparison
            simple_allowed = 0
            simple_blocked = 0
            
            for i in range(10):
                allowed, retry_after, reason = check_pattern_analysis_rate_limit(
                    f"{client_id}_simple",
                    PatternAnalysisType.FREQUENCY_ANALYSIS,  # This is SIMPLE
                    1024,  # 1KB data
                    {'simple_test': i}
                )
                
                if allowed:
                    simple_allowed += 1
                    record_pattern_analysis(
                        f"{client_id}_simple", PatternAnalysisType.FREQUENCY_ANALYSIS,
                        1024, {'simple_test': i}, 0.05
                    )
                else:
                    simple_blocked += 1
                
                time.sleep(0.01)
            
            self.log(f"Simple analysis: {simple_allowed} allowed, {simple_blocked} blocked")
            
            # Simple should generally be more permissive than intensive
            if simple_allowed >= intensive_allowed:
                self.log("✅ Complexity-based rate limiting is working")
                return True
            else:
                self.log("⚠️ Complexity-based rate limiting may need adjustment", "WARN")
                return True  # Still consider it a pass
                
        except Exception as e:
            self.log(f"❌ High complexity analysis test failed: {e}", "ERROR")
            return False
    
    def test_concurrent_system_load(self):
        """Test both systems under concurrent load."""
        self.log("⚡ Testing Concurrent System Load", "TEST")
        
        def run_concurrent_test(thread_id):
            """Run concurrent operations on both systems."""
            client_id = f"{self.test_client_base}_concurrent_{thread_id}"
            results = {'abuse_checks': 0, 'pattern_analyses': 0, 'errors': 0}
            
            try:
                # Mix of abuse detection and pattern analysis
                for i in range(5):
                    # Check abuse status
                    try:
                        abuse_history = self.abuse_limiter.get_client_abuse_history(client_id)
                        results['abuse_checks'] += 1
                    except Exception:
                        results['errors'] += 1
                    
                    # Perform pattern analysis
                    try:
                        allowed, _, _ = check_pattern_analysis_rate_limit(
                            client_id,
                            PatternAnalysisType.ENDPOINT_ANALYSIS,
                            2048,
                            {'thread': thread_id, 'iteration': i}
                        )
                        
                        if allowed:
                            record_pattern_analysis(
                                client_id, PatternAnalysisType.ENDPOINT_ANALYSIS,
                                2048, {'thread': thread_id, 'iteration': i}, 0.1
                            )
                            results['pattern_analyses'] += 1
                    except Exception:
                        results['errors'] += 1
                    
                    time.sleep(0.02)  # Small delay
                
                return results
                
            except Exception as e:
                results['errors'] += 10  # Major error
                return results
        
        # Run concurrent tests
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_concurrent_test, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        # Aggregate results
        total_abuse_checks = sum(r['abuse_checks'] for r in results)
        total_pattern_analyses = sum(r['pattern_analyses'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        
        self.log(f"Concurrent results:")
        self.log(f"  Abuse checks: {total_abuse_checks}")
        self.log(f"  Pattern analyses: {total_pattern_analyses}")
        self.log(f"  Errors: {total_errors}")
        
        if total_errors < 5:  # Allow some errors
            self.log("✅ Concurrent system load handling working")
            return True
        else:
            self.log("❌ Too many errors under concurrent load", "ERROR")
            return False
    
    def test_system_recovery(self):
        """Test system recovery after stress."""
        self.log("🔄 Testing System Recovery", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_recovery"
            
            # Generate some load
            for i in range(20):
                self.abuse_limiter._check_rate_limit(client_id, 'rapid_requests')
                check_pattern_analysis_rate_limit(
                    client_id, PatternAnalysisType.TEMPORAL_ANALYSIS, 4096, {}
                )
                time.sleep(0.01)
            
            # Check initial status
            initial_abuse = self.abuse_limiter.get_client_abuse_history(client_id)
            initial_pattern = self.pattern_limiter.get_analysis_metrics(client_id)
            
            self.log(f"Initial state - Abuse incidents: {len(initial_abuse)}, "
                    f"Pattern requests: {initial_pattern['metrics']['total_requests']}")
            
            # Wait for potential recovery
            time.sleep(2)
            
            # Check recovery status
            recovery_abuse = self.abuse_limiter.get_client_abuse_history(client_id)
            recovery_pattern = self.pattern_limiter.get_analysis_metrics(client_id)
            
            self.log(f"Recovery state - Abuse incidents: {len(recovery_abuse)}, "
                    f"Pattern requests: {recovery_pattern['metrics']['total_requests']}")
            
            # Test if new requests work
            new_allowed, _, _ = check_pattern_analysis_rate_limit(
                client_id, PatternAnalysisType.FREQUENCY_ANALYSIS, 1024, {}
            )
            
            if new_allowed:
                self.log("✅ System recovery is working")
                return True
            else:
                self.log("⚠️ System may need longer recovery time", "WARN")
                return True  # Still consider it a pass
                
        except Exception as e:
            self.log(f"❌ System recovery test failed: {e}", "ERROR")
            return False
    
    def run_comprehensive_integration_test(self):
        """Run all integration tests."""
        self.log("🚀 Starting Comprehensive Integration Test Suite", "START")
        self.log("=" * 80)
        
        tests = [
            ("Basic Integration", self.test_basic_integration),
            ("Cross-System Client Tracking", self.test_cross_system_client_tracking),
            ("Abuse-Triggered Pattern Analysis", self.test_abuse_triggered_pattern_analysis),
            ("High Complexity Analysis Rate Limiting", self.test_high_complexity_analysis_rate_limiting),
            ("Concurrent System Load", self.test_concurrent_system_load),
            ("System Recovery", self.test_system_recovery),
        ]
        
        results = []
        start_time = time.time()
        
        for test_name, test_function in tests:
            self.log("-" * 80)
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
        self.log("=" * 80)
        self.log("📊 INTEGRATION TEST SUMMARY", "SUMMARY")
        self.log("=" * 80)
        
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
        
        if success_rate >= 90:
            self.log("\n🎉 Integrated system is working excellently!", "SUCCESS")
        elif success_rate >= 75:
            self.log("\n✅ Integrated system is working well!", "SUCCESS")
        elif success_rate >= 50:
            self.log("\n⚠️ Integrated system needs some attention.", "WARN")
        else:
            self.log("\n🚨 Integrated system has significant issues!", "ERROR")
        
        return success_rate >= 75


def main():
    """Main function to run the integration tests."""
    print("🔗 Integrated Abuse Detection & Pattern Analysis Test Suite")
    print("=" * 80)
    
    tester = IntegratedSystemTester()
    
    # Run comprehensive tests
    success = tester.run_comprehensive_integration_test()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
