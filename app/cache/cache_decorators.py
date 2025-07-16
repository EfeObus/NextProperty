"""
Cache decorators for NextProperty AI platform.
Provides function-level caching with automatic key generation.
"""

import functools
import hashlib
import json
from typing import Any, Callable, Optional, Union, List
from flask import request, g
import logging

from .cache_manager import cache_manager

logger = logging.getLogger(__name__)


def _generate_cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    # Create a deterministic key from arguments
    key_data = {
        'args': str(args),
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_route(ttl: int = 3600, key_prefix: str = 'route',
                vary_on: Optional[List[str]] = None):
    """
    Cache decorator for Flask routes.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        vary_on: List of request parameters to include in cache key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add request parameters to key
            if vary_on:
                for param in vary_on:
                    value = request.args.get(param, '')
                    key_parts.append(f"{param}:{value}")
            
            # Add user context if available
            if hasattr(g, 'current_user') and g.current_user:
                key_parts.append(f"user:{g.current_user.id}")
            
            cache_key = ':'.join(key_parts)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for route '{func.__name__}'")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for route '{func.__name__}'")
            result = func(*args, **kwargs)
            
            # Cache the result
            cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def cached_api_response(ttl: int = 1800, key_prefix: str = 'api',
                       include_user: bool = True,
                       cache_condition: Optional[Callable] = None):
    """
    Cache decorator for API responses.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        include_user: Whether to include user ID in cache key
        cache_condition: Function to determine if response should be cached
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add function arguments
            if args or kwargs:
                arg_hash = _generate_cache_key(*args, **kwargs)
                key_parts.append(arg_hash)
            
            # Add user context
            if include_user and hasattr(g, 'current_user') and g.current_user:
                key_parts.append(f"user:{g.current_user.id}")
            
            # Add request parameters
            if request.args:
                params_hash = hashlib.md5(
                    json.dumps(dict(request.args), sort_keys=True).encode()
                ).hexdigest()[:8]
                key_parts.append(f"params:{params_hash}")
            
            cache_key = ':'.join(key_parts)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"API cache hit for '{func.__name__}'")
                return cached_result
            
            # Execute function
            logger.debug(f"API cache miss for '{func.__name__}'")
            result = func(*args, **kwargs)
            
            # Check cache condition
            should_cache = True
            if cache_condition:
                should_cache = cache_condition(result)
            
            # Cache successful responses
            if should_cache and isinstance(result, (dict, list, tuple)):
                cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def cache_property_data(ttl: int = 3600):
    """Cache decorator specifically for property data."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key with property context
            key_parts = ['property', func.__name__]
            
            # Add property ID if available
            property_id = kwargs.get('property_id') or (args[0] if args else None)
            if property_id:
                key_parts.append(f"id:{property_id}")
            
            # Add other parameters
            if len(args) > 1 or (len(kwargs) > 1 if property_id in kwargs else len(kwargs) > 0):
                param_hash = _generate_cache_key(*args[1:] if property_id == args[0] else args, 
                                                **{k: v for k, v in kwargs.items() if k != 'property_id'})
                key_parts.append(param_hash[:8])
            
            cache_key = ':'.join(key_parts)
            
            # Try cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute and cache
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def cache_market_data(ttl: int = 1800):
    """Cache decorator specifically for market data."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key with market context
            key_parts = ['market', func.__name__]
            
            # Add location context
            for param in ['city', 'province', 'postal_code', 'location']:
                if param in kwargs:
                    key_parts.append(f"{param}:{kwargs[param]}")
            
            # Add time context
            for param in ['start_date', 'end_date', 'period']:
                if param in kwargs:
                    key_parts.append(f"{param}:{kwargs[param]}")
            
            # Add other parameters
            remaining_kwargs = {k: v for k, v in kwargs.items() 
                              if k not in ['city', 'province', 'postal_code', 'location', 
                                         'start_date', 'end_date', 'period']}
            if args or remaining_kwargs:
                param_hash = _generate_cache_key(*args, **remaining_kwargs)
                key_parts.append(param_hash[:8])
            
            cache_key = ':'.join(key_parts)
            
            # Try cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute and cache
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def cache_with_invalidation(ttl: int = 3600, 
                           invalidation_patterns: Optional[List[str]] = None):
    """
    Cache decorator with automatic invalidation patterns.
    
    Args:
        ttl: Time to live in seconds
        invalidation_patterns: Patterns to invalidate when this function is called
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = ['func', func.__name__]
            if args or kwargs:
                param_hash = _generate_cache_key(*args, **kwargs)
                key_parts.append(param_hash)
            
            cache_key = ':'.join(key_parts)
            
            # For read operations, try cache first
            if func.__name__.startswith(('get', 'find', 'search', 'list')):
                cached_result = cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # For write operations, invalidate related caches
            if func.__name__.startswith(('create', 'update', 'delete', 'save')):
                if invalidation_patterns:
                    for pattern in invalidation_patterns:
                        cache_manager.delete_pattern(pattern)
                        logger.debug(f"Invalidated cache pattern: {pattern}")
            
            # Cache read operation results
            if (func.__name__.startswith(('get', 'find', 'search', 'list')) and 
                result is not None):
                cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str):
    """
    Decorator to invalidate cache patterns after function execution.
    
    Args:
        pattern: Cache pattern to invalidate
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache pattern
            deleted_count = cache_manager.delete_pattern(pattern)
            logger.debug(f"Invalidated {deleted_count} cache keys with pattern: {pattern}")
            
            return result
        return wrapper
    return decorator


def cache_unless_condition(condition: Callable, ttl: int = 3600):
    """
    Cache decorator that skips caching based on condition.
    
    Args:
        condition: Function that returns True to skip caching
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check condition
            if condition(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Normal caching logic
            cache_key = f"conditional:{func.__name__}:{_generate_cache_key(*args, **kwargs)}"
            
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        return wrapper
    return decorator


def cache_with_lock(ttl: int = 3600, lock_timeout: int = 30):
    """
    Cache decorator with distributed locking to prevent cache stampede.
    
    Args:
        ttl: Time to live in seconds
        lock_timeout: Lock timeout in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"locked:{func.__name__}:{_generate_cache_key(*args, **kwargs)}"
            lock_key = f"lock:{cache_key}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Try to acquire lock
            lock_acquired = cache_manager.set(lock_key, "1", ttl=lock_timeout)
            
            if lock_acquired:
                try:
                    # Double-check cache after acquiring lock
                    cached_result = cache_manager.get(cache_key)
                    if cached_result is not None:
                        return cached_result
                    
                    # Execute function and cache result
                    result = func(*args, **kwargs)
                    if result is not None:
                        cache_manager.set(cache_key, result, ttl=ttl)
                    
                    return result
                finally:
                    # Release lock
                    cache_manager.delete(lock_key)
            else:
                # Lock not acquired, execute without caching
                logger.warning(f"Could not acquire lock for {func.__name__}, executing without cache")
                return func(*args, **kwargs)
        return wrapper
    return decorator
