"""
Market data cache manager for NextProperty AI platform.
Handles caching of market analysis, trends, and economic data.
"""

from typing import Dict, List, Optional, Any, Union
import logging
from datetime import datetime, timedelta

from .cache_manager import cache_manager

logger = logging.getLogger(__name__)


class MarketCacheManager:
    """Manages caching for market data and analysis."""
    
    def __init__(self, default_ttl: int = 1800):  # 30 minutes default
        """
        Initialize market cache manager.
        
        Args:
            default_ttl: Default TTL for market data in seconds
        """
        self.default_ttl = default_ttl
        self.cache = cache_manager
    
    def cache_market_trends(self, location: str, time_period: str,
                           trends_data: Dict[str, Any], 
                           ttl: Optional[int] = None) -> bool:
        """
        Cache market trends data.
        
        Args:
            location: Location identifier (city, postal_code, etc.)
            time_period: Time period (monthly, quarterly, yearly)
            trends_data: Market trends data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"market:trends:{location}:{time_period}"
        ttl = ttl or self.default_ttl
        
        cached_data = {
            **trends_data,
            'location': location,
            'time_period': time_period,
            'cached_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
        }
        
        success = self.cache.set(cache_key, cached_data, ttl=ttl)
        if success:
            logger.debug(f"Cached market trends for {location} ({time_period})")
        
        return success
    
    def get_market_trends(self, location: str, 
                         time_period: str) -> Optional[Dict[str, Any]]:
        """
        Get cached market trends data.
        
        Args:
            location: Location identifier
            time_period: Time period
        
        Returns:
            Cached trends data or None
        """
        cache_key = f"market:trends:{location}:{time_period}"
        return self.cache.get(cache_key)
    
    def cache_price_analysis(self, location: str, property_type: str,
                           analysis_data: Dict[str, Any],
                           ttl: Optional[int] = None) -> bool:
        """
        Cache price analysis data.
        
        Args:
            location: Location identifier
            property_type: Type of property
            analysis_data: Price analysis data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"market:price_analysis:{location}:{property_type}"
        ttl = ttl or self.default_ttl
        
        cached_data = {
            **analysis_data,
            'location': location,
            'property_type': property_type,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_price_analysis(self, location: str, 
                          property_type: str) -> Optional[Dict[str, Any]]:
        """Get cached price analysis data."""
        cache_key = f"market:price_analysis:{location}:{property_type}"
        return self.cache.get(cache_key)
    
    def cache_market_statistics(self, location: str, 
                              stats_data: Dict[str, Any],
                              ttl: Optional[int] = None) -> bool:
        """
        Cache market statistics.
        
        Args:
            location: Location identifier
            stats_data: Market statistics data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"market:stats:{location}"
        ttl = ttl or self.default_ttl
        
        cached_data = {
            **stats_data,
            'location': location,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_market_statistics(self, location: str) -> Optional[Dict[str, Any]]:
        """Get cached market statistics."""
        cache_key = f"market:stats:{location}"
        return self.cache.get(cache_key)
    
    def cache_economic_indicators(self, indicator_type: str, 
                                region: str,
                                indicators_data: Dict[str, Any],
                                ttl: Optional[int] = None) -> bool:
        """
        Cache economic indicators data.
        
        Args:
            indicator_type: Type of indicator (interest_rates, inflation, etc.)
            region: Geographic region
            indicators_data: Economic indicators data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"market:economic:{indicator_type}:{region}"
        ttl = ttl or (self.default_ttl * 2)  # Longer TTL for economic data
        
        cached_data = {
            **indicators_data,
            'indicator_type': indicator_type,
            'region': region,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_economic_indicators(self, indicator_type: str, 
                              region: str) -> Optional[Dict[str, Any]]:
        """Get cached economic indicators."""
        cache_key = f"market:economic:{indicator_type}:{region}"
        return self.cache.get(cache_key)
    
    def cache_comparative_analysis(self, locations: List[str],
                                 analysis_data: Dict[str, Any],
                                 ttl: Optional[int] = None) -> bool:
        """
        Cache comparative market analysis.
        
        Args:
            locations: List of locations being compared
            analysis_data: Comparative analysis data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        import hashlib
        
        # Create cache key from sorted locations
        locations_str = ':'.join(sorted(locations))
        locations_hash = hashlib.md5(locations_str.encode()).hexdigest()[:12]
        cache_key = f"market:comparative:{locations_hash}"
        
        ttl = ttl or self.default_ttl
        
        cached_data = {
            **analysis_data,
            'locations': sorted(locations),
            'cached_at': datetime.utcnow().isoformat()
        }
        
        success = self.cache.set(cache_key, cached_data, ttl=ttl)
        if success:
            logger.debug(f"Cached comparative analysis for {len(locations)} locations")
        
        return success
    
    def get_comparative_analysis(self, locations: List[str]) -> Optional[Dict[str, Any]]:
        """Get cached comparative analysis."""
        import hashlib
        
        locations_str = ':'.join(sorted(locations))
        locations_hash = hashlib.md5(locations_str.encode()).hexdigest()[:12]
        cache_key = f"market:comparative:{locations_hash}"
        
        return self.cache.get(cache_key)
    
    def cache_market_forecast(self, location: str, forecast_horizon: str,
                            forecast_data: Dict[str, Any],
                            ttl: Optional[int] = None) -> bool:
        """
        Cache market forecast data.
        
        Args:
            location: Location identifier
            forecast_horizon: Forecast time horizon (1m, 3m, 6m, 1y, etc.)
            forecast_data: Forecast data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"market:forecast:{location}:{forecast_horizon}"
        ttl = ttl or (self.default_ttl * 3)  # Longer TTL for forecasts
        
        cached_data = {
            **forecast_data,
            'location': location,
            'forecast_horizon': forecast_horizon,
            'cached_at': datetime.utcnow().isoformat(),
            'forecast_generated_at': forecast_data.get('generated_at', datetime.utcnow().isoformat())
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_market_forecast(self, location: str, 
                           forecast_horizon: str) -> Optional[Dict[str, Any]]:
        """Get cached market forecast."""
        cache_key = f"market:forecast:{location}:{forecast_horizon}"
        return self.cache.get(cache_key)
    
    def cache_investment_metrics(self, location: str, 
                               metrics_data: Dict[str, Any],
                               ttl: Optional[int] = None) -> bool:
        """
        Cache investment metrics for a location.
        
        Args:
            location: Location identifier
            metrics_data: Investment metrics data
            ttl: Time to live in seconds
        
        Returns:
            True if cached successfully
        """
        cache_key = f"market:investment:{location}"
        ttl = ttl or self.default_ttl
        
        cached_data = {
            **metrics_data,
            'location': location,
            'cached_at': datetime.utcnow().isoformat()
        }
        
        return self.cache.set(cache_key, cached_data, ttl=ttl)
    
    def get_investment_metrics(self, location: str) -> Optional[Dict[str, Any]]:
        """Get cached investment metrics."""
        cache_key = f"market:investment:{location}"
        return self.cache.get(cache_key)
    
    def invalidate_market_data(self, location: Optional[str] = None) -> int:
        """
        Invalidate market data caches.
        
        Args:
            location: Specific location to invalidate, or None for all
        
        Returns:
            Number of cache keys deleted
        """
        if location:
            patterns = [
                f"market:trends:{location}:*",
                f"market:price_analysis:{location}:*",
                f"market:stats:{location}",
                f"market:forecast:{location}:*",
                f"market:investment:{location}"
            ]
        else:
            patterns = ["market:*"]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = self.cache.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Invalidated {total_deleted} market data cache keys")
        return total_deleted
    
    def invalidate_economic_data(self, indicator_type: Optional[str] = None,
                               region: Optional[str] = None) -> int:
        """
        Invalidate economic data caches.
        
        Args:
            indicator_type: Specific indicator type to invalidate
            region: Specific region to invalidate
        
        Returns:
            Number of cache keys deleted
        """
        if indicator_type and region:
            pattern = f"market:economic:{indicator_type}:{region}"
        elif indicator_type:
            pattern = f"market:economic:{indicator_type}:*"
        elif region:
            pattern = f"market:economic:*:{region}"
        else:
            pattern = "market:economic:*"
        
        deleted = self.cache.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} economic data cache keys")
        return deleted
    
    def warm_market_cache(self, locations: List[str], 
                         data_functions: Dict[str, callable]) -> Dict[str, int]:
        """
        Warm market cache for multiple locations.
        
        Args:
            locations: List of locations to cache
            data_functions: Dict of data type -> function to get data
        
        Returns:
            Dict of data type -> number of items cached
        """
        results = {}
        
        for data_type, data_func in data_functions.items():
            cached_count = 0
            
            for location in locations:
                try:
                    # Check what data type we're warming
                    if data_type == 'trends':
                        for period in ['monthly', 'quarterly', 'yearly']:
                            if not self.get_market_trends(location, period):
                                data = data_func(location, period)
                                if data and self.cache_market_trends(location, period, data):
                                    cached_count += 1
                    
                    elif data_type == 'statistics':
                        if not self.get_market_statistics(location):
                            data = data_func(location)
                            if data and self.cache_market_statistics(location, data):
                                cached_count += 1
                    
                    elif data_type == 'investment':
                        if not self.get_investment_metrics(location):
                            data = data_func(location)
                            if data and self.cache_investment_metrics(location, data):
                                cached_count += 1
                
                except Exception as e:
                    logger.error(f"Failed to warm {data_type} cache for {location}: {e}")
            
            results[data_type] = cached_count
        
        logger.info(f"Warmed market cache: {results}")
        return results
    
    def get_market_cache_stats(self) -> Dict[str, Any]:
        """Get market cache statistics."""
        try:
            # Count different types of market caches
            trends = len(self.cache.redis.keys(
                self.cache._make_key("market:trends:*")
            ))
            price_analysis = len(self.cache.redis.keys(
                self.cache._make_key("market:price_analysis:*")
            ))
            statistics = len(self.cache.redis.keys(
                self.cache._make_key("market:stats:*")
            ))
            economic = len(self.cache.redis.keys(
                self.cache._make_key("market:economic:*")
            ))
            forecasts = len(self.cache.redis.keys(
                self.cache._make_key("market:forecast:*")
            ))
            investment = len(self.cache.redis.keys(
                self.cache._make_key("market:investment:*")
            ))
            comparative = len(self.cache.redis.keys(
                self.cache._make_key("market:comparative:*")
            ))
            
            return {
                'market_trends': trends,
                'price_analysis': price_analysis,
                'market_statistics': statistics,
                'economic_indicators': economic,
                'market_forecasts': forecasts,
                'investment_metrics': investment,
                'comparative_analysis': comparative,
                'total_market_keys': (
                    trends + price_analysis + statistics + 
                    economic + forecasts + investment + comparative
                )
            }
        except Exception as e:
            logger.error(f"Failed to get market cache stats: {e}")
            return {}
    
    def schedule_cache_refresh(self, location: str, 
                             refresh_functions: Dict[str, callable]) -> bool:
        """
        Schedule cache refresh for a location.
        
        Args:
            location: Location to refresh
            refresh_functions: Functions to refresh different data types
        
        Returns:
            True if scheduled successfully
        """
        try:
            # This could be integrated with a job queue like Celery
            # For now, we'll mark items for refresh
            refresh_key = f"market:refresh_schedule:{location}"
            refresh_data = {
                'location': location,
                'scheduled_at': datetime.utcnow().isoformat(),
                'data_types': list(refresh_functions.keys())
            }
            
            # Store refresh schedule (short TTL as this is just for tracking)
            return self.cache.set(refresh_key, refresh_data, ttl=300)
            
        except Exception as e:
            logger.error(f"Failed to schedule cache refresh for {location}: {e}")
            return False


# Global market cache manager instance
market_cache = MarketCacheManager()
