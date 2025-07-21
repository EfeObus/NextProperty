"""
Predictive Rate Limiting System
Implements intelligent rate limiting based on usage patterns, predictions, and behavioral analysis.
"""

import time
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
from threading import Lock
import json

# Try to import Redis for distributed caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class PredictionModel(Enum):
    """Prediction models for different types of rate limiting."""
    LINEAR_REGRESSION = "linear_regression"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    MOVING_AVERAGE = "moving_average"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    ADAPTIVE_THRESHOLD = "adaptive_threshold"


class PredictiveStrategy(Enum):
    """Strategies for predictive rate limiting."""
    CONSERVATIVE = "conservative"     # Stricter limits based on predictions
    BALANCED = "balanced"            # Moderate adjustments
    AGGRESSIVE = "aggressive"        # More permissive with predictions
    ADAPTIVE = "adaptive"            # Self-adjusting based on accuracy


class ClientBehaviorType(Enum):
    """Types of client behavior patterns."""
    NORMAL = "normal"
    BURSTY = "bursty"
    STEADY = "steady"
    IRREGULAR = "irregular"
    SUSPICIOUS = "suspicious"


@dataclass
class PredictionMetrics:
    """Metrics for prediction accuracy and performance."""
    predicted_requests: int = 0
    actual_requests: int = 0
    accuracy_score: float = 0.0
    prediction_confidence: float = 0.0
    model_variance: float = 0.0
    last_updated: float = field(default_factory=time.time)


@dataclass
class ClientProfile:
    """Profile of client behavior and patterns."""
    client_id: str
    behavior_type: ClientBehaviorType = ClientBehaviorType.NORMAL
    request_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    hourly_patterns: Dict[int, List[int]] = field(default_factory=lambda: defaultdict(list))
    daily_patterns: Dict[int, List[int]] = field(default_factory=lambda: defaultdict(list))
    prediction_metrics: PredictionMetrics = field(default_factory=PredictionMetrics)
    trust_score: float = 1.0
    last_activity: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)


@dataclass
class PredictiveLimit:
    """A predictive rate limit configuration."""
    base_limit: int
    prediction_window: int  # seconds
    adjustment_factor: float = 1.0
    min_limit: int = 1
    max_limit: int = 1000
    strategy: PredictiveStrategy = PredictiveStrategy.BALANCED
    model: PredictionModel = PredictionModel.EXPONENTIAL_SMOOTHING


class PredictiveRateLimiter:
    """Advanced rate limiter with predictive capabilities."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.client_profiles: Dict[str, ClientProfile] = {}
        self.global_patterns: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()
        
        # Predictive limits configuration
        self.predictive_limits = {
            # API endpoint categories
            'search_api': PredictiveLimit(
                base_limit=100, prediction_window=300, 
                strategy=PredictiveStrategy.BALANCED,
                model=PredictionModel.EXPONENTIAL_SMOOTHING
            ),
            'property_details': PredictiveLimit(
                base_limit=200, prediction_window=600,
                strategy=PredictiveStrategy.CONSERVATIVE,
                model=PredictionModel.MOVING_AVERAGE
            ),
            'user_uploads': PredictiveLimit(
                base_limit=50, prediction_window=900,
                strategy=PredictiveStrategy.CONSERVATIVE,
                model=PredictionModel.ADAPTIVE_THRESHOLD
            ),
            'analytics': PredictiveLimit(
                base_limit=30, prediction_window=1800,
                strategy=PredictiveStrategy.AGGRESSIVE,
                model=PredictionModel.SEASONAL_DECOMPOSITION
            ),
            'admin_operations': PredictiveLimit(
                base_limit=500, prediction_window=300,
                strategy=PredictiveStrategy.ADAPTIVE,
                model=PredictionModel.LINEAR_REGRESSION
            ),
            
            # Client types
            'premium_users': PredictiveLimit(
                base_limit=300, prediction_window=600,
                strategy=PredictiveStrategy.AGGRESSIVE,
                adjustment_factor=1.5
            ),
            'free_users': PredictiveLimit(
                base_limit=100, prediction_window=300,
                strategy=PredictiveStrategy.CONSERVATIVE,
                adjustment_factor=0.8
            ),
            'api_clients': PredictiveLimit(
                base_limit=1000, prediction_window=3600,
                strategy=PredictiveStrategy.BALANCED,
                adjustment_factor=1.2
            ),
            
            # Behavioral patterns
            'burst_tolerance': PredictiveLimit(
                base_limit=50, prediction_window=60,
                strategy=PredictiveStrategy.ADAPTIVE,
                model=PredictionModel.EXPONENTIAL_SMOOTHING
            ),
            'sustained_load': PredictiveLimit(
                base_limit=200, prediction_window=1800,
                strategy=PredictiveStrategy.BALANCED,
                model=PredictionModel.LINEAR_REGRESSION
            )
        }
        
        # Prediction accuracy tracking
        self.prediction_history: deque = deque(maxlen=10000)
        self.model_performance: Dict[PredictionModel, PredictionMetrics] = {
            model: PredictionMetrics() for model in PredictionModel
        }
        
    def get_or_create_client_profile(self, client_id: str) -> ClientProfile:
        """Get or create a client profile."""
        if client_id not in self.client_profiles:
            with self.lock:
                if client_id not in self.client_profiles:
                    self.client_profiles[client_id] = ClientProfile(client_id=client_id)
        
        return self.client_profiles[client_id]
    
    def record_request(self, client_id: str, endpoint_category: str, 
                      request_data: Dict[str, Any] = None):
        """Record a request for predictive analysis."""
        current_time = time.time()
        profile = self.get_or_create_client_profile(client_id)
        
        # Update request history
        request_info = {
            'timestamp': current_time,
            'endpoint_category': endpoint_category,
            'data': request_data or {}
        }
        profile.request_history.append(request_info)
        profile.last_activity = current_time
        
        # Update hourly and daily patterns
        dt = datetime.fromtimestamp(current_time)
        hour = dt.hour
        day_of_week = dt.weekday()
        
        profile.hourly_patterns[hour].append(1)
        profile.daily_patterns[day_of_week].append(1)
        
        # Keep only recent pattern data
        for hour_data in profile.hourly_patterns.values():
            if len(hour_data) > 100:
                hour_data[:] = hour_data[-50:]
        
        for day_data in profile.daily_patterns.values():
            if len(day_data) > 50:
                day_data[:] = day_data[-25:]
        
        # Update global patterns
        self.global_patterns[endpoint_category].append(current_time)
        if len(self.global_patterns[endpoint_category]) > 10000:
            self.global_patterns[endpoint_category] = \
                self.global_patterns[endpoint_category][-5000:]
        
        # Analyze behavior type
        self._update_behavior_type(profile)
    
    def _update_behavior_type(self, profile: ClientProfile):
        """Update client behavior type based on request patterns."""
        if len(profile.request_history) < 10:
            return
        
        recent_requests = list(profile.request_history)[-50:]
        timestamps = [req['timestamp'] for req in recent_requests]
        
        if len(timestamps) < 5:
            return
        
        # Calculate request intervals
        intervals = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        
        # Analyze patterns
        mean_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
        coefficient_of_variation = std_interval / mean_interval if mean_interval > 0 else 0
        
        # Classify behavior
        if coefficient_of_variation < 0.3:
            profile.behavior_type = ClientBehaviorType.STEADY
        elif coefficient_of_variation > 1.5:
            profile.behavior_type = ClientBehaviorType.BURSTY
        elif mean_interval < 1.0:  # Very frequent requests
            profile.behavior_type = ClientBehaviorType.SUSPICIOUS
        elif coefficient_of_variation > 0.8:
            profile.behavior_type = ClientBehaviorType.IRREGULAR
        else:
            profile.behavior_type = ClientBehaviorType.NORMAL
    
    def predict_future_requests(self, client_id: str, endpoint_category: str,
                               prediction_window: int, model: PredictionModel) -> Tuple[int, float]:
        """Predict future request count using specified model."""
        profile = self.get_or_create_client_profile(client_id)
        
        if len(profile.request_history) < 5:
            return 0, 0.5  # Low confidence for new clients
        
        current_time = time.time()
        
        # Get recent request data
        window_start = current_time - prediction_window * 2  # Look back 2x prediction window
        recent_requests = [
            req for req in profile.request_history 
            if req['timestamp'] >= window_start and 
               req.get('endpoint_category') == endpoint_category
        ]
        
        if len(recent_requests) < 3:
            return 0, 0.3
        
        # Apply prediction model
        if model == PredictionModel.LINEAR_REGRESSION:
            return self._linear_regression_prediction(recent_requests, prediction_window)
        elif model == PredictionModel.EXPONENTIAL_SMOOTHING:
            return self._exponential_smoothing_prediction(recent_requests, prediction_window)
        elif model == PredictionModel.MOVING_AVERAGE:
            return self._moving_average_prediction(recent_requests, prediction_window)
        elif model == PredictionModel.SEASONAL_DECOMPOSITION:
            return self._seasonal_prediction(profile, endpoint_category, prediction_window)
        elif model == PredictionModel.ADAPTIVE_THRESHOLD:
            return self._adaptive_threshold_prediction(recent_requests, prediction_window)
        else:
            return self._exponential_smoothing_prediction(recent_requests, prediction_window)
    
    def _linear_regression_prediction(self, requests: List[Dict], window: int) -> Tuple[int, float]:
        """Linear regression prediction model."""
        if len(requests) < 3:
            return 0, 0.3
        
        # Group requests by time buckets
        bucket_size = 60  # 1-minute buckets
        buckets = defaultdict(int)
        
        base_time = requests[0]['timestamp']
        for req in requests:
            bucket = int((req['timestamp'] - base_time) / bucket_size)
            buckets[bucket] += 1
        
        if len(buckets) < 2:
            return len(requests), 0.5
        
        # Simple linear regression
        x_values = list(buckets.keys())
        y_values = list(buckets.values())
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Calculate slope and intercept
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return int(sum_y / n), 0.4
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        # Predict for the next window
        next_bucket = max(x_values) + (window / bucket_size)
        predicted = max(0, slope * next_bucket + intercept)
        
        # Calculate confidence based on variance
        variance = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, y_values)) / n
        confidence = max(0.1, min(0.9, 1.0 / (1.0 + variance)))
        
        return int(predicted), confidence
    
    def _exponential_smoothing_prediction(self, requests: List[Dict], window: int) -> Tuple[int, float]:
        """Exponential smoothing prediction model."""
        if len(requests) < 2:
            return 0, 0.3
        
        # Group by time intervals
        interval_size = max(60, window // 10)  # At least 1 minute intervals
        intervals = defaultdict(int)
        
        base_time = requests[0]['timestamp']
        for req in requests:
            interval = int((req['timestamp'] - base_time) / interval_size)
            intervals[interval] += 1
        
        if len(intervals) < 2:
            return len(requests), 0.4
        
        # Exponential smoothing
        alpha = 0.3  # Smoothing parameter
        values = [intervals.get(i, 0) for i in range(max(intervals.keys()) + 1)]
        
        if len(values) < 2:
            return int(statistics.mean(values)), 0.4
        
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[i-1])
        
        # Predict next value
        predicted = smoothed[-1]
        
        # Scale to prediction window
        predicted_count = predicted * (window / interval_size)
        
        # Calculate confidence based on recent accuracy
        recent_errors = [abs(values[i] - smoothed[i]) for i in range(len(values))]
        avg_error = statistics.mean(recent_errors) if recent_errors else 0
        confidence = max(0.1, min(0.9, 1.0 / (1.0 + avg_error)))
        
        return int(predicted_count), confidence
    
    def _moving_average_prediction(self, requests: List[Dict], window: int) -> Tuple[int, float]:
        """Moving average prediction model."""
        if len(requests) < 3:
            return 0, 0.3
        
        # Calculate request rate over time
        time_span = requests[-1]['timestamp'] - requests[0]['timestamp']
        if time_span < 60:  # Less than 1 minute of data
            return len(requests), 0.4
        
        # Calculate moving averages for different window sizes
        windows = [300, 600, 1800]  # 5min, 10min, 30min
        rates = []
        
        current_time = time.time()
        
        for w in windows:
            window_start = current_time - w
            window_requests = [r for r in requests if r['timestamp'] >= window_start]
            if window_requests:
                rate = len(window_requests) / (w / 60)  # requests per minute
                rates.append(rate)
        
        if not rates:
            return 0, 0.3
        
        # Weighted average (more recent = higher weight)
        weights = [3, 2, 1][:len(rates)]
        weighted_rate = sum(r * w for r, w in zip(rates, weights)) / sum(weights)
        
        # Predict for the window
        predicted_count = weighted_rate * (window / 60)
        
        # Confidence based on rate consistency
        if len(rates) > 1:
            rate_variance = statistics.variance(rates)
            confidence = max(0.2, min(0.8, 1.0 / (1.0 + rate_variance)))
        else:
            confidence = 0.5
        
        return int(predicted_count), confidence
    
    def _seasonal_prediction(self, profile: ClientProfile, endpoint_category: str, 
                           window: int) -> Tuple[int, float]:
        """Seasonal decomposition prediction model."""
        current_time = time.time()
        dt = datetime.fromtimestamp(current_time)
        current_hour = dt.hour
        current_day = dt.weekday()
        
        # Get hourly pattern
        hourly_avg = 0
        if current_hour in profile.hourly_patterns:
            hourly_data = profile.hourly_patterns[current_hour]
            if hourly_data:
                hourly_avg = statistics.mean(hourly_data)
        
        # Get daily pattern
        daily_avg = 0
        if current_day in profile.daily_patterns:
            daily_data = profile.daily_patterns[current_day]
            if daily_data:
                daily_avg = statistics.mean(daily_data)
        
        # Combine patterns with global trends
        global_recent = [
            t for t in self.global_patterns[endpoint_category]
            if t >= current_time - 3600  # Last hour
        ]
        global_rate = len(global_recent) / 60 if global_recent else 0  # per minute
        
        # Weighted prediction
        if hourly_avg > 0 and daily_avg > 0:
            seasonal_factor = (hourly_avg + daily_avg) / 2
            predicted = seasonal_factor * (window / 300) + global_rate * (window / 60)
            confidence = 0.7
        elif hourly_avg > 0:
            predicted = hourly_avg * (window / 300)
            confidence = 0.5
        else:
            predicted = global_rate * (window / 60)
            confidence = 0.3
        
        return int(predicted), confidence
    
    def _adaptive_threshold_prediction(self, requests: List[Dict], window: int) -> Tuple[int, float]:
        """Adaptive threshold prediction model."""
        if len(requests) < 5:
            return 0, 0.3
        
        # Calculate recent request patterns
        recent_intervals = []
        for i in range(1, len(requests)):
            interval = requests[i]['timestamp'] - requests[i-1]['timestamp']
            recent_intervals.append(interval)
        
        if not recent_intervals:
            return 0, 0.3
        
        # Adaptive threshold based on recent behavior
        mean_interval = statistics.mean(recent_intervals)
        std_interval = statistics.stdev(recent_intervals) if len(recent_intervals) > 1 else 0
        
        # Predict based on adaptive threshold
        if mean_interval > 0:
            expected_requests = window / mean_interval
            
            # Adjust for variance
            if std_interval > mean_interval:  # High variance
                adjustment = 1.3  # Expect more burst
            else:  # Low variance
                adjustment = 0.9  # Expect steady rate
            
            predicted = expected_requests * adjustment
            
            # Confidence based on interval consistency
            coefficient_of_variation = std_interval / mean_interval if mean_interval > 0 else 1
            confidence = max(0.2, min(0.8, 1.0 / (1.0 + coefficient_of_variation)))
        else:
            predicted = len(requests)
            confidence = 0.4
        
        return int(predicted), confidence
    
    def check_predictive_rate_limit(self, client_id: str, endpoint_category: str,
                                  limit_type: str = None) -> Tuple[bool, int, Dict[str, Any]]:
        """Check if request should be allowed based on predictive analysis."""
        current_time = time.time()
        profile = self.get_or_create_client_profile(client_id)
        
        # Determine which limit to use
        if limit_type and limit_type in self.predictive_limits:
            limit_config = self.predictive_limits[limit_type]
        elif endpoint_category in self.predictive_limits:
            limit_config = self.predictive_limits[endpoint_category]
        else:
            # Use default based on client type
            client_type = self._determine_client_type(client_id)
            limit_config = self.predictive_limits.get(client_type, 
                          self.predictive_limits['free_users'])
        
        # Get current request count in window
        window_start = current_time - limit_config.prediction_window
        current_requests = len([
            req for req in profile.request_history
            if req['timestamp'] >= window_start and 
               req.get('endpoint_category') == endpoint_category
        ])
        
        # Get prediction
        predicted_requests, confidence = self.predict_future_requests(
            client_id, endpoint_category, limit_config.prediction_window, limit_config.model
        )
        
        # Calculate dynamic limit based on strategy
        dynamic_limit = self._calculate_dynamic_limit(
            limit_config, profile, predicted_requests, confidence
        )
        
        # Check if current + predicted exceeds limit
        total_expected = current_requests + predicted_requests
        
        # Apply strategy-based decision
        if limit_config.strategy == PredictiveStrategy.CONSERVATIVE:
            # Block if likely to exceed 80% of limit
            threshold = dynamic_limit * 0.8
        elif limit_config.strategy == PredictiveStrategy.AGGRESSIVE:
            # Allow until likely to exceed 120% of limit
            threshold = dynamic_limit * 1.2
        elif limit_config.strategy == PredictiveStrategy.ADAPTIVE:
            # Use confidence to adjust threshold
            threshold = dynamic_limit * (0.7 + confidence * 0.5)
        else:  # BALANCED
            threshold = dynamic_limit
        
        allowed = total_expected <= threshold
        
        # Calculate retry after if blocked
        retry_after = 0
        if not allowed:
            excess = total_expected - threshold
            # Estimate time for excess requests to expire
            if current_requests > 0:
                avg_interval = limit_config.prediction_window / current_requests
                retry_after = int(excess * avg_interval)
            else:
                retry_after = limit_config.prediction_window // 4
        
        # Update prediction accuracy if we have historical data
        self._update_prediction_accuracy(
            client_id, endpoint_category, predicted_requests, limit_config.model
        )
        
        # Return decision with metadata
        metadata = {
            'current_requests': current_requests,
            'predicted_requests': predicted_requests,
            'prediction_confidence': confidence,
            'dynamic_limit': dynamic_limit,
            'threshold_used': threshold,
            'strategy': limit_config.strategy.value,
            'model': limit_config.model.value,
            'behavior_type': profile.behavior_type.value,
            'trust_score': profile.trust_score
        }
        
        return allowed, retry_after, metadata
    
    def _determine_client_type(self, client_id: str) -> str:
        """Determine client type from client ID."""
        if client_id.startswith('premium:'):
            return 'premium_users'
        elif client_id.startswith('api:'):
            return 'api_clients'
        elif client_id.startswith('admin:'):
            return 'admin_operations'
        else:
            return 'free_users'
    
    def _calculate_dynamic_limit(self, limit_config: PredictiveLimit, 
                               profile: ClientProfile, predicted_requests: int,
                               confidence: float) -> int:
        """Calculate dynamic limit based on client profile and predictions."""
        base_limit = limit_config.base_limit
        
        # Adjust based on behavior type
        behavior_multipliers = {
            ClientBehaviorType.NORMAL: 1.0,
            ClientBehaviorType.STEADY: 1.1,
            ClientBehaviorType.BURSTY: 0.9,
            ClientBehaviorType.IRREGULAR: 0.8,
            ClientBehaviorType.SUSPICIOUS: 0.6
        }
        
        behavior_adj = behavior_multipliers.get(profile.behavior_type, 1.0)
        
        # Adjust based on trust score
        trust_adj = profile.trust_score
        
        # Adjust based on prediction confidence
        confidence_adj = 0.8 + (confidence * 0.4)  # 0.8 to 1.2 range
        
        # Apply adjustments
        dynamic_limit = base_limit * limit_config.adjustment_factor
        dynamic_limit *= behavior_adj * trust_adj * confidence_adj
        
        # Ensure within bounds
        dynamic_limit = max(limit_config.min_limit, 
                           min(limit_config.max_limit, int(dynamic_limit)))
        
        return dynamic_limit
    
    def _update_prediction_accuracy(self, client_id: str, endpoint_category: str,
                                  predicted_requests: int, model: PredictionModel):
        """Update prediction accuracy metrics for continuous improvement."""
        current_time = time.time()
        profile = self.get_or_create_client_profile(client_id)
        
        # Check if we have a previous prediction to validate
        window_start = current_time - 300  # 5 minutes ago
        actual_requests = len([
            req for req in profile.request_history
            if req['timestamp'] >= window_start and
               req.get('endpoint_category') == endpoint_category
        ])
        
        # Update model performance
        if model in self.model_performance:
            metrics = self.model_performance[model]
            metrics.actual_requests = actual_requests
            metrics.predicted_requests = predicted_requests
            
            if predicted_requests > 0:
                accuracy = 1.0 - abs(actual_requests - predicted_requests) / predicted_requests
                metrics.accuracy_score = max(0.0, accuracy)
            
            metrics.last_updated = current_time
        
        # Update client trust score based on behavior consistency
        if len(profile.request_history) > 20:
            recent_pattern_variance = self._calculate_pattern_variance(profile)
            if recent_pattern_variance < 0.5:  # Consistent behavior
                profile.trust_score = min(1.0, profile.trust_score + 0.01)
            elif recent_pattern_variance > 1.5:  # Erratic behavior
                profile.trust_score = max(0.1, profile.trust_score - 0.02)
    
    def _calculate_pattern_variance(self, profile: ClientProfile) -> float:
        """Calculate variance in request patterns for trust scoring."""
        if len(profile.request_history) < 10:
            return 0.5
        
        recent_requests = list(profile.request_history)[-20:]
        intervals = [
            recent_requests[i]['timestamp'] - recent_requests[i-1]['timestamp']
            for i in range(1, len(recent_requests))
        ]
        
        if len(intervals) < 2:
            return 0.5
        
        mean_interval = statistics.mean(intervals)
        variance = statistics.variance(intervals)
        
        return variance / (mean_interval ** 2) if mean_interval > 0 else 1.0
    
    def get_client_prediction_status(self, client_id: str) -> Dict[str, Any]:
        """Get prediction status and metrics for a client."""
        profile = self.get_or_create_client_profile(client_id)
        
        status = {
            'client_id': client_id,
            'behavior_type': profile.behavior_type.value,
            'trust_score': profile.trust_score,
            'total_requests': len(profile.request_history),
            'last_activity': datetime.fromtimestamp(profile.last_activity).isoformat(),
            'prediction_metrics': {
                'accuracy': profile.prediction_metrics.accuracy_score,
                'confidence': profile.prediction_metrics.prediction_confidence,
                'variance': profile.prediction_metrics.model_variance
            },
            'pattern_analysis': {
                'hourly_patterns': {
                    hour: statistics.mean(data) if data else 0
                    for hour, data in profile.hourly_patterns.items()
                },
                'daily_patterns': {
                    day: statistics.mean(data) if data else 0
                    for day, data in profile.daily_patterns.items()
                }
            }
        }
        
        return status
    
    def get_global_prediction_metrics(self) -> Dict[str, Any]:
        """Get global prediction system metrics."""
        total_clients = len(self.client_profiles)
        
        # Calculate average metrics across all models
        model_stats = {}
        for model, metrics in self.model_performance.items():
            model_stats[model.value] = {
                'accuracy_score': metrics.accuracy_score,
                'prediction_confidence': metrics.prediction_confidence,
                'last_updated': datetime.fromtimestamp(metrics.last_updated).isoformat()
            }
        
        # Behavior type distribution
        behavior_distribution = defaultdict(int)
        trust_scores = []
        
        for profile in self.client_profiles.values():
            behavior_distribution[profile.behavior_type.value] += 1
            trust_scores.append(profile.trust_score)
        
        avg_trust_score = statistics.mean(trust_scores) if trust_scores else 0.0
        
        return {
            'total_clients': total_clients,
            'average_trust_score': avg_trust_score,
            'behavior_distribution': dict(behavior_distribution),
            'model_performance': model_stats,
            'global_patterns': {
                category: len(patterns) for category, patterns in self.global_patterns.items()
            }
        }
    
    def clear_client_data(self, client_id: str):
        """Clear all data for a specific client."""
        if client_id in self.client_profiles:
            del self.client_profiles[client_id]
        
        logger.info(f"Cleared predictive rate limiting data for client: {client_id}")
    
    def cleanup_old_data(self, max_age_hours: int = 24):
        """Clean up old client data and patterns."""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        # Clean up inactive client profiles
        inactive_clients = [
            client_id for client_id, profile in self.client_profiles.items()
            if profile.last_activity < cutoff_time
        ]
        
        for client_id in inactive_clients:
            del self.client_profiles[client_id]
        
        # Clean up global patterns
        for category in self.global_patterns:
            self.global_patterns[category] = [
                timestamp for timestamp in self.global_patterns[category]
                if timestamp >= cutoff_time
            ]
        
        logger.info(f"Cleaned up {len(inactive_clients)} inactive client profiles")


# Convenience functions for easy integration
def check_predictive_rate_limit(client_id: str, endpoint_category: str,
                               request_data: Dict[str, Any] = None,
                               limit_type: str = None) -> Tuple[bool, int, Dict[str, Any]]:
    """Check predictive rate limit for a client and endpoint."""
    if not hasattr(check_predictive_rate_limit, '_limiter'):
        check_predictive_rate_limit._limiter = PredictiveRateLimiter()
    
    limiter = check_predictive_rate_limit._limiter
    
    # Record the request attempt
    limiter.record_request(client_id, endpoint_category, request_data)
    
    # Check the limit
    return limiter.check_predictive_rate_limit(client_id, endpoint_category, limit_type)


def get_client_prediction_status(client_id: str) -> Dict[str, Any]:
    """Get prediction status for a client."""
    if not hasattr(check_predictive_rate_limit, '_limiter'):
        check_predictive_rate_limit._limiter = PredictiveRateLimiter()
    
    return check_predictive_rate_limit._limiter.get_client_prediction_status(client_id)


def get_global_prediction_metrics() -> Dict[str, Any]:
    """Get global prediction metrics."""
    if not hasattr(check_predictive_rate_limit, '_limiter'):
        check_predictive_rate_limit._limiter = PredictiveRateLimiter()
    
    return check_predictive_rate_limit._limiter.get_global_prediction_metrics()
