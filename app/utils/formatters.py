"""
Data formatters for NextProperty AI platform.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal
import json
from .helpers import format_currency, format_phone, format_address, format_percentage, format_square_feet


def format_property_data(property_obj: Any, include_sensitive: bool = False) -> Dict[str, Any]:
    """
    Format property data for API response.
    
    Args:
        property_obj: Property model instance
        include_sensitive: Whether to include sensitive data
        
    Returns:
        dict: Formatted property data
    """
    if not property_obj:
        return {}
    
    data = {
        'id': property_obj.id,
        'mls_number': property_obj.mls_number,
        'address': format_address({
            'street_number': property_obj.street_number,
            'street_name': property_obj.street_name,
            'unit': property_obj.unit,
            'city': property_obj.city,
            'province': property_obj.province,
            'postal_code': property_obj.postal_code
        }),
        'price': format_currency(property_obj.price),
        'price_raw': float(property_obj.price) if property_obj.price else None,
        'property_type': property_obj.property_type,
        'bedrooms': property_obj.bedrooms,
        'bathrooms': property_obj.bathrooms,
        'square_feet': format_square_feet(property_obj.square_feet),
        'square_feet_raw': property_obj.square_feet,
        'lot_size': property_obj.lot_size,
        'year_built': property_obj.year_built,
        'description': property_obj.description,
        'features': json.loads(property_obj.features) if property_obj.features else {},
        'images': json.loads(property_obj.images) if property_obj.images else [],
        'status': property_obj.status,
        'listed_date': property_obj.listed_date.isoformat() if property_obj.listed_date else None,
        'sold_date': property_obj.sold_date.isoformat() if property_obj.sold_date else None,
        'days_on_market': property_obj.days_on_market,
        'virtual_tour_url': property_obj.virtual_tour_url,
        'latitude': property_obj.latitude,
        'longitude': property_obj.longitude,
        'created_at': property_obj.created_at.isoformat() if property_obj.created_at else None,
        'updated_at': property_obj.updated_at.isoformat() if property_obj.updated_at else None
    }
    
    # Add agent information if available
    if hasattr(property_obj, 'agent') and property_obj.agent:
        data['agent'] = format_agent_data(property_obj.agent, include_sensitive=include_sensitive)
    
    # Add price history if available
    if hasattr(property_obj, 'price_history') and property_obj.price_history:
        data['price_history'] = [
            {
                'price': format_currency(history.price),
                'price_raw': float(history.price),
                'date': history.date.isoformat(),
                'change_type': history.change_type
            }
            for history in property_obj.price_history
        ]
    
    # Add sensitive data if requested and user has permission
    if include_sensitive:
        data.update({
            'property_tax': format_currency(property_obj.property_tax) if property_obj.property_tax else None,
            'monthly_fees': format_currency(property_obj.monthly_fees) if property_obj.monthly_fees else None,
            'utilities_included': property_obj.utilities_included,
            'possession_date': property_obj.possession_date.isoformat() if property_obj.possession_date else None
        })
    
    return data


def format_search_results(properties: List[Any], total: int, page: int, per_page: int, 
                         include_sensitive: bool = False) -> Dict[str, Any]:
    """
    Format property search results.
    
    Args:
        properties: List of property objects
        total: Total number of results
        page: Current page number
        per_page: Results per page
        include_sensitive: Whether to include sensitive data
        
    Returns:
        dict: Formatted search results
    """
    return {
        'properties': [format_property_data(prop, include_sensitive) for prop in properties],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'has_prev': page > 1,
            'has_next': page * per_page < total
        },
        'summary': {
            'total_properties': total,
            'avg_price': _calculate_avg_price(properties),
            'price_range': _calculate_price_range(properties),
            'property_types': _get_property_types_summary(properties)
        }
    }


def format_market_data(market_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format market data for API response.
    
    Args:
        market_data: Raw market data
        
    Returns:
        dict: Formatted market data
    """
    return {
        'area': market_data.get('area', ''),
        'period': market_data.get('period', ''),
        'metrics': {
            'average_price': format_currency(market_data.get('average_price')),
            'average_price_raw': market_data.get('average_price'),
            'median_price': format_currency(market_data.get('median_price')),
            'median_price_raw': market_data.get('median_price'),
            'price_per_sqft': format_currency(market_data.get('price_per_sqft'), currency=''),
            'price_per_sqft_raw': market_data.get('price_per_sqft'),
            'sales_volume': market_data.get('sales_volume'),
            'inventory_levels': market_data.get('inventory_levels'),
            'days_on_market': market_data.get('days_on_market'),
            'absorption_rate': format_percentage(market_data.get('absorption_rate')),
            'price_change_mom': format_percentage(market_data.get('price_change_mom')),
            'price_change_yoy': format_percentage(market_data.get('price_change_yoy'))
        },
        'trends': market_data.get('trends', {}),
        'forecasts': market_data.get('forecasts', {}),
        'last_updated': market_data.get('last_updated', '')
    }


def format_agent_data(agent_obj: Any, include_sensitive: bool = False) -> Dict[str, Any]:
    """
    Format agent data for API response.
    
    Args:
        agent_obj: Agent model instance
        include_sensitive: Whether to include sensitive data
        
    Returns:
        dict: Formatted agent data
    """
    if not agent_obj:
        return {}
    
    data = {
        'id': agent_obj.id,
        'name': f"{agent_obj.first_name} {agent_obj.last_name}",
        'first_name': agent_obj.first_name,
        'last_name': agent_obj.last_name,
        'license_number': agent_obj.license_number,
        'brokerage': agent_obj.brokerage,
        'phone': format_phone(agent_obj.phone),
        'email': agent_obj.email,
        'website': agent_obj.website,
        'bio': agent_obj.bio,
        'specialties': json.loads(agent_obj.specialties) if agent_obj.specialties else [],
        'languages': json.loads(agent_obj.languages) if agent_obj.languages else [],
        'profile_image': agent_obj.profile_image,
        'years_experience': agent_obj.years_experience,
        'total_sales': agent_obj.total_sales,
        'average_rating': agent_obj.average_rating,
        'review_count': agent_obj.review_count,
        'is_active': agent_obj.is_active,
        'created_at': agent_obj.created_at.isoformat() if agent_obj.created_at else None
    }
    
    # Add sensitive data if requested
    if include_sensitive:
        data.update({
            'commission_rate': agent_obj.commission_rate,
            'business_address': agent_obj.business_address,
            'emergency_contact': agent_obj.emergency_contact
        })
    
    return data


def format_user_data(user_obj: Any, include_sensitive: bool = False) -> Dict[str, Any]:
    """
    Format user data for API response.
    
    Args:
        user_obj: User model instance
        include_sensitive: Whether to include sensitive data
        
    Returns:
        dict: Formatted user data
    """
    if not user_obj:
        return {}
    
    data = {
        'id': user_obj.id,
        'username': user_obj.username,
        'email': user_obj.email,
        'first_name': user_obj.first_name,
        'last_name': user_obj.last_name,
        'phone': format_phone(user_obj.phone) if user_obj.phone else None,
        'profile_image': user_obj.profile_image,
        'preferences': json.loads(user_obj.preferences) if user_obj.preferences else {},
        'is_verified': user_obj.is_verified,
        'is_active': user_obj.is_active,
        'last_login': user_obj.last_login.isoformat() if user_obj.last_login else None,
        'created_at': user_obj.created_at.isoformat() if user_obj.created_at else None
    }
    
    # Add sensitive data if requested and user has permission
    if include_sensitive:
        data.update({
            'date_of_birth': user_obj.date_of_birth.isoformat() if user_obj.date_of_birth else None,
            'address': user_obj.address,
            'emergency_contact': user_obj.emergency_contact,
            'notification_settings': json.loads(user_obj.notification_settings) if user_obj.notification_settings else {}
        })
    
    return data


def format_api_response(data: Any, message: str = None, status: str = 'success', 
                       meta: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Format standardized API response.
    
    Args:
        data: Response data
        message: Response message
        status: Response status
        meta: Additional metadata
        
    Returns:
        dict: Formatted API response
    """
    response = {
        'status': status,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    
    if message:
        response['message'] = message
    
    if meta:
        response['meta'] = meta
    
    return response


def format_error_response(error: str, code: str = None, details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Format error response.
    
    Args:
        error: Error message
        code: Error code
        details: Additional error details
        
    Returns:
        dict: Formatted error response
    """
    response = {
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat(),
        'error': {
            'message': error
        }
    }
    
    if code:
        response['error']['code'] = code
    
    if details:
        response['error']['details'] = details
    
    return response


def format_validation_errors(errors: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Format validation errors.
    
    Args:
        errors: Validation errors dictionary
        
    Returns:
        dict: Formatted validation errors
    """
    return {
        'status': 'error',
        'timestamp': datetime.utcnow().isoformat(),
        'error': {
            'message': 'Validation failed',
            'code': 'VALIDATION_ERROR',
            'validation_errors': errors
        }
    }


def format_economic_data(economic_data: Any) -> Dict[str, Any]:
    """
    Format economic data for API response.
    
    Args:
        economic_data: Economic data model instance
        
    Returns:
        dict: Formatted economic data
    """
    if not economic_data:
        return {}
    
    return {
        'id': economic_data.id,
        'indicator_name': economic_data.indicator_name,
        'value': economic_data.value,
        'unit': economic_data.unit,
        'date': economic_data.date.isoformat() if economic_data.date else None,
        'frequency': economic_data.frequency,
        'source': economic_data.source,
        'region': economic_data.region,
        'category': economic_data.category,
        'seasonal_adjustment': economic_data.seasonal_adjustment,
        'last_updated': economic_data.last_updated.isoformat() if economic_data.last_updated else None
    }


# Helper functions for calculations
def _calculate_avg_price(properties: List[Any]) -> Optional[str]:
    """Calculate average price from property list."""
    if not properties:
        return None
    
    prices = [float(prop.price) for prop in properties if prop.price]
    if not prices:
        return None
    
    avg_price = sum(prices) / len(prices)
    return format_currency(avg_price)


def _calculate_price_range(properties: List[Any]) -> Dict[str, Optional[str]]:
    """Calculate price range from property list."""
    if not properties:
        return {'min': None, 'max': None}
    
    prices = [float(prop.price) for prop in properties if prop.price]
    if not prices:
        return {'min': None, 'max': None}
    
    return {
        'min': format_currency(min(prices)),
        'max': format_currency(max(prices))
    }


def _get_property_types_summary(properties: List[Any]) -> Dict[str, int]:
    """Get property types summary from property list."""
    if not properties:
        return {}
    
    types_count = {}
    for prop in properties:
        prop_type = prop.property_type
        if prop_type:
            types_count[prop_type] = types_count.get(prop_type, 0) + 1
    
    return types_count
