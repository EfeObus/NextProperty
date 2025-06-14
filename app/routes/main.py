from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from app.extensions import db
from app.models.property import Property, PropertyPhoto
from app.models.user import SavedProperty, User
from app.services.ml_service import MLService
from app.services.data_service import DataService
from app.services.external_apis import ExternalAPIsService
from app.utils.validators import validate_property_photos
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os
import uuid

bp = Blueprint('main', __name__)

# Initialize services
ml_service = MLService()
data_service = DataService()
external_apis_service = ExternalAPIsService()

@bp.route('/')
def index():
    """Homepage with featured properties, top properties, and market overview."""
    try:
        # Get top properties (below AI prediction price - good deals)
        top_properties = ml_service.get_top_properties(limit=6)
        
        # Get featured properties (recent high-value properties)
        featured_properties = Property.query.filter(
            Property.sold_price.isnot(None)
        ).order_by(Property.sold_price.desc()).limit(6).all()
        
        # Get market statistics
        try:
            total_properties = Property.query.count()
            avg_price = db.session.query(func.avg(Property.sold_price)).filter(
                Property.sold_price.isnot(None)
            ).scalar()
            market_stats = {
                'total_properties': total_properties,
                'avg_price': float(avg_price) if avg_price else 0,
                'cities_covered': Property.query.with_entities(Property.city).distinct().count(),
                'ai_analyzed': Property.query.filter(Property.ai_valuation.isnot(None)).count()
            }
        except Exception as stats_error:
            current_app.logger.warning(f"Could not get market stats: {str(stats_error)}")
            market_stats = {
                'total_properties': 0,
                'avg_price': 0,
                'cities_covered': 0,
                'ai_analyzed': 0
            }
        
        # Get top cities by property count
        try:
            top_cities = db.session.query(
                Property.city,
                func.count(Property.listing_id).label('count'),
                func.avg(Property.sold_price).label('avg_price')
            ).filter(
                Property.city.isnot(None),
                Property.sold_price.isnot(None)
            ).group_by(Property.city).order_by(
                func.count(Property.listing_id).desc()
            ).limit(8).all()
        except Exception as cities_error:
            current_app.logger.warning(f"Could not get top cities: {str(cities_error)}")
            top_cities = []
        
        # Get market predictions summary
        try:
            market_predictions = ml_service.get_market_predictions()
        except Exception as pred_error:
            current_app.logger.warning(f"Could not get market predictions: {str(pred_error)}")
            market_predictions = {}
        
        return render_template('index.html',
                             top_properties=top_properties,
                             featured_properties=featured_properties,
                             market_stats=market_stats,
                             top_cities=top_cities,
                             market_predictions=market_predictions)
    
    except Exception as e:
        current_app.logger.error(f"Error loading homepage: {str(e)}")
        flash('Error loading data. Please try again.', 'error')
        # Return template with empty data to avoid undefined errors
        return render_template('index.html',
                             top_properties=[],
                             featured_properties=[],
                             market_stats={
                                 'total_properties': 0,
                                 'avg_price': 0,
                                 'cities_covered': 0,
                                 'ai_analyzed': 0
                             },
                             top_cities=[],
                             market_predictions={})


@bp.route('/properties')
def properties():
    """Property listings page with search and filter."""
    try:
        # Get search parameters
        city = request.args.get('city', '').strip()
        property_type = request.args.get('type', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        bedrooms = request.args.get('bedrooms', type=int)
        bathrooms = request.args.get('bathrooms', type=float)
        page = request.args.get('page', 1, type=int)
        
        # Build query
        query = Property.query
        
        # Apply filters
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))
        if property_type:
            query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
        if min_price:
            query = query.filter(Property.sold_price >= min_price)
        if max_price:
            query = query.filter(Property.sold_price <= max_price)
        if bedrooms:
            query = query.filter(Property.bedrooms >= bedrooms)
        if bathrooms:
            query = query.filter(Property.bathrooms >= bathrooms)
        
        # Order by most recent
        query = query.order_by(Property.sold_date.desc())
        
        # Paginate
        properties = query.paginate(
            page=page,
            per_page=current_app.config.get('PROPERTIES_PER_PAGE', 20),
            error_out=False
        )
        
        # Get filter options for dropdowns
        cities = data_service.get_unique_cities()
        property_types = data_service.get_property_types()
        
        return render_template('properties/list.html',
                             properties=properties,
                             cities=cities,
                             property_types=property_types,
                             search_params={
                                 'city': city,
                                 'type': property_type,
                                 'min_price': min_price,
                                 'max_price': max_price,
                                 'bedrooms': bedrooms,
                                 'bathrooms': bathrooms
                             })
    
    except Exception as e:
        current_app.logger.error(f"Error loading properties: {str(e)}")
        flash('Error loading properties. Please try again.', 'error')
        return render_template('properties/list.html',
                             properties=None,
                             cities=[],
                             property_types=[],
                             search_params={
                                 'city': '',
                                 'type': '',
                                 'min_price': None,
                                 'max_price': None,
                                 'bedrooms': None,
                                 'bathrooms': None
                             })


@bp.route('/property/<listing_id>')
def property_detail(listing_id):
    """Property detail page."""
    try:
        property_obj = Property.query.get_or_404(listing_id)
        
        # Get AI analysis if available
        ai_analysis = None
        try:
            ai_analysis = ml_service.analyze_property(property_obj)
        except Exception as e:
            current_app.logger.warning(f"Could not get AI analysis for property {listing_id}: {str(e)}")
        
        # Get nearby properties
        nearby_properties = []
        if property_obj.latitude and property_obj.longitude:
            try:
                nearby_properties = Property.query.filter(
                    Property.listing_id != listing_id,
                    Property.latitude.isnot(None),
                    Property.longitude.isnot(None)
                ).limit(10).all()  # Simplified - should use geospatial query
            except Exception as e:
                current_app.logger.warning(f"Could not get nearby properties: {str(e)}")
        
        # Check if property is saved by current user (demo mode for now)
        is_saved = False
        is_favorite = False
        saved_property = None
        
        return render_template('properties/detail.html',
                             property=property_obj,
                             ai_analysis=ai_analysis,
                             nearby_properties=nearby_properties,
                             is_saved=is_saved,
                             is_favorite=is_favorite,
                             saved_property=saved_property)
    
    except Exception as e:
        current_app.logger.error(f"Error loading property detail: {str(e)}")
        flash('Property not found.', 'error')
        return redirect(url_for('main.properties'))


@bp.route('/search')
def search():
    """Advanced search page."""
    try:
        # Get search parameters
        location = request.args.get('location', '').strip()
        property_type = request.args.get('property_type', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        bedrooms = request.args.get('bedrooms', type=int)
        bathrooms = request.args.get('bathrooms', type=float)
        page = request.args.get('page', 1, type=int)
        
        # Get form options
        cities = data_service.get_unique_cities()
        property_types = data_service.get_property_types()
        
        # Get price ranges for suggestions
        price_stats = data_service.get_price_statistics()
        
        # If we have search parameters, perform search
        if any([location, property_type, min_price, max_price, bedrooms, bathrooms]):
            # Build search query
            query = Property.query
            
            # Apply filters
            if location:
                query = query.filter(
                    Property.city.ilike(f'%{location}%') |
                    Property.province.ilike(f'%{location}%') |
                    Property.postal_code.ilike(f'%{location}%')
                )
            if property_type:
                query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
            if min_price:
                query = query.filter(Property.sold_price >= min_price)
            if max_price:
                query = query.filter(Property.sold_price <= max_price)
            if bedrooms:
                query = query.filter(Property.bedrooms >= bedrooms)
            if bathrooms:
                query = query.filter(Property.bathrooms >= bathrooms)
            
            # Order by most recent
            query = query.order_by(Property.sold_date.desc())
            
            # Paginate results
            properties = query.paginate(
                page=page,
                per_page=current_app.config.get('PROPERTIES_PER_PAGE', 20),
                error_out=False
            )
            
            return render_template('properties/search.html',
                                 cities=cities,
                                 property_types=property_types,
                                 price_stats=price_stats,
                                 properties=properties,
                                 search_params={
                                     'location': location,
                                     'property_type': property_type,
                                     'min_price': min_price,
                                     'max_price': max_price,
                                     'bedrooms': bedrooms,
                                     'bathrooms': bathrooms
                                 })
        else:
            # Just show the search form
            # Create empty pagination object for template compatibility
            from flask_sqlalchemy import Pagination
            empty_properties = Pagination(
                page=1,
                per_page=20,
                total=0,
                items=[],
                prev_num=None,
                next_num=None,
                has_prev=False,
                has_next=False
            )
            
            return render_template('properties/search.html',
                                 cities=cities,
                                 property_types=property_types,
                                 price_stats=price_stats,
                                 properties=empty_properties,
                                 search_params={})
    
    except Exception as e:
        current_app.logger.error(f"Error loading search page: {str(e)}")
        flash('Error loading search page.', 'error')
        # Return minimal template to avoid template errors
        from flask_sqlalchemy import Pagination
        empty_properties = Pagination(
            page=1,
            per_page=20,
            total=0,
            items=[],
            prev_num=None,
            next_num=None,
            has_prev=False,
            has_next=False
        )
        return render_template('properties/search.html',
                             cities=[],
                             property_types=[],
                             price_stats={},
                             properties=empty_properties,
                             search_params={})


@bp.route('/mapview')
def mapview():
    """Map view showing properties on an interactive map."""
    try:
        # Get search parameters
        city = request.args.get('city', '').strip()
        property_type = request.args.get('type', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        bedrooms = request.args.get('bedrooms', type=int)
        bathrooms = request.args.get('bathrooms', type=float)
        
        # Build query for properties with coordinates
        query = Property.query.filter(
            Property.latitude.isnot(None),
            Property.longitude.isnot(None)
        )
        
        # Apply filters
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))
        if property_type:
            query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
        if min_price:
            query = query.filter(Property.sold_price >= min_price)
        if max_price:
            query = query.filter(Property.sold_price <= max_price)
        if bedrooms:
            query = query.filter(Property.bedrooms >= bedrooms)
        if bathrooms:
            query = query.filter(Property.bathrooms >= bathrooms)
        
        # Limit results for performance (max 500 properties on map)
        properties = query.limit(500).all()
        
        # Convert properties to dictionaries for JSON serialization
        properties_data = []
        for prop in properties:
            prop_dict = {
                'listing_id': prop.listing_id,
                'address': prop.address,
                'city': prop.city,
                'province': prop.province,
                'property_type': prop.property_type,
                'bedrooms': prop.bedrooms,
                'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
                'sqft': prop.sqft,
                'sold_price': float(prop.sold_price) if prop.sold_price else None,
                'latitude': float(prop.latitude) if prop.latitude else None,
                'longitude': float(prop.longitude) if prop.longitude else None
            }
            properties_data.append(prop_dict)
        
        # Get filter options for dropdowns
        cities = data_service.get_unique_cities()
        property_types = data_service.get_property_types()
        
        # Calculate map center
        if properties:
            avg_lat = sum(float(p.latitude) for p in properties if p.latitude) / len(properties)
            avg_lng = sum(float(p.longitude) for p in properties if p.longitude) / len(properties)
            map_center = [avg_lat, avg_lng]
        else:
            # Default to Canada's geographic center if no properties
            map_center = [56.1304, -106.3468]
        
        return render_template('mapview.html',
                             properties=properties_data,
                             cities=cities,
                             property_types=property_types,
                             map_center=map_center,
                             current_filters={
                                 'city': city,
                                 'type': property_type,
                                 'min_price': min_price,
                                 'max_price': max_price,
                                 'bedrooms': bedrooms,
                                 'bathrooms': bathrooms
                             })
    
    except Exception as e:
        current_app.logger.error(f"Error loading map view: {str(e)}")
        flash('Error loading map data. Please try again.', 'error')
        return render_template('mapview.html',
                             properties=[],
                             cities=[],
                             property_types=[],
                             map_center=[56.1304, -106.3468],  # Canada center instead of Toronto
                             current_filters={})


@bp.route('/favourites')
def favourites():
    """Demo favourites page - will be enhanced with authentication later."""
    try:
        # For now, show a demo page explaining the feature
        # This will be replaced with actual functionality once auth is implemented
        
        # Get some sample properties to show what the feature would look like
        sample_properties = Property.query.filter(
            Property.sold_price.isnot(None)
        ).order_by(Property.sold_price.desc()).limit(6).all()
        
        # Demo stats
        stats = {
            'total_saved': 0,
            'favourites': 0,
            'total_value': 0,
            'avg_price': 0
        }
        
        return render_template('favourites.html',
                             saved_properties=[],
                             favourite_properties=[],
                             saved_only=[],
                             sample_properties=sample_properties,
                             stats=stats,
                             is_demo=True)
    
    except Exception as e:
        current_app.logger.error(f"Error loading favourites demo: {str(e)}")
        flash('Error loading page. Please try again.', 'error')
        return render_template('favourites.html',
                             saved_properties=[],
                             favourite_properties=[],
                             saved_only=[],
                             sample_properties=[],
                             stats={},
                             is_demo=True)


@bp.route('/api/save-property', methods=['POST'])
def save_property():
    """Demo save property endpoint - will require authentication when implemented."""
    try:
        data = request.get_json()
        listing_id = data.get('listing_id')
        
        if not listing_id:
            return jsonify({'error': 'Listing ID is required'}), 400
        
        # For demo purposes, just return a success message
        return jsonify({
            'message': 'Authentication required to save properties. This feature will be available when user accounts are implemented.',
            'demo': True
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in demo save property: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/update-saved-property', methods=['POST'])
# @login_required  # Commented out until authentication is implemented
def update_saved_property():
    """Update notes and tags for a saved property."""
    return jsonify({'message': 'Authentication required', 'demo': True}), 401


@bp.route('/api/check-saved-status/<listing_id>')
# @login_required  # Commented out until authentication is implemented
def check_saved_status(listing_id):
    """Check if a property is saved by the current user."""
    return jsonify({'message': 'Authentication required', 'demo': True}), 401


@bp.route('/api/properties/map-data')
def map_data():
    """API endpoint to get property data for map display."""
    try:
        # Get search parameters
        city = request.args.get('city', '').strip()
        property_type = request.args.get('type', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        bedrooms = request.args.get('bedrooms', type=int)
        bathrooms = request.args.get('bathrooms', type=float)
        
        # Build query for properties with coordinates within Canada bounds
        query = Property.query.filter(
            Property.latitude.isnot(None),
            Property.longitude.isnot(None),
            # Constrain to Canada geographic bounds
            Property.latitude.between(41.7, 83.5),  # Canada's southern to northern border
            Property.longitude.between(-141.0, -52.6)  # Canada's western to eastern border
        )
        
        # Apply filters
        if city:
            query = query.filter(Property.city.ilike(f'%{city}%'))
        if property_type:
            query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
        if min_price:
            query = query.filter(Property.sold_price >= min_price)
        if max_price:
            query = query.filter(Property.sold_price <= max_price)
        if bedrooms:
            query = query.filter(Property.bedrooms >= bedrooms)
        if bathrooms:
            query = query.filter(Property.bathrooms >= bathrooms)
        
        # Limit results for performance
        properties = query.limit(500).all()
        
        # Format data for map
        map_data = []
        for prop in properties:
            map_data.append({
                'listing_id': prop.listing_id,
                'lat': float(prop.latitude),
                'lng': float(prop.longitude),
                'price': float(prop.sold_price) if prop.sold_price else None,
                'address': prop.address,
                'city': prop.city,
                'property_type': prop.property_type,
                'bedrooms': prop.bedrooms,
                'bathrooms': float(prop.bathrooms) if prop.bathrooms else None,
                'sqft': prop.sqft,
                'sold_date': prop.sold_date.isoformat() if prop.sold_date else None
            })
        
        return jsonify({
            'properties': map_data,
            'count': len(map_data)
        })
    
    except Exception as e:
        current_app.logger.error(f"Error getting map data: {str(e)}")
        return jsonify({'error': 'Failed to load map data'}), 500


@bp.route('/api/saved-property/<int:saved_id>')
# @login_required  # Commented out until authentication is implemented
def get_saved_property(saved_id):
    """Get saved property details."""
    return jsonify({'message': 'Authentication required', 'demo': True}), 401

# Template context processors
@bp.app_context_processor
def inject_global_vars():
    """Inject global variables into all templates."""
    return {
        'current_year': 2025,
        'app_name': 'NextProperty AI',
        'app_version': '1.0.0'
    }


# Template filters
@bp.app_template_filter('format_currency')
def format_currency(value):
    """Format currency values."""
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        return f"${value:,.0f}"
    except (ValueError, TypeError):
        return "N/A"

@bp.app_template_filter('format_price')
def format_price(value):
    """Format price with appropriate K/M suffixes."""
    if value is None:
        return "N/A"
    
    value = float(value)
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:,.0f}"


@bp.app_template_filter('format_sqft')
def format_sqft(value):
    """Format square footage."""
    if value is None:
        return "N/A"
    return f"{value:,} sq ft"


@bp.app_template_filter('format_date')
def format_date(value):
    """Format date for display."""
    if value is None:
        return "N/A"
    
    if hasattr(value, 'strftime'):
        return value.strftime('%B %d, %Y')
    return str(value)


@bp.route('/login')
def login():
    """Simple login page for demonstration."""
    return render_template('auth/login.html')


@bp.route('/register')
def register():
    """Simple registration page for demonstration."""
    return render_template('auth/register.html')


@bp.route('/predict-price', methods=['GET', 'POST'])
def predict_price():
    """Property price prediction page."""
    try:
        if request.method == 'GET':
            # Get form options
            cities = data_service.get_unique_cities()
            property_types = data_service.get_property_types()
            
            return render_template('properties/price_prediction_form.html',
                                 cities=cities,
                                 property_types=property_types)
        
        # POST request - process prediction
        property_features = {
            'bedrooms': request.form.get('bedrooms', type=int),
            'bathrooms': request.form.get('bathrooms', type=float),
            'square_feet': request.form.get('square_feet', type=int),
            'lot_size': request.form.get('lot_size', type=int),
            'year_built': request.form.get('year_built', type=int),
            'property_type': request.form.get('property_type'),
            'city': request.form.get('city'),
            'province': request.form.get('province'),
            'postal_code': request.form.get('postal_code')
        }
        
        # Validate required fields
        required_fields = ['bedrooms', 'bathrooms', 'square_feet', 'property_type', 'city', 'province']
        missing_fields = [field for field in required_fields if not property_features.get(field)]
        
        if missing_fields:
            flash(f'Please fill in all required fields: {", ".join(missing_fields)}', 'error')
            cities = data_service.get_unique_cities()
            property_types = data_service.get_property_types()
            return render_template('properties/price_prediction_form.html',
                                 cities=cities,
                                 property_types=property_types,
                                 form_data=property_features)
        
        # Get prediction from ML service
        prediction_result = ml_service.predict_property_price(property_features)
        
        if prediction_result.get('error'):
            flash(f'Prediction error: {prediction_result["error"]}', 'error')
            cities = data_service.get_unique_cities()
            property_types = data_service.get_property_types()
            return render_template('properties/price_prediction_form.html',
                                 cities=cities,
                                 property_types=property_types,
                                 form_data=property_features)
        
        return render_template('properties/price_prediction.html',
                             prediction=prediction_result,
                             property_data=property_features)
    
    except Exception as e:
        current_app.logger.error(f"Error in price prediction: {str(e)}")
        flash('Error generating prediction. Please try again.', 'error')
        cities = data_service.get_unique_cities()
        property_types = data_service.get_property_types()
        return render_template('properties/price_prediction_form.html',
                             cities=cities,
                             property_types=property_types)


@bp.route('/upload-property', methods=['GET', 'POST'])
def upload_property():
    """Property upload page for adding new properties."""
    try:
        if request.method == 'GET':
            # Get form options
            cities = data_service.get_unique_cities()
            property_types = data_service.get_property_types()
            
            return render_template('properties/upload_form.html',
                                 cities=cities,
                                 property_types=property_types)
        
        # POST request - process property upload
        property_data = {
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'province': request.form.get('province'),
            'postal_code': request.form.get('postal_code'),
            'property_type': request.form.get('property_type'),
            'bedrooms': request.form.get('bedrooms', type=int),
            'bathrooms': request.form.get('bathrooms', type=float),
            'sqft': request.form.get('sqft', type=int),
            'lot_size': request.form.get('lot_size', type=float),
            'year_built': request.form.get('year_built', type=int),
            'listing_price': request.form.get('listing_price', type=float),
            'features': request.form.get('features'),
            'description': request.form.get('description')
        }
        
        # Validate required fields
        required_fields = ['address', 'city', 'province', 'property_type', 'bedrooms', 'bathrooms', 'sqft']
        missing_fields = [field for field in required_fields if not property_data.get(field)]
        
        if missing_fields:
            flash(f'Please fill in all required fields: {", ".join(missing_fields)}', 'error')
            cities = data_service.get_unique_cities()
            property_types = data_service.get_property_types()
            return render_template('properties/upload_form.html',
                                 cities=cities,
                                 property_types=property_types,
                                 form_data=property_data)
        
        # Generate listing ID
        import uuid
        listing_id = f"NP{str(uuid.uuid4()).replace('-', '')[:8].upper()}"
        
        # Create property object
        from datetime import datetime
        import random
        
        # Generate coordinates for the city (simplified)
        city_coords = {
            'toronto': (43.6532, -79.3832),
            'vancouver': (49.2827, -123.1207),
            'calgary': (51.0447, -114.0719),
            'ottawa': (45.4215, -75.6972),
            'montreal': (45.5017, -73.5673)
        }
        
        city_lower = property_data['city'].lower()
        if city_lower in city_coords:
            lat, lng = city_coords[city_lower]
            # Add small random offset
            latitude = lat + random.uniform(-0.05, 0.05)
            longitude = lng + random.uniform(-0.05, 0.05)
        else:
            # Default Toronto area with random offset
            latitude = 43.6532 + random.uniform(-0.1, 0.1)
            longitude = -79.3832 + random.uniform(-0.1, 0.1)
        
        # Create property
        property_obj = Property(
            listing_id=listing_id,
            mls=f"MLS{random.randint(100000, 999999)}",
            property_type=property_data['property_type'],
            address=property_data['address'],
            city=property_data['city'],
            province=property_data['province'],
            postal_code=property_data['postal_code'],
            latitude=latitude,
            longitude=longitude,
            original_price=property_data['listing_price'],
            bedrooms=property_data['bedrooms'],
            bathrooms=property_data['bathrooms'],
            sqft=property_data['sqft'],
            lot_size=property_data['lot_size'],
            features=property_data['features'],
            remarks=property_data['description'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Get AI prediction for the property
        prediction_features = {
            'bedrooms': property_data['bedrooms'],
            'bathrooms': property_data['bathrooms'],
            'square_feet': property_data['sqft'],
            'lot_size': property_data['lot_size'] or 0,
            'year_built': property_data['year_built'] or 2020,
            'property_type': property_data['property_type'],
            'city': property_data['city'],
            'province': property_data['province'],
            'postal_code': property_data['postal_code']
        }
        
        try:
            prediction_result = ml_service.predict_property_price(prediction_features)
            if prediction_result and not prediction_result.get('error'):
                property_obj.ai_valuation = prediction_result.get('predicted_price')
        except Exception as pred_error:
            current_app.logger.warning(f"Could not generate AI prediction: {str(pred_error)}")
        
        # Process photo uploads
        uploaded_photos = request.files.getlist('photos')
        if uploaded_photos and uploaded_photos[0].filename:
            try:
                # Validate photos
                validate_property_photos(uploaded_photos, 
                                       max_photos=current_app.config.get('MAX_PHOTOS_PER_PROPERTY', 20),
                                       max_size_per_photo=current_app.config.get('MAX_PHOTO_SIZE', 3 * 1024 * 1024))
                
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'properties', listing_id)
                os.makedirs(upload_dir, exist_ok=True)
                
                # Process each photo
                for index, photo in enumerate(uploaded_photos):
                    if photo and photo.filename:
                        # Generate secure filename
                        filename = secure_filename(photo.filename)
                        file_extension = filename.rsplit('.', 1)[1].lower()
                        new_filename = f"{uuid.uuid4().hex}.{file_extension}"
                        
                        # Save file
                        filepath = os.path.join(upload_dir, new_filename)
                        photo.save(filepath)
                        
                        # Create photo record
                        photo_url = f"/static/uploads/properties/{listing_id}/{new_filename}"
                        property_photo = PropertyPhoto(
                            listing_id=listing_id,
                            photo_url=photo_url,
                            photo_type='uploaded',
                            order_index=index,
                            caption=f"Property photo {index + 1}"
                        )
                        db.session.add(property_photo)
                
                current_app.logger.info(f"Successfully processed {len(uploaded_photos)} photos for property {listing_id}")
                
            except Exception as photo_error:
                current_app.logger.error(f"Error processing photos for property {listing_id}: {str(photo_error)}")
                flash(f'Property uploaded but some photos could not be processed: {str(photo_error)}', 'warning')
        
        # Save to database
        db.session.add(property_obj)
        db.session.commit()
        
        # Create success message
        success_message = 'Property uploaded successfully! AI prediction has been generated.'
        if uploaded_photos and uploaded_photos[0].filename:
            photo_count = len([p for p in uploaded_photos if p and p.filename])
            success_message += f' {photo_count} photo(s) were also uploaded.'
        
        flash(success_message, 'success')
        return redirect(url_for('main.property_detail', listing_id=listing_id))
    
    except Exception as e:
        current_app.logger.error(f"Error uploading property: {str(e)}")
        db.session.rollback()
        flash('Error uploading property. Please try again.', 'error')
        cities = data_service.get_unique_cities()
        property_types = data_service.get_property_types()
        return render_template('properties/upload_form.html',
                             cities=cities,
                             property_types=property_types)


@bp.route('/top-properties')
def top_properties():
    """Top properties page showing undervalued properties (below AI prediction)."""
    try:
        page = request.args.get('page', 1, type=int)
        city = request.args.get('city', '').strip()
        property_type = request.args.get('type', '').strip()
        sort_by = request.args.get('sort_by', 'investment_potential').strip()
        
        # Get top properties from ML service
        top_properties_data = ml_service.get_top_properties(
            limit=20,
            location=city if city else None,
            property_type=property_type if property_type else None,
            offset=(page - 1) * 20
        )
        
        # Transform data structure for template compatibility
        # The template expects properties with direct attributes like property.sqft, property.predicted_price
        top_properties = []
        for item in top_properties_data:
            try:
                property_obj = item['property']
                analysis = item['analysis']
                
                # Ensure property_obj is a Property object, not a dict
                if isinstance(property_obj, dict):
                    # If it's a dict, we need to handle it differently
                    current_app.logger.warning(f"Property object is a dict instead of Property model: {property_obj.get('listing_id', 'unknown')}")
                    continue
                
                # Create a property object with additional analysis data as attributes
                enhanced_property = property_obj
                enhanced_property.predicted_price = float(item.get('predicted_price', 0))
                enhanced_property.actual_price = float(item.get('actual_price', 0))
                enhanced_property.value_difference = float(item.get('value_difference', 0))
                enhanced_property.value_difference_percent = float(item.get('value_difference_percent', 0))
                enhanced_property.investment_potential = float(item.get('investment_potential', 0))
                
                top_properties.append(enhanced_property)
                
            except (ValueError, TypeError, AttributeError) as e:
                current_app.logger.warning(f"Error processing property data: {str(e)}")
                continue
        
        # Apply sorting with safe type conversion
        def get_sort_key(prop):
            try:
                if sort_by == 'investment_potential':
                    val = getattr(prop, 'investment_potential', 0)
                    return float(val) if val is not None and val != '' else 0.0
                elif sort_by == 'value_difference':
                    val = getattr(prop, 'value_difference', 0)
                    return float(val) if val is not None and val != '' else 0.0
                elif sort_by == 'predicted_price':
                    val = getattr(prop, 'predicted_price', 0)
                    return float(val) if val is not None and val != '' else 0.0
                elif sort_by == 'actual_price':
                    val = getattr(prop, 'sold_price', 0)
                    if val is None or val == '':
                        return 0.0
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        return 0.0
                elif sort_by == 'bedrooms':
                    val = getattr(prop, 'bedrooms', 0)
                    if val is None or val == '':
                        return 0
                    try:
                        # Handle string values that might contain non-digits
                        str_val = str(val).strip()
                        if str_val.replace('.', '').replace('-', '').isdigit():
                            return int(float(str_val))
                        else:
                            return 0
                    except (ValueError, TypeError):
                        return 0
                elif sort_by == 'sqft':
                    val = getattr(prop, 'sqft', 0)
                    if val is None or val == '':
                        return 0.0
                    try:
                        # Handle string values that might contain non-digits
                        str_val = str(val).strip()
                        if str_val.replace('.', '').replace('-', '').replace(',', '').isdigit():
                            return float(str_val.replace(',', ''))
                        else:
                            return 0.0
                    except (ValueError, TypeError):
                        return 0.0
                else:
                    val = getattr(prop, 'investment_potential', 0)
                    return float(val) if val is not None and val != '' else 0.0
            except (ValueError, TypeError, AttributeError) as e:
                current_app.logger.debug(f"Error in get_sort_key for property {getattr(prop, 'listing_id', 'unknown')}: {str(e)}")
                return 0.0
        
        top_properties.sort(key=get_sort_key, reverse=True)
        
        # Get total count for pagination
        total_count = ml_service.get_top_properties_count(
            location=city if city else None,
            property_type=property_type if property_type else None
        )
        
        # Calculate pagination info
        has_next = len(top_properties) == 20 and (page * 20) < total_count
        has_prev = page > 1
        
        # Get filter options
        cities = data_service.get_unique_cities()
        property_types = data_service.get_property_types()
        
        return render_template('properties/top_properties.html',
                             top_properties=top_properties,
                             cities=cities,
                             property_types=property_types,
                             pagination={
                                 'page': page,
                                 'has_next': has_next,
                                 'has_prev': has_prev,
                                 'total': total_count
                             },
                             current_filters={
                                 'city': city,
                                 'type': property_type,
                                 'sort_by': sort_by
                             })
    
    except Exception as e:
        current_app.logger.error(f"Error loading top properties: {str(e)}")
        flash('Error loading top properties. Please try again.', 'error')
        return render_template('properties/top_properties.html',
                             top_properties=[],
                             cities=[],
                             property_types=[],
                             pagination={
                                 'page': 1,
                                 'has_next': False,
                                 'has_prev': False,
                                 'total': 0
                             },
                             current_filters={})


@bp.route('/market-insights')
def market_insights():
    """Market insights page."""
    return render_template('market_insights.html')

@bp.route('/economic-dashboard')
def economic_dashboard():
    """Economic dashboard page."""
    return render_template('economic_dashboard.html')

@bp.route('/api/market-summary')
def api_market_summary():
    """API endpoint for market summary data."""
    try:
        summary = data_service.get_market_summary()
        return jsonify(summary)
    except Exception as e:
        current_app.logger.error(f"Error getting market summary: {str(e)}")
        return jsonify({
            'total_properties': 0,
            'avg_price': 0,
            'median_price': 0,
            'avg_sqft': 0,
            'avg_dom': 0,
            'market_condition': 'Error Loading Data'
        }), 500

@bp.route('/api/economic-indicators')
def api_economic_indicators():
    """API endpoint for economic indicators."""
    try:
        # Get economic indicators from the ML service
        indicators = ml_service._get_economic_indicators()
        return jsonify(indicators)
    except Exception as e:
        current_app.logger.error(f"Error getting economic indicators: {str(e)}")
        return jsonify({
            'policy_rate': None,
            'prime_rate': None,
            'mortgage_rate': None,
            'inflation_rate': None,
            'unemployment_rate': None,
            'exchange_rate': None,
            'gdp_growth': None
        }), 500

@bp.route('/api/market-impact')
def api_market_impact():
    """API endpoint for market impact analysis."""
    try:
        # Get economic indicators
        indicators = ml_service._get_economic_indicators()
        
        # Calculate impact scores
        interest_env = ml_service._calculate_interest_environment(indicators)
        
        economic_momentum = ml_service._calculate_economic_momentum(indicators)
        
        affordability_pressure = ml_service._calculate_affordability_pressure(indicators)
        
        # Convert to descriptive text
        interest_desc = {
            0: "Very Low - Excellent borrowing conditions",
            0.25: "Low - Favorable borrowing conditions", 
            0.5: "Moderate - Average borrowing conditions",
            0.75: "High - Challenging borrowing conditions",
            1.0: "Very High - Difficult borrowing conditions"
        }
        
        momentum_desc = {
            -1: "Declining - Economic contraction",
            -0.5: "Slowing - Economic slowdown",
            0: "Stable - Balanced economic conditions",
            0.5: "Growing - Economic expansion",
            1: "Strong - Robust economic growth"
        }
        
        affordability_desc = {
            0: "Easy - High affordability",
            0.25: "Moderate - Good affordability",
            0.5: "Average - Typical affordability",
            0.75: "Challenging - Limited affordability", 
            1.0: "Difficult - Low affordability"
        }
        
        # Find closest descriptions
        def find_closest_desc(value, desc_dict):
            closest_key = min(desc_dict.keys(), key=lambda x: abs(x - value))
            return desc_dict[closest_key]
        
        return jsonify({
            'interest_environment': f"{interest_env:.1f}/1.0",
            'interest_description': find_closest_desc(interest_env, interest_desc),
            'economic_momentum': f"{economic_momentum:.1f}/1.0", 
            'momentum_description': find_closest_desc(economic_momentum, momentum_desc),
            'affordability_pressure': f"{affordability_pressure:.1f}/1.0",
            'affordability_description': find_closest_desc(affordability_pressure, affordability_desc)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error calculating market impact: {str(e)}")
        return jsonify({
            'interest_environment': 'N/A',
            'interest_description': 'Unable to calculate',
            'economic_momentum': 'N/A',
            'momentum_description': 'Unable to calculate', 
            'affordability_pressure': 'N/A',
            'affordability_description': 'Unable to calculate'
        }), 500

@bp.route('/api/economic-insights')
def api_economic_insights():
    """API endpoint for economic insights."""
    try:
        # Get economic indicators
        indicators = ml_service._get_economic_indicators()
        
        insights = []
        
        # Interest rate insights
        policy_rate = indicators.get('policy_rate', 5.0)
        if policy_rate < 2.0:
            insights.append({
                'title': 'Low Interest Rates',
                'message': 'Current low policy rates create favorable conditions for real estate investment and homebuying.',
                'type': 'success'
            })
        elif policy_rate > 5.0:
            insights.append({
                'title': 'High Interest Rates', 
                'message': 'Elevated policy rates may dampen real estate demand and affect affordability.',
                'type': 'warning'
            })
        
        # Inflation insights
        inflation = indicators.get('inflation_rate', 3.0)
        if inflation > 4.0:
            insights.append({
                'title': 'High Inflation',
                'message': 'Rising inflation may continue to pressure interest rates and housing affordability.',
                'type': 'danger'
            })
        elif inflation < 2.0:
            insights.append({
                'title': 'Low Inflation',
                'message': 'Subdued inflation provides room for accommodative monetary policy.',
                'type': 'info'
            })
        
        # GDP insights
        gdp_growth = indicators.get('gdp_growth', 2.0)
        if gdp_growth > 3.0:
            insights.append({
                'title': 'Strong Economic Growth',
                'message': 'Robust GDP growth supports employment and housing demand.',
                'type': 'success'
            })
        elif gdp_growth < 1.0:
            insights.append({
                'title': 'Slow Economic Growth',
                'message': 'Weak GDP growth may affect employment and housing market activity.',
                'type': 'warning'
            })
        
        return jsonify({
            'insights': insights,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating economic insights: {str(e)}")
        return jsonify({
            'insights': [],
            'error': 'Unable to generate insights at this time'
        }), 500
