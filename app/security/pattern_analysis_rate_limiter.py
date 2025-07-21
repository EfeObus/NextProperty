"""
Pattern Analysis Rate Limiting for NextProperty AI
Provides rate limiting specifically for pattern analysis operations to prevent abuse
and ensure optimal performance of the analysis system.
"""

import time
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from flask import request, current_app, g
import redis
from threading import Lock
import logging
import json

logger = logging.getLogger(__name__)


class PatternAnalysisType(Enum):
    """Types of pattern analysis operations."""
    BEHAVIORAL_ANALYSIS = "behavioral_analysis"
    FREQUENCY_ANALYSIS = "frequency_analysis"
    ENDPOINT_ANALYSIS = "endpoint_analysis"
    PARAMETER_ANALYSIS = "parameter_analysis"
    TEMPORAL_ANALYSIS = "temporal_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_ANALYSIS = "trend_analysis"


class AnalysisComplexity(Enum):
    """Complexity levels for pattern analysis operations."""
    SIMPLE = 1      # Basic pattern matching
    MODERATE = 2    # Statistical analysis
    COMPLEX = 3     # Machine learning inference
    INTENSIVE = 4   # Deep analysis with correlation


@dataclass
class AnalysisRequest:
    """Represents a pattern analysis request."""
    timestamp: float
    client_id: str
    analysis_type: PatternAnalysisType
    complexity: AnalysisComplexity
    data_size: int
    parameters: Dict[str, Any]
    processing_time: float = 0.0
    cache_hit: bool = False


@dataclass
class AnalysisMetrics:
    """Metrics for pattern analysis operations."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_processing_time: float = 0.0
    cache_hit_rate: float = 0.0
    complexity_distribution: Dict[str, int] = None
    
    def __post_init__(self):
        if self.complexity_distribution is None:
            self.complexity_distribution = {}


class PatternAnalysisRateLimiter:
    """Rate limiter specifically for pattern analysis operations."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.analysis_history = defaultdict(lambda: defaultdict(deque))
        self.metrics = defaultdict(AnalysisMetrics)
        self.lock = Lock()
        
        # Rate limits based on analysis complexity
        self.complexity_limits = {
            AnalysisComplexity.SIMPLE: {
                'requests': 100,    # 100 simple analyses per minute
                'window': 60,
                'concurrent': 10    # Max 10 concurrent simple analyses
            },
            AnalysisComplexity.MODERATE: {
                'requests': 50,     # 50 moderate analyses per minute
                'window': 60,
                'concurrent': 5     # Max 5 concurrent moderate analyses
            },
            AnalysisComplexity.COMPLEX: {
                'requests': 20,     # 20 complex analyses per minute
                'window': 60,
                'concurrent': 3     # Max 3 concurrent complex analyses
            },
            AnalysisComplexity.INTENSIVE: {
                'requests': 5,      # 5 intensive analyses per minute
                'window': 60,
                'concurrent': 1     # Max 1 concurrent intensive analysis
            }
        }
        
        # Type-specific rate limits
        self.type_limits = {
            PatternAnalysisType.BEHAVIORAL_ANALYSIS: {
                'requests': 30, 'window': 60,
                'description': 'Behavioral pattern analysis'
            },
            PatternAnalysisType.FREQUENCY_ANALYSIS: {
                'requests': 60, 'window': 60,
                'description': 'Request frequency analysis'
            },
            PatternAnalysisType.ENDPOINT_ANALYSIS: {
                'requests': 40, 'window': 60,
                'description': 'Endpoint access pattern analysis'
            },
            PatternAnalysisType.PARAMETER_ANALYSIS: {
                'requests': 50, 'window': 60,
                'description': 'Parameter variation analysis'
            },
            PatternAnalysisType.TEMPORAL_ANALYSIS: {
                'requests': 25, 'window': 60,
                'description': 'Temporal pattern analysis'
            },
            PatternAnalysisType.CORRELATION_ANALYSIS: {
                'requests': 15, 'window': 60,
                'description': 'Cross-pattern correlation analysis'
            },
            PatternAnalysisType.ANOMALY_DETECTION: {
                'requests': 20, 'window': 60,
                'description': 'Anomaly detection analysis'
            },
            PatternAnalysisType.TREND_ANALYSIS: {
                'requests': 10, 'window': 60,
                'description': 'Long-term trend analysis'
            }
        }
        
        # Data size-based limits (requests per minute based on data size)
        self.data_size_limits = {
            'small': {'max_size': 1024, 'requests': 100},      # <1KB
            'medium': {'max_size': 10240, 'requests': 50},     # <10KB
            'large': {'max_size': 102400, 'requests': 20},     # <100KB
            'xlarge': {'max_size': 1048576, 'requests': 5},    # <1MB
            'massive': {'max_size': float('inf'), 'requests': 1}  # >1MB
        }
        
        # Client-specific limits
        self.client_limits = {
            'default': {'requests': 100, 'window': 60},
            'premium': {'requests': 200, 'window': 60},
            'admin': {'requests': 500, 'window': 60},
            'system': {'requests': 1000, 'window': 60}
        }
        
        # Cache configuration for analysis results
        self.cache_config = {
            'enabled': True,
            'ttl': 300,  # 5 minutes default TTL
            'max_size': 1000,  # Maximum cached results
            'hit_ratio_threshold': 0.7  # Minimum cache hit ratio
        }
        
        # Performance thresholds
        self.performance_thresholds = {
            'max_processing_time': 30.0,  # 30 seconds max processing time
            'warning_processing_time': 10.0,  # 10 seconds warning threshold
            'max_queue_size': 100,  # Maximum queued analysis requests
            'memory_limit': 512 * 1024 * 1024  # 512MB memory limit
        }
    
    def determine_complexity(self, analysis_type: PatternAnalysisType, 
                           data_size: int, parameters: Dict[str, Any]) -> AnalysisComplexity:
        """Determine the complexity level of an analysis request."""
        
        # Base complexity by analysis type
        type_complexity = {
            PatternAnalysisType.BEHAVIORAL_ANALYSIS: AnalysisComplexity.COMPLEX,
            PatternAnalysisType.FREQUENCY_ANALYSIS: AnalysisComplexity.SIMPLE,
            PatternAnalysisType.ENDPOINT_ANALYSIS: AnalysisComplexity.MODERATE,
            PatternAnalysisType.PARAMETER_ANALYSIS: AnalysisComplexity.MODERATE,
            PatternAnalysisType.TEMPORAL_ANALYSIS: AnalysisComplexity.COMPLEX,
            PatternAnalysisType.CORRELATION_ANALYSIS: AnalysisComplexity.INTENSIVE,
            PatternAnalysisType.ANOMALY_DETECTION: AnalysisComplexity.COMPLEX,
            PatternAnalysisType.TREND_ANALYSIS: AnalysisComplexity.INTENSIVE
        }
        
        base_complexity = type_complexity.get(analysis_type, AnalysisComplexity.MODERATE)
        
        # Adjust based on data size
        if data_size > 1048576:  # >1MB
            return AnalysisComplexity.INTENSIVE
        elif data_size > 102400:  # >100KB
            complexity_value = max(base_complexity.value, AnalysisComplexity.COMPLEX.value)
            return AnalysisComplexity(complexity_value)
        
        # Adjust based on parameters
        if parameters:
            param_count = len(parameters)
            if param_count > 10:
                complexity_value = min(base_complexity.value + 1, AnalysisComplexity.INTENSIVE.value)
                return AnalysisComplexity(complexity_value)
            elif param_count > 5:
                complexity_value = min(base_complexity.value + 1, AnalysisComplexity.COMPLEX.value)
                return AnalysisComplexity(complexity_value)
        
        return base_complexity
    
    def determine_data_size_category(self, data_size: int) -> str:
        """Determine the data size category for rate limiting."""
        for category, config in self.data_size_limits.items():
            if data_size <= config['max_size']:
                return category
        return 'massive'
    
    def get_client_tier(self, client_id: str) -> str:
        """Determine the client tier for rate limiting."""
        if 'admin:' in client_id:
            return 'admin'
        elif 'system:' in client_id:
            return 'system'
        elif 'premium:' in client_id:
            return 'premium'
        else:
            return 'default'
    
    def check_rate_limit(self, client_id: str, analysis_type: PatternAnalysisType,
                        data_size: int, parameters: Dict[str, Any]) -> Tuple[bool, int, str]:
        """Check if the analysis request should be rate limited."""
        
        current_time = time.time()
        complexity = self.determine_complexity(analysis_type, data_size, parameters)
        data_category = self.determine_data_size_category(data_size)
        client_tier = self.get_client_tier(client_id)
        
        # Check complexity-based rate limit
        complexity_allowed, complexity_retry = self._check_complexity_limit(
            client_id, complexity, current_time
        )
        if not complexity_allowed:
            return False, complexity_retry, f"Complexity rate limit exceeded ({complexity.name})"
        
        # Check type-specific rate limit
        type_allowed, type_retry = self._check_type_limit(
            client_id, analysis_type, current_time
        )
        if not type_allowed:
            return False, type_retry, f"Analysis type rate limit exceeded ({analysis_type.value})"
        
        # Check data size-based rate limit
        size_allowed, size_retry = self._check_data_size_limit(
            client_id, data_category, current_time
        )
        if not size_allowed:
            return False, size_retry, f"Data size rate limit exceeded ({data_category})"
        
        # Check client tier rate limit
        client_allowed, client_retry = self._check_client_tier_limit(
            client_id, client_tier, current_time
        )
        if not client_allowed:
            return False, client_retry, f"Client tier rate limit exceeded ({client_tier})"
        
        # Check concurrent analysis limit
        concurrent_allowed, concurrent_reason = self._check_concurrent_limit(
            client_id, complexity
        )
        if not concurrent_allowed:
            return False, 60, concurrent_reason  # 1 minute retry for concurrent limits
        
        return True, 0, "Rate limit check passed"
    
    def _check_complexity_limit(self, client_id: str, complexity: AnalysisComplexity,
                               current_time: float) -> Tuple[bool, int]:
        """Check complexity-based rate limit."""
        if complexity not in self.complexity_limits:
            return True, 0
        
        limit_config = self.complexity_limits[complexity]
        key = f"complexity:{complexity.name}:{client_id}"
        
        return self._check_time_window_limit(
            key, limit_config['requests'], limit_config['window'], current_time
        )
    
    def _check_type_limit(self, client_id: str, analysis_type: PatternAnalysisType,
                         current_time: float) -> Tuple[bool, int]:
        """Check analysis type-based rate limit."""
        if analysis_type not in self.type_limits:
            return True, 0
        
        limit_config = self.type_limits[analysis_type]
        key = f"type:{analysis_type.value}:{client_id}"
        
        return self._check_time_window_limit(
            key, limit_config['requests'], limit_config['window'], current_time
        )
    
    def _check_data_size_limit(self, client_id: str, data_category: str,
                              current_time: float) -> Tuple[bool, int]:
        """Check data size-based rate limit."""
        if data_category not in self.data_size_limits:
            return True, 0
        
        limit_config = self.data_size_limits[data_category]
        key = f"datasize:{data_category}:{client_id}"
        
        return self._check_time_window_limit(
            key, limit_config['requests'], 60, current_time  # 1 minute window
        )
    
    def _check_client_tier_limit(self, client_id: str, client_tier: str,
                                current_time: float) -> Tuple[bool, int]:
        """Check client tier-based rate limit."""
        if client_tier not in self.client_limits:
            return True, 0
        
        limit_config = self.client_limits[client_tier]
        key = f"client:{client_tier}:{client_id}"
        
        return self._check_time_window_limit(
            key, limit_config['requests'], limit_config['window'], current_time
        )
    
    def _check_concurrent_limit(self, client_id: str, complexity: AnalysisComplexity) -> Tuple[bool, str]:
        """Check concurrent analysis limit."""
        if complexity not in self.complexity_limits:
            return True, ""
        
        max_concurrent = self.complexity_limits[complexity]['concurrent']
        current_concurrent = self._get_concurrent_count(client_id, complexity)
        
        if current_concurrent >= max_concurrent:
            return False, f"Maximum concurrent {complexity.name} analyses exceeded ({current_concurrent}/{max_concurrent})"
        
        return True, ""
    
    def _check_time_window_limit(self, key: str, max_requests: int, window: int,
                                current_time: float) -> Tuple[bool, int]:
        """Check time window-based rate limit."""
        if self.redis_client:
            return self._check_redis_time_window(key, max_requests, window, current_time)
        else:
            return self._check_memory_time_window(key, max_requests, window, current_time)
    
    def _check_redis_time_window(self, key: str, max_requests: int, window: int,
                                current_time: float) -> Tuple[bool, int]:
        """Check time window using Redis."""
        try:
            redis_key = f"pattern_analysis:{key}"
            cutoff_time = current_time - window
            
            # Remove old entries
            self.redis_client.zremrangebyscore(redis_key, 0, cutoff_time)
            
            # Count current entries
            current_count = self.redis_client.zcard(redis_key)
            
            if current_count >= max_requests:
                # Calculate retry time
                oldest_entries = self.redis_client.zrange(redis_key, 0, 0, withscores=True)
                if oldest_entries:
                    oldest_time = oldest_entries[0][1]
                    retry_after = int(window - (current_time - oldest_time)) + 1
                else:
                    retry_after = window
                return False, retry_after
            
            # Add current request
            self.redis_client.zadd(redis_key, {str(current_time): current_time})
            self.redis_client.expire(redis_key, window)
            
            return True, 0
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            return True, 0  # Fail open
    
    def _check_memory_time_window(self, key: str, max_requests: int, window: int,
                                 current_time: float) -> Tuple[bool, int]:
        """Check time window using in-memory storage."""
        cutoff_time = current_time - window
        
        with self.lock:
            if key not in self.analysis_history:
                self.analysis_history[key]['timestamps'] = deque()
            
            timestamps = self.analysis_history[key]['timestamps']
            
            # Remove old timestamps
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            if len(timestamps) >= max_requests:
                retry_after = int(window - (current_time - timestamps[0])) + 1
                return False, retry_after
            
            # Add current timestamp
            timestamps.append(current_time)
            
            return True, 0
    
    def _get_concurrent_count(self, client_id: str, complexity: AnalysisComplexity) -> int:
        """Get current concurrent analysis count."""
        # This would integrate with the actual analysis execution system
        # For now, return a mock value
        return 0
    
    def record_analysis_request(self, request: AnalysisRequest):
        """Record an analysis request for metrics."""
        with self.lock:
            metrics = self.metrics[request.client_id]
            metrics.total_requests += 1
            
            if request.processing_time > 0:
                metrics.successful_requests += 1
                # Update average processing time
                total_time = (metrics.average_processing_time * 
                            (metrics.successful_requests - 1) + request.processing_time)
                metrics.average_processing_time = total_time / metrics.successful_requests
            else:
                metrics.failed_requests += 1
            
            # Update cache hit rate
            if request.cache_hit:
                cache_hits = getattr(metrics, '_cache_hits', 0) + 1
                setattr(metrics, '_cache_hits', cache_hits)
                metrics.cache_hit_rate = cache_hits / metrics.total_requests
            
            # Update complexity distribution
            complexity_name = request.complexity.name
            metrics.complexity_distribution[complexity_name] = (
                metrics.complexity_distribution.get(complexity_name, 0) + 1
            )
    
    def get_analysis_metrics(self, client_id: str = None) -> Dict[str, Any]:
        """Get analysis metrics for a client or all clients."""
        if client_id:
            return {
                'client_id': client_id,
                'metrics': self.metrics.get(client_id, AnalysisMetrics()).__dict__
            }
        
        # Aggregate metrics for all clients
        total_metrics = AnalysisMetrics()
        client_count = len(self.metrics)
        
        if client_count == 0:
            return {'total_clients': 0, 'aggregate_metrics': total_metrics.__dict__}
        
        for client_metrics in self.metrics.values():
            total_metrics.total_requests += client_metrics.total_requests
            total_metrics.successful_requests += client_metrics.successful_requests
            total_metrics.failed_requests += client_metrics.failed_requests
            
            # Aggregate complexity distribution
            for complexity, count in client_metrics.complexity_distribution.items():
                total_metrics.complexity_distribution[complexity] = (
                    total_metrics.complexity_distribution.get(complexity, 0) + count
                )
        
        # Calculate averages
        if total_metrics.total_requests > 0:
            total_metrics.cache_hit_rate = sum(
                m.cache_hit_rate * m.total_requests for m in self.metrics.values()
            ) / total_metrics.total_requests
            
            total_metrics.average_processing_time = sum(
                m.average_processing_time * m.successful_requests for m in self.metrics.values()
            ) / total_metrics.successful_requests if total_metrics.successful_requests > 0 else 0
        
        return {
            'total_clients': client_count,
            'aggregate_metrics': total_metrics.__dict__
        }
    
    def get_rate_limit_status(self, client_id: str) -> Dict[str, Any]:
        """Get current rate limit status for a client."""
        current_time = time.time()
        status = {
            'client_id': client_id,
            'timestamp': current_time,
            'limits': {}
        }
        
        # Check each type of rate limit
        for complexity in AnalysisComplexity:
            key = f"complexity:{complexity.name}:{client_id}"
            current_count = self._get_current_count(key, 60)  # 1 minute window
            limit = self.complexity_limits[complexity]['requests']
            
            status['limits'][f'complexity_{complexity.name}'] = {
                'current': current_count,
                'limit': limit,
                'remaining': max(0, limit - current_count),
                'utilization': current_count / limit if limit > 0 else 0
            }
        
        for analysis_type in PatternAnalysisType:
            if analysis_type in self.type_limits:
                key = f"type:{analysis_type.value}:{client_id}"
                current_count = self._get_current_count(key, 60)
                limit = self.type_limits[analysis_type]['requests']
                
                status['limits'][f'type_{analysis_type.value}'] = {
                    'current': current_count,
                    'limit': limit,
                    'remaining': max(0, limit - current_count),
                    'utilization': current_count / limit if limit > 0 else 0
                }
        
        return status
    
    def _get_current_count(self, key: str, window: int) -> int:
        """Get current request count for a key within time window."""
        current_time = time.time()
        cutoff_time = current_time - window
        
        if self.redis_client:
            try:
                redis_key = f"pattern_analysis:{key}"
                self.redis_client.zremrangebyscore(redis_key, 0, cutoff_time)
                return self.redis_client.zcard(redis_key)
            except Exception:
                return 0
        else:
            with self.lock:
                if key not in self.analysis_history:
                    return 0
                
                timestamps = self.analysis_history[key]['timestamps']
                # Count timestamps within window
                return sum(1 for ts in timestamps if ts >= cutoff_time)
    
    def clear_client_data(self, client_id: str):
        """Clear all data for a specific client."""
        with self.lock:
            # Clear metrics
            if client_id in self.metrics:
                del self.metrics[client_id]
            
            # Clear analysis history
            keys_to_remove = [key for key in self.analysis_history.keys() 
                             if key.endswith(f":{client_id}")]
            for key in keys_to_remove:
                del self.analysis_history[key]
        
        # Clear Redis data
        if self.redis_client:
            try:
                pattern = f"pattern_analysis:*:{client_id}"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Failed to clear Redis data for {client_id}: {e}")
        
        logger.info(f"Cleared pattern analysis data for client: {client_id}")


# Global instance
pattern_analysis_limiter = None

def init_pattern_analysis_rate_limiter(redis_client=None):
    """Initialize the pattern analysis rate limiter."""
    global pattern_analysis_limiter
    pattern_analysis_limiter = PatternAnalysisRateLimiter(redis_client=redis_client)
    return pattern_analysis_limiter


def check_pattern_analysis_rate_limit(client_id: str, analysis_type: PatternAnalysisType,
                                     data_size: int, parameters: Dict[str, Any] = None) -> Tuple[bool, int, str]:
    """Convenience function to check pattern analysis rate limit."""
    if not pattern_analysis_limiter:
        return True, 0, "Rate limiter not initialized"
    
    return pattern_analysis_limiter.check_rate_limit(
        client_id, analysis_type, data_size, parameters or {}
    )


def record_pattern_analysis(client_id: str, analysis_type: PatternAnalysisType,
                           data_size: int, parameters: Dict[str, Any], 
                           processing_time: float, cache_hit: bool = False):
    """Convenience function to record pattern analysis request."""
    if not pattern_analysis_limiter:
        return
    
    complexity = pattern_analysis_limiter.determine_complexity(analysis_type, data_size, parameters)
    
    request = AnalysisRequest(
        timestamp=time.time(),
        client_id=client_id,
        analysis_type=analysis_type,
        complexity=complexity,
        data_size=data_size,
        parameters=parameters,
        processing_time=processing_time,
        cache_hit=cache_hit
    )
    
    pattern_analysis_limiter.record_analysis_request(request)
