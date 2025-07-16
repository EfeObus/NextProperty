"""
Cache warming utilities for NextProperty AI platform.
Provides mechanisms to pre-populate caches with frequently accessed data.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .cache_manager import cache_manager
from .property_cache import property_cache
from .market_cache import market_cache
from .api_cache import api_cache

logger = logging.getLogger(__name__)


class CacheWarmer:
    """Manages cache warming operations."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize cache warmer.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.cache = cache_manager
        self.property_cache = property_cache
        self.market_cache = market_cache
        self.api_cache = api_cache
    
    def warm_property_caches(self, 
                           property_ids: List[Union[str, int]],
                           data_functions: Dict[str, Callable],
                           batch_size: int = 50) -> Dict[str, Any]:
        """
        Warm property caches in batches.
        
        Args:
            property_ids: List of property IDs to warm
            data_functions: Dict of data type -> function to get data
            batch_size: Number of properties to process per batch
        
        Returns:
            Warming results summary
        """
        logger.info(f"Starting property cache warming for {len(property_ids)} properties")
        start_time = time.time()
        
        results = {
            'total_properties': len(property_ids),
            'processed': 0,
            'cached': 0,
            'errors': 0,
            'data_types': {},
            'execution_time': 0
        }
        
        # Process in batches
        for i in range(0, len(property_ids), batch_size):
            batch = property_ids[i:i + batch_size]
            batch_results = self._warm_property_batch(batch, data_functions)
            
            # Aggregate results
            results['processed'] += batch_results['processed']
            results['cached'] += batch_results['cached']
            results['errors'] += batch_results['errors']
            
            for data_type, count in batch_results['data_types'].items():
                results['data_types'][data_type] = results['data_types'].get(data_type, 0) + count
            
            logger.info(f"Completed batch {i//batch_size + 1}/{(len(property_ids) + batch_size - 1)//batch_size}")
        
        results['execution_time'] = time.time() - start_time
        logger.info(f"Property cache warming completed in {results['execution_time']:.2f}s")
        
        return results
    
    def _warm_property_batch(self, 
                           property_ids: List[Union[str, int]],
                           data_functions: Dict[str, Callable]) -> Dict[str, Any]:
        """Warm a batch of property caches."""
        batch_results = {
            'processed': 0,
            'cached': 0,
            'errors': 0,
            'data_types': {}
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks for each property
            future_to_property = {}
            
            for property_id in property_ids:
                future = executor.submit(self._warm_single_property, property_id, data_functions)
                future_to_property[future] = property_id
            
            # Collect results
            for future in as_completed(future_to_property):
                property_id = future_to_property[future]
                try:
                    property_results = future.result()
                    batch_results['processed'] += 1
                    batch_results['cached'] += property_results['cached']
                    
                    for data_type, success in property_results['data_types'].items():
                        if success:
                            batch_results['data_types'][data_type] = batch_results['data_types'].get(data_type, 0) + 1
                
                except Exception as e:
                    logger.error(f"Error warming cache for property {property_id}: {e}")
                    batch_results['errors'] += 1
        
        return batch_results
    
    def _warm_single_property(self, 
                            property_id: Union[str, int],
                            data_functions: Dict[str, Callable]) -> Dict[str, Any]:
        """Warm cache for a single property."""
        results = {
            'cached': 0,
            'data_types': {}
        }
        
        for data_type, data_func in data_functions.items():
            try:
                if data_type == 'details':
                    # Check if already cached
                    if not self.property_cache.get_property(property_id):
                        data = data_func(property_id)
                        if data:
                            success = self.property_cache.cache_property(property_id, data)
                            results['data_types'][data_type] = success
                            if success:
                                results['cached'] += 1
                
                elif data_type == 'analytics':
                    if not self.property_cache.get_property_analytics(property_id):
                        data = data_func(property_id)
                        if data:
                            success = self.property_cache.cache_property_analytics(property_id, data)
                            results['data_types'][data_type] = success
                            if success:
                                results['cached'] += 1
                
            except Exception as e:
                logger.error(f"Error warming {data_type} for property {property_id}: {e}")
                results['data_types'][data_type] = False
        
        return results
    
    def warm_market_caches(self, 
                          locations: List[str],
                          data_functions: Dict[str, Callable]) -> Dict[str, Any]:
        """
        Warm market data caches for multiple locations.
        
        Args:
            locations: List of locations to warm
            data_functions: Dict of data type -> function to get data
        
        Returns:
            Warming results summary
        """
        logger.info(f"Starting market cache warming for {len(locations)} locations")
        start_time = time.time()
        
        results = {
            'total_locations': len(locations),
            'processed': 0,
            'cached': 0,
            'errors': 0,
            'data_types': {},
            'execution_time': 0
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_location = {}
            
            for location in locations:
                future = executor.submit(self._warm_single_location, location, data_functions)
                future_to_location[future] = location
            
            for future in as_completed(future_to_location):
                location = future_to_location[future]
                try:
                    location_results = future.result()
                    results['processed'] += 1
                    results['cached'] += location_results['cached']
                    
                    for data_type, count in location_results['data_types'].items():
                        results['data_types'][data_type] = results['data_types'].get(data_type, 0) + count
                
                except Exception as e:
                    logger.error(f"Error warming market cache for {location}: {e}")
                    results['errors'] += 1
        
        results['execution_time'] = time.time() - start_time
        logger.info(f"Market cache warming completed in {results['execution_time']:.2f}s")
        
        return results
    
    def _warm_single_location(self, 
                            location: str,
                            data_functions: Dict[str, Callable]) -> Dict[str, Any]:
        """Warm market cache for a single location."""
        results = {
            'cached': 0,
            'data_types': {}
        }
        
        for data_type, data_func in data_functions.items():
            try:
                if data_type == 'trends':
                    cached_count = 0
                    for period in ['monthly', 'quarterly', 'yearly']:
                        if not self.market_cache.get_market_trends(location, period):
                            data = data_func(location, period)
                            if data:
                                success = self.market_cache.cache_market_trends(location, period, data)
                                if success:
                                    cached_count += 1
                    results['data_types'][data_type] = cached_count
                    results['cached'] += cached_count
                
                elif data_type == 'statistics':
                    if not self.market_cache.get_market_statistics(location):
                        data = data_func(location)
                        if data:
                            success = self.market_cache.cache_market_statistics(location, data)
                            results['data_types'][data_type] = 1 if success else 0
                            if success:
                                results['cached'] += 1
                
                elif data_type == 'investment':
                    if not self.market_cache.get_investment_metrics(location):
                        data = data_func(location)
                        if data:
                            success = self.market_cache.cache_investment_metrics(location, data)
                            results['data_types'][data_type] = 1 if success else 0
                            if success:
                                results['cached'] += 1
                
            except Exception as e:
                logger.error(f"Error warming {data_type} for location {location}: {e}")
                results['data_types'][data_type] = 0
        
        return results
    
    def warm_popular_searches(self, 
                            search_queries: List[Dict[str, Any]],
                            search_function: Callable) -> Dict[str, Any]:
        """
        Warm cache for popular search queries.
        
        Args:
            search_queries: List of search query parameters
            search_function: Function to execute search
        
        Returns:
            Warming results summary
        """
        logger.info(f"Starting search cache warming for {len(search_queries)} queries")
        start_time = time.time()
        
        results = {
            'total_queries': len(search_queries),
            'cached': 0,
            'errors': 0,
            'execution_time': 0
        }
        
        for query in search_queries:
            try:
                # Check if already cached
                cached_results = self.property_cache.get_property_search(query)
                if not cached_results:
                    # Execute search and cache results
                    search_results = search_function(query)
                    if search_results:
                        success = self.property_cache.cache_property_search(
                            query, 
                            search_results.get('properties', []),
                            search_results.get('total_count', 0)
                        )
                        if success:
                            results['cached'] += 1
                        
            except Exception as e:
                logger.error(f"Error warming search cache for query {query}: {e}")
                results['errors'] += 1
        
        results['execution_time'] = time.time() - start_time
        logger.info(f"Search cache warming completed in {results['execution_time']:.2f}s")
        
        return results
    
    def warm_economic_data_cache(self, 
                               indicators: List[Dict[str, str]],
                               data_functions: Dict[str, Callable]) -> Dict[str, Any]:
        """
        Warm economic data caches.
        
        Args:
            indicators: List of indicator configurations
            data_functions: Dict of source -> function to get data
        
        Returns:
            Warming results summary
        """
        logger.info(f"Starting economic data cache warming for {len(indicators)} indicators")
        start_time = time.time()
        
        results = {
            'total_indicators': len(indicators),
            'cached': 0,
            'errors': 0,
            'sources': {},
            'execution_time': 0
        }
        
        for indicator in indicators:
            source = indicator.get('source')
            if source not in data_functions:
                continue
                
            try:
                data_func = data_functions[source]
                
                if source == 'bank_of_canada':
                    series_name = indicator.get('series_name')
                    start_date = indicator.get('start_date')
                    end_date = indicator.get('end_date')
                    
                    if not self.api_cache.get_bank_of_canada_data(series_name, start_date, end_date):
                        data = data_func(series_name, start_date, end_date)
                        if data:
                            success = self.api_cache.cache_bank_of_canada_data(
                                series_name, start_date, end_date, data
                            )
                            if success:
                                results['cached'] += 1
                                results['sources'][source] = results['sources'].get(source, 0) + 1
                
                elif source == 'statistics_canada':
                    table_id = indicator.get('table_id')
                    dimensions = indicator.get('dimensions', {})
                    
                    if not self.api_cache.get_statistics_canada_data(table_id, dimensions):
                        data = data_func(table_id, dimensions)
                        if data:
                            success = self.api_cache.cache_statistics_canada_data(
                                table_id, dimensions, data
                            )
                            if success:
                                results['cached'] += 1
                                results['sources'][source] = results['sources'].get(source, 0) + 1
                
            except Exception as e:
                logger.error(f"Error warming economic data for {indicator}: {e}")
                results['errors'] += 1
        
        results['execution_time'] = time.time() - start_time
        logger.info(f"Economic data cache warming completed in {results['execution_time']:.2f}s")
        
        return results
    
    def schedule_cache_warming(self, 
                             warming_config: Dict[str, Any],
                             schedule_interval: int = 3600) -> bool:
        """
        Schedule periodic cache warming.
        
        Args:
            warming_config: Configuration for what to warm
            schedule_interval: Interval between warming cycles in seconds
        
        Returns:
            True if scheduled successfully
        """
        try:
            # Store warming configuration
            config_key = "cache:warming:config"
            config_data = {
                'config': warming_config,
                'schedule_interval': schedule_interval,
                'next_run': (datetime.utcnow() + timedelta(seconds=schedule_interval)).isoformat(),
                'created_at': datetime.utcnow().isoformat()
            }
            
            success = self.cache.set(config_key, config_data, ttl=schedule_interval * 2)
            
            if success:
                logger.info(f"Scheduled cache warming with {schedule_interval}s interval")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to schedule cache warming: {e}")
            return False
    
    def get_warming_status(self) -> Dict[str, Any]:
        """Get current cache warming status."""
        try:
            # Get warming configuration
            config_key = "cache:warming:config"
            warming_config = self.cache.get(config_key)
            
            # Get last warming results
            results_pattern = "cache:warming:results:*"
            recent_results = []
            
            try:
                result_keys = self.cache.redis.keys(self.cache._make_key(results_pattern))
                for key in sorted(result_keys)[-5:]:  # Last 5 results
                    result_data = self.cache.get(key.split(':')[-1])
                    if result_data:
                        recent_results.append(result_data)
            except Exception:
                pass
            
            # Get cache statistics
            cache_stats = self.cache.get_cache_stats()
            property_stats = self.property_cache.get_property_cache_stats()
            market_stats = self.market_cache.get_market_cache_stats()
            api_stats = self.api_cache.get_api_cache_stats()
            
            return {
                'warming_config': warming_config,
                'recent_results': recent_results,
                'cache_statistics': {
                    'overall': cache_stats,
                    'properties': property_stats,
                    'market': market_stats,
                    'apis': api_stats
                },
                'status': 'active' if warming_config else 'inactive',
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get warming status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def execute_warming_cycle(self, 
                            warming_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete cache warming cycle.
        
        Args:
            warming_config: Configuration for warming cycle
        
        Returns:
            Results of warming cycle
        """
        logger.info("Starting cache warming cycle")
        cycle_start_time = time.time()
        
        cycle_results = {
            'cycle_id': f"warming_{int(cycle_start_time)}",
            'started_at': datetime.utcnow().isoformat(),
            'components': {},
            'total_cached': 0,
            'total_errors': 0,
            'execution_time': 0
        }
        
        # Warm property caches
        if warming_config.get('properties'):
            property_config = warming_config['properties']
            property_results = self.warm_property_caches(
                property_config.get('property_ids', []),
                property_config.get('data_functions', {}),
                property_config.get('batch_size', 50)
            )
            cycle_results['components']['properties'] = property_results
            cycle_results['total_cached'] += property_results.get('cached', 0)
            cycle_results['total_errors'] += property_results.get('errors', 0)
        
        # Warm market caches
        if warming_config.get('market'):
            market_config = warming_config['market']
            market_results = self.warm_market_caches(
                market_config.get('locations', []),
                market_config.get('data_functions', {})
            )
            cycle_results['components']['market'] = market_results
            cycle_results['total_cached'] += market_results.get('cached', 0)
            cycle_results['total_errors'] += market_results.get('errors', 0)
        
        # Warm search caches
        if warming_config.get('searches'):
            search_config = warming_config['searches']
            search_results = self.warm_popular_searches(
                search_config.get('queries', []),
                search_config.get('search_function')
            )
            cycle_results['components']['searches'] = search_results
            cycle_results['total_cached'] += search_results.get('cached', 0)
            cycle_results['total_errors'] += search_results.get('errors', 0)
        
        # Warm economic data caches
        if warming_config.get('economic_data'):
            economic_config = warming_config['economic_data']
            economic_results = self.warm_economic_data_cache(
                economic_config.get('indicators', []),
                economic_config.get('data_functions', {})
            )
            cycle_results['components']['economic_data'] = economic_results
            cycle_results['total_cached'] += economic_results.get('cached', 0)
            cycle_results['total_errors'] += economic_results.get('errors', 0)
        
        cycle_results['execution_time'] = time.time() - cycle_start_time
        cycle_results['completed_at'] = datetime.utcnow().isoformat()
        
        # Store cycle results
        results_key = f"cache:warming:results:{cycle_results['cycle_id']}"
        self.cache.set(results_key, cycle_results, ttl=86400 * 7)  # Keep for 7 days
        
        logger.info(f"Cache warming cycle completed in {cycle_results['execution_time']:.2f}s")
        return cycle_results


# Global cache warmer instance
cache_warmer = CacheWarmer()
