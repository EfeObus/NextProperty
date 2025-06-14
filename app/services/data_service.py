"""
Data service for market analysis and property insights.
Handles data processing, aggregation, and market trend analysis.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_
from app.models.property import Property
from app.models.economic_data import EconomicIndicator
from app.extensions import db, cache
import logging

logger = logging.getLogger(__name__)

class DataService:
    """Service for handling data operations and market analysis."""
    
    @staticmethod
    # # @cache.memoize(timeout=3600)  # Cache temporarily disabled
    def get_property_price_trends(city: str = None, property_type: str = None, 
                                 period_days: int = 365) -> Dict:
        """Get property price trends over specified period."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            query = db.session.query(
                func.DATE(Property.sold_date).label('date'),
                func.avg(Property.sold_price).label('avg_price'),
                func.count(Property.listing_id).label('transaction_count')
            )
            
            if city:
                query = query.filter(Property.city.ilike(f'%{city}%'))
            if property_type:
                query = query.filter(Property.property_type == property_type)
                
            query = query.filter(
                Property.sold_date >= start_date
            ).group_by(func.DATE(Property.sold_date))
            
            results = query.all()
            
            trend_data = {
                'dates': [r.date.strftime('%Y-%m-%d') for r in results],
                'avg_prices': [float(r.avg_price) for r in results],
                'transaction_counts': [r.transaction_count for r in results],
                'period_days': period_days,
                'city': city,
                'property_type': property_type
            }
            
            # Calculate trend metrics
            if len(trend_data['avg_prices']) > 1:
                price_change = trend_data['avg_prices'][-1] - trend_data['avg_prices'][0]
                price_change_pct = (price_change / trend_data['avg_prices'][0]) * 100
                trend_data['price_change'] = price_change
                trend_data['price_change_pct'] = price_change_pct
                trend_data['trend_direction'] = 'up' if price_change > 0 else 'down'
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error getting price trends: {str(e)}")
            return {}
    
    @staticmethod
    # @cache.memoize(timeout=1800)  # Cache for 30 minutes
    def get_market_statistics(city: str = None) -> Dict:
        """Get comprehensive market statistics."""
        try:
            base_query = db.session.query(Property)
            if city:
                base_query = base_query.filter(Property.city.ilike(f'%{city}%'))
            
            # Basic statistics
            total_properties = base_query.count()
            avg_price = base_query.with_entities(func.avg(Property.sold_price)).scalar() or 0
            median_price = DataService._calculate_median_price(base_query)
            
            # Price ranges
            price_ranges = DataService._get_price_distribution(base_query)
            
            # Property types distribution
            type_distribution = db.session.query(
                Property.property_type,
                func.count(Property.listing_id).label('count'),
                func.avg(Property.sold_price).label('avg_price')
            ).group_by(Property.property_type)
            
            if city:
                type_distribution = type_distribution.filter(
                    Property.city.ilike(f'%{city}%')
                )
            
            type_data = type_distribution.all()
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_activity = db.session.query(func.count(Property.listing_id)).filter(
                Property.sold_date >= thirty_days_ago
            )
            
            if city:
                recent_activity = recent_activity.filter(
                    Property.city.ilike(f'%{city}%')
                )
            
            recent_transactions = recent_activity.scalar() or 0
            
            return {
                'total_properties': total_properties,
                'avg_price': float(avg_price),
                'median_price': float(median_price),
                'price_ranges': price_ranges,
                'property_types': [
                    {
                        'type': t.property_type,
                        'count': t.count,
                        'avg_price': float(t.avg_price)
                    } for t in type_data
                ],
                'recent_transactions': recent_transactions,
                'city': city
            }
            
        except Exception as e:
            logger.error(f"Error getting market statistics: {str(e)}")
            return {}
    
    @staticmethod
    def _calculate_median_price(query) -> float:
        """Calculate median price from query results."""
        try:
            prices = [p.sold_price for p in query.with_entities(Property.sold_price).all()]
            if not prices:
                return 0.0
            return float(np.median(prices))
        except Exception:
            return 0.0
    
    @staticmethod
    def _get_price_distribution(query) -> Dict:
        """Get price distribution in ranges."""
        try:
            price_ranges = {
                '0-300k': 0,
                '300k-500k': 0,
                '500k-750k': 0,
                '750k-1M': 0,
                '1M+': 0
            }
            
            properties = query.with_entities(Property.sold_price).all()
            
            for prop in properties:
                price = prop.sold_price
                if price < 300000:
                    price_ranges['0-300k'] += 1
                elif price < 500000:
                    price_ranges['300k-500k'] += 1
                elif price < 750000:
                    price_ranges['500k-750k'] += 1
                elif price < 1000000:
                    price_ranges['750k-1M'] += 1
                else:
                    price_ranges['1M+'] += 1
            
            return price_ranges
            
        except Exception as e:
            logger.error(f"Error calculating price distribution: {str(e)}")
            return {}
    
    @staticmethod
    # @cache.memoize(timeout=7200)  # Cache for 2 hours
    def get_neighborhood_insights(city: str, neighborhood: str = None) -> Dict:
        """Get detailed neighborhood insights and comparisons."""
        try:
            base_query = db.session.query(Property).filter(
                Property.city.ilike(f'%{city}%')
            )
            
            if neighborhood:
                base_query = base_query.filter(
                    Property.neighborhood.ilike(f'%{neighborhood}%')
                )
            
            # Neighborhood statistics
            neighborhoods = db.session.query(
                Property.neighborhood,
                func.count(Property.listing_id).label('property_count'),
                func.avg(Property.sold_price).label('avg_price'),
                func.avg(Property.sqft).label('avg_sqft'),
                func.avg(Property.bedrooms).label('avg_bedrooms'),
                func.avg(Property.bathrooms).label('avg_bathrooms')
            ).filter(Property.city.ilike(f'%{city}%')).group_by(
                Property.neighborhood
            ).having(func.count(Property.listing_id) >= 5).all()  # Min 5 properties
            
            neighborhood_data = []
            for n in neighborhoods:
                data = {
                    'neighborhood': n.neighborhood,
                    'property_count': n.property_count,
                    'avg_price': float(n.avg_price),
                    'avg_sqft': float(n.avg_sqft or 0),
                    'avg_bedrooms': float(n.avg_bedrooms or 0),
                    'avg_bathrooms': float(n.avg_bathrooms or 0),
                    'price_per_sqft': float(n.avg_price / (n.avg_sqft or 1))
                }
                neighborhood_data.append(data)
            
            # Sort by average price
            neighborhood_data.sort(key=lambda x: x['avg_price'], reverse=True)
            
            return {
                'city': city,
                'neighborhoods': neighborhood_data,
                'total_neighborhoods': len(neighborhood_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting neighborhood insights: {str(e)}")
            return {}
    
    @staticmethod
    # @cache.memoize(timeout=3600)
    def get_market_trends_analysis(days: int = 90) -> Dict:
        """Analyze market trends over specified period."""
        try:
            # Simplified market trends analysis using property data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Basic market analysis from property transactions
            recent_sales = db.session.query(Property).filter(
                Property.sold_date >= start_date.date()
            ).all()
            
            if not recent_sales:
                return {}
            
            avg_price = np.mean([float(p.sold_price) for p in recent_sales if p.sold_price])
            avg_dom = np.mean([p.dom for p in recent_sales if p.dom])
            
            return {
                'analysis': {
                    'avg_price': avg_price,
                    'avg_days_on_market': avg_dom,
                    'total_sales': len(recent_sales),
                    'market_condition': 'Balanced Market'  # Simplified for now
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {str(e)}")
            return {}
    
    @staticmethod
    def _determine_market_condition(inventory_level: float, avg_dom: float) -> str:
        """Determine market condition based on trend data."""
        if inventory_level < 3 and avg_dom < 30:
            return "Seller's Market"
        elif inventory_level > 6 and avg_dom > 60:
            return "Buyer's Market"
        else:
            return "Balanced Market"
    
    @staticmethod
    def get_comparable_properties(property_id: int, limit: int = 5) -> List[Dict]:
        """Find comparable properties for valuation."""
        try:
            target_property = Property.query.get(property_id)
            if not target_property:
                return []
            
            # Find similar properties
            comparables = db.session.query(Property).filter(
                and_(
                    Property.listing_id != property_id,
                    Property.city == target_property.city,
                    Property.property_type == target_property.property_type,
                    Property.bedrooms.between(
                        target_property.bedrooms - 1,
                        target_property.bedrooms + 1
                    ),
                    Property.sqft.between(
                        target_property.sqft * 0.8,
                        target_property.sqft * 1.2
                    ) if target_property.sqft else True
                )                ).order_by(
                func.abs(Property.sold_price - target_property.sold_price)
            ).limit(limit).all()
            
            return [comp.to_dict() for comp in comparables]
            
        except Exception as e:
            logger.error(f"Error finding comparable properties: {str(e)}")
            return []
    
    @staticmethod
    def export_market_data(city: str = None, format: str = 'csv') -> str:
        """Export market data to specified format."""
        try:
            query = db.session.query(Property)
            if city:
                query = query.filter(Property.city.ilike(f'%{city}%'))
            
            properties = query.all()
            
            # Convert to DataFrame
            data = []
            for prop in properties:
                data.append({
                    'id': prop.id,
                    'address': prop.address,
                    'city': prop.city,
                    'province': prop.province,
                    'postal_code': prop.postal_code,
                    'price': prop.price,
                    'property_type': prop.property_type,
                    'bedrooms': prop.bedrooms,
                    'bathrooms': prop.bathrooms,
                    'square_feet': prop.square_feet,
                    'year_built': prop.year_built,
                    'listing_date': prop.listing_date,
                    'status': prop.status
                })
            
            df = pd.DataFrame(data)
            
            # Export based on format
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"market_data_{city or 'all'}_{timestamp}"
            
            format = format or 'csv'  # Default to csv if format is None
            if format.lower() == 'csv':
                filepath = f"/Users/efeobukohwo/Desktop/Nextproperty Real Estate/data/exports/{filename}.csv"
                df.to_csv(filepath, index=False)
            elif format.lower() == 'json':
                filepath = f"/Users/efeobukohwo/Desktop/Nextproperty Real Estate/data/exports/{filename}.json"
                df.to_json(filepath, orient='records', date_format='iso')
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting market data: {str(e)}")
            raise
    
    @staticmethod
    # @cache.memoize(timeout=1800)  # Cache for 30 minutes
    def get_market_summary() -> Dict:
        """Get a comprehensive market summary with key statistics."""
        try:
            # Get basic market statistics
            total_properties = db.session.query(Property).count()
            
            if total_properties == 0:
                return {
                    'total_properties': 0,
                    'avg_price': 0,
                    'median_price': 0,
                    'avg_sqft': 0,
                    'avg_dom': 0,
                    'market_condition': 'No Data Available'
                }
            
            # Calculate key metrics
            avg_price = db.session.query(func.avg(Property.sold_price)).scalar() or 0
            avg_sqft = db.session.query(func.avg(Property.sqft)).scalar() or 0
            
            # Calculate median price
            prices = [p.sold_price for p in db.session.query(Property.sold_price).all() if p.sold_price]
            median_price = float(np.median(prices)) if prices else 0
            
            # Calculate average days on market (simplified)
            properties_with_dom = db.session.query(Property).filter(Property.dom.isnot(None)).all()
            avg_dom = np.mean([p.dom for p in properties_with_dom]) if properties_with_dom else 30
            
            # Determine market condition based on data
            if avg_dom < 20:
                market_condition = "Hot Market"
            elif avg_dom < 40:
                market_condition = "Balanced Market"
            else:
                market_condition = "Buyer's Market"
            
            return {
                'total_properties': total_properties,
                'avg_price': float(avg_price),
                'median_price': median_price,
                'avg_sqft': float(avg_sqft),
                'avg_dom': float(avg_dom),
                'market_condition': market_condition
            }
            
        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return {
                'total_properties': 0,
                'avg_price': 0,
                'median_price': 0,
                'avg_sqft': 0,
                'avg_dom': 0,
                'market_condition': 'Error Loading Data'
            }
    
    @staticmethod
    # @cache.memoize(timeout=3600)  # Cache for 1 hour
    def get_top_cities(limit: int = 10) -> List[Dict]:
        """Get top cities by property count and market activity."""
        try:
            # Get cities with most properties
            cities = db.session.query(
                Property.city,
                func.count(Property.listing_id).label('property_count'),
                func.avg(Property.sold_price).label('avg_price'),
                func.avg(Property.sqft).label('avg_sqft')
            ).filter(
                Property.city.isnot(None)
            ).group_by(Property.city).order_by(
                func.count(Property.listing_id).desc()
            ).limit(limit).all()
            
            city_data = []
            for city in cities:
                city_info = {
                    'city': city.city,
                    'property_count': city.property_count,
                    'avg_price': float(city.avg_price or 0),
                    'avg_sqft': float(city.avg_sqft or 0),
                    'price_per_sqft': float((city.avg_price or 0) / (city.avg_sqft or 1))
                }
                city_data.append(city_info)
            
            return city_data
            
        except Exception as e:
            logger.error(f"Error getting top cities: {str(e)}")
            return []
    
    @staticmethod
    # @cache.memoize(timeout=3600)  # Cache for 1 hour
    def get_unique_cities(limit: int = None) -> List[str]:
        """Get unique cities from properties."""
        try:
            query = db.session.query(Property.city.distinct()).filter(
                Property.city.isnot(None),
                Property.city != '',
                Property.city != 'NULL'
            ).order_by(Property.city)
            
            if limit:
                query = query.limit(limit)
            
            results = query.all()
            return [city[0] for city in results if city[0]]
            
        except Exception as e:
            logger.error(f"Error getting unique cities: {str(e)}")
            return []
    
    @staticmethod
    # @cache.memoize(timeout=3600)  # Cache for 1 hour
    def get_property_types() -> List[str]:
        """Get unique property types from properties."""
        try:
            results = db.session.query(Property.property_type.distinct()).filter(
                Property.property_type.isnot(None),
                Property.property_type != '',
                Property.property_type != 'NULL'
            ).order_by(Property.property_type).all()
            
            return [prop_type[0] for prop_type in results if prop_type[0]]
            
        except Exception as e:
            logger.error(f"Error getting property types: {str(e)}")
            return []
    
    @staticmethod
    # @cache.memoize(timeout=1800)  # Cache for 30 minutes
    def get_price_statistics() -> Dict:
        """Get price statistics for form suggestions."""
        try:
            # Use basic stats query that works with SQLite
            basic_stats = db.session.query(
                func.min(Property.sold_price).label('min_price'),
                func.max(Property.sold_price).label('max_price'),
                func.avg(Property.sold_price).label('avg_price'),
                func.count(Property.sold_price).label('count')
            ).filter(Property.sold_price.isnot(None)).first()
            
            # Calculate percentiles manually for SQLite compatibility
            # Get all prices sorted
            prices_query = db.session.query(Property.sold_price)\
                .filter(Property.sold_price.isnot(None))\
                .order_by(Property.sold_price)
            
            prices = [p[0] for p in prices_query.all()]
            
            q1_price = 0
            q3_price = 0
            if prices:
                import numpy as np
                q1_price = float(np.percentile(prices, 25))
                q3_price = float(np.percentile(prices, 75))
            
            return {
                'min_price': float(basic_stats.min_price) if basic_stats.min_price else 0,
                'max_price': float(basic_stats.max_price) if basic_stats.max_price else 0,
                'avg_price': float(basic_stats.avg_price) if basic_stats.avg_price else 0,
                'q1_price': q1_price,
                'q3_price': q3_price,
                'suggested_ranges': [
                    {'label': 'Under $300K', 'min': 0, 'max': 300000},
                    {'label': '$300K - $500K', 'min': 300000, 'max': 500000},
                    {'label': '$500K - $750K', 'min': 500000, 'max': 750000},
                    {'label': '$750K - $1M', 'min': 750000, 'max': 1000000},
                    {'label': 'Over $1M', 'min': 1000000, 'max': None}
                ]
            }
        except Exception as e:
            logger.error(f"Error getting price statistics: {str(e)}")
            return {
                'min_price': 0,
                'max_price': 0,
                'avg_price': 0,
                'q1_price': 0,
                'q3_price': 0,
                'suggested_ranges': []
            }
