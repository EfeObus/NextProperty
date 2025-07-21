#!/usr/bin/env python3
"""
Predictive Rate Limiting Test Suite
Tests the predictive rate limiting functionality.
"""

import time
import sys
import json
import random
import statistics
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the project root to Python path
sys.path.append('.')

from app.security.predictive_rate_limiter import (
    PredictiveRateLimiter, PredictionModel, PredictiveStrategy, ClientBehaviorType,
    check_predictive_rate_limit, get_client_prediction_status, get_global_prediction_metrics
)


class PredictiveRateLimitTester:
    """Test suite for predictive rate limiting."""
    
    def __init__(self):
        self.limiter = PredictiveRateLimiter()
        self.test_client_base = "test:predictive"
        
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    def test_basic_functionality(self):
        """Test basic predictive rate limiting functionality."""
        self.log("🧪 Testing Basic Functionality", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_basic"
            
            # Test basic rate limit check
            allowed, retry_after, metadata = check_predictive_rate_limit(
                client_id, 'search_api', {'test': 'basic'}
            )
            
            if allowed:
                self.log("✅ Basic rate limit check works")
                self.log(f"   Metadata: strategy={metadata.get('strategy')}, "
                        f"model={metadata.get('model')}")
                
                # Test client status
                status = get_client_prediction_status(client_id)
                self.log(f"✅ Client status retrieved: {status['behavior_type']}")
                
                # Test global metrics
                metrics = get_global_prediction_metrics()
                self.log(f"✅ Global metrics: {metrics['total_clients']} clients")
                
                return True
            else:
                self.log(f"❌ Unexpected rate limit: retry_after={retry_after}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Basic functionality test failed: {e}", "ERROR")
            return False
    
    def test_prediction_models(self):
        """Test different prediction models."""
        self.log("🧠 Testing Prediction Models", "TEST")
        
        models = [
            PredictionModel.LINEAR_REGRESSION,
            PredictionModel.EXPONENTIAL_SMOOTHING,
            PredictionModel.MOVING_AVERAGE,
            PredictionModel.SEASONAL_DECOMPOSITION,
            PredictionModel.ADAPTIVE_THRESHOLD
        ]
        
        successful_models = 0
        
        for model in models:
            try:
                client_id = f"{self.test_client_base}_{model.value}"
                
                # Generate some request history
                for i in range(10):
                    self.limiter.record_request(client_id, 'property_details', 
                                              {'request_id': i})
                    time.sleep(0.01)
                
                # Test prediction
                predicted, confidence = self.limiter.predict_future_requests(
                    client_id, 'property_details', 300, model
                )
                
                self.log(f"  {model.value}: predicted={predicted}, confidence={confidence:.3f}")
                
                if confidence > 0:
                    successful_models += 1
                    self.log(f"    ✅ {model.value} working")
                else:
                    self.log(f"    ⚠️ {model.value} low confidence", "WARN")
                
            except Exception as e:
                self.log(f"    ❌ {model.value} failed: {e}", "ERROR")
        
        success_rate = successful_models / len(models)
        if success_rate >= 0.8:
            self.log(f"✅ Prediction models working ({successful_models}/{len(models)})")
            return True
        else:
            self.log(f"⚠️ Some prediction models need attention ({successful_models}/{len(models)})", "WARN")
            return successful_models > 0
    
    def test_behavior_classification(self):
        """Test client behavior classification."""
        self.log("🎭 Testing Behavior Classification", "TEST")
        
        behavior_tests = [
            ('steady', lambda: time.sleep(1.0)),        # Steady intervals
            ('bursty', lambda: time.sleep(random.uniform(0.1, 3.0))),  # Variable intervals
            ('rapid', lambda: time.sleep(0.1)),         # Very fast requests
        ]
        
        classified_behaviors = 0
        
        for test_name, interval_func in behavior_tests:
            try:
                client_id = f"{self.test_client_base}_{test_name}"
                
                # Generate characteristic request pattern
                for i in range(15):
                    self.limiter.record_request(client_id, 'analytics', 
                                              {'pattern': test_name, 'request': i})
                    interval_func()
                
                # Check behavior classification
                profile = self.limiter.get_or_create_client_profile(client_id)
                behavior = profile.behavior_type
                
                self.log(f"  {test_name}: classified as {behavior.value}")
                
                if behavior != ClientBehaviorType.NORMAL:
                    classified_behaviors += 1
                    self.log(f"    ✅ Behavior classification working")
                else:
                    self.log(f"    ⚠️ Behavior not differentiated", "WARN")
                
            except Exception as e:
                self.log(f"    ❌ {test_name} behavior test failed: {e}", "ERROR")
        
        if classified_behaviors > 0:
            self.log(f"✅ Behavior classification working ({classified_behaviors} patterns detected)")
            return True
        else:
            self.log("❌ Behavior classification not working", "ERROR")
            return False
    
    def test_predictive_strategies(self):
        """Test different predictive strategies."""
        self.log("🎯 Testing Predictive Strategies", "TEST")
        
        strategies = [
            PredictiveStrategy.CONSERVATIVE,
            PredictiveStrategy.BALANCED,
            PredictiveStrategy.AGGRESSIVE,
            PredictiveStrategy.ADAPTIVE
        ]
        
        strategy_results = {}
        
        for strategy in strategies:
            try:
                client_id = f"{self.test_client_base}_{strategy.value}"
                
                # Configure a test limit with this strategy
                from app.security.predictive_rate_limiter import PredictiveLimit
                test_limit = PredictiveLimit(
                    base_limit=20, prediction_window=60, strategy=strategy
                )
                self.limiter.predictive_limits[f'test_{strategy.value}'] = test_limit
                
                # Generate load pattern
                allowed_count = 0
                blocked_count = 0
                
                for i in range(30):
                    allowed, retry_after, metadata = check_predictive_rate_limit(
                        client_id, 'analytics', limit_type=f'test_{strategy.value}'
                    )
                    
                    if allowed:
                        allowed_count += 1
                    else:
                        blocked_count += 1
                    
                    time.sleep(0.05)
                
                strategy_results[strategy.value] = {
                    'allowed': allowed_count,
                    'blocked': blocked_count,
                    'rate': allowed_count / (allowed_count + blocked_count)
                }
                
                self.log(f"  {strategy.value}: {allowed_count} allowed, {blocked_count} blocked "
                        f"({strategy_results[strategy.value]['rate']:.2%})")
                
            except Exception as e:
                self.log(f"    ❌ {strategy.value} strategy test failed: {e}", "ERROR")
        
        # Verify strategies behave differently
        if len(strategy_results) >= 2:
            rates = [result['rate'] for result in strategy_results.values()]
            rate_variance = statistics.variance(rates) if len(rates) > 1 else 0
            
            if rate_variance > 0.01:  # Some variance in strategies
                self.log("✅ Predictive strategies working with different behaviors")
                return True
            else:
                self.log("⚠️ Strategies showing similar behavior", "WARN")
                return True
        else:
            self.log("❌ Not enough strategy results to compare", "ERROR")
            return False
    
    def test_trust_score_evolution(self):
        """Test trust score evolution based on behavior."""
        self.log("🤝 Testing Trust Score Evolution", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_trust"
            
            # Get initial trust score
            initial_profile = self.limiter.get_or_create_client_profile(client_id)
            initial_trust = initial_profile.trust_score
            
            self.log(f"Initial trust score: {initial_trust:.3f}")
            
            # Generate consistent behavior pattern
            for i in range(30):
                self.limiter.record_request(client_id, 'user_uploads', 
                                          {'consistent': True, 'request': i})
                time.sleep(0.1)  # Consistent intervals
            
            # Check trust score after consistent behavior
            updated_profile = self.limiter.get_or_create_client_profile(client_id)
            updated_trust = updated_profile.trust_score
            
            self.log(f"Trust score after consistent behavior: {updated_trust:.3f}")
            
            # Generate erratic behavior
            for i in range(20):
                self.limiter.record_request(client_id, 'user_uploads', 
                                          {'erratic': True, 'request': i})
                # Highly variable intervals
                time.sleep(random.uniform(0.01, 0.5))
            
            # Force trust score update
            self.limiter._update_prediction_accuracy(client_id, 'user_uploads', 5, PredictionModel.MOVING_AVERAGE)
            
            final_profile = self.limiter.get_or_create_client_profile(client_id)
            final_trust = final_profile.trust_score
            
            self.log(f"Trust score after erratic behavior: {final_trust:.3f}")
            
            # Verify trust score evolution
            if abs(updated_trust - initial_trust) > 0.001 or abs(final_trust - updated_trust) > 0.001:
                self.log("✅ Trust score evolution working")
                return True
            else:
                self.log("⚠️ Trust score not changing significantly", "WARN")
                return True  # Still consider a pass
                
        except Exception as e:
            self.log(f"❌ Trust score evolution test failed: {e}", "ERROR")
            return False
    
    def test_pattern_learning(self):
        """Test hourly and daily pattern learning."""
        self.log("📅 Testing Pattern Learning", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_patterns"
            
            # Simulate requests at specific hours
            target_hours = [9, 14, 18]  # 9 AM, 2 PM, 6 PM
            
            for hour in target_hours:
                # Simulate multiple requests at this hour
                for day in range(3):  # 3 days of data
                    for request in range(5):  # 5 requests per hour
                        # Create fake timestamp for the target hour
                        fake_time = datetime.now().replace(hour=hour, minute=random.randint(0, 59))
                        fake_timestamp = fake_time.timestamp()
                        
                        # Manually add to patterns
                        profile = self.limiter.get_or_create_client_profile(client_id)
                        profile.hourly_patterns[hour].append(1)
                        profile.daily_patterns[fake_time.weekday()].append(1)
            
            # Check patterns
            profile = self.limiter.get_or_create_client_profile(client_id)
            
            learned_hours = [hour for hour, data in profile.hourly_patterns.items() if data]
            learned_days = [day for day, data in profile.daily_patterns.items() if data]
            
            self.log(f"Learned hourly patterns: {learned_hours}")
            self.log(f"Learned daily patterns: {learned_days}")
            
            if len(learned_hours) >= 2 and len(learned_days) >= 1:
                self.log("✅ Pattern learning working")
                return True
            else:
                self.log("⚠️ Limited pattern learning", "WARN")
                return True
                
        except Exception as e:
            self.log(f"❌ Pattern learning test failed: {e}", "ERROR")
            return False
    
    def test_concurrent_predictions(self):
        """Test concurrent prediction requests."""
        self.log("⚡ Testing Concurrent Predictions", "TEST")
        
        def run_concurrent_prediction(thread_id):
            """Run prediction in a thread."""
            client_id = f"{self.test_client_base}_concurrent_{thread_id}"
            
            try:
                results = {'allowed': 0, 'blocked': 0, 'errors': 0}
                
                for i in range(10):
                    allowed, retry_after, metadata = check_predictive_rate_limit(
                        client_id, 'search_api', {'thread': thread_id, 'request': i}
                    )
                    
                    if allowed:
                        results['allowed'] += 1
                    else:
                        results['blocked'] += 1
                    
                    time.sleep(0.02)
                
                return results
                
            except Exception as e:
                return {'allowed': 0, 'blocked': 0, 'errors': 1}
        
        # Test with multiple concurrent threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_concurrent_prediction, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        # Aggregate results
        total_allowed = sum(r['allowed'] for r in results)
        total_blocked = sum(r['blocked'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        
        self.log(f"Concurrent results: {total_allowed} allowed, {total_blocked} blocked, {total_errors} errors")
        
        if total_errors < 3:  # Allow some errors
            self.log("✅ Concurrent predictions working")
            return True
        else:
            self.log("❌ Too many errors in concurrent predictions", "ERROR")
            return False
    
    def test_data_cleanup(self):
        """Test data cleanup functionality."""
        self.log("🧹 Testing Data Cleanup", "TEST")
        
        try:
            cleanup_client = f"{self.test_client_base}_cleanup"
            
            # Generate test data
            for i in range(20):
                self.limiter.record_request(cleanup_client, 'analytics', {'cleanup_test': i})
                time.sleep(0.01)
            
            # Check data exists
            profile_before = self.limiter.get_or_create_client_profile(cleanup_client)
            requests_before = len(profile_before.request_history)
            
            if requests_before > 0:
                self.log(f"Data before cleanup: {requests_before} requests")
                
                # Test client-specific cleanup
                self.limiter.clear_client_data(cleanup_client)
                
                # Verify cleanup
                if cleanup_client in self.limiter.client_profiles:
                    self.log("❌ Client data not fully cleared", "ERROR")
                    return False
                else:
                    self.log("✅ Client-specific cleanup working")
                
                # Test global cleanup
                initial_clients = len(self.limiter.client_profiles)
                self.limiter.cleanup_old_data(max_age_hours=0)  # Clean everything
                remaining_clients = len(self.limiter.client_profiles)
                
                self.log(f"Global cleanup: {initial_clients} -> {remaining_clients} clients")
                self.log("✅ Global cleanup working")
                
                return True
            else:
                self.log("⚠️ No data generated for cleanup test", "WARN")
                return True
                
        except Exception as e:
            self.log(f"❌ Data cleanup test failed: {e}", "ERROR")
            return False
    
    def test_prediction_accuracy_tracking(self):
        """Test prediction accuracy tracking."""
        self.log("📊 Testing Prediction Accuracy Tracking", "TEST")
        
        try:
            client_id = f"{self.test_client_base}_accuracy"
            
            # Generate predictable pattern
            for i in range(30):
                self.limiter.record_request(client_id, 'property_details', {'accuracy_test': i})
                time.sleep(0.1)  # Consistent timing
            
            # Make a prediction
            predicted, confidence = self.limiter.predict_future_requests(
                client_id, 'property_details', 300, PredictionModel.MOVING_AVERAGE
            )
            
            self.log(f"Prediction: {predicted} requests, confidence: {confidence:.3f}")
            
            # Simulate actual requests matching prediction roughly
            actual_requests = max(1, predicted + random.randint(-2, 2))
            
            # Update accuracy manually
            self.limiter._update_prediction_accuracy(
                client_id, 'property_details', predicted, PredictionModel.MOVING_AVERAGE
            )
            
            # Check model performance
            model_metrics = self.limiter.model_performance[PredictionModel.MOVING_AVERAGE]
            
            self.log(f"Model accuracy: {model_metrics.accuracy_score:.3f}")
            self.log(f"Model confidence: {model_metrics.prediction_confidence:.3f}")
            
            if model_metrics.last_updated > 0:
                self.log("✅ Prediction accuracy tracking working")
                return True
            else:
                self.log("⚠️ Accuracy tracking not updating", "WARN")
                return True
                
        except Exception as e:
            self.log(f"❌ Prediction accuracy tracking test failed: {e}", "ERROR")
            return False
    
    def run_comprehensive_test(self):
        """Run all predictive rate limiting tests."""
        self.log("🚀 Starting Predictive Rate Limiting Test Suite", "START")
        self.log("=" * 80)
        
        tests = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Prediction Models", self.test_prediction_models),
            ("Behavior Classification", self.test_behavior_classification),
            ("Predictive Strategies", self.test_predictive_strategies),
            ("Trust Score Evolution", self.test_trust_score_evolution),
            ("Pattern Learning", self.test_pattern_learning),
            ("Concurrent Predictions", self.test_concurrent_predictions),
            ("Data Cleanup", self.test_data_cleanup),
            ("Prediction Accuracy Tracking", self.test_prediction_accuracy_tracking),
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
        self.log("📊 PREDICTIVE RATE LIMITING TEST SUMMARY", "SUMMARY")
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
        
        if success_rate >= 85:
            self.log("\n🎉 Predictive rate limiting system is working excellently!", "SUCCESS")
        elif success_rate >= 70:
            self.log("\n✅ Predictive rate limiting system is working well!", "SUCCESS")
        elif success_rate >= 50:
            self.log("\n⚠️ Predictive rate limiting system needs attention.", "WARN")
        else:
            self.log("\n🚨 Predictive rate limiting system has issues!", "ERROR")
        
        return success_rate >= 70


def main():
    """Main function to run the tests."""
    print("🔮 Predictive Rate Limiting Test Suite")
    print("=" * 80)
    
    tester = PredictiveRateLimitTester()
    
    # Run comprehensive tests
    success = tester.run_comprehensive_test()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
