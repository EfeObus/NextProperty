"""
Cache module for NextProperty AI platform.
Provides Redis-based caching with specialized managers and decorators.
"""

from .cache_manager import CacheManager
from .property_cache import PropertyCacheManager
from .market_cache import MarketCacheManager
from .api_cache import APICacheManager
from .cache_decorators import (
    cached_route,
    cached_api_response,
    cache_property_data,
    cache_market_data,
    invalidate_cache_pattern
)
from .cache_warming import CacheWarmer

__all__ = [
    'CacheManager',
    'PropertyCacheManager',
    'MarketCacheManager',
    'APICacheManager',
    'cached_route',
    'cached_api_response',
    'cache_property_data',
    'cache_market_data',
    'invalidate_cache_pattern',
    'CacheWarmer'
]
