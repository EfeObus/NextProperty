"""
API response cache manager for NextProperty AI platform.
Handles caching of external API responses and internal API endpoints.
"""

from typing import Dict, List, Optional, Any, Union, Callable
import logging
from datetime import datetime, timedelta
import hashlib
import json

from .cache_manager import cache_manager

logger = logging.getLogger(__name__)


class APICacheManager:
    """Manages caching for API responses."""
    
    def __init__(self, default_ttl: int = 900):  # 15 minutes default
        """
        Initialize API cache manager.
        
        Args:
            default_ttl: Default TTL for API responses in seconds
        """
        self.default_ttl = default_ttl
        self.cache = cache_manager
    
    def cache_external_api_response(self, api_name: str, endpoint: str,
                                  params: Dict[str, Any],
                                  response_data: Any,
                                  ttl: Optional[int] = None) -> bool:
        """
        Cache external API response.
        
        Args:
            api_name: Name of the external API
            endpoint: API endpoint
            params: Request parameters
            response_data: API response data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        # Create cache key from API details
        params_str = json.dumps(params, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        
        cache_key = f"api:external:{api_name}:{endpoint}:{params_hash}"
        ttl = ttl or self.default_ttl
        
        cached_data = {
            'api_name': api_name,
            'endpoint': endpoint,
            'params': params,
            'response_data': response_data,
            'cached_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
        }
        
        success = self.cache.set(cache_key, cached_data, ttl=ttl)
        if success:
            logger.debug(f"Cached {api_name} API response for {endpoint}")
        
        return success
    
    def get_external_api_response(self, api_name: str, endpoint: str,
                                params: Dict[str, Any]) -> Optional[Any]:
        """
        Get cached external API response.
        
        Args:
            api_name: Name of the external API
            endpoint: API endpoint
            params: Request parameters
        
        Returns:
            Cached response data or None
        """
        params_str = json.dumps(params, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        
        cache_key = f"api:external:{api_name}:{endpoint}:{params_hash}"
        cached_data = self.cache.get(cache_key)
        
        return cached_data.get('response_data') if cached_data else None
    
    def cache_bank_of_canada_data(self, series_name: str, 
                                 start_date: str, end_date: str,
                                 data: Dict[str, Any],
                                 ttl: Optional[int] = None) -> bool:
        """
        Cache Bank of Canada API data.
        
        Args:
            series_name: Data series name
            start_date: Start date for data
            end_date: End date for data
            data: API response data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"api:boc:{series_name}:{start_date}:{end_date}"
        ttl = ttl or (self.default_ttl * 4)  # Longer TTL for economic data
        
        cached_data = {
            'series_name': series_name,
            'start_date': start_date,
            'end_date': end_date,
            'data': data,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_bank_of_canada_data(self, series_name: str,
                               start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """Get cached Bank of Canada data."""
        cache_key = f"api:boc:{series_name}:{start_date}:{end_date}"
        cached_data = self.cache.get(cache_key)
        
        return cached_data.get('data') if cached_data else None
    
    def cache_statistics_canada_data(self, table_id: str, 
                                   dimensions: Dict[str, Any],
                                   data: Dict[str, Any],
                                   ttl: Optional[int] = None) -> bool:
        """
        Cache Statistics Canada API data.
        
        Args:
            table_id: Statistics Canada table ID
            dimensions: Data dimensions/filters
            data: API response data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        dimensions_str = json.dumps(dimensions, sort_keys=True, default=str)
        dimensions_hash = hashlib.md5(dimensions_str.encode()).hexdigest()[:12]
        
        cache_key = f"api:statcan:{table_id}:{dimensions_hash}"
        ttl = ttl or (self.default_ttl * 6)  # Longer TTL for government data
        
        cached_data = {
            'table_id': table_id,
            'dimensions': dimensions,
            'data': data,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_statistics_canada_data(self, table_id: str,
                                  dimensions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached Statistics Canada data."""
        dimensions_str = json.dumps(dimensions, sort_keys=True, default=str)
        dimensions_hash = hashlib.md5(dimensions_str.encode()).hexdigest()[:12]
        
        cache_key = f"api:statcan:{table_id}:{dimensions_hash}"
        cached_data = self.cache.get(cache_key)
        
        return cached_data.get('data') if cached_data else None
    
    def cache_geocoding_result(self, address: str, 
                              geocoding_data: Dict[str, Any],
                              ttl: Optional[int] = None) -> bool:
        """
        Cache geocoding API result.
        
        Args:
            address: Address that was geocoded
            geocoding_data: Geocoding result
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        # Check for valid address
        if not address:
            return False
            
        # Normalize address for consistent caching
        normalized_address = address.lower().strip()
        address_hash = hashlib.md5(normalized_address.encode()).hexdigest()[:16]
        
        cache_key = f"api:geocoding:{address_hash}"
        ttl = ttl or (self.default_ttl * 8)  # Long TTL for geocoding
        
        cached_data = {
            'original_address': address,
            'normalized_address': normalized_address,
            'geocoding_data': geocoding_data,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_geocoding_result(self, address: str) -> Optional[Dict[str, Any]]:
        """Get cached geocoding result."""
        if not address:
            return None
            
        normalized_address = address.lower().strip()
        address_hash = hashlib.md5(normalized_address.encode()).hexdigest()[:16]
        
        cache_key = f"api:geocoding:{address_hash}"
        cached_data = self.cache.get(cache_key)
        
        return cached_data.get('geocoding_data') if cached_data else None
    
    def cache_internal_api_response(self, endpoint: str, 
                                  request_data: Dict[str, Any],
                                  response_data: Any,
                                  user_id: Optional[str] = None,
                                  ttl: Optional[int] = None) -> bool:
        """
        Cache internal API response.
        
        Args:
            endpoint: Internal API endpoint
            request_data: Request parameters/data
            response_data: API response
            user_id: User ID if user-specific
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        # Create cache key
        request_str = json.dumps(request_data, sort_keys=True, default=str)
        request_hash = hashlib.md5(request_str.encode()).hexdigest()[:12]
        
        key_parts = ['api', 'internal', endpoint, request_hash]
        if user_id:
            key_parts.append(f"user:{user_id}")
        
        cache_key = ':'.join(key_parts)
        ttl = ttl or self.default_ttl
        
        cached_data = {
            'endpoint': endpoint,
            'request_data': request_data,
            'response_data': response_data,
            'user_id': user_id,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_internal_api_response(self, endpoint: str,
                                request_data: Dict[str, Any],
                                user_id: Optional[str] = None) -> Optional[Any]:
        """Get cached internal API response."""
        request_str = json.dumps(request_data, sort_keys=True, default=str)
        request_hash = hashlib.md5(request_str.encode()).hexdigest()[:12]
        
        key_parts = ['api', 'internal', endpoint, request_hash]
        if user_id:
            key_parts.append(f"user:{user_id}")
        
        cache_key = ':'.join(key_parts)
        cached_data = self.cache.get(cache_key)
        
        return cached_data.get('response_data') if cached_data else None
    
    def cache_api_rate_limit_status(self, api_name: str, 
                                  status_data: Dict[str, Any],
                                  ttl: Optional[int] = None) -> bool:
        """
        Cache API rate limit status.
        
        Args:
            api_name: Name of the API
            status_data: Rate limit status information
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"api:rate_limit:{api_name}"
        ttl = ttl or 300  # 5 minutes for rate limit data
        
        cached_data = {
            'api_name': api_name,
            'status': status_data,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_api_rate_limit_status(self, api_name: str) -> Optional[Dict[str, Any]]:
        """Get cached API rate limit status."""
        cache_key = f"api:rate_limit:{api_name}"
        cached_data = self.cache.get(cache_key)
        
        return cached_data.get('status') if cached_data else None
    
    def invalidate_external_api_cache(self, api_name: Optional[str] = None) -> int:
        """
        Invalidate external API caches.
        
        Args:
            api_name: Specific API to invalidate, or None for all
        
        Returns:
            Number of cache keys deleted
        """
        if api_name:
            pattern = f"api:external:{api_name}:*"
        else:
            pattern = "api:external:*"
        
        deleted = self.cache.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} external API cache keys")
        return deleted
    
    def invalidate_internal_api_cache(self, endpoint: Optional[str] = None,
                                    user_id: Optional[str] = None) -> int:
        """
        Invalidate internal API caches.
        
        Args:
            endpoint: Specific endpoint to invalidate
            user_id: Specific user's cache to invalidate
        
        Returns:
            Number of cache keys deleted
        """
        if endpoint and user_id:
            pattern = f"api:internal:{endpoint}:*:user:{user_id}"
        elif endpoint:
            pattern = f"api:internal:{endpoint}:*"
        elif user_id:
            pattern = f"api:internal:*:user:{user_id}"
        else:
            pattern = "api:internal:*"
        
        deleted = self.cache.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} internal API cache keys")
        return deleted
    
    def cache_api_health_status(self, api_name: str, 
                              health_data: Dict[str, Any],
                              ttl: Optional[int] = None) -> bool:
        """
        Cache API health check status.
        
        Args:
            api_name: Name of the API
            health_data: Health check results
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"api:health:{api_name}"
        ttl = ttl or 120  # 2 minutes for health data
        
        cached_data = {
            'api_name': api_name,
            'health_data': health_data,
            'checked_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_api_health_status(self, api_name: str) -> Optional[Dict[str, Any]]:
        """Get cached API health status."""
        cache_key = f"api:health:{api_name}"
        cached_data = self.cache.get(cache_key)
        
        return cached_data.get('health_data') if cached_data else None
    
    def get_api_cache_stats(self) -> Dict[str, Any]:
        """Get API cache statistics."""
        try:
            # Count different types of API caches
            external_apis = len(self.cache.redis.keys(
                self.cache._make_key("api:external:*")
            ))
            internal_apis = len(self.cache.redis.keys(
                self.cache._make_key("api:internal:*")
            ))
            boc_data = len(self.cache.redis.keys(
                self.cache._make_key("api:boc:*")
            ))
            statcan_data = len(self.cache.redis.keys(
                self.cache._make_key("api:statcan:*")
            ))
            geocoding = len(self.cache.redis.keys(
                self.cache._make_key("api:geocoding:*")
            ))
            rate_limits = len(self.cache.redis.keys(
                self.cache._make_key("api:rate_limit:*")
            ))
            health_checks = len(self.cache.redis.keys(
                self.cache._make_key("api:health:*")
            ))
            
            return {
                'external_apis': external_apis,
                'internal_apis': internal_apis,
                'bank_of_canada': boc_data,
                'statistics_canada': statcan_data,
                'geocoding': geocoding,
                'rate_limits': rate_limits,
                'health_checks': health_checks,
                'total_api_keys': (
                    external_apis + internal_apis + boc_data + 
                    statcan_data + geocoding + rate_limits + health_checks
                )
            }
        except Exception as e:
            logger.error(f"Failed to get API cache stats: {e}")
            return {}
    
    def cache_with_fallback(self, cache_key: str, 
                           data_function: Callable,
                           fallback_function: Optional[Callable] = None,
                           ttl: Optional[int] = None) -> Any:
        """
        Cache data with fallback mechanism.
        
        Args:
            cache_key: Key to cache under
            data_function: Function to get fresh data
            fallback_function: Fallback function if primary fails
            ttl: Time to live in seconds
        
        Returns:
            Data from cache, primary function, or fallback
        """
        # Try cache first
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Try primary data function
        try:
            data = data_function()
            if data is not None:
                self.cache.set(cache_key, data, ttl=ttl or self.default_ttl)
                return data
        except Exception as e:
            logger.error(f"Primary data function failed for {cache_key}: {e}")
        
        # Try fallback function
        if fallback_function:
            try:
                fallback_data = fallback_function()
                if fallback_data is not None:
                    # Cache with shorter TTL for fallback data
                    self.cache.set(cache_key, fallback_data, ttl=300)
                    return fallback_data
            except Exception as e:
                logger.error(f"Fallback function failed for {cache_key}: {e}")
        
        return None
    
    def bulk_invalidate_user_cache(self, user_id: str) -> int:
        """
        Invalidate all cached data for a specific user.
        
        Args:
            user_id: User ID
        
        Returns:
            Number of cache keys deleted
        """
        patterns = [
            f"api:internal:*:user:{user_id}",
            f"*:user:{user_id}:*",
            f"user:{user_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = self.cache.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Invalidated {total_deleted} cache keys for user {user_id}")
        return total_deleted


# Global API cache manager instance
api_cache = APICacheManager()
