"""
Advanced Rate Limiting System for NextProperty AI
Provides comprehensive rate limiting with multiple strategies and intelligent detection.
"""

import time
import json
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from functools import wraps
from flask import request, jsonify, current_app, g, session
from werkzeug.exceptions import TooManyRequests
import redis
from threading import Lock
import logging

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, limit_type: str, retry_after: int, message: str = None):
        self.limit_type = limit_type
        self.retry_after = retry_after
        self.message = message or f"Rate limit exceeded for {limit_type}"
        super().__init__(self.message)


class InMemoryStore:
    """In-memory storage for rate limiting when Redis is not available."""
    
    def __init__(self):
        self._store = defaultdict(lambda: defaultdict(deque))
        self._lock = Lock()
        self._cleanup_interval = 300  # 5 minutes
        self._last_cleanup = time.time()
    
    def _cleanup_expired(self):
        """Remove expired entries to prevent memory leaks."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        with self._lock:
            for key_type in list(self._store.keys()):
                for identifier in list(self._store[key_type].keys()):
                    queue = self._store[key_type][identifier]
                    # Remove entries older than 1 hour
                    cutoff_time = current_time - 3600
                    while queue and queue[0] < cutoff_time:
                        queue.popleft()
                    
                    # Remove empty queues
                    if not queue:
                        del self._store[key_type][identifier]
                
                # Remove empty key types
                if not self._store[key_type]:
                    del self._store[key_type]
            
            self._last_cleanup = current_time
    
    def add_request(self, key: str, timestamp: float = None):
        """Add a request timestamp."""
        if timestamp is None:
            timestamp = time.time()
        
        with self._lock:
            parts = key.split(':')
            if len(parts) >= 2:
                key_type, identifier = parts[0], ':'.join(parts[1:])
                self._store[key_type][identifier].append(timestamp)
        
        self._cleanup_expired()
    
    def get_request_count(self, key: str, window: int) -> int:
        """Get the number of requests in the time window."""
        current_time = time.time()
        cutoff_time = current_time - window
        
        with self._lock:
            parts = key.split(':')
            if len(parts) >= 2:
                key_type, identifier = parts[0], ':'.join(parts[1:])
                queue = self._store[key_type][identifier]
                
                # Remove expired entries
                while queue and queue[0] < cutoff_time:
                    queue.popleft()
                
                return len(queue)
        
        return 0
    
    def get_oldest_request(self, key: str) -> Optional[float]:
        """Get the timestamp of the oldest request."""
        with self._lock:
            parts = key.split(':')
            if len(parts) >= 2:
                key_type, identifier = parts[0], ':'.join(parts[1:])
                queue = self._store[key_type][identifier]
                return queue[0] if queue else None
        
        return None


class RedisStore:
    """Redis-based storage for rate limiting in production."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def add_request(self, key: str, timestamp: float = None):
        """Add a request timestamp using Redis sorted sets."""
        if timestamp is None:
            timestamp = time.time()
        
        try:
            # Use sorted sets for efficient time-based queries
            self.redis.zadd(key, {str(timestamp): timestamp})
            # Set expiration to clean up old keys
            self.redis.expire(key, 3600)  # 1 hour
        except Exception as e:
            logger.warning(f"Redis add_request failed: {e}")
    
    def get_request_count(self, key: str, window: int) -> int:
        """Get the number of requests in the time window."""
        try:
            current_time = time.time()
            cutoff_time = current_time - window
            
            # Remove old entries and count recent ones
            self.redis.zremrangebyscore(key, 0, cutoff_time)
            return self.redis.zcard(key)
        except Exception as e:
            logger.warning(f"Redis get_request_count failed: {e}")
            return 0
    
    def get_oldest_request(self, key: str) -> Optional[float]:
        """Get the timestamp of the oldest request."""
        try:
            result = self.redis.zrange(key, 0, 0, withscores=True)
            return result[0][1] if result else None
        except Exception as e:
            logger.warning(f"Redis get_oldest_request failed: {e}")
            return None


class RateLimiter:
    """Advanced rate limiter with multiple strategies and intelligent detection."""
    
    def __init__(self, app=None, redis_client=None):
        self.app = app
        self.store = None
        self.redis_client = redis_client
        
        # Rate limiting rules - Very lenient for development testing
        self.default_limits = {
            'global': {'requests': 50000, 'window': 3600},  # 50000 requests per hour
            'ip': {'requests': 10000, 'window': 3600},      # 10000 requests per hour per IP
            'user': {'requests': 20000, 'window': 3600},    # 20000 requests per hour per user
            'endpoint': {'requests': 2000, 'window': 300},  # 2000 requests per 5 minutes per endpoint
        }
        
        # Stricter limits for sensitive endpoints - Very relaxed for development
        self.sensitive_limits = {
            'auth': {'requests': 500, 'window': 300},       # 500 auth attempts per 5 minutes
            'api': {'requests': 10000, 'window': 3600},     # 10000 API calls per hour
            'upload': {'requests': 1000, 'window': 3600},   # 1000 uploads per hour
            'admin': {'requests': 2000, 'window': 3600},    # 2000 admin actions per hour
        }
        
        # Burst protection - Extremely lenient for development
        self.burst_limits = {
            'ip': {'requests': 10000, 'window': 60},         # 10000 requests per minute
            'user': {'requests': 20000, 'window': 60},       # 20000 requests per minute
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize rate limiter with Flask app."""
        self.app = app
        
        # Initialize storage backend
        if self.redis_client:
            self.store = RedisStore(self.redis_client)
            app.logger.info("Rate limiter using Redis backend")
        else:
            self.store = InMemoryStore()
            app.logger.info("Rate limiter using in-memory backend")
        
        # Configure from app config
        self._configure_from_app(app)
        
        # Register request hooks
        app.before_request(self._before_request)
        app.after_request(self._after_request)
    
    def _configure_from_app(self, app):
        """Configure rate limiter from app configuration."""
        # Update limits from configuration
        if 'RATE_LIMIT_DEFAULTS' in app.config:
            self.default_limits.update(app.config['RATE_LIMIT_DEFAULTS'])
        
        if 'RATE_LIMIT_SENSITIVE' in app.config:
            self.sensitive_limits.update(app.config['RATE_LIMIT_SENSITIVE'])
        
        if 'RATE_LIMIT_BURST' in app.config:
            self.burst_limits.update(app.config['RATE_LIMIT_BURST'])
    
    def _get_client_identifier(self) -> str:
        """Get unique client identifier."""
        # Try to get user ID first
        if hasattr(g, 'current_user') and g.current_user and hasattr(g.current_user, 'id'):
            return f"user:{g.current_user.id}"
        
        # Fall back to IP address
        ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ip:
            # Handle multiple IPs in X-Forwarded-For
            ip = ip.split(',')[0].strip()
        
        return f"ip:{ip or 'unknown'}"
    
    def _get_endpoint_identifier(self) -> str:
        """Get endpoint identifier for rate limiting."""
        endpoint = request.endpoint or 'unknown'
        method = request.method
        return f"endpoint:{endpoint}:{method}"
    
    def _categorize_request(self) -> str:
        """Categorize the request for applying appropriate limits."""
        path = request.path.lower()
        endpoint = request.endpoint or ''
        
        # Authentication endpoints
        if any(auth_path in path for auth_path in ['/login', '/register', '/auth', '/reset-password']):
            return 'auth'
        
        # API endpoints
        if path.startswith('/api/'):
            return 'api'
        
        # Admin endpoints
        if path.startswith('/admin/'):
            return 'admin'
        
        # Upload endpoints
        if 'upload' in path or request.method == 'POST' and any(
            keyword in path for keyword in ['image', 'file', 'photo']
        ):
            return 'upload'
        
        return 'general'
    
    def _check_rate_limit(self, key: str, limit: Dict[str, int]) -> Tuple[bool, int]:
        """Check if rate limit is exceeded."""
        requests = limit['requests']
        window = limit['window']
        
        current_count = self.store.get_request_count(key, window)
        
        if current_count >= requests:
            # Calculate retry after time
            oldest_request = self.store.get_oldest_request(key)
            if oldest_request:
                retry_after = int(window - (time.time() - oldest_request)) + 1
            else:
                retry_after = window
            
            return False, retry_after
        
        return True, 0
    
    def _before_request(self):
        """Check rate limits before processing request."""
        # Skip rate limiting for certain endpoints
        if self._should_skip_rate_limiting():
            return
        
        try:
            # Get identifiers
            client_id = self._get_client_identifier()
            endpoint_id = self._get_endpoint_identifier()
            category = self._categorize_request()
            
            # Store in g for later use
            g.rate_limit_client_id = client_id
            g.rate_limit_endpoint_id = endpoint_id
            g.rate_limit_category = category
            
            # Check various rate limits
            current_time = time.time()
            
            # 1. Check global rate limit
            global_key = "global:all"
            global_limit = self.default_limits['global']
            allowed, retry_after = self._check_rate_limit(global_key, global_limit)
            if not allowed:
                raise RateLimitExceeded('global', retry_after, 'Global rate limit exceeded')
            
            # 2. Check client-specific rate limit
            client_limit = self.default_limits['user'] if 'user:' in client_id else self.default_limits['ip']
            allowed, retry_after = self._check_rate_limit(client_id, client_limit)
            if not allowed:
                raise RateLimitExceeded('client', retry_after, 'Client rate limit exceeded')
            
            # 3. Check burst protection
            burst_type = 'user' if 'user:' in client_id else 'ip'
            if burst_type in self.burst_limits:
                burst_key = f"burst:{client_id}"
                allowed, retry_after = self._check_rate_limit(burst_key, self.burst_limits[burst_type])
                if not allowed:
                    raise RateLimitExceeded('burst', retry_after, 'Burst rate limit exceeded')
            
            # 4. Check endpoint-specific rate limit
            allowed, retry_after = self._check_rate_limit(endpoint_id, self.default_limits['endpoint'])
            if not allowed:
                raise RateLimitExceeded('endpoint', retry_after, 'Endpoint rate limit exceeded')
            
            # 5. Check category-specific rate limit (for sensitive endpoints)
            if category in self.sensitive_limits:
                category_key = f"category:{category}:{client_id}"
                allowed, retry_after = self._check_rate_limit(category_key, self.sensitive_limits[category])
                if not allowed:
                    raise RateLimitExceeded('category', retry_after, f'{category.title()} rate limit exceeded')
            
        except RateLimitExceeded as e:
            logger.warning(f"Rate limit exceeded: {e.message} for {client_id}")
            return self._rate_limit_response(e)
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Don't block requests on rate limiter errors
            return None
    
    def _after_request(self, response):
        """Record the request after processing."""
        # Skip if rate limiting was skipped
        if not hasattr(g, 'rate_limit_client_id'):
            return response
        
        try:
            current_time = time.time()
            
            # Record the request
            self.store.add_request("global:all", current_time)
            self.store.add_request(g.rate_limit_client_id, current_time)
            self.store.add_request(g.rate_limit_endpoint_id, current_time)
            
            # Record burst request
            burst_type = 'user' if 'user:' in g.rate_limit_client_id else 'ip'
            if burst_type in self.burst_limits:
                self.store.add_request(f"burst:{g.rate_limit_client_id}", current_time)
            
            # Record category request for sensitive endpoints
            if g.rate_limit_category in self.sensitive_limits:
                category_key = f"category:{g.rate_limit_category}:{g.rate_limit_client_id}"
                self.store.add_request(category_key, current_time)
            
            # Add rate limit headers
            self._add_rate_limit_headers(response)
            
        except Exception as e:
            logger.error(f"Error recording request in rate limiter: {e}")
        
        return response
    
    def _should_skip_rate_limiting(self) -> bool:
        """Determine if rate limiting should be skipped."""
        # Skip for health checks
        if request.path in ['/health', '/status']:
            return True
        
        # Skip for static files
        if request.path.startswith('/static/'):
            return True
        
        # Skip for certain content types
        if request.content_type and 'text/css' in request.content_type:
            return True
        
        return False
    
    def _rate_limit_response(self, exception: RateLimitExceeded):
        """Generate rate limit exceeded response."""
        headers = {
            'Retry-After': str(exception.retry_after),
            'X-RateLimit-Limit-Type': exception.limit_type,
            'X-RateLimit-Retry-After': str(exception.retry_after)
        }
        
        if request.is_json or request.path.startswith('/api/'):
            response = jsonify({
                'error': 'Rate limit exceeded',
                'message': exception.message,
                'limit_type': exception.limit_type,
                'retry_after': exception.retry_after
            })
            response.status_code = 429
        else:
            from flask import render_template
            from datetime import datetime
            try:
                response = current_app.make_response(
                    render_template('errors/429.html', 
                                  retry_after=exception.retry_after,
                                  limit_type=exception.limit_type,
                                  current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                )
                response.status_code = 429
            except:
                # Fallback to simple text response
                response = current_app.make_response(
                    f"Rate limit exceeded. Try again in {exception.retry_after} seconds."
                )
                response.status_code = 429
        
        for header, value in headers.items():
            response.headers[header] = value
        
        return response
    
    def _add_rate_limit_headers(self, response):
        """Add rate limiting headers to response."""
        try:
            if hasattr(g, 'rate_limit_client_id'):
                # Add remaining requests header
                client_limit = self.default_limits['user'] if 'user:' in g.rate_limit_client_id else self.default_limits['ip']
                current_count = self.store.get_request_count(g.rate_limit_client_id, client_limit['window'])
                remaining = max(0, client_limit['requests'] - current_count)
                
                response.headers['X-RateLimit-Limit'] = str(client_limit['requests'])
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Window'] = str(client_limit['window'])
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {e}")


def rate_limit(requests: int = None, window: int = None, category: str = None):
    """Decorator for applying custom rate limits to specific routes."""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This decorator adds metadata that the rate limiter can use
            # The actual rate limiting is handled by the global middleware
            if not hasattr(f, '_rate_limits'):
                f._rate_limits = []
            
            limit_info = {
                'requests': requests,
                'window': window,
                'category': category
            }
            f._rate_limits.append(limit_info)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# Global rate limiter instance
rate_limiter = RateLimiter()
