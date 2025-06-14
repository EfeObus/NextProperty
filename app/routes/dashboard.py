from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.property import Property
from app.models.user import SavedProperty
from app.models.economic_data import EconomicData, EconomicIndicator
from app.services.ml_service import MLService
from app.services.data_service import DataService
from datetime import datetime, timedelta
import json

bp = Blueprint('dashboard', __name__)

# Initialize services
ml_service = MLService()
data_service = DataService()

@bp.route('/')
@login_required
def overview():
    """Dashboard overview page."""
    try:
        # Get user's saved properties count
        saved_count = current_user.saved_properties.count()
        
        # Get recent market activity
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_properties = Property.query.filter(
            Property.created_at >= recent_date
        ).count()
        
        # Get user's preferred cities data
        preferred_cities = []
        if current_user.preferred_cities:
            cities = json.loads(current_user.preferred_cities)
            for city in cities[:5]:  # Limit to top 5
                city_stats = data_service.get_city_statistics(city)
                preferred_cities.append(city_stats)
        
        # Get market trends for user's interests
        market_trends = data_service.get_personalized_trends(current_user)
        
        # Get investment recommendations
        recommendations = ml_service.get_investment_recommendations(current_user)
        
        # Get economic indicators dashboard
        key_indicators = data_service.get_dashboard_economic_indicators()
        
        return render_template('dashboard/overview.html',
                             saved_count=saved_count,
                             recent_properties=recent_properties,
                             preferred_cities=preferred_cities,
                             market_trends=market_trends,
                             recommendations=recommendations,
                             key_indicators=key_indicators)
    
    except Exception as e:
        current_app.logger.error(f"Error loading dashboard: {str(e)}")
        return render_template('dashboard/overview.html', error=True)


@bp.route('/portfolio')
@login_required
def portfolio():
    """User's property portfolio page."""
    try:
        # Get user's saved properties
        saved_properties = current_user.saved_properties.join(Property).all()
        
        # Calculate portfolio statistics
        portfolio_stats = {
            'total_properties': len(saved_properties),
            'total_value': 0,
            'avg_price': 0,
            'property_types': {},
            'cities': {}
        }
        
        if saved_properties:
            values = []
            for saved in saved_properties:
                prop = saved.property
                if prop.sold_price:
                    values.append(float(prop.sold_price))
                    portfolio_stats['total_value'] += float(prop.sold_price)
                
                # Count by type
                if prop.property_type:
                    portfolio_stats['property_types'][prop.property_type] = \
                        portfolio_stats['property_types'].get(prop.property_type, 0) + 1
                
                # Count by city
                if prop.city:
                    portfolio_stats['cities'][prop.city] = \
                        portfolio_stats['cities'].get(prop.city, 0) + 1
            
            if values:
                portfolio_stats['avg_price'] = sum(values) / len(values)
        
        # Get portfolio performance analysis
        performance = ml_service.analyze_portfolio_performance(saved_properties)
        
        return render_template('dashboard/portfolio.html',
                             saved_properties=saved_properties,
                             portfolio_stats=portfolio_stats,
                             performance=performance)
    
    except Exception as e:
        current_app.logger.error(f"Error loading portfolio: {str(e)}")
        return render_template('dashboard/portfolio.html', error=True)


@bp.route('/market')
@login_required
def market():
    """Market analysis dashboard."""
    try:
        # Get comprehensive market data
        market_overview = data_service.get_comprehensive_market_overview()
        
        # Get economic indicators with trends
        economic_indicators = data_service.get_trending_economic_indicators()
        
        # Get regional market comparison
        regional_data = data_service.get_regional_market_comparison()
        
        # Get property type performance
        type_performance = data_service.get_property_type_performance()
        
        # Get market predictions
        predictions = ml_service.get_market_predictions()
        
        return render_template('dashboard/market.html',
                             market_overview=market_overview,
                             economic_indicators=economic_indicators,
                             regional_data=regional_data,
                             type_performance=type_performance,
                             predictions=predictions)
    
    except Exception as e:
        current_app.logger.error(f"Error loading market dashboard: {str(e)}")
        return render_template('dashboard/market.html', error=True)


@bp.route('/analytics')
@login_required
def analytics():
    """Advanced analytics dashboard."""
    try:
        # Get user's search and activity analytics
        user_analytics = data_service.get_user_analytics(current_user)
        
        # Get investment opportunity analysis
        opportunities = ml_service.identify_investment_opportunities(current_user)
        
        # Get risk analysis
        risk_analysis = ml_service.get_portfolio_risk_analysis(current_user)
        
        # Get ROI projections
        roi_projections = ml_service.calculate_roi_projections(current_user)
        
        return render_template('dashboard/analytics.html',
                             user_analytics=user_analytics,
                             opportunities=opportunities,
                             risk_analysis=risk_analysis,
                             roi_projections=roi_projections)
    
    except Exception as e:
        current_app.logger.error(f"Error loading analytics: {str(e)}")
        return render_template('dashboard/analytics.html', error=True)


@bp.route('/economic')
@login_required
def economic():
    """Economic indicators dashboard."""
    try:
        from app.services.external_apis import ExternalAPIsService
        
        # Get latest economic summary
        economic_summary = ExternalAPIsService.get_latest_economic_summary()
        
        # Get detailed economic indicators
        economic_indicators = data_service.get_trending_economic_indicators()
        
        # Get interest rates data
        interest_rates = ExternalAPIsService.get_current_interest_rates()
        
        # Get housing market indicators
        housing_indicators = ExternalAPIsService.get_housing_market_indicators()
        
        # Get economic outlook
        economic_outlook = ExternalAPIsService.get_economic_outlook()
        
        return render_template('dashboard/economic.html',
                             economic_summary=economic_summary,
                             economic_indicators=economic_indicators,
                             interest_rates=interest_rates,
                             housing_indicators=housing_indicators,
                             economic_outlook=economic_outlook)
    
    except Exception as e:
        current_app.logger.error(f"Error loading economic dashboard: {str(e)}")
        # Return a fallback economic summary for error cases
        fallback_summary = type('obj', (object,), {})()
        fallback_summary.bank_rate = 2.75
        fallback_summary.prime_rate = 4.95
        fallback_summary.inflation_rate = 2.3
        fallback_summary.cad_usd_rate = 1.369
        fallback_summary.market_sentiment = "Economic data temporarily unavailable"
        fallback_summary.key_trends = ["Real-time data will be restored shortly"]
        
        return render_template('dashboard/economic.html',
                             economic_summary=fallback_summary,
                             economic_indicators={},
                             interest_rates={},
                             housing_indicators={},
                             economic_outlook={},
                             error=True)


@bp.route('/api/chart-data/<chart_type>')
@login_required
def get_chart_data(chart_type):
    """API endpoint for dashboard chart data."""
    try:
        city = request.args.get('city')
        property_type = request.args.get('type')
        timeframe = request.args.get('timeframe', '12m')
        
        if chart_type == 'price_trends':
            data = data_service.get_price_trend_data(city, property_type, timeframe)
        elif chart_type == 'market_volume':
            data = data_service.get_market_volume_data(city, timeframe)
        elif chart_type == 'economic_indicators':
            data = data_service.get_economic_indicators_chart_data(timeframe)
        elif chart_type == 'portfolio_performance':
            data = ml_service.get_portfolio_performance_data(current_user, timeframe)
        elif chart_type == 'regional_comparison':
            data = data_service.get_regional_comparison_data()
        else:
            return jsonify({'error': 'Invalid chart type'}), 400
        
        return jsonify({'success': True, 'data': data})
    
    except Exception as e:
        current_app.logger.error(f"Error fetching chart data {chart_type}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/property-analysis/<listing_id>')
@login_required
def get_property_analysis(listing_id):
    """Get detailed AI analysis for a property."""
    try:
        property = Property.query.filter_by(listing_id=listing_id).first()
        if not property:
            return jsonify({'error': 'Property not found'}), 404
        
        # Get comprehensive AI analysis
        analysis = ml_service.get_comprehensive_property_analysis(property)
        
        return jsonify({'success': True, 'data': analysis})
    
    except Exception as e:
        current_app.logger.error(f"Error analyzing property {listing_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/investment-simulator', methods=['POST'])
@login_required
def investment_simulator():
    """Investment scenario simulator."""
    try:
        data = request.get_json()
        
        property_price = data.get('property_price')
        down_payment = data.get('down_payment')
        interest_rate = data.get('interest_rate')
        loan_term = data.get('loan_term')
        rental_income = data.get('rental_income')
        expenses = data.get('expenses')
        
        # Validate inputs
        if not all([property_price, down_payment, interest_rate, loan_term]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Run investment simulation
        simulation = ml_service.simulate_investment_scenario({
            'property_price': property_price,
            'down_payment': down_payment,
            'interest_rate': interest_rate,
            'loan_term': loan_term,
            'rental_income': rental_income or 0,
            'expenses': expenses or 0
        })
        
        return jsonify({'success': True, 'data': simulation})
    
    except Exception as e:
        current_app.logger.error(f"Error in investment simulation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/market-alerts')
@login_required
def get_market_alerts():
    """Get personalized market alerts."""
    try:
        alerts = data_service.get_market_alerts(current_user)
        return jsonify({'success': True, 'data': alerts})
    
    except Exception as e:
        current_app.logger.error(f"Error fetching market alerts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/api/save-preferences', methods=['POST'])
@login_required
def save_preferences():
    """Save user dashboard preferences."""
    try:
        data = request.get_json()
        
        # Update user preferences
        if 'preferred_cities' in data:
            current_user.preferred_cities = json.dumps(data['preferred_cities'])
        
        if 'preferred_property_types' in data:
            current_user.preferred_property_types = json.dumps(data['preferred_property_types'])
        
        if 'price_range_min' in data:
            current_user.price_range_min = data['price_range_min']
        
        if 'price_range_max' in data:
            current_user.price_range_max = data['price_range_max']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Preferences saved successfully'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving preferences: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Dashboard template filters
@bp.app_template_filter('format_percentage')
def format_percentage(value):
    """Format percentage values."""
    if value is None:
        return "N/A"
    return f"{float(value):.1f}%"


@bp.app_template_filter('format_large_number')
def format_large_number(value):
    """Format large numbers with K/M/B suffixes."""
    if value is None:
        return "N/A"
    
    value = float(value)
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:,.0f}"


@bp.app_template_filter('trend_icon')
def trend_icon(value):
    """Get trend icon based on value."""
    if value is None:
        return "📊"
    
    if isinstance(value, str) and value:
        value_lower = value.lower()
        if 'up' in value_lower or 'rising' in value_lower:
            return "📈"
        elif 'down' in value_lower or 'falling' in value_lower:
            return "📉"
        else:
            return "📊"
    
    # Numeric value
    if value > 0:
        return "📈"
    elif value < 0:
        return "📉"
    else:
        return "📊"
