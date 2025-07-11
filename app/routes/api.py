from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db, cache
from app.extensions import limiter
from app.models.property import Property, PropertyPhoto, PropertyRoom
from app.models.agent import Agent
from app.models.economic_data import EconomicData, EconomicIndicator
from app.services.ml_service import MLService
from app.services.data_service import DataService
from app.services.geospatial_service import GeospatialService
from app.security.middleware import csrf_protect, xss_protect
from app.security.rate_limiter import rate_limit
# from app.utils.helpers import validate_request_args, paginate_query  # TODO: Implement these functions
from sqlalchemy import func, text
import json
from datetime import datetime, timedelta

bp = Blueprint('api', __name__)

# Initialize services
ml_service = MLService()
data_service = DataService()
geo_service = GeospatialService()

@bp.route('/health', methods=['GET'])
@cache.cached(timeout=60)
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Simple database check
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'nextproperty-ai',
            'version': '1.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@bp.route('/statistics', methods=['GET'])
@limiter.limit("50 per hour")
@cache.cached(timeout=300)
def get_statistics():
    """Get general platform statistics."""
    try:
        total_properties = Property.query.count()
        total_agents = Agent.query.count()
        
        # Get average price
        avg_price = db.session.query(func.avg(Property.original_price)).scalar() or 0
        
        # Get property types distribution
        property_types = db.session.query(
            Property.property_type,
            func.count(Property.listing_id)
        ).group_by(Property.property_type).all()
        
        return jsonify({
            'total_properties': total_properties,
            'total_agents': total_agents,
            'average_price': round(avg_price, 2),
            'property_types': dict(property_types),
            'updated_at': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Statistics error: {e}")
        return jsonify({'error': 'Failed to fetch statistics'}), 500

@bp.route('/agents', methods=['GET'])
@limiter.limit("100 per hour")
@cache.cached(timeout=300, query_string=True)
def get_agents():
    """Get list of agents."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        agents = Agent.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'agents': [{
                'id': agent.id,
                'name': agent.name,
                'email': agent.email,
                'phone': agent.phone,
                'properties_count': agent.properties.count() if hasattr(agent, 'properties') else 0
            } for agent in agents.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': agents.total,
                'pages': agents.pages
            }
        })
    except Exception as e:
        current_app.logger.error(f"Agents error: {e}")
        return jsonify({'error': 'Failed to fetch agents'}), 500

@bp.route('/cities', methods=['GET'])
@limiter.limit("100 per hour")
@cache.cached(timeout=600)
def get_cities():
    """Get list of cities with property counts."""
    try:
        cities = db.session.query(
            Property.city,
            func.count(Property.listing_id).label('property_count'),
            func.avg(Property.original_price).label('avg_price')
        ).filter(
            Property.city.isnot(None)
        ).group_by(Property.city).order_by(
            func.count(Property.listing_id).desc()
        ).limit(100).all()
        
        return jsonify({
            'cities': [{
                'name': city[0],
                'property_count': city[1],
                'average_price': round(city[2] or 0, 2)
            } for city in cities]
        })
    except Exception as e:
        current_app.logger.error(f"Cities error: {e}")
        return jsonify({'error': 'Failed to fetch cities'}), 500

@bp.route('/market-data', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=300, query_string=True)
def get_market_data():
    """Get market data and trends."""
    try:
        city = request.args.get('city')
        
        query = Property.query
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))
        
        # Get price statistics
        price_stats = db.session.query(
            func.min(Property.original_price).label('min_price'),
            func.max(Property.original_price).label('max_price'),
            func.avg(Property.original_price).label('avg_price'),
            func.count(Property.listing_id).label('total_properties')
        ).filter(query.whereclause).first()
        
        # Get recent listings
        recent_count = query.filter(
            Property.sold_date >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        return jsonify({
            'market_summary': {
                'min_price': price_stats.min_price or 0,
                'max_price': price_stats.max_price or 0,
                'average_price': round(price_stats.avg_price or 0, 2),
                'total_properties': price_stats.total_properties or 0,
                'recent_listings_30d': recent_count
            },
            'city': city,
            'updated_at': datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Market data error: {e}")
        return jsonify({'error': 'Failed to fetch market data'}), 500

@bp.route('/properties', methods=['GET'])
@limiter.limit("100 per hour")
@cache.cached(timeout=300, query_string=True)
def get_properties():
    """Get filtered property listings."""
    try:
        # Get query parameters
        city = request.args.get('city')
        property_type = request.args.get('type')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Build query
        query = Property.query
        
        # Apply filters
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))
        if property_type:
            query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
        if min_price:
            query = query.filter(
                db.or_(
                    Property.original_price >= min_price,
                    Property.sold_price >= min_price
                )
            )
        if max_price:
            query = query.filter(
                db.or_(
                    Property.original_price <= max_price,
                    Property.sold_price <= max_price
                )
            )
        
        # Order by most recent
        query = query.order_by(Property.sold_date.desc())
        
        # Paginate
        properties = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [prop.to_dict() for prop in properties.items],
            'pagination': {
                'page': properties.page,
                'per_page': properties.per_page,
                'total': properties.total,
                'pages': properties.pages,
                'has_next': properties.has_next,
                'has_prev': properties.has_prev
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching properties: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/properties/<string:listing_id>', methods=['GET'])
@cache.cached(timeout=600)
def get_property(listing_id):
    """Get single property by listing ID."""
    try:
        property = Property.query.filter_by(listing_id=listing_id).first()
        
        if not property:
            return jsonify({'success': False, 'error': 'Property not found'}), 404
        
        return jsonify({
            'success': True,
            'data': property.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching property {listing_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/properties/<string:listing_id>/photos', methods=['GET'])
@cache.cached(timeout=3600)
def get_property_photos(listing_id):
    """Get property photos."""
    try:
        property = Property.query.filter_by(listing_id=listing_id).first()
        
        if not property:
            return jsonify({'success': False, 'error': 'Property not found'}), 404
        
        photos = PropertyPhoto.query.filter_by(listing_id=listing_id)\
                                 .order_by(PropertyPhoto.order_index)\
                                 .all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': photo.id,
                'photo_url': photo.photo_url,
                'photo_type': photo.photo_type,
                'caption': photo.caption,
                'order_index': photo.order_index
            } for photo in photos]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching photos for {listing_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/properties/<string:listing_id>/rooms', methods=['GET'])
@cache.cached(timeout=3600)
def get_property_rooms(listing_id):
    """Get property room details."""
    try:
        property = Property.query.filter_by(listing_id=listing_id).first()
        
        if not property:
            return jsonify({'success': False, 'error': 'Property not found'}), 404
        
        rooms = PropertyRoom.query.filter_by(listing_id=listing_id).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': room.id,
                'room_type': room.room_type,
                'level': room.level,
                'dimensions': room.dimensions,
                'features': room.features
            } for room in rooms]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching rooms for {listing_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/properties/<string:listing_id>/analyze', methods=['POST'])
@csrf_protect
@xss_protect
def analyze_property(listing_id):
    """Get AI analysis for a property."""
    try:
        property = Property.query.filter_by(listing_id=listing_id).first()
        
        if not property:
            return jsonify({'success': False, 'error': 'Property not found'}), 404
        
        # Get ML predictions
        analysis = ml_service.analyze_property(property)
        
        # Update property with AI analysis
        property.ai_valuation = analysis.get('predicted_price')
        property.investment_score = analysis.get('investment_score')
        property.risk_assessment = analysis.get('risk_level')
        property.market_trend = analysis.get('market_trend')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'listing_id': listing_id,
                'analysis': analysis
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing property {listing_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/agents/<string:agent_id>', methods=['GET'])
@cache.cached(timeout=1800)
def get_agent(agent_id):
    """Get agent details."""
    try:
        agent = Agent.query.filter_by(agent_id=agent_id).first()
        
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        return jsonify({
            'success': True,
            'data': agent.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching agent {agent_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/agents/<string:agent_id>/properties', methods=['GET'])
@cache.cached(timeout=900, query_string=True)
def get_agent_properties(agent_id):
    """Get agent's property listings."""
    try:
        agent = Agent.query.filter_by(agent_id=agent_id).first()
        
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        properties = Property.query.filter_by(agent_id=agent_id)\
                                 .order_by(Property.sold_date.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [prop.to_dict() for prop in properties.items],
            'pagination': {
                'page': properties.page,
                'per_page': properties.per_page,
                'total': properties.total,
                'pages': properties.pages
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching properties for agent {agent_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/search', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=300, query_string=True)
def search_properties():
    """Advanced property search."""
    try:
        query_text = request.args.get('q', '')
        city = request.args.get('city')
        property_type = request.args.get('type')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        bedrooms = request.args.get('bedrooms', type=int)
        bathrooms = request.args.get('bathrooms', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Start with base query
        query = Property.query
        
        # Apply text search if provided
        if query_text:
            query = query.filter(
                db.or_(
                    Property.features.contains(query_text),
                    Property.community_features.contains(query_text),
                    Property.remarks.contains(query_text),
                    Property.address.contains(query_text)
                )
            )
        
        # Apply filters
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))
        if property_type:
            query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
        if min_price:
            query = query.filter(
                db.or_(
                    Property.original_price >= min_price,
                    Property.sold_price >= min_price
                )
            )
        if max_price:
            query = query.filter(
                db.or_(
                    Property.original_price <= max_price,
                    Property.sold_price <= max_price
                )
            )
        if bedrooms:
            query = query.filter(Property.bedrooms >= bedrooms)
        if bathrooms:
            query = query.filter(Property.bathrooms >= bathrooms)
        
        # Order by relevance (sold_date for now)
        query = query.order_by(Property.sold_date.desc())
        
        # Paginate
        properties = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': [prop.to_dict() for prop in properties.items],
            'pagination': {
                'page': properties.page,
                'per_page': properties.per_page,
                'total': properties.total,
                'pages': properties.pages
            },
            'search_params': {
                'query': query_text,
                'city': city,
                'property_type': property_type,
                'min_price': min_price,
                'max_price': max_price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in property search: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/search/geospatial', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def geospatial_search():
    """Location-based property search."""
    try:
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lng', type=float)
        radius = request.args.get('radius', 5, type=float)  # km
        
        if not latitude or not longitude:
            return jsonify({'success': False, 'error': 'Latitude and longitude required'}), 400
        
        # Get nearby properties
        properties = geo_service.find_properties_within_radius(latitude, longitude, radius)
        
        return jsonify({
            'success': True,
            'data': properties,
            'search_center': {
                'latitude': latitude,
                'longitude': longitude,
                'radius_km': radius
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in geospatial search: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/market/trends', methods=['GET'])
@cache.cached(timeout=3600)
def get_market_trends():
    """Get market trends and statistics."""
    try:
        city = request.args.get('city')
        property_type = request.args.get('type')
        months = request.args.get('months', 12, type=int)
        
        trends = data_service.get_market_trends(city, property_type, months)
        
        return jsonify({
            'success': True,
            'data': trends
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching market trends: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/market/economic-indicators', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=3600)
def get_economic_indicators():
    """Get economic indicators."""
    try:
        source = request.args.get('source')  # BOC or STATCAN
        category = request.args.get('category')
        limit = request.args.get('limit', 20, type=int)
        
        indicators = EconomicIndicator.get_active_indicators(source, category)[:limit]
        
        # Get latest values for each indicator
        indicator_data = []
        for indicator in indicators:
            latest_data = EconomicData.get_latest_value(indicator.indicator_code)
            indicator_dict = indicator.to_dict()
            indicator_dict['latest_value'] = latest_data.to_dict() if latest_data else None
            indicator_data.append(indicator_dict)
        
        return jsonify({
            'success': True,
            'data': indicator_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching economic indicators: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/market/predictions', methods=['GET'])
@limiter.exempt
@cache.cached(timeout=1800, query_string=True)
def get_market_predictions():
    """Get market predictions."""
    try:
        city = request.args.get('city')
        property_type = request.args.get('type')
        horizon = request.args.get('horizon', 6, type=int)  # months
        
        predictions = ml_service.predict_market_trends(city, property_type, horizon)
        
        return jsonify({
            'success': True,
            'data': predictions
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating predictions: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/stats/summary', methods=['GET'])
@cache.cached(timeout=1800)
def get_stats_summary():
    """Get platform statistics summary."""
    try:
        # Get basic statistics
        total_properties = Property.query.count()
        total_agents = Agent.query.filter_by(is_active=True).count()
        
        # Recent activity
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_properties = Property.query.filter(Property.created_at >= recent_date).count()
        
        # Price statistics
        price_stats = db.session.query(
            func.avg(Property.sold_price).label('avg_price'),
            func.min(Property.sold_price).label('min_price'),
            func.max(Property.sold_price).label('max_price')
        ).filter(Property.sold_price.isnot(None)).first()
        
        # City distribution
        city_stats = db.session.query(
            Property.city,
            func.count(Property.listing_id).label('count')
        ).group_by(Property.city)\
         .order_by(func.count(Property.listing_id).desc())\
         .limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_properties': total_properties,
                'total_agents': total_agents,
                'recent_properties': recent_properties,
                'price_statistics': {
                    'average_price': float(price_stats.avg_price) if price_stats.avg_price else 0,
                    'min_price': float(price_stats.min_price) if price_stats.min_price else 0,
                    'max_price': float(price_stats.max_price) if price_stats.max_price else 0
                },
                'top_cities': [{'city': city, 'count': count} for city, count in city_stats]
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching stats summary: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/property-prediction', methods=['POST'])
@limiter.exempt
@csrf_protect
@xss_protect
def predict_property_price():
    """API endpoint for property price prediction."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['bedrooms', 'bathrooms', 'square_feet', 'property_type', 'city', 'province']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Get prediction
        prediction_result = ml_service.predict_property_price(data)
        
        if prediction_result.get('error'):
            return jsonify({
                'success': False,
                'error': prediction_result['error']
            }), 500
        
        return jsonify({
            'success': True,
            'prediction': prediction_result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in property prediction API: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/property-prediction/<string:listing_id>')
def get_property_prediction(listing_id):
    """Get AI prediction for an existing property."""
    try:
        property_obj = Property.query.filter_by(listing_id=listing_id).first()
        
        if not property_obj:
            return jsonify({'success': False, 'error': 'Property not found'}), 404
        
        # Check if we already have an AI valuation
        if property_obj.ai_valuation:
            return jsonify({
                'success': True,
                'prediction': {
                    'predicted_price': float(property_obj.ai_valuation),
                    'confidence': 0.8,
                    'confidence_interval': {
                        'lower': float(property_obj.ai_valuation) * 0.85,
                        'upper': float(property_obj.ai_valuation) * 1.15
                    },
                    'cached': True
                }
            })
        
        # Generate new prediction
        property_features = {
            'bedrooms': property_obj.bedrooms or 3,
            'bathrooms': property_obj.bathrooms or 2,
            'square_feet': property_obj.sqft or 1500,
            'lot_size': property_obj.lot_size or 0,
            'year_built': 2020,  # Default if not available
            'property_type': property_obj.property_type or 'Detached',
            'city': property_obj.city or 'Toronto',
            'province': property_obj.province or 'ON',
            'postal_code': property_obj.postal_code or 'M1M1M1'
        }
        
        prediction_result = ml_service.predict_property_price(property_features)
        
        if prediction_result.get('error'):
            return jsonify({
                'success': False,
                'error': prediction_result['error']
            }), 500
        
        # Save the AI valuation to the property
        property_obj.ai_valuation = prediction_result['predicted_price']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prediction': prediction_result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting property prediction: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/properties/bulk-analyze', methods=['POST'])
def bulk_analyze_properties():
    """Analyze multiple properties and generate AI predictions."""
    try:
        # Get properties without AI valuation or need update
        properties_to_analyze = Property.query.filter(
            db.or_(
                Property.ai_valuation.is_(None),
                Property.investment_score.is_(None)
            ),
            Property.bedrooms.isnot(None)
        ).limit(100).all()
        
        analyzed_count = 0
        
        for property_obj in properties_to_analyze:
            try:
                # Generate prediction
                property_features = {
                    'bedrooms': property_obj.bedrooms or 3,
                    'bathrooms': property_obj.bathrooms or 2,
                    'square_feet': property_obj.sqft or 1500,
                    'lot_size': property_obj.lot_size or 0,
                    'year_built': 2020,
                    'property_type': property_obj.property_type or 'Detached',
                    'city': property_obj.city or 'Toronto',
                    'province': property_obj.province or 'ON',
                    'postal_code': property_obj.postal_code or 'M1M1M1'
                }
                
                prediction_result = ml_service.predict_property_price(property_features)
                
                if not prediction_result.get('error'):
                    # Update property with AI analysis
                    analysis = ml_service.analyze_property(property_obj)
                    property_obj.ai_valuation = prediction_result['predicted_price']
                    property_obj.investment_score = analysis.get('investment_score')
                    property_obj.risk_assessment = analysis.get('risk_level')
                    property_obj.market_trend = analysis.get('market_trend')
                    analyzed_count += 1
                    
            except Exception as prop_error:
                current_app.logger.warning(f"Error analyzing property {property_obj.listing_id}: {str(prop_error)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analyzed_count': analyzed_count,
            'total_processed': len(properties_to_analyze)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk analysis: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500


@bp.route('/top-deals')
@cache.cached(timeout=1800, query_string=True)
def get_top_deals():
    """Get top property deals (undervalued properties)."""
    try:
        limit = request.args.get('limit', 20, type=int)
        city = request.args.get('city')
        property_type = request.args.get('type')
        
        top_properties = ml_service.get_top_properties(
            limit=min(limit, 50),
            location=city,
            property_type=property_type
        )
        
        # Format response
        deals = []
        for item in top_properties:
            property_obj = item['property']
            analysis = item['analysis']
            
            deals.append({
                'listing_id': property_obj.listing_id,
                'address': property_obj.address,
                'city': property_obj.city,
                'property_type': property_obj.property_type,
                'bedrooms': property_obj.bedrooms,
                'bathrooms': property_obj.bathrooms,
                'sqft': property_obj.sqft,
                'actual_price': float(property_obj.sold_price) if property_obj.sold_price else None,
                'predicted_price': item['predicted_price'],
                'value_difference': item['value_difference'],
                'value_difference_percent': item['value_difference_percent'],
                'investment_potential': item['investment_potential'],
                'investment_score': analysis.get('investment_score'),
                'risk_level': analysis.get('risk_level')
            })
        
        return jsonify({
            'success': True,
            'deals': deals,
            'count': len(deals)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting top deals: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Error handlers for API blueprint
@bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@bp.errorhandler(400)
def api_bad_request(error):
    return jsonify({'success': False, 'error': 'Bad request'}), 400

@bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# Model Management Endpoints
@bp.route('/model/status')
def get_model_status():
    """Get current ML model status and performance metrics."""
    try:
        validation = ml_service.validate_model_performance()
        metadata = ml_service.get_model_metadata()
        
        return jsonify({
            'success': True,
            'model_status': validation,
            'metadata': metadata,
            'retrain_recommended': ml_service.retrain_recommended()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/model/available')
def get_available_models():
    """Get list of available trained models with performance comparison."""
    try:
        models = ml_service.get_available_models()
        comparison = ml_service.get_model_comparison()
        
        return jsonify({
            'success': True,
            'available_models': models,
            'comparison': comparison
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/model/switch', methods=['POST'])
def switch_model():
    """Switch to a different trained model."""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'Model name is required'
            }), 400
        
        success = ml_service.switch_model(model_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully switched to {model_name}',
                'current_model': model_name
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to switch to {model_name}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/model/test', methods=['POST'])
def test_model():
    """Test the current model with provided property features."""
    try:
        data = request.get_json()
        
        # Use provided features or default test features
        test_features = data.get('features', {
            'bedrooms': 3,
            'bathrooms': 2,
            'square_feet': 2000,
            'lot_size': 0.5,
            'year_built': 2015,
            'property_type': 'Detached',
            'city': 'Toronto',
            'province': 'ON',
            'dom': 25,
            'taxes': 8000
        })
        
        # Make prediction
        result = ml_service.predict_property_price(test_features)
        
        return jsonify({
            'success': True,
            'test_features': test_features,
            'prediction_result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/model/performance-history')
def get_model_performance_history():
    """Get historical performance data for all models."""
    try:
        metadata = ml_service.get_model_metadata()
        all_models = metadata.get('all_models_performance', {})
        
        # Format for charting
        performance_data = []
        for model_name, metrics in all_models.items():
            performance_data.append({
                'model': model_name,
                'r2_score': metrics.get('r2', 0),
                'rmse': metrics.get('rmse', 0),
                'mae': metrics.get('mae', 0),
                'mape': metrics.get('mape', 0),
                'training_time': metrics.get('training_time', 0)
            })
        
        # Sort by R² score
        performance_data.sort(key=lambda x: x['r2_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'performance_data': performance_data,
            'best_model': metadata.get('best_model'),
            'training_info': metadata.get('training_info', {})
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/analytics/real-time-updates', methods=['GET'])
@limiter.limit("20 per minute")
def get_real_time_analytics():
    """Get real-time analytics updates for the dashboard."""
    try:
        # Check if we should force refresh (bypass cache)
        force_refresh = request.args.get('force_refresh', '').lower() == 'true'
        
        # If force refresh, clear relevant caches first
        if force_refresh:
            try:
                cache.delete('analytics_real_time_updates')
                cache.delete('market_summary')
                cache.delete('stats_summary')
            except:
                pass  # Ignore cache errors
        
        # Try to get from cache first (unless forced refresh)
        cache_key = 'analytics_real_time_updates'
        if not force_refresh:
            cached_data = cache.get(cache_key)
            if cached_data:
                return jsonify({
                    'success': True,
                    'timestamp': datetime.utcnow().isoformat(),
                    'data': cached_data,
                    'cached': True
                })
        
        # Get recent activity (last 24 hours)
        recent_date = datetime.utcnow() - timedelta(hours=24)
        
        # Recent properties count
        recent_properties = Property.query.filter(Property.created_at >= recent_date).count()
        
        # Properties requiring AI analysis
        properties_needing_analysis = Property.query.filter(
            db.or_(
                Property.ai_valuation.is_(None),
                Property.investment_score.is_(None)
            )
        ).count()
        
        # Get city distribution with all cities having properties
        city_stats = db.session.query(
            Property.city,
            Property.province,
            func.count(Property.listing_id).label('property_count'),
            func.avg(
                func.coalesce(Property.sold_price, Property.original_price)
            ).label('avg_price'),
            func.min(
                func.coalesce(Property.sold_price, Property.original_price)
            ).label('min_price'),
            func.max(
                func.coalesce(Property.sold_price, Property.original_price)
            ).label('max_price')
        ).filter(
            Property.city.isnot(None),
            Property.province.isnot(None),
            db.or_(
                Property.sold_price.isnot(None),
                Property.original_price.isnot(None)
            )
        ).group_by(Property.city, Property.province)\
         .having(func.count(Property.listing_id) >= 1)\
         .order_by(func.count(Property.listing_id).desc()).all()
        
        # Get market trends for top cities
        market_trends = []
        for city_stat in city_stats[:20]:  # Top 20 cities
            city_name = city_stat.city
            province = city_stat.province
            
            # Get 30-day trend
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_city_properties = Property.query.filter(
                Property.city == city_name,
                Property.province == province,
                Property.sold_date >= thirty_days_ago,
                db.or_(
                    Property.sold_price.isnot(None),
                    Property.original_price.isnot(None)
                )
            ).count()
            
            market_trends.append({
                'city': city_name,
                'province': province,
                'total_properties': city_stat.property_count,
                'avg_price': round(float(city_stat.avg_price), 2) if city_stat.avg_price else 0,
                'min_price': float(city_stat.min_price) if city_stat.min_price else 0,
                'max_price': float(city_stat.max_price) if city_stat.max_price else 0,
                'recent_activity': recent_city_properties,
                'market_activity': 'High' if recent_city_properties > 5 else 'Moderate' if recent_city_properties > 2 else 'Low'
            })
        
        # Get property type distribution
        type_distribution = db.session.query(
            Property.property_type,
            func.count(Property.listing_id).label('count'),
            func.avg(
                func.coalesce(Property.sold_price, Property.original_price)
            ).label('avg_price')
        ).filter(
            Property.property_type.isnot(None),
            db.or_(
                Property.sold_price.isnot(None),
                Property.original_price.isnot(None)
            )
        ).group_by(Property.property_type)\
         .order_by(func.count(Property.listing_id).desc()).all()
        
        # Get price range distribution using raw SQL for MySQL compatibility
        price_ranges_query = text("""
            SELECT 
                CASE 
                    WHEN COALESCE(sold_price, original_price) < 300000 THEN 'Under $300K'
                    WHEN COALESCE(sold_price, original_price) < 500000 THEN '$300K - $500K'
                    WHEN COALESCE(sold_price, original_price) < 750000 THEN '$500K - $750K'
                    WHEN COALESCE(sold_price, original_price) < 1000000 THEN '$750K - $1M'
                    WHEN COALESCE(sold_price, original_price) < 1500000 THEN '$1M - $1.5M'
                    ELSE 'Over $1.5M'
                END as price_range,
                COUNT(listing_id) as count
            FROM properties 
            WHERE COALESCE(sold_price, original_price) IS NOT NULL 
            GROUP BY price_range 
            ORDER BY count DESC
        """)
        price_ranges = db.session.execute(price_ranges_query).fetchall()
        
        # Overall market statistics
        total_properties = Property.query.count()
        total_analyzed = Property.query.filter(Property.ai_valuation.isnot(None)).count()
        analysis_percentage = round((total_analyzed / total_properties * 100), 2) if total_properties > 0 else 0
        
        # Average prices by province
        province_stats = db.session.query(
            Property.province,
            func.count(Property.listing_id).label('count'),
            func.avg(
                func.coalesce(Property.sold_price, Property.original_price)
            ).label('avg_price')
        ).filter(
            Property.province.isnot(None),
            db.or_(
                Property.sold_price.isnot(None),
                Property.original_price.isnot(None)
            )
        ).group_by(Property.province)\
         .having(func.count(Property.listing_id) >= 1)\
         .order_by(func.avg(func.coalesce(Property.sold_price, Property.original_price)).desc()).all()
        
        analytics_data = {
            'recent_activity': {
                'new_properties_24h': recent_properties,
                'properties_needing_analysis': properties_needing_analysis,
                'total_properties': total_properties,
                'analysis_completion': f"{analysis_percentage}%"
            },
            'market_overview': {
                'total_cities': len(city_stats),
                'total_provinces': len(province_stats),
                'active_markets': len([c for c in city_stats if c.property_count >= 5])
            },
            'city_insights': market_trends,
            'property_types': [
                {
                    'type': pt.property_type,
                    'count': pt.count,
                    'avg_price': round(float(pt.avg_price), 2) if pt.avg_price else 0
                }
                for pt in type_distribution
            ],
            'price_distribution': [
                {
                    'range': pr.price_range,
                    'count': pr.count
                }
                for pr in price_ranges
            ],
            'province_summary': [
                {
                    'province': ps.province,
                    'property_count': ps.count,
                    'avg_price': round(float(ps.avg_price), 2) if ps.avg_price else 0
                }
                for ps in province_stats
            ]
        }
        
        # Cache the data for 60 seconds
        cache.set(cache_key, analytics_data, timeout=60)
        
        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'data': analytics_data,
            'cached': False
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching real-time analytics: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@bp.route('/analytics/trigger-analysis', methods=['POST'])
@csrf_protect
@xss_protect
@login_required
def trigger_analytics_analysis():
    """Trigger analysis for properties that need AI valuation."""
    try:
        # Get properties that need analysis
        properties_to_analyze = Property.query.filter(
            db.or_(
                Property.ai_valuation.is_(None),
                Property.investment_score.is_(None)
            ),
            Property.bedrooms.isnot(None),
            Property.city.isnot(None)
        ).limit(50).all()  # Process in batches
        
        analyzed_count = 0
        errors = []
        
        for property_obj in properties_to_analyze:
            try:
                # Generate AI analysis
                analysis = ml_service.analyze_property(property_obj)
                
                if analysis and not analysis.get('error'):
                    property_obj.ai_valuation = analysis.get('predicted_price')
                    property_obj.investment_score = analysis.get('investment_score')
                    property_obj.risk_assessment = analysis.get('risk_level')
                    property_obj.market_trend = analysis.get('market_trend')
                    analyzed_count += 1
                    
            except Exception as prop_error:
                errors.append({
                    'listing_id': property_obj.listing_id,
                    'error': str(prop_error)
                })
                current_app.logger.warning(f"Error analyzing property {property_obj.listing_id}: {str(prop_error)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analyzed_count': analyzed_count,
            'total_processed': len(properties_to_analyze),
            'errors': errors[:5]  # Return first 5 errors only
        })
        
    except Exception as e:
        current_app.logger.error(f"Error triggering analysis: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
