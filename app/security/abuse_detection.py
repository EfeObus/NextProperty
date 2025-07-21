"""
Abuse Detection System with Rate Limiting for NextProperty AI
Provides intelligent abuse detection with progressive rate limiting and behavioral analysis.
"""

import time
import json
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from flask import request, current_app, g, session
import redis
from threading import Lock
import logging
import numpy as np
import statistics

# Import pattern analysis rate limiter
from app.security.pattern_analysis_rate_limiter import (
    PatternAnalysisType, AnalysisComplexity, 
    check_pattern_analysis_rate_limit, record_pattern_analysis
)

logger = logging.getLogger(__name__)


class AbuseType(Enum):
    """Types of abuse that can be detected."""
    RAPID_REQUESTS = "rapid_requests"
    SUSPICIOUS_PATTERNS = "suspicious_patterns"
    BRUTE_FORCE = "brute_force"
    SCRAPING = "scraping"
    API_ABUSE = "api_abuse"
    INJECTION_ATTEMPTS = "injection_attempts"
    SPAM_BEHAVIOR = "spam_behavior"
    DISTRIBUTED_ATTACK = "distributed_attack"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


class AbuseLevel(Enum):
    """Severity levels for abuse detection."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AbuseMetrics:
    """Metrics for abuse detection analysis."""
    request_count: int = 0
    error_rate: float = 0.0
    response_time_variance: float = 0.0
    suspicious_patterns: int = 0
    failed_auth_attempts: int = 0
    unique_endpoints: int = 0
    parameter_variations: int = 0
    user_agent_switches: int = 0
    geographic_anomalies: int = 0


@dataclass
class AbuseIncident:
    """Record of detected abuse incident."""
    timestamp: float
    client_id: str
    abuse_type: AbuseType
    level: AbuseLevel
    confidence: float
    metrics: AbuseMetrics
    details: Dict[str, Any]
    actions_taken: List[str] = field(default_factory=list)


class AbuseDetectionRateLimiter:
    """Rate limiter specifically designed for abuse detection and prevention."""
    
    def __init__(self, redis_client=None, app=None):
        self.redis_client = redis_client
        self.app = app
        self.incidents = defaultdict(list)
        self.client_metrics = defaultdict(lambda: defaultdict(deque))
        self.lock = Lock()
        
        # Abuse-specific rate limiting rules
        self.abuse_limits = {
            # Progressive limits based on abuse level
            'low_abuse': {'requests': 50, 'window': 300},      # 50 requests per 5 minutes
            'medium_abuse': {'requests': 20, 'window': 300},   # 20 requests per 5 minutes
            'high_abuse': {'requests': 5, 'window': 300},      # 5 requests per 5 minutes
            'critical_abuse': {'requests': 1, 'window': 600},  # 1 request per 10 minutes
            
            # Pattern-specific limits
            'rapid_requests': {'requests': 100, 'window': 60},     # 100 requests per minute
            'auth_attempts': {'requests': 10, 'window': 300},      # 10 auth attempts per 5 minutes
            'api_calls': {'requests': 200, 'window': 3600},        # 200 API calls per hour
            'search_queries': {'requests': 50, 'window': 300},     # 50 searches per 5 minutes
            'form_submissions': {'requests': 20, 'window': 300},   # 20 form submissions per 5 minutes
        }
        
        # Abuse detection thresholds
        self.detection_thresholds = {
            'rapid_requests': {'count': 50, 'window': 60},         # 50 requests in 1 minute
            'error_rate': 0.5,                                     # 50% error rate
            'auth_failure_rate': 0.8,                             # 80% auth failure rate
            'unique_endpoints': 20,                                # 20+ unique endpoints in short time
            'parameter_variations': 15,                            # 15+ parameter variations
            'user_agent_switches': 5,                              # 5+ user agent changes
            'suspicious_pattern_score': 0.7,                      # 70% suspicion threshold
        }
        
        # Penalty escalation
        self.penalty_escalation = {
            1: {'duration': 300, 'multiplier': 1.0},      # 5 minutes, normal rate
            2: {'duration': 900, 'multiplier': 0.5},      # 15 minutes, half rate
            3: {'duration': 1800, 'multiplier': 0.2},     # 30 minutes, 20% rate
            4: {'duration': 3600, 'multiplier': 0.1},     # 1 hour, 10% rate
            5: {'duration': 7200, 'multiplier': 0.05},    # 2 hours, 5% rate
        }
    
    def analyze_request_patterns(self, client_id: str) -> AbuseMetrics:
        """Analyze request patterns for a specific client with rate limiting."""
        current_time = time.time()
        window = 300  # 5 minutes
        cutoff_time = current_time - window
        
        # Get recent requests for this client
        requests = self.client_metrics[client_id]['requests']
        
        # Clean old requests
        while requests and requests[0]['timestamp'] < cutoff_time:
            requests.popleft()
        
        if not requests:
            return AbuseMetrics()
        
        # Check rate limit for pattern analysis
        data_size = len(str(requests))  # Approximate data size
        parameters = {'window': window, 'client_id': client_id}
        
        analysis_allowed, retry_after, reason = check_pattern_analysis_rate_limit(
            client_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS, data_size, parameters
        )
        
        if not analysis_allowed:
            logger.warning(f"Pattern analysis rate limited for {client_id}: {reason}")
            # Return cached or simplified analysis
            return self._get_cached_or_simple_analysis(client_id, requests)
        
        # Record the start of analysis
        analysis_start_time = time.time()
        
        try:
            # Perform full pattern analysis
            metrics = self._perform_detailed_pattern_analysis(requests)
            
            # Record successful analysis
            processing_time = time.time() - analysis_start_time
            record_pattern_analysis(
                client_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS, 
                data_size, parameters, processing_time
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Pattern analysis failed for {client_id}: {e}")
            processing_time = time.time() - analysis_start_time
            record_pattern_analysis(
                client_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS, 
                data_size, parameters, processing_time
            )
            # Return simplified analysis on error
            return self._get_simple_analysis(requests)
    
    def _get_cached_or_simple_analysis(self, client_id: str, requests: deque) -> AbuseMetrics:
        """Get cached analysis or perform simple analysis when rate limited."""
        # Check if we have cached results
        cache_key = f"pattern_analysis_cache:{client_id}"
        if self.redis_client:
            try:
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    cached_data = json.loads(cached_result)
                    # Record cache hit
                    record_pattern_analysis(
                        client_id, PatternAnalysisType.BEHAVIORAL_ANALYSIS,
                        0, {}, 0, cache_hit=True
                    )
                    return AbuseMetrics(**cached_data)
            except Exception as e:
                logger.debug(f"Cache lookup failed: {e}")
        
        # Perform simple analysis
        return self._get_simple_analysis(requests)
    
    def _perform_detailed_pattern_analysis(self, requests: deque) -> AbuseMetrics:
        """Perform detailed pattern analysis with full metrics calculation."""
        request_count = len(requests)
        
        # Error rate calculation
        error_requests = sum(1 for r in requests if r.get('status_code', 200) >= 400)
        error_rate = error_requests / request_count if request_count > 0 else 0
        
        # Response time variance
        response_times = [r.get('response_time', 0) for r in requests]
        response_time_variance = np.var(response_times) if len(response_times) > 1 else 0
        
        # Unique endpoints analysis
        unique_endpoints = len(set(r.get('endpoint', '') for r in requests))
        
        # Parameter variations analysis
        param_sets = set()
        for r in requests:
            params = r.get('parameters', {})
            param_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
            param_sets.add(param_hash)
        parameter_variations = len(param_sets)
        
        # User agent analysis
        user_agents = set(r.get('user_agent', '') for r in requests)
        user_agent_switches = len(user_agents) - 1 if len(user_agents) > 1 else 0
        
        # Failed auth attempts
        failed_auth_attempts = sum(1 for r in requests 
                                 if 'auth' in r.get('endpoint', '') and r.get('status_code', 200) >= 400)
        
        return AbuseMetrics(
            request_count=request_count,
            error_rate=error_rate,
            response_time_variance=response_time_variance,
            unique_endpoints=unique_endpoints,
            parameter_variations=parameter_variations,
            user_agent_switches=user_agent_switches,
            failed_auth_attempts=failed_auth_attempts
        )
    
    def _get_simple_analysis(self, requests: deque) -> AbuseMetrics:
        """Perform simple analysis when detailed analysis is not available."""
        request_count = len(requests)
        
        # Basic calculations only
        error_requests = sum(1 for r in requests if r.get('status_code', 200) >= 400)
        error_rate = error_requests / request_count if request_count > 0 else 0
        
        failed_auth_attempts = sum(1 for r in requests 
                                 if 'auth' in r.get('endpoint', '') and r.get('status_code', 200) >= 400)
        
        return AbuseMetrics(
            request_count=request_count,
            error_rate=error_rate,
            response_time_variance=0,  # Skip complex calculation
            unique_endpoints=0,        # Skip complex calculation
            parameter_variations=0,    # Skip complex calculation
            user_agent_switches=0,     # Skip complex calculation
            failed_auth_attempts=failed_auth_attempts
        )
    
    def detect_abuse_type(self, metrics: AbuseMetrics, client_id: str) -> Tuple[AbuseType, AbuseLevel, float]:
        """Detect the type and severity of abuse based on metrics."""
        scores = {}
        
        # Rapid requests detection
        if metrics.request_count >= self.detection_thresholds['rapid_requests']['count']:
            scores[AbuseType.RAPID_REQUESTS] = min(metrics.request_count / 100, 1.0)
        
        # Brute force detection
        if metrics.failed_auth_attempts > 0:
            auth_failure_rate = metrics.failed_auth_attempts / max(metrics.request_count, 1)
            if auth_failure_rate >= self.detection_thresholds['auth_failure_rate']:
                scores[AbuseType.BRUTE_FORCE] = auth_failure_rate
        
        # Scraping detection
        if (metrics.unique_endpoints >= self.detection_thresholds['unique_endpoints'] or
            metrics.parameter_variations >= self.detection_thresholds['parameter_variations']):
            scraping_score = (metrics.unique_endpoints / 50 + 
                            metrics.parameter_variations / 30) / 2
            scores[AbuseType.SCRAPING] = min(scraping_score, 1.0)
        
        # API abuse detection
        if metrics.error_rate >= self.detection_thresholds['error_rate']:
            scores[AbuseType.API_ABUSE] = metrics.error_rate
        
        # Suspicious patterns detection
        if metrics.user_agent_switches >= self.detection_thresholds['user_agent_switches']:
            scores[AbuseType.SUSPICIOUS_PATTERNS] = min(metrics.user_agent_switches / 10, 1.0)
        
        # Resource exhaustion detection
        if metrics.response_time_variance > 1000:  # High variance in response times
            scores[AbuseType.RESOURCE_EXHAUSTION] = min(metrics.response_time_variance / 5000, 1.0)
        
        if not scores:
            return None, AbuseLevel.LOW, 0.0
        
        # Find highest scoring abuse type
        max_abuse_type = max(scores.keys(), key=lambda k: scores[k])
        confidence = scores[max_abuse_type]
        
        # Determine abuse level based on confidence
        if confidence >= 0.9:
            level = AbuseLevel.CRITICAL
        elif confidence >= 0.7:
            level = AbuseLevel.HIGH
        elif confidence >= 0.4:
            level = AbuseLevel.MEDIUM
        else:
            level = AbuseLevel.LOW
        
        return max_abuse_type, level, confidence
    
    def record_request(self, client_id: str, request_data: Dict[str, Any]):
        """Record a request for analysis."""
        current_time = time.time()
        
        request_record = {
            'timestamp': current_time,
            'endpoint': request_data.get('endpoint', ''),
            'method': request_data.get('method', 'GET'),
            'status_code': request_data.get('status_code', 200),
            'response_time': request_data.get('response_time', 0),
            'user_agent': request_data.get('user_agent', ''),
            'parameters': request_data.get('parameters', {}),
            'ip_address': request_data.get('ip_address', ''),
        }
        
        with self.lock:
            self.client_metrics[client_id]['requests'].append(request_record)
            
            # Keep only recent requests (last hour)
            cutoff_time = current_time - 3600
            requests = self.client_metrics[client_id]['requests']
            while requests and requests[0]['timestamp'] < cutoff_time:
                requests.popleft()
    
    def check_abuse_rate_limit(self, client_id: str) -> Tuple[bool, int, Optional[AbuseIncident]]:
        """Check if client should be rate limited based on abuse detection."""
        # Analyze current request patterns
        metrics = self.analyze_request_patterns(client_id)
        
        # Detect abuse
        abuse_type, abuse_level, confidence = self.detect_abuse_type(metrics, client_id)
        
        if abuse_type is None:
            return True, 0, None  # No abuse detected, allow request
        
        # Create abuse incident
        incident = AbuseIncident(
            timestamp=time.time(),
            client_id=client_id,
            abuse_type=abuse_type,
            level=abuse_level,
            confidence=confidence,
            metrics=metrics,
            details={
                'detection_method': 'pattern_analysis',
                'thresholds_triggered': self._get_triggered_thresholds(metrics)
            }
        )
        
        # Record incident
        self.incidents[client_id].append(incident)
        
        # Check rate limit based on abuse level
        limit_key = f"{abuse_level.name.lower()}_abuse"
        if limit_key in self.abuse_limits:
            allowed, retry_after = self._check_rate_limit(client_id, limit_key)
            
            if not allowed:
                incident.actions_taken.append(f"rate_limited_{limit_key}")
                logger.warning(f"Abuse detected for {client_id}: {abuse_type.value} "
                             f"(level: {abuse_level.value}, confidence: {confidence:.2f})")
                return False, retry_after, incident
        
        # Log but allow request for lower severity
        if abuse_level in [AbuseLevel.LOW, AbuseLevel.MEDIUM]:
            logger.info(f"Low-level abuse detected for {client_id}: {abuse_type.value} "
                       f"(confidence: {confidence:.2f})")
        
        return True, 0, incident
    
    def _get_triggered_thresholds(self, metrics: AbuseMetrics) -> List[str]:
        """Get list of thresholds that were triggered."""
        triggered = []
        
        if metrics.request_count >= self.detection_thresholds['rapid_requests']['count']:
            triggered.append('rapid_requests')
        
        if metrics.error_rate >= self.detection_thresholds['error_rate']:
            triggered.append('high_error_rate')
        
        if metrics.unique_endpoints >= self.detection_thresholds['unique_endpoints']:
            triggered.append('many_unique_endpoints')
        
        if metrics.parameter_variations >= self.detection_thresholds['parameter_variations']:
            triggered.append('parameter_variations')
        
        if metrics.user_agent_switches >= self.detection_thresholds['user_agent_switches']:
            triggered.append('user_agent_switches')
        
        return triggered
    
    def _check_rate_limit(self, client_id: str, limit_key: str) -> Tuple[bool, int]:
        """Check rate limit for specific abuse type."""
        if limit_key not in self.abuse_limits:
            return True, 0
        
        limit = self.abuse_limits[limit_key]
        current_time = time.time()
        window = limit['window']
        max_requests = limit['requests']
        
        # Apply escalation penalty if there are previous incidents
        incident_count = len(self.incidents[client_id])
        if incident_count > 0:
            penalty_level = min(incident_count, len(self.penalty_escalation))
            escalation = self.penalty_escalation[penalty_level]
            max_requests = int(max_requests * escalation['multiplier'])
        
        # Count recent requests
        if self.redis_client:
            return self._check_redis_rate_limit(client_id, limit_key, max_requests, window)
        else:
            return self._check_memory_rate_limit(client_id, limit_key, max_requests, window)
    
    def _check_redis_rate_limit(self, client_id: str, limit_key: str, max_requests: int, window: int) -> Tuple[bool, int]:
        """Check rate limit using Redis."""
        try:
            key = f"abuse_rl:{limit_key}:{client_id}"
            current_time = time.time()
            cutoff_time = current_time - window
            
            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, cutoff_time)
            
            # Count current entries
            current_count = self.redis_client.zcard(key)
            
            if current_count >= max_requests:
                # Get oldest entry to calculate retry time
                oldest_entries = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_entries:
                    oldest_time = oldest_entries[0][1]
                    retry_after = int(window - (current_time - oldest_time)) + 1
                else:
                    retry_after = window
                return False, retry_after
            
            # Add current request
            self.redis_client.zadd(key, {str(current_time): current_time})
            self.redis_client.expire(key, window)
            
            return True, 0
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            return True, 0  # Fail open
    
    def _check_memory_rate_limit(self, client_id: str, limit_key: str, max_requests: int, window: int) -> Tuple[bool, int]:
        """Check rate limit using in-memory storage."""
        current_time = time.time()
        cutoff_time = current_time - window
        
        key = f"{limit_key}:{client_id}"
        
        with self.lock:
            if key not in self.client_metrics:
                self.client_metrics[key]['timestamps'] = deque()
            
            timestamps = self.client_metrics[key]['timestamps']
            
            # Remove old timestamps
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            if len(timestamps) >= max_requests:
                # Calculate retry time based on oldest remaining timestamp
                if timestamps:
                    retry_after = int(window - (current_time - timestamps[0])) + 1
                else:
                    retry_after = window  # If no timestamps, use full window
                return False, retry_after
            
            # Add current timestamp
            timestamps.append(current_time)
            
            return True, 0
    
    def get_client_abuse_history(self, client_id: str) -> List[AbuseIncident]:
        """Get abuse history for a client."""
        return self.incidents.get(client_id, [])
    
    def get_abuse_statistics(self) -> Dict[str, Any]:
        """Get overall abuse detection statistics."""
        total_incidents = sum(len(incidents) for incidents in self.incidents.values())
        
        if total_incidents == 0:
            return {
                'total_incidents': 0,
                'unique_clients': 0,
                'abuse_types': {},
                'abuse_levels': {}
            }
        
        abuse_types = defaultdict(int)
        abuse_levels = defaultdict(int)
        
        for incidents in self.incidents.values():
            for incident in incidents:
                abuse_types[incident.abuse_type.value] += 1
                abuse_levels[incident.level.value] += 1
        
        return {
            'total_incidents': total_incidents,
            'unique_clients': len(self.incidents),
            'abuse_types': dict(abuse_types),
            'abuse_levels': dict(abuse_levels),
            'most_common_abuse': max(abuse_types.keys(), key=abuse_types.get) if abuse_types else None
        }
    
    def clear_client_history(self, client_id: str):
        """Clear abuse history for a client (admin function)."""
        if client_id in self.incidents:
            del self.incidents[client_id]
        if client_id in self.client_metrics:
            del self.client_metrics[client_id]
        
        logger.info(f"Cleared abuse history for client: {client_id}")


class AbuseDetectionMiddleware:
    """Flask middleware for abuse detection."""
    
    def __init__(self, app=None, redis_client=None):
        self.abuse_detector = AbuseDetectionRateLimiter(redis_client=redis_client, app=app)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the abuse detection middleware with Flask app."""
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def _get_client_identifier(self) -> str:
        """Get client identifier for tracking."""
        # Prefer user ID if available
        if hasattr(g, 'current_user') and g.current_user:
            return f"user:{g.current_user.id}"
        
        # Fall back to IP address
        return f"ip:{request.remote_addr}"
    
    def _before_request(self):
        """Check for abuse before processing request."""
        # Skip abuse detection for certain endpoints
        if self._should_skip_abuse_detection():
            return
        
        client_id = self._get_client_identifier()
        g.abuse_client_id = client_id
        
        # Check abuse rate limit
        allowed, retry_after, incident = self.abuse_detector.check_abuse_rate_limit(client_id)
        
        if not allowed:
            response_data = {
                'error': 'Request blocked due to abuse detection',
                'type': 'abuse_rate_limit',
                'retry_after': retry_after,
                'incident_id': incident.timestamp if incident else None,
                'abuse_type': incident.abuse_type.value if incident else None,
                'level': incident.level.value if incident else None
            }
            
            from flask import jsonify
            response = jsonify(response_data)
            response.status_code = 429
            response.headers['Retry-After'] = str(retry_after)
            response.headers['X-Abuse-Type'] = incident.abuse_type.value if incident else 'unknown'
            response.headers['X-Abuse-Level'] = incident.level.value if incident else 'unknown'
            
            return response
    
    def _after_request(self, response):
        """Record request data after processing."""
        if not hasattr(g, 'abuse_client_id'):
            return response
        
        start_time = getattr(g, 'request_start_time', time.time())
        
        # Handle both datetime objects and float timestamps
        if hasattr(start_time, 'timestamp'):
            # It's a datetime object, convert to timestamp
            start_time = start_time.timestamp()
        
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        
        request_data = {
            'endpoint': request.endpoint or request.path,
            'method': request.method,
            'status_code': response.status_code,
            'response_time': response_time,
            'user_agent': request.headers.get('User-Agent', ''),
            'parameters': dict(request.args),
            'ip_address': request.remote_addr,
        }
        
        self.abuse_detector.record_request(g.abuse_client_id, request_data)
        
        return response
    
    def _should_skip_abuse_detection(self) -> bool:
        """Determine if abuse detection should be skipped."""
        # Skip for health checks and static files
        skip_paths = ['/health', '/status', '/static/', '/favicon.ico']
        for path in skip_paths:
            if request.path.startswith(path):
                return True
        
        return False


# Global instance for easy access
abuse_detector = None

def init_abuse_detection(app, redis_client=None):
    """Initialize abuse detection system."""
    global abuse_detector
    
    # Initialize pattern analysis rate limiter first
    from app.security.pattern_analysis_rate_limiter import init_pattern_analysis_rate_limiter
    pattern_limiter = init_pattern_analysis_rate_limiter(redis_client)
    
    # Initialize abuse detection with pattern analysis integration
    abuse_detector = AbuseDetectionMiddleware(app=app, redis_client=redis_client)
    
    return abuse_detector
