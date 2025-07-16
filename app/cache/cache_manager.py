"""
Core cache manager for NextProperty AI platform.
Provides Redis connection management and basic caching operations.
"""

import redis
import json
import pickle
from typing import Any, Optional, Union, List, Dict
from datetime import timedelta, datetime
import logging
from flask import current_app
import time

logger = logging.getLogger(__name__)


class FallbackCache:
    """In-memory fallback cache that mimics Redis interface."""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def _is_expired(self, key: str) -> bool:
        """Check if key has expired."""
        if key not in self._expiry:
            return False
        return time.time() > self._expiry[key]
    
    def _cleanup_expired(self):
        """Remove expired keys."""
        current_time = time.time()
        expired_keys = [k for k, exp_time in self._expiry.items() if current_time > exp_time]
        for key in expired_keys:
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
    
    def ping(self):
        """Ping method for connection testing."""
        return True
    
    def setex(self, key: str, time_seconds: int, value: Any) -> bool:
        """Set key with expiration time."""
        self._cleanup_expired()
        self._cache[key] = value
        self._expiry[key] = time.time() + time_seconds
        return True
    
    def get(self, key: str) -> Any:
        """Get value by key."""
        self._cleanup_expired()
        if self._is_expired(key):
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
            return None
        return self._cache.get(key)
    
    def delete(self, *keys: str) -> int:
        """Delete keys."""
        self._cleanup_expired()
        deleted = 0
        for key in keys:
            if key in self._cache:
                self._cache.pop(key, None)
                self._expiry.pop(key, None)
                deleted += 1
        return deleted
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        self._cleanup_expired()
        if self._is_expired(key):
            self._cache.pop(key, None)
            self._expiry.pop(key, None)
            return False
        return key in self._cache
    
    def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        self._cleanup_expired()
        if pattern == "*":
            return list(self._cache.keys())
        # Simple pattern matching for basic cases
        import fnmatch
        return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
    
    def ttl(self, key: str) -> int:
        """Get TTL for key."""
        self._cleanup_expired()
        if key not in self._expiry:
            return -1
        if self._is_expired(key):
            return -2
        return int(self._expiry[key] - time.time())
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        if key in self._cache:
            self._expiry[key] = time.time() + seconds
            return True
        return False
    
    def incrby(self, key: str, amount: int = 1) -> int:
        """Increment key by amount."""
        self._cleanup_expired()
        current_val = self._cache.get(key, 0)
        try:
            new_val = int(current_val) + amount
            self._cache[key] = str(new_val)
            return new_val
        except (ValueError, TypeError):
            raise redis.ResponseError("value is not an integer")
    
    def hmset(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set hash mapping."""
        self._cleanup_expired()
        if key not in self._cache:
            self._cache[key] = {}
        if not isinstance(self._cache[key], dict):
            self._cache[key] = {}
        self._cache[key].update(mapping)
        return True
    
    def hget(self, key: str, field: str) -> Any:
        """Get hash field."""
        self._cleanup_expired()
        if self._is_expired(key):
            return None
        hash_data = self._cache.get(key, {})
        if isinstance(hash_data, dict):
            return hash_data.get(field)
        return None
    
    def hgetall(self, key: str) -> Dict[str, Any]:
        """Get all hash fields."""
        self._cleanup_expired()
        if self._is_expired(key):
            return {}
        hash_data = self._cache.get(key, {})
        return hash_data if isinstance(hash_data, dict) else {}
    
    def info(self) -> Dict[str, Any]:
        """Get cache info."""
        self._cleanup_expired()
        return {
            'redis_version': 'fallback-cache-1.0',
            'uptime_in_seconds': 0,
            'used_memory_human': f"{len(self._cache)} keys",
            'used_memory_peak_human': f"{len(self._cache)} keys",
            'connected_clients': 1,
            'keyspace_hits': 0,
            'keyspace_misses': 0
        }


class CacheManager:
    """Core cache manager using Redis."""
    
    def __init__(self, redis_url: Optional[str] = None, 
                 default_ttl: int = 3600, 
                 key_prefix: str = 'nextprop'):
        """
        Initialize cache manager.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default TTL in seconds
            key_prefix: Prefix for all cache keys
        """
        self.redis_url = redis_url or current_app.config.get(
            'REDIS_URL', 'redis://localhost:6379/0'
        )
        self.default_ttl = default_ttl
        self.key_prefix = key_prefix
        self._redis = None
    
    @property
    def redis(self) -> redis.Redis:
        """Get Redis connection (lazy loading)."""
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                self._redis.ping()
                logger.info("Redis connection established successfully")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                # Fallback to in-memory cache for development
                self._redis = self._get_fallback_cache()
        return self._redis
    
    def _get_fallback_cache(self) -> FallbackCache:
        """Fallback in-memory cache when Redis is unavailable."""
        logger.warning("Using fallback in-memory cache")
        return FallbackCache()
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.key_prefix}:{key}"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            serialize_method: str = 'json') -> bool:
        """
        Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            serialize_method: 'json' or 'pickle'
        
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._make_key(key)
            ttl = ttl or self.default_ttl
            
            # Serialize value
            if serialize_method == 'json':
                serialized_value = json.dumps(value, default=str)
            elif serialize_method == 'pickle':
                serialized_value = pickle.dumps(value)
            else:
                raise ValueError(f"Unknown serialize_method: {serialize_method}")
            
            result = self.redis.setex(cache_key, ttl, serialized_value)
            logger.debug(f"Cached key '{cache_key}' with TTL {ttl}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to set cache key '{key}': {e}")
            return False
    
    def get(self, key: str, serialize_method: str = 'json') -> Optional[Any]:
        """
        Get cache value.
        
        Args:
            key: Cache key
            serialize_method: 'json' or 'pickle'
        
        Returns:
            Cached value or None if not found
        """
        try:
            cache_key = self._make_key(key)
            serialized_value = self.redis.get(cache_key)
            
            if serialized_value is None:
                return None
            
            # Deserialize value
            if serialize_method == 'json':
                return json.loads(serialized_value)
            elif serialize_method == 'pickle':
                return pickle.loads(serialized_value)
            else:
                raise ValueError(f"Unknown serialize_method: {serialize_method}")
                
        except Exception as e:
            logger.error(f"Failed to get cache key '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete cache key."""
        try:
            cache_key = self._make_key(key)
            result = self.redis.delete(cache_key)
            logger.debug(f"Deleted cache key '{cache_key}'")
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to delete cache key '{key}': {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Pattern to match (use * for wildcards)
        
        Returns:
            Number of keys deleted
        """
        try:
            cache_pattern = self._make_key(pattern)
            keys = self.redis.keys(cache_pattern)
            if keys:
                deleted_count = self.redis.delete(*keys)
                logger.info(f"Deleted {deleted_count} keys matching pattern '{pattern}'")
                return deleted_count
            return 0
        except Exception as e:
            logger.error(f"Failed to delete pattern '{pattern}': {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            cache_key = self._make_key(key)
            return bool(self.redis.exists(cache_key))
        except Exception as e:
            logger.error(f"Failed to check existence of key '{key}': {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """Get TTL for key in seconds."""
        try:
            cache_key = self._make_key(key)
            return self.redis.ttl(cache_key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key '{key}': {e}")
            return -1
    
    def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Extend TTL for existing key."""
        try:
            cache_key = self._make_key(key)
            current_ttl = self.redis.ttl(cache_key)
            if current_ttl > 0:
                new_ttl = current_ttl + additional_seconds
                result = self.redis.expire(cache_key, new_ttl)
                logger.debug(f"Extended TTL for key '{cache_key}' by {additional_seconds}s")
                return result
            return False
        except Exception as e:
            logger.error(f"Failed to extend TTL for key '{key}': {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value."""
        try:
            cache_key = self._make_key(key)
            return self.redis.incrby(cache_key, amount)
        except Exception as e:
            logger.error(f"Failed to increment key '{key}': {e}")
            return None
    
    def set_hash(self, key: str, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set hash values."""
        try:
            cache_key = self._make_key(key)
            
            # Convert values to strings
            string_mapping = {k: json.dumps(v, default=str) for k, v in mapping.items()}
            
            result = self.redis.hmset(cache_key, string_mapping)
            
            if ttl:
                self.redis.expire(cache_key, ttl)
            
            logger.debug(f"Set hash '{cache_key}' with {len(mapping)} fields")
            return result
            
        except Exception as e:
            logger.error(f"Failed to set hash '{key}': {e}")
            return False
    
    def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Union[Dict, Any]]:
        """Get hash values."""
        try:
            cache_key = self._make_key(key)
            
            if field:
                value = self.redis.hget(cache_key, field)
                return json.loads(value) if value else None
            else:
                hash_data = self.redis.hgetall(cache_key)
                return {k: json.loads(v) for k, v in hash_data.items()} if hash_data else None
                
        except Exception as e:
            logger.error(f"Failed to get hash '{key}': {e}")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            info = self.redis.info()
            pattern = self._make_key("*")
            keys = self.redis.keys(pattern)
            
            return {
                'total_keys': len(keys),
                'memory_used': info.get('used_memory_human', 'N/A'),
                'memory_peak': info.get('used_memory_peak_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                )
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate."""
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0
    
    def clear_all(self) -> bool:
        """Clear all cache keys with prefix."""
        try:
            pattern = self._make_key("*")
            keys = self.redis.keys(pattern)
            if keys:
                deleted_count = self.redis.delete(*keys)
                logger.info(f"Cleared {deleted_count} cache keys")
                return True
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform cache health check."""
        try:
            # Test basic operations
            test_key = "health_check"
            test_value = {"timestamp": "test"}
            
            # Set test value
            set_success = self.set(test_key, test_value, ttl=60)
            
            # Get test value
            get_result = self.get(test_key)
            get_success = get_result == test_value
            
            # Delete test value
            delete_success = self.delete(test_key)
            
            # Get cache info
            info = self.redis.info()
            
            return {
                'status': 'healthy' if all([set_success, get_success, delete_success]) else 'unhealthy',
                'operations': {
                    'set': set_success,
                    'get': get_success,
                    'delete': delete_success
                },
                'redis_info': {
                    'version': info.get('redis_version', 'unknown'),
                    'uptime': info.get('uptime_in_seconds', 0),
                    'memory_used': info.get('used_memory_human', 'N/A')
                }
            }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }


# Global cache manager instance
cache_manager = CacheManager()
