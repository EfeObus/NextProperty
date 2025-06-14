from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from app.extensions import db
from app.models.property import Property
from app.services.ml_service import MLService
from app.services.data_service import DataService
from app.services.database_optimizer import DatabaseOptimizer, BulkOperationManager
from datetime import datetime, timedelta
from sqlalchemy import func, text
import json

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize services
ml_service = MLService()
data_service = DataService()
db_optimizer = DatabaseOptimizer()

@bp.route('/')
def dashboard():
    """Admin dashboard with system overview."""
    try:
        # Get system statistics
        stats = {
            'total_properties': Property.query.count(),
            'properties_with_ai': Property.query.filter(Property.ai_valuation.isnot(None)).count(),
            'properties_without_ai': Property.query.filter(Property.ai_valuation.is_(None)).count(),
            'recent_properties': Property.query.filter(
                Property.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
        
        # Get model status
        model_status = ml_service.get_model_metadata()
        
        # Get database health
        db_health = db_optimizer.get_database_health()
        
        # Get recent activity
        recent_activity = Property.query.order_by(Property.created_at.desc()).limit(10).all()
        
        return render_template('admin/dashboard.html',
                             stats=stats,
                             model_status=model_status,
                             db_health=db_health,
                             recent_activity=recent_activity)
    
    except Exception as e:
        current_app.logger.error(f"Error loading admin dashboard: {str(e)}")
        flash('Error loading dashboard', 'error')
        return render_template('admin/dashboard.html', error=True)

@bp.route('/bulk-operations')
def bulk_operations():
    """Bulk operations management page."""
    try:
        # Get counts for different operations
        operations_status = {
            'properties_need_analysis': Property.query.filter(
                Property.ai_valuation.is_(None),
                Property.bedrooms.isnot(None)
            ).count(),
            'properties_outdated_analysis': Property.query.filter(
                Property.ai_valuation.isnot(None),
                Property.updated_at < datetime.utcnow() - timedelta(days=30)
            ).count(),
            'total_analyzed': Property.query.filter(Property.ai_valuation.isnot(None)).count()
        }
        
        return render_template('admin/bulk_operations.html',
                             operations_status=operations_status)
    
    except Exception as e:
        current_app.logger.error(f"Error loading bulk operations: {str(e)}")
        flash('Error loading bulk operations', 'error')
        return render_template('admin/bulk_operations.html', error=True)

@bp.route('/api/bulk-ai-analysis', methods=['POST'])
def bulk_ai_analysis():
    """Generate AI valuations for properties in bulk."""
    try:
        data = request.get_json()
        batch_size = data.get('batch_size', 50)
        force_update = data.get('force_update', False)
        
        # Get properties that need analysis
        query = Property.query.filter(Property.bedrooms.isnot(None))
        
        if not force_update:
            query = query.filter(Property.ai_valuation.is_(None))
        
        properties_to_analyze = query.limit(batch_size).all()
        
        if not properties_to_analyze:
            return jsonify({
                'success': True,
                'message': 'No properties found that need analysis',
                'processed': 0
            })
        
        processed_count = 0
        errors = []
        
        # Use bulk operations context manager for optimization
        with BulkOperationManager():
            for property_obj in properties_to_analyze:
                try:
                    # Generate AI prediction
                    property_features = {
                        'bedrooms': property_obj.bedrooms or 3,
                        'bathrooms': property_obj.bathrooms or 2,
                        'square_feet': property_obj.sqft or 1500,
                        'lot_size': property_obj.lot_size or 0,
                        'year_built': property_obj.year_built or 2010,
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
                        property_obj.updated_at = datetime.utcnow()
                        processed_count += 1
                    else:
                        errors.append(f"Property {property_obj.listing_id}: {prediction_result.get('error')}")
                        
                except Exception as prop_error:
                    error_msg = f"Property {property_obj.listing_id}: {str(prop_error)}"
                    errors.append(error_msg)
                    current_app.logger.warning(error_msg)
                    continue
            
            # Commit all changes at once
            db.session.commit()
        
        return jsonify({
            'success': True,
            'processed': processed_count,
            'total_batch': len(properties_to_analyze),
            'errors': errors[:10]  # Limit error messages
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk AI analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Bulk analysis failed: {str(e)}'
        }), 500

@bp.route('/api/optimize-database', methods=['POST'])
def optimize_database():
    """Optimize database for better performance."""
    try:
        results = db_optimizer.optimize_for_bulk_operations()
        return jsonify({
            'success': True,
            'message': 'Database optimization completed',
            'results': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error optimizing database: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Database optimization failed: {str(e)}'
        }), 500

@bp.route('/api/cleanup-data', methods=['POST'])
def cleanup_data():
    """Clean up invalid or incomplete data."""
    try:
        data = request.get_json()
        cleanup_type = data.get('type', 'all')
        
        results = {
            'removed_duplicates': 0,
            'fixed_invalid_data': 0,
            'updated_coordinates': 0
        }
        
        if cleanup_type in ['all', 'duplicates']:
            # Remove duplicate properties based on address
            duplicates = db.session.query(
                Property.address,
                Property.city,
                func.count(Property.listing_id).label('count')
            ).group_by(Property.address, Property.city).having(
                func.count(Property.listing_id) > 1
            ).all()
            
            for address, city, count in duplicates:
                # Keep the most recent one, delete others
                duplicate_properties = Property.query.filter(
                    Property.address == address,
                    Property.city == city
                ).order_by(Property.created_at.desc()).all()
                
                for prop in duplicate_properties[1:]:  # Skip the first (most recent)
                    db.session.delete(prop)
                    results['removed_duplicates'] += 1
        
        if cleanup_type in ['all', 'invalid_data']:
            # Fix properties with invalid prices
            invalid_price_props = Property.query.filter(
                db.or_(
                    Property.sold_price < 10000,
                    Property.sold_price > 50000000
                )
            ).all()
            
            for prop in invalid_price_props:
                prop.sold_price = None
                results['fixed_invalid_data'] += 1
        
        if cleanup_type in ['all', 'coordinates']:
            # Update missing coordinates
            props_without_coords = Property.query.filter(
                db.or_(
                    Property.latitude.is_(None),
                    Property.longitude.is_(None)
                ),
                Property.city.isnot(None)
            ).limit(100).all()
            
            city_coords = {
                'toronto': (43.6532, -79.3832),
                'vancouver': (49.2827, -123.1207),
                'calgary': (51.0447, -114.0719),
                'ottawa': (45.4215, -75.6972),
                'montreal': (45.5017, -73.5673)
            }
            
            for prop in props_without_coords:
                city_lower = prop.city.lower()
                if city_lower in city_coords:
                    import random
                    lat, lng = city_coords[city_lower]
                    prop.latitude = lat + random.uniform(-0.05, 0.05)
                    prop.longitude = lng + random.uniform(-0.05, 0.05)
                    results['updated_coordinates'] += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Data cleanup completed',
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in data cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Data cleanup failed: {str(e)}'
        }), 500

@bp.route('/api/system-stats', methods=['GET'])
def system_stats():
    """Get detailed system statistics."""
    try:
        # Property statistics
        property_stats = {
            'total': Property.query.count(),
            'with_ai_valuation': Property.query.filter(Property.ai_valuation.isnot(None)).count(),
            'by_city': dict(db.session.query(
                Property.city,
                func.count(Property.listing_id)
            ).group_by(Property.city).order_by(
                func.count(Property.listing_id).desc()
            ).limit(10).all()),
            'by_type': dict(db.session.query(
                Property.property_type,
                func.count(Property.listing_id)
            ).group_by(Property.property_type).order_by(
                func.count(Property.listing_id).desc()
            ).all()),
            'price_ranges': dict(db.session.query(
                text("""
                    CASE 
                        WHEN sold_price < 300000 THEN 'Under $300K'
                        WHEN sold_price < 500000 THEN '$300K-$500K'
                        WHEN sold_price < 750000 THEN '$500K-$750K'
                        WHEN sold_price < 1000000 THEN '$750K-$1M'
                        WHEN sold_price >= 1000000 THEN 'Over $1M'
                        ELSE 'Unknown'
                    END as price_range
                """),
                func.count(Property.listing_id)
            ).filter(Property.sold_price.isnot(None)).group_by(
                text("""
                    CASE 
                        WHEN sold_price < 300000 THEN 'Under $300K'
                        WHEN sold_price < 500000 THEN '$300K-$500K'
                        WHEN sold_price < 750000 THEN '$500K-$750K'
                        WHEN sold_price < 1000000 THEN '$750K-$1M'
                        WHEN sold_price >= 1000000 THEN 'Over $1M'
                        ELSE 'Unknown'
                    END
                """)
            ).all())
        }
        
        # ML model statistics
        model_stats = ml_service.get_model_metadata()
        
        # Database health
        db_health = db_optimizer.get_database_health()
        
        return jsonify({
            'success': True,
            'property_stats': property_stats,
            'model_stats': model_stats,
            'db_health': db_health,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting system stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get system stats: {str(e)}'
        }), 500

@bp.route('/model-management')
def model_management():
    """Model management page."""
    try:
        # Get available models
        available_models = ml_service.get_available_models()
        
        # Get current model metadata
        current_model = ml_service.get_model_metadata()
        
        # Get model comparison data
        model_comparison = ml_service.get_model_comparison()
        
        return render_template('admin/model_management.html',
                             available_models=available_models,
                             current_model=current_model,
                             model_comparison=model_comparison)
    
    except Exception as e:
        current_app.logger.error(f"Error loading model management: {str(e)}")
        flash('Error loading model management', 'error')
        return render_template('admin/model_management.html', error=True)

@bp.route('/api/switch-model', methods=['POST'])
def switch_model():
    """Switch to a different ML model."""
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
        current_app.logger.error(f"Error switching model: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Model switch failed: {str(e)}'
        }), 500

# Admin-only decorator (placeholder for when authentication is implemented)
def admin_required(f):
    """Decorator to require admin privileges."""
    def decorated_function(*args, **kwargs):
        # For now, allow all access - will be restricted when auth is implemented
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Apply admin_required to all routes
for rule in bp.deferred_functions:
    if hasattr(rule, 'func'):
        rule.func = admin_required(rule.func)
