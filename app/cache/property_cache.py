"""
Property-specific cache manager for NextProperty AI platform.
Handles caching of property data, search results, and related operations.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime, timedelta

from .cache_manager import cache_manager

logger = logging.getLogger(__name__)


class PropertyCacheManager:
    """Manages caching for property-related data."""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize property cache manager.
        
        Args:
            default_ttl: Default TTL for property data in seconds
        """
        self.default_ttl = default_ttl
        self.cache = cache_manager
    
    def cache_property(self, property_id: Union[str, int], 
                      property_data: Dict[str, Any], 
                      ttl: Optional[int] = None) -> bool:
        """
        Cache individual property data.
        
        Args:
            property_id: Property ID
            property_data: Property data to cache
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"property:details:{property_id}"
        ttl = ttl or self.default_ttl
        
        # Add caching metadata
        cached_data = {
            **property_data,
            '_cached_at': datetime.utcnow().isoformat(),
            '_cache_ttl': ttl
        }
        
        success = self.cache.set(cache_key, cached_data, ttl=ttl)
        if success:
            logger.debug(f"Cached property {property_id}")
            # Also cache in hash for quick lookups
            self.cache.set_hash(
                f"property:hash:{property_id}",
                {
                    'id': str(property_id),
                    'price': str(property_data.get('price', 0)),
                    'status': property_data.get('status', 'unknown'),
                    'updated_at': property_data.get('updated_at', ''),
                    'cached_at': datetime.utcnow().isoformat()
                },
                ttl=ttl
            )
        
        return success
    
    def get_property(self, property_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        Get cached property data.
        
        Args:
            property_id: Property ID
        
        Returns:
            Property data or None if not cached
        """
        cache_key = f"property:details:{property_id}"
        return self.cache.get(cache_key)
    
    def cache_property_search(self, search_params: Dict[str, Any], 
                            results: List[Dict[str, Any]], 
                            total_count: int,
                            ttl: Optional[int] = None) -> bool:
        """
        Cache property search results.
        
        Args:
            search_params: Search parameters used
            results: Search results
            total_count: Total number of matching properties
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        # Create cache key from search parameters
        import hashlib
        import json
        
        # Normalize search parameters for consistent caching
        normalized_params = self._normalize_search_params(search_params)
        params_str = json.dumps(normalized_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        cache_key = f"property:search:{params_hash}"
        ttl = ttl or (self.default_ttl // 2)  # Shorter TTL for search results
        
        cached_data = {
            'search_params': normalized_params,
            'results': results,
            'total_count': total_count,
            'cached_at': datetime.utcnow().isoformat(),
            'result_count': len(results)
        }
        
        success = self.cache.set(cache_key, cached_data, ttl=ttl)
        if success:
            logger.debug(f"Cached search results for {len(results)} properties")
        
        return success
    
    def get_property_search(self, search_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached property search results.
        
        Args:
            search_params: Search parameters
        
        Returns:
            Cached search results or None
        """
        import hashlib
        import json
        
        normalized_params = self._normalize_search_params(search_params)
        params_str = json.dumps(normalized_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        
        cache_key = f"property:search:{params_hash}"
        return self.cache.get(cache_key)
    
    def cache_property_list(self, list_type: str, filters: Dict[str, Any],
                           properties: List[Dict[str, Any]], 
                           ttl: Optional[int] = None) -> bool:
        """
        Cache property lists (featured, recent, etc.).
        
        Args:
            list_type: Type of list (featured, recent, popular, etc.)
            filters: Filters applied to the list
            properties: List of properties
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        import hashlib
        import json
        
        # Create cache key
        filters_str = json.dumps(filters, sort_keys=True) if filters else "no_filters"
        filters_hash = hashlib.md5(filters_str.encode()).hexdigest()[:8]
        cache_key = f"property:list:{list_type}:{filters_hash}"
        
        ttl = ttl or (self.default_ttl // 3)  # Shorter TTL for lists
        
        cached_data = {
            'list_type': list_type,
            'filters': filters,
            'properties': properties,
            'count': len(properties),
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_property_list(self, list_type: str, 
                         filters: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached property list.
        
        Args:
            list_type: Type of list
            filters: Filters applied
        
        Returns:
            Cached property list or None
        """
        import hashlib
        import json
        
        filters = filters or {}
        filters_str = json.dumps(filters, sort_keys=True)
        filters_hash = hashlib.md5(filters_str.encode()).hexdigest()[:8]
        cache_key = f"property:list:{list_type}:{filters_hash}"
        
        cached_data = self.cache.get(cache_key)
        return cached_data.get('properties') if cached_data else None
    
    def cache_property_analytics(self, property_id: Union[str, int], 
                               analytics_data: Dict[str, Any],
                               ttl: Optional[int] = None) -> bool:
        """
        Cache property analytics data.
        
        Args:
            property_id: Property ID
            analytics_data: Analytics data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"property:analytics:{property_id}"
        ttl = ttl or (self.default_ttl * 2)  # Longer TTL for analytics
        
        cached_data = {
            **analytics_data,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_property_analytics(self, property_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Get cached property analytics."""
        cache_key = f"property:analytics:{property_id}"
        return self.cache.get(cache_key)
    
    def invalidate_property(self, property_id: Union[str, int]) -> int:
        """
        Invalidate all cached data for a property.
        
        Args:
            property_id: Property ID
        
        Returns:
            Number of cache keys deleted
        """
        patterns = [
            f"property:details:{property_id}",
            f"property:hash:{property_id}",
            f"property:analytics:{property_id}",
            f"property:*:{property_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = self.cache.delete_pattern(pattern)
            total_deleted += deleted
        
        # Also invalidate search results (broad invalidation)
        search_deleted = self.cache.delete_pattern("property:search:*")
        total_deleted += search_deleted
        
        logger.info(f"Invalidated {total_deleted} cache keys for property {property_id}")
        return total_deleted
    
    def invalidate_property_searches(self) -> int:
        """Invalidate all property search caches."""
        deleted = self.cache.delete_pattern("property:search:*")
        logger.info(f"Invalidated {deleted} property search cache keys")
        return deleted
    
    def invalidate_property_lists(self, list_type: Optional[str] = None) -> int:
        """
        Invalidate property list caches.
        
        Args:
            list_type: Specific list type to invalidate, or None for all
        
        Returns:
            Number of cache keys deleted
        """
        if list_type:
            pattern = f"property:list:{list_type}:*"
        else:
            pattern = "property:list:*"
        
        deleted = self.cache.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} property list cache keys")
        return deleted
    
    def warm_property_cache(self, property_ids: List[Union[str, int]], 
                           property_data_func: callable) -> int:
        """
        Warm cache for multiple properties.
        
        Args:
            property_ids: List of property IDs to cache
            property_data_func: Function to get property data
        
        Returns:
            Number of properties cached
        """
        cached_count = 0
        
        for property_id in property_ids:
            try:
                # Check if already cached
                if not self.get_property(property_id):
                    # Get fresh data and cache it
                    property_data = property_data_func(property_id)
                    if property_data:
                        success = self.cache_property(property_id, property_data)
                        if success:
                            cached_count += 1
            except Exception as e:
                logger.error(f"Failed to warm cache for property {property_id}: {e}")
        
        logger.info(f"Warmed cache for {cached_count} properties")
        return cached_count
    
    def get_property_cache_stats(self) -> Dict[str, Any]:
        """Get property cache statistics."""
        try:
            # Count different types of property caches
            property_details = len(self.cache.redis.keys(
                self.cache._make_key("property:details:*")
            ))
            property_searches = len(self.cache.redis.keys(
                self.cache._make_key("property:search:*")
            ))
            property_lists = len(self.cache.redis.keys(
                self.cache._make_key("property:list:*")
            ))
            property_analytics = len(self.cache.redis.keys(
                self.cache._make_key("property:analytics:*")
            ))
            
            return {
                'property_details': property_details,
                'property_searches': property_searches,
                'property_lists': property_lists,
                'property_analytics': property_analytics,
                'total_property_keys': (
                    property_details + property_searches + 
                    property_lists + property_analytics
                )
            }
        except Exception as e:
            logger.error(f"Failed to get property cache stats: {e}")
            return {}
    
    def _normalize_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize search parameters for consistent caching."""
        normalized = {}
        
        # Sort and normalize common parameters
        for key, value in params.items():
            if value is not None and value != '':
                # Convert to string for consistent hashing
                if isinstance(value, (list, tuple)):
                    normalized[key] = sorted([str(v) for v in value])
                else:
                    normalized[key] = str(value)
        
        return normalized


# Global property cache manager instance
property_cache = PropertyCacheManager()
