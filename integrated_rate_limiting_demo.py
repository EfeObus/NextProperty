#!/usr/bin/env python3
"""
Complete Rate Limiting Integration Demo
Demonstrates how abuse detection, pattern analysis, and predictive rate limiting work together.
"""

import time
import sys
import random
from datetime import datetime

# Add the project root to Python path
sys.path.append('.')

from app.security.abuse_detection import AbuseDetectionRateLimiter
from app.security.pattern_analysis_rate_limiter import (
    check_pattern_analysis_rate_limit, PatternAnalysisType, record_pattern_analysis
)
from app.security.predictive_rate_limiter import check_predictive_rate_limit


class IntegratedRateLimitingDemo:
    """Demo showing integrated rate limiting capabilities."""
    
    def __init__(self):
        self.abuse_limiter = AbuseDetectionRateLimiter()
        
    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")
    
    def simulate_normal_user(self, user_id: str, num_requests: int = 20):
        """Simulate a normal user's request pattern."""
        self.log(f"👤 Simulating Normal User: {user_id}", "DEMO")
        
        allowed_requests = 0
        blocked_requests = 0
        
        for i in range(num_requests):
            # Simulate normal search behavior
            endpoint_category = random.choice(['search_api', 'property_details', 'user_uploads'])
            
            # 1. Check predictive rate limiting first
            pred_allowed, pred_retry, pred_meta = check_predictive_rate_limit(
                user_id, endpoint_category, {'request_id': i, 'user_type': 'normal'}
            )
            
            if pred_allowed:
                # 2. If predictive allows, check pattern analysis for complex operations
                if endpoint_category == 'property_details':
                    pattern_allowed, pattern_retry, pattern_reason = check_pattern_analysis_rate_limit(
                        user_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS, 2048, {'analysis_depth': 'moderate'}
                    )
                    
                    if pattern_allowed:
                        record_pattern_analysis(
                            user_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS, 2048, 
                            {'analysis_depth': 'moderate'}, random.uniform(0.1, 0.5)
                        )
                        allowed_requests += 1
                        self.log(f"  ✅ Request {i+1}: Predictive + Pattern Analysis allowed")
                    else:
                        blocked_requests += 1
                        self.log(f"  🚫 Request {i+1}: Blocked by pattern analysis ({pattern_reason})")
                else:
                    allowed_requests += 1
                    self.log(f"  ✅ Request {i+1}: Predictive allowed")
            else:
                blocked_requests += 1
                self.log(f"  🚫 Request {i+1}: Blocked by predictive limiting")
            
            # Normal user has reasonable intervals
            time.sleep(random.uniform(0.5, 2.0))
        
        self.log(f"👤 Normal User Results: {allowed_requests} allowed, {blocked_requests} blocked")
        return allowed_requests, blocked_requests
    
    def simulate_power_user(self, user_id: str, num_requests: int = 50):
        """Simulate a power user with higher usage patterns."""
        self.log(f"💪 Simulating Power User: {user_id}", "DEMO")
        
        allowed_requests = 0
        blocked_requests = 0
        
        for i in range(num_requests):
            # Power users do more complex operations
            endpoint_category = random.choice(['analytics', 'property_details', 'search_api'])
            
            # 1. Predictive rate limiting with premium tier
            pred_allowed, pred_retry, pred_meta = check_predictive_rate_limit(
                f"premium:{user_id}", endpoint_category, 
                {'request_id': i, 'user_type': 'power', 'tier': 'premium'}
            )
            
            if pred_allowed:
                # 2. Complex pattern analysis for analytics
                if endpoint_category == 'analytics':
                    pattern_allowed, pattern_retry, pattern_reason = check_pattern_analysis_rate_limit(
                        f"premium:{user_id}", PatternAnalysisType.CORRELATION_ANALYSIS, 
                        10240, {'complexity': 'high', 'data_sources': 3}
                    )
                    
                    if pattern_allowed:
                        record_pattern_analysis(
                            f"premium:{user_id}", PatternAnalysisType.CORRELATION_ANALYSIS, 
                            10240, {'complexity': 'high'}, random.uniform(0.3, 1.0)
                        )
                        allowed_requests += 1
                        self.log(f"  ✅ Request {i+1}: Complex analytics allowed")
                    else:
                        blocked_requests += 1
                        self.log(f"  🚫 Request {i+1}: Complex analytics blocked ({pattern_reason})")
                else:
                    allowed_requests += 1
                    self.log(f"  ✅ Request {i+1}: Standard request allowed")
            else:
                blocked_requests += 1
                self.log(f"  🚫 Request {i+1}: Blocked by predictive limiting")
            
            # Power users work faster
            time.sleep(random.uniform(0.2, 1.0))
        
        self.log(f"💪 Power User Results: {allowed_requests} allowed, {blocked_requests} blocked")
        return allowed_requests, blocked_requests
    
    def simulate_suspicious_user(self, user_id: str, num_requests: int = 100):
        """Simulate a suspicious user triggering abuse detection."""
        self.log(f"🚨 Simulating Suspicious User: {user_id}", "DEMO")
        
        allowed_requests = 0
        blocked_requests = 0
        abuse_detected = False
        
        for i in range(num_requests):
            # Suspicious users make rapid, repetitive requests
            endpoint_category = 'search_api'  # Repetitive behavior
            
            # 1. Check abuse detection first for rapid requests
            abuse_allowed, abuse_retry, abuse_incident = self.abuse_limiter.check_abuse_rate_limit(user_id)
            
            if abuse_incident:
                abuse_detected = True
                self.log(f"  🚨 Abuse detected: {abuse_incident.abuse_type.value} (Level: {abuse_incident.level.value})")
            
            if abuse_allowed:
                # 2. Predictive rate limiting (will learn suspicious pattern)
                pred_allowed, pred_retry, pred_meta = check_predictive_rate_limit(
                    user_id, endpoint_category, 
                    {'request_id': i, 'user_type': 'suspicious', 'rapid': True}
                )
                
                if pred_allowed:
                    allowed_requests += 1
                    if i % 20 == 0:  # Log every 20th request
                        self.log(f"  ✅ Request {i+1}: Still allowed (behavior: {pred_meta.get('behavior_type')})")
                else:
                    blocked_requests += 1
                    self.log(f"  🚫 Request {i+1}: Blocked by predictive limiting")
            else:
                blocked_requests += 1
                if i % 10 == 0:  # Log every 10th blocked request
                    self.log(f"  🚫 Request {i+1}: Blocked by abuse detection")
            
            # Suspicious users make very rapid requests
            time.sleep(random.uniform(0.01, 0.1))
        
        self.log(f"🚨 Suspicious User Results: {allowed_requests} allowed, {blocked_requests} blocked")
        self.log(f"🚨 Abuse Detection Triggered: {abuse_detected}")
        return allowed_requests, blocked_requests, abuse_detected
    
    def simulate_api_client(self, client_id: str, num_requests: int = 200):
        """Simulate an API client with batch operations."""
        self.log(f"🤖 Simulating API Client: {client_id}", "DEMO")
        
        allowed_requests = 0
        blocked_requests = 0
        
        # API clients often do batch operations
        batch_sizes = [10, 20, 5, 15, 8]
        
        for batch_num, batch_size in enumerate(batch_sizes):
            self.log(f"  📦 Processing batch {batch_num + 1} ({batch_size} requests)")
            
            for i in range(batch_size):
                request_id = batch_num * 50 + i
                
                # API clients use different endpoints
                endpoint_category = random.choice(['api_calls', 'analytics', 'property_details'])
                
                # 1. Predictive rate limiting for API tier
                pred_allowed, pred_retry, pred_meta = check_predictive_rate_limit(
                    f"api:{client_id}", endpoint_category,
                    {'batch_id': batch_num, 'request_id': request_id, 'client_type': 'api'}
                )
                
                if pred_allowed:
                    # 2. Pattern analysis for complex data processing
                    if endpoint_category == 'analytics':
                        pattern_allowed, pattern_retry, pattern_reason = check_pattern_analysis_rate_limit(
                            f"api:{client_id}", PatternAnalysisType.TEMPORAL_ANALYSIS,
                            51200, {'batch_processing': True, 'data_range': '30_days'}
                        )
                        
                        if pattern_allowed:
                            record_pattern_analysis(
                                f"api:{client_id}", PatternAnalysisType.TEMPORAL_ANALYSIS,
                                51200, {'batch_processing': True}, random.uniform(0.5, 2.0)
                            )
                            allowed_requests += 1
                        else:
                            blocked_requests += 1
                            self.log(f"    🚫 Batch {batch_num + 1}, Request {i+1}: Pattern analysis blocked")
                    else:
                        allowed_requests += 1
                else:
                    blocked_requests += 1
                    self.log(f"    🚫 Batch {batch_num + 1}, Request {i+1}: Predictive limiting blocked")
                
                # API clients are consistent but fast
                time.sleep(0.05)
            
            # Pause between batches
            time.sleep(1.0)
        
        self.log(f"🤖 API Client Results: {allowed_requests} allowed, {blocked_requests} blocked")
        return allowed_requests, blocked_requests
    
    def run_comprehensive_demo(self):
        """Run comprehensive demo of all rate limiting systems."""
        self.log("🚀 Starting Comprehensive Rate Limiting Demo", "DEMO")
        self.log("=" * 80)
        
        start_time = time.time()
        
        # Simulate different user types
        scenarios = [
            ("Normal User", lambda: self.simulate_normal_user("user_normal_001", 15)),
            ("Power User", lambda: self.simulate_power_user("user_power_001", 25)),
            ("Suspicious User", lambda: self.simulate_suspicious_user("user_suspicious_001", 50)),
            ("API Client", lambda: self.simulate_api_client("client_api_001", 40)),
        ]
        
        results = {}
        
        for scenario_name, scenario_func in scenarios:
            self.log("-" * 80)
            self.log(f"🎬 Running Scenario: {scenario_name}", "SCENARIO")
            
            try:
                result = scenario_func()
                results[scenario_name] = result
                self.log(f"✅ {scenario_name} completed")
            except Exception as e:
                self.log(f"❌ {scenario_name} failed: {e}", "ERROR")
                results[scenario_name] = (0, 0)
            
            time.sleep(2)  # Pause between scenarios
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Summary
        self.log("=" * 80)
        self.log("📊 COMPREHENSIVE RATE LIMITING DEMO SUMMARY", "SUMMARY")
        self.log("=" * 80)
        
        total_allowed = 0
        total_blocked = 0
        
        for scenario_name, result in results.items():
            if len(result) == 2:  # Normal result
                allowed, blocked = result
                total_allowed += allowed
                total_blocked += blocked
                self.log(f"{scenario_name}: {allowed} allowed, {blocked} blocked")
            else:  # Suspicious user with abuse detection
                allowed, blocked, abuse_detected = result
                total_allowed += allowed
                total_blocked += blocked
                self.log(f"{scenario_name}: {allowed} allowed, {blocked} blocked (Abuse: {abuse_detected})")
        
        total_requests = total_allowed + total_blocked
        success_rate = (total_allowed / total_requests * 100) if total_requests > 0 else 0
        
        self.log(f"\nOverall Statistics:")
        self.log(f"  Total requests: {total_requests}")
        self.log(f"  Allowed: {total_allowed} ({success_rate:.1f}%)")
        self.log(f"  Blocked: {total_blocked} ({100-success_rate:.1f}%)")
        self.log(f"  Demo duration: {total_time:.1f}s")
        
        # Get system status
        try:
            from app.security.predictive_rate_limiter import get_global_prediction_metrics
            metrics = get_global_prediction_metrics()
            self.log(f"\nSystem Status:")
            self.log(f"  Tracked clients: {metrics['total_clients']}")
            self.log(f"  Average trust score: {metrics['average_trust_score']:.3f}")
            
            if metrics['behavior_distribution']:
                self.log(f"  Behavior distribution:")
                for behavior, count in metrics['behavior_distribution'].items():
                    self.log(f"    {behavior}: {count}")
        except Exception as e:
            self.log(f"Could not get system metrics: {e}", "WARN")
        
        self.log("\n🎉 Demo completed successfully!")
        self.log("All three rate limiting systems (Abuse Detection, Pattern Analysis, Predictive) are working together!")


def main():
    """Main function to run the demo."""
    print("🔗 Integrated Rate Limiting Systems Demo")
    print("Demonstrating Abuse Detection + Pattern Analysis + Predictive Limiting")
    print("=" * 80)
    
    demo = IntegratedRateLimitingDemo()
    demo.run_comprehensive_demo()


if __name__ == "__main__":
    main()
