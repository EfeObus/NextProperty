"""
Decorator utilities for NextProperty AI platform.
"""

import functools
import time
import logging
from typing import Any, Callable, Dict, Optional
from flask import request, jsonify, session, g, current_app
from flask_login import current_user
from werkzeug.exceptions import Unauthorized, Forbidden, TooManyRequests
import redis
import json
import hashlib
from datetime import datetime, timedelta

# Set up logging
logger = logging.getLogger(__name__)


def login_required(f: Callable) -> Callable:
    """
    Decorator to require user login.
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f: Callable) -> Callable:
    """
    Decorator to require admin privileges.
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            if request.is_json:
                return jsonify({'error': 'Admin privileges required'}), 403
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(max_requests: int = 100, window: int = 3600, key_func: Callable = None):
    """
    Decorator for rate limiting requests.
    
    Args:
        max_requests: Maximum requests allowed in window
        window: Time window in seconds
        key_func: Function to generate rate limit key
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr
            
            redis_key = f"rate_limit:{key}:{f.__name__}"
            
            try:
                # Try to get Redis connection
                redis_client = current_app.extensions.get('redis')
                if redis_client:
                    current_requests = redis_client.get(redis_key)
                    if current_requests and int(current_requests) >= max_requests:
                        if request.is_json:
                            return jsonify({'error': 'Rate limit exceeded'}), 429
                        raise TooManyRequests()
                    
                    # Increment counter
                    pipe = redis_client.pipeline()
                    pipe.incr(redis_key)
                    pipe.expire(redis_key, window)
                    pipe.execute()
                
            except Exception as e:
                logger.warning(f"Rate limiting failed: {e}")
                # Continue without rate limiting if Redis fails
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def cache_result(timeout: int = 300, key_prefix: str = "", vary_on: list = None):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
        vary_on: List of request parameters to include in cache key
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, f.__name__]
            
            if vary_on:
                for param in vary_on:
                    value = request.args.get(param, '')
                    key_parts.append(f"{param}:{value}")
            
            # Add function arguments to key
            if args:
                key_parts.append(f"args:{hashlib.md5(str(args).encode()).hexdigest()}")
            if kwargs:
                key_parts.append(f"kwargs:{hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()}")
            
            cache_key = ":".join(key_parts)
            
            try:
                # Try to get cached result
                redis_client = current_app.extensions.get('redis')
                if redis_client:
                    cached_result = redis_client.get(cache_key)
                    if cached_result:
                        return json.loads(cached_result)
                
                # Execute function and cache result
                result = f(*args, **kwargs)
                
                if redis_client:
                    redis_client.setex(cache_key, timeout, json.dumps(result, default=str))
                
                return result
                
            except Exception as e:
                logger.warning(f"Caching failed: {e}")
                # Return result without caching if Redis fails
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_json(required_fields: list = None, optional_fields: list = None):
    """
    Decorator to validate JSON request data.
    
    Args:
        required_fields: List of required field names
        optional_fields: List of optional field names
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': 'Missing required fields',
                        'missing_fields': missing_fields
                    }), 400
            
            # Filter allowed fields
            if required_fields or optional_fields:
                allowed_fields = set(required_fields or []) | set(optional_fields or [])
                filtered_data = {k: v for k, v in data.items() if k in allowed_fields}
                g.json_data = filtered_data
            else:
                g.json_data = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_activity(activity_type: str = "api_call", include_response: bool = False):
    """
    Decorator to log user activity.
    
    Args:
        activity_type: Type of activity to log
        include_response: Whether to include response in log
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            # Log request
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'activity_type': activity_type,
                'function': f.__name__,
                'user_id': current_user.id if current_user.is_authenticated else None,
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string,
                'method': request.method,
                'url': request.url,
                'args': dict(request.args),
            }
            
            if request.is_json:
                log_data['request_data'] = request.get_json()
            
            try:
                result = f(*args, **kwargs)
                
                # Log response
                execution_time = time.time() - start_time
                log_data['execution_time'] = execution_time
                log_data['status'] = 'success'
                
                if include_response and hasattr(result, 'get_json'):
                    log_data['response_data'] = result.get_json()
                
                logger.info(f"Activity logged: {json.dumps(log_data, default=str)}")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                log_data['execution_time'] = execution_time
                log_data['status'] = 'error'
                log_data['error'] = str(e)
                
                logger.error(f"Activity failed: {json.dumps(log_data, default=str)}")
                raise
        
        return decorated_function
    return decorator


def handle_errors(default_message: str = "An error occurred", log_errors: bool = True):
    """
    Decorator to handle and format errors.
    
    Args:
        default_message: Default error message
        log_errors: Whether to log errors
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValueError as e:
                if log_errors:
                    logger.warning(f"ValueError in {f.__name__}: {e}")
                if request.is_json:
                    return jsonify({'error': str(e)}), 400
                return str(e), 400
            except KeyError as e:
                if log_errors:
                    logger.warning(f"KeyError in {f.__name__}: {e}")
                if request.is_json:
                    return jsonify({'error': f"Missing parameter: {e}"}), 400
                return f"Missing parameter: {e}", 400
            except Unauthorized:
                if log_errors:
                    logger.warning(f"Unauthorized access to {f.__name__}")
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                return 'Authentication required', 401
            except Forbidden:
                if log_errors:
                    logger.warning(f"Forbidden access to {f.__name__}")
                if request.is_json:
                    return jsonify({'error': 'Access forbidden'}), 403
                return 'Access forbidden', 403
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {f.__name__}: {e}", exc_info=True)
                if request.is_json:
                    return jsonify({'error': default_message}), 500
                return default_message, 500
        
        return decorated_function
    return decorator


def require_api_key(f: Callable) -> Callable:
    """
    Decorator to require API key authentication.
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key (this would check against database)
        # For now, just check if it's not empty
        if not api_key.strip():
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.api_key = api_key
        return f(*args, **kwargs)
    
    return decorated_function


def cors_enabled(origins: str = "*", methods: list = None, headers: list = None):
    """
    Decorator to enable CORS for specific endpoints.
    
    Args:
        origins: Allowed origins
        methods: Allowed methods
        headers: Allowed headers
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            
            # Add CORS headers
            if hasattr(response, 'headers'):
                response.headers['Access-Control-Allow-Origin'] = origins
                if methods:
                    response.headers['Access-Control-Allow-Methods'] = ', '.join(methods)
                if headers:
                    response.headers['Access-Control-Allow-Headers'] = ', '.join(headers)
            
            return response
        
        return decorated_function
    return decorator


def timer(f: Callable) -> Callable:
    """
    Decorator to time function execution.
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.debug(f"Function {f.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return decorated_function
