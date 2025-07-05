"""
Performance optimization utilities for NextProperty AI.
"""
from functools import wraps
from flask import request, current_app
from app.extensions import cache
import time
import logging

logger = logging.getLogger(__name__)

def performance_monitor(f):
    """Decorator to monitor function execution time."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            if execution_time > 1.0:  # Log slow queries (>1 second)
                logger.warning(f"Slow execution: {f.__name__} took {execution_time:.2f} seconds")
            
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.error(f"Error in {f.__name__} after {execution_time:.2f} seconds: {str(e)}")
            raise
    return decorated_function

def cache_key_generator(*args, **kwargs):
    """Generate cache key based on request parameters."""
    cache_key = f"{request.endpoint}:"
    
    # Add query parameters
    for key, value in request.args.items():
        cache_key += f"{key}:{value}:"
    
    # Add path parameters
    for arg in args:
        cache_key += f"{str(arg)}:"
    
    return cache_key

def batch_query_optimizer(query, batch_size=100):
    """Optimize queries by processing in batches."""
    offset = 0
    while True:
        batch = query.offset(offset).limit(batch_size).all()
        if not batch:
            break
        yield batch
        offset += batch_size

class QueryOptimizer:
    """Utility class for optimizing database queries."""
    
    @staticmethod
    def optimize_property_queries():
        """Return optimized query patterns for properties."""
        from app.models.property import Property
        from sqlalchemy.orm import selectinload
        
        return {
            'with_photos': Property.query.options(
                selectinload(Property.photos).selectinload(Property.url)
            ),
            'basic_listing': Property.query.with_entities(
                Property.listing_id,
                Property.address,
                Property.city,
                Property.sold_price,
                Property.original_price,
                Property.property_type,
                Property.bedrooms,
                Property.bathrooms,
                Property.sqft
            ),
            'summary_stats': Property.query.with_entities(
                Property.sold_price,
                Property.city,
                Property.property_type
            )
        }
    
    @staticmethod
    def get_property_filters():
        """Get commonly used property filters."""
        from app.models.property import Property
        from sqlalchemy import and_
        
        return {
            'valid_price': and_(
                Property.sold_price.isnot(None),
                Property.sold_price >= 50000,
                Property.sold_price <= 20000000
            ),
            'has_location': and_(
                Property.latitude.isnot(None),
                Property.longitude.isnot(None)
            ),
            'complete_data': and_(
                Property.sqft.isnot(None),
                Property.bedrooms.isnot(None),
                Property.city.isnot(None)
            )
        }

def lazy_load_template_data(template_vars):
    """Lazy load expensive template data only when needed."""
    class LazyDict(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._lazy_funcs = {}
        
        def add_lazy(self, key, func):
            self._lazy_funcs[key] = func
        
        def __getitem__(self, key):
            if key in self._lazy_funcs and key not in self:
                self[key] = self._lazy_funcs[key]()
            return super().__getitem__(key)
    
    return LazyDict(template_vars)
