"""
Caching utilities for NextProperty AI platform.
"""

import hashlib
import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import datetime, timedelta
from functools import wraps
import redis
from flask import current_app, request
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Centralized cache management."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.default_timeout = 300  # 5 minutes
        self.key_prefix = "nextproperty:"
    
    def get_redis_client(self):
        """Get Redis client instance."""
        if self.redis_client:
            return self.redis_client
        
        try:
            return current_app.extensions.get('redis')
        except Exception:
            return None
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_parts = [str(arg) for arg in args]
        
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.extend([f"{k}:{v}" for k, v in sorted_kwargs])
        
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{self.key_prefix}{key_hash}"
    
    def set(self, key: str, value: Any, timeout: int = None) -> bool:
        """Set cache value."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            timeout = timeout or self.default_timeout
            
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = pickle.dumps(value)
            
            return redis_client.setex(key, timeout, serialized_value)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
            return False
    
    def get(self, key: str) -> Any:
        """Get cache value."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return None
            
            value = redis_client.get(key)
            if not value:
                return None
            
            # Try JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache value."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            return bool(redis_client.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete failed: {e}")
            return False
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return 0
            
            keys = redis_client.keys(f"{self.key_prefix}{pattern}")
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache flush pattern failed: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            return bool(redis_client.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists check failed: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment cache value."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return None
            
            return redis_client.incr(key, amount)
        except Exception as e:
            logger.warning(f"Cache increment failed: {e}")
            return None
    
    def set_hash(self, key: str, mapping: Dict[str, Any], timeout: int = None) -> bool:
        """Set hash values in cache."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return False
            
            # Serialize hash values
            serialized_mapping = {}
            for k, v in mapping.items():
                if isinstance(v, (dict, list)):
                    serialized_mapping[k] = json.dumps(v, default=str)
                else:
                    serialized_mapping[k] = str(v)
            
            redis_client.hmset(key, serialized_mapping)
            
            if timeout:
                redis_client.expire(key, timeout)
            
            return True
        except Exception as e:
            logger.warning(f"Cache set hash failed: {e}")
            return False
    
    def get_hash(self, key: str, field: str = None) -> Any:
        """Get hash values from cache."""
        try:
            redis_client = self.get_redis_client()
            if not redis_client:
                return None
            
            if field:
                value = redis_client.hget(key, field)
                if value:
                    try:
                        return json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        return value.decode() if isinstance(value, bytes) else value
                return None
            else:
                hash_data = redis_client.hgetall(key)
                if not hash_data:
                    return None
                
                result = {}
                for k, v in hash_data.items():
                    k = k.decode() if isinstance(k, bytes) else k
                    v = v.decode() if isinstance(v, bytes) else v
                    try:
                        result[k] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        result[k] = v
                
                return result
        except Exception as e:
            logger.warning(f"Cache get hash failed: {e}")
            return None


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key."""
    return cache_manager.generate_key(*args, **kwargs)


def cache_set(key: str, value: Any, timeout: int = None) -> bool:
    """Set cache value."""
    return cache_manager.set(key, value, timeout)


def cache_get(key: str) -> Any:
    """Get cache value."""
    return cache_manager.get(key)


def cache_delete(key: str) -> bool:
    """Delete cache value."""
    return cache_manager.delete(key)


def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching pattern."""
    return cache_manager.flush_pattern(pattern)


def warm_cache(cache_functions: List[Dict[str, Any]]) -> Dict[str, bool]:
    """Warm cache with predefined data."""
    results = {}
    
    for cache_func in cache_functions:
        func_name = cache_func.get('name', 'unknown')
        try:
            func = cache_func['function']
            args = cache_func.get('args', [])
            kwargs = cache_func.get('kwargs', {})
            timeout = cache_func.get('timeout', None)
            
            result = func(*args, **kwargs)
            key = cache_func.get('key') or cache_key(func_name, *args, **kwargs)
            
            success = cache_set(key, result, timeout)
            results[func_name] = success
            
            if success:
                logger.info(f"Cache warmed for {func_name}")
            else:
                logger.warning(f"Failed to warm cache for {func_name}")
                
        except Exception as e:
            logger.error(f"Error warming cache for {func_name}: {e}")
            results[func_name] = False
    
    return results


def cached(timeout: int = 300, key_prefix: str = "", vary_on: List[str] = None,
          skip_cache: bool = False):
    """
    Decorator for caching function results.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache key
        vary_on: List of request parameters to include in cache key
        skip_cache: Skip cache if True
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if skip_cache:
                return func(*args, **kwargs)
            
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            if vary_on:
                for param in vary_on:
                    value = request.args.get(param, '') if hasattr(request, 'args') else ''
                    key_parts.append(f"{param}:{value}")
            
            if args:
                key_parts.append(f"args:{hashlib.md5(str(args).encode()).hexdigest()}")
            if kwargs:
                key_parts.append(f"kwargs:{hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()}")
            
            cache_key_str = cache_key(*key_parts)
            
            # Try to get from cache
            cached_result = cache_get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            
            cache_set(cache_key_str, result, timeout)
            
            return result
        return wrapper
    return decorator


class PropertyCache:
    """Cache specifically for property data."""
    
    @staticmethod
    def get_property_key(property_id: int) -> str:
        """Get cache key for property."""
        return cache_key("property", property_id)
    
    @staticmethod
    def set_property(property_id: int, data: Dict[str, Any], timeout: int = 3600) -> bool:
        """Cache property data."""
        key = PropertyCache.get_property_key(property_id)
        return cache_set(key, data, timeout)
    
    @staticmethod
    def get_property(property_id: int) -> Optional[Dict[str, Any]]:
        """Get cached property data."""
        key = PropertyCache.get_property_key(property_id)
        return cache_get(key)
    
    @staticmethod
    def delete_property(property_id: int) -> bool:
        """Delete cached property data."""
        key = PropertyCache.get_property_key(property_id)
        return cache_delete(key)
    
    @staticmethod
    def get_search_key(search_params: Dict[str, Any]) -> str:
        """Get cache key for property search."""
        # Sort parameters for consistent key generation
        sorted_params = sorted(search_params.items())
        params_hash = hashlib.md5(str(sorted_params).encode()).hexdigest()
        return cache_key("property_search", params_hash)
    
    @staticmethod
    def set_search_results(search_params: Dict[str, Any], results: Dict[str, Any], 
                          timeout: int = 600) -> bool:
        """Cache property search results."""
        key = PropertyCache.get_search_key(search_params)
        return cache_set(key, results, timeout)
    
    @staticmethod
    def get_search_results(search_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached property search results."""
        key = PropertyCache.get_search_key(search_params)
        return cache_get(key)


class MarketDataCache:
    """Cache specifically for market data."""
    
    @staticmethod
    def get_market_key(region: str, period: str) -> str:
        """Get cache key for market data."""
        return cache_key("market_data", region, period)
    
    @staticmethod
    def set_market_data(region: str, period: str, data: Dict[str, Any], 
                       timeout: int = 7200) -> bool:
        """Cache market data."""
        key = MarketDataCache.get_market_key(region, period)
        return cache_set(key, data, timeout)
    
    @staticmethod
    def get_market_data(region: str, period: str) -> Optional[Dict[str, Any]]:
        """Get cached market data."""
        key = MarketDataCache.get_market_key(region, period)
        return cache_get(key)
    
    @staticmethod
    def invalidate_market_data(region: str = None) -> int:
        """Invalidate market data cache."""
        if region:
            pattern = f"market_data:{region}:*"
        else:
            pattern = "market_data:*"
        return invalidate_cache(pattern)


class APIResponseCache:
    """Cache for API responses."""
    
    @staticmethod
    def get_response_key(endpoint: str, params: Dict[str, Any]) -> str:
        """Get cache key for API response."""
        params_hash = hashlib.md5(str(sorted(params.items())).encode()).hexdigest()
        return cache_key("api_response", endpoint, params_hash)
    
    @staticmethod
    def set_response(endpoint: str, params: Dict[str, Any], response: Dict[str, Any],
                    timeout: int = 300) -> bool:
        """Cache API response."""
        key = APIResponseCache.get_response_key(endpoint, params)
        return cache_set(key, response, timeout)
    
    @staticmethod
    def get_response(endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached API response."""
        key = APIResponseCache.get_response_key(endpoint, params)
        return cache_get(key)


def invalidate_property_related_caches(property_id: int = None) -> Dict[str, int]:
    """Invalidate all property-related caches."""
    results = {}
    
    if property_id:
        # Invalidate specific property cache
        results['property'] = int(PropertyCache.delete_property(property_id))
    
    # Invalidate search results
    results['search_results'] = invalidate_cache("property_search:*")
    
    # Invalidate API responses related to properties
    results['api_responses'] = invalidate_cache("api_response:*properties*")
    
    return results


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        redis_client = cache_manager.get_redis_client()
        if not redis_client:
            return {'error': 'Redis not available'}
        
        info = redis_client.info()
        
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory': info.get('used_memory_human', '0B'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'hit_rate': _calculate_hit_rate(info),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'uptime_in_seconds': info.get('uptime_in_seconds', 0)
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {'error': str(e)}


def _calculate_hit_rate(redis_info: Dict[str, Any]) -> str:
    """Calculate cache hit rate."""
    hits = redis_info.get('keyspace_hits', 0)
    misses = redis_info.get('keyspace_misses', 0)
    total = hits + misses
    
    if total == 0:
        return "0.00%"
    
    hit_rate = (hits / total) * 100
    return f"{hit_rate:.2f}%"
