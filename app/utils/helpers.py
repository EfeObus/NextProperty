"""
Helper utilities for NextProperty AI platform.
"""

import uuid
import re
import math
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, date
from decimal import Decimal
import phonenumbers
from geopy.distance import geodesic
import html
import json


def generate_uuid() -> str:
    """
    Generate a new UUID string.
    
    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())


def sanitize_input(text: str, max_length: int = None) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags and escape HTML entities
    text = html.escape(text.strip())
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\'\`]', '', text)
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def parse_coordinates(coord_string: str) -> Tuple[float, float]:
    """
    Parse coordinate string into latitude and longitude.
    
    Args:
        coord_string: Coordinate string (e.g., "43.6532,-79.3832")
        
    Returns:
        tuple: (latitude, longitude)
        
    Raises:
        ValueError: If coordinates cannot be parsed
    """
    try:
        parts = coord_string.split(',')
        if len(parts) != 2:
            raise ValueError("Invalid coordinate format")
        
        lat = float(parts[0].strip())
        lng = float(parts[1].strip())
        
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValueError("Coordinates out of valid range")
        
        return lat, lng
    except (ValueError, AttributeError, IndexError):
        raise ValueError("Unable to parse coordinates")


def format_currency(amount: Union[int, float, Decimal], currency: str = 'CAD') -> str:
    """
    Format currency amount.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: CAD)
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "N/A"
    
    try:
        amount = float(amount)
        if currency == 'CAD':
            return f"${amount:,.2f} CAD"
        elif currency == 'USD':
            return f"${amount:,.2f} USD"
        else:
            return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return "N/A"


def format_phone(phone: str, country: str = 'CA') -> str:
    """
    Format phone number for display.
    
    Args:
        phone: Phone number to format
        country: Country code (default: Canada)
        
    Returns:
        str: Formatted phone number
    """
    if not phone:
        return ""
    
    try:
        parsed_number = phonenumbers.parse(phone, country)
        if country == 'CA':
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        else:
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        return phone


def format_address(address_parts: Dict[str, str]) -> str:
    """
    Format address components into a readable string.
    
    Args:
        address_parts: Dictionary with address components
        
    Returns:
        str: Formatted address
    """
    parts = []
    
    if address_parts.get('street_number') and address_parts.get('street_name'):
        parts.append(f"{address_parts['street_number']} {address_parts['street_name']}")
    elif address_parts.get('address'):
        parts.append(address_parts['address'])
    
    if address_parts.get('unit'):
        parts[0] = f"Unit {address_parts['unit']}, {parts[0]}" if parts else f"Unit {address_parts['unit']}"
    
    if address_parts.get('city'):
        parts.append(address_parts['city'])
    
    if address_parts.get('province'):
        parts.append(address_parts['province'])
    
    if address_parts.get('postal_code'):
        parts.append(address_parts['postal_code'])
    
    return ', '.join(parts)


def calculate_distance(coord1: Tuple[float, float], coord2: Tuple[float, float], unit: str = 'km') -> float:
    """
    Calculate distance between two coordinates.
    
    Args:
        coord1: First coordinate (latitude, longitude)
        coord2: Second coordinate (latitude, longitude)
        unit: Distance unit ('km' or 'miles')
        
    Returns:
        float: Distance in specified unit
    """
    try:
        distance = geodesic(coord1, coord2)
        if unit == 'miles':
            return distance.miles
        else:
            return distance.kilometers
    except:
        return 0.0


def get_property_features(property_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and format property features.
    
    Args:
        property_data: Property data dictionary
        
    Returns:
        dict: Formatted property features
    """
    features = {
        'basic': {},
        'details': {},
        'financial': {},
        'location': {}
    }
    
    # Basic features
    basic_fields = ['bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'year_built', 'property_type']
    for field in basic_fields:
        if field in property_data and property_data[field] is not None:
            features['basic'][field] = property_data[field]
    
    # Property details
    detail_fields = ['garage_spaces', 'basement', 'pool', 'fireplace', 'air_conditioning', 'heating_type']
    for field in detail_fields:
        if field in property_data and property_data[field] is not None:
            features['details'][field] = property_data[field]
    
    # Financial information
    financial_fields = ['price', 'property_tax', 'monthly_fees', 'utilities_included']
    for field in financial_fields:
        if field in property_data and property_data[field] is not None:
            features['financial'][field] = property_data[field]
    
    # Location information
    location_fields = ['address', 'city', 'province', 'postal_code', 'neighborhood', 'school_district']
    for field in location_fields:
        if field in property_data and property_data[field] is not None:
            features['location'][field] = property_data[field]
    
    return features


def parse_amenities(amenities_string: str) -> List[str]:
    """
    Parse amenities string into a list.
    
    Args:
        amenities_string: Comma-separated amenities string
        
    Returns:
        list: List of amenities
    """
    if not amenities_string:
        return []
    
    amenities = [amenity.strip() for amenity in amenities_string.split(',')]
    return [amenity for amenity in amenities if amenity]


def get_neighborhood_info(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get neighborhood information based on coordinates.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        dict: Neighborhood information
    """
    # This would typically integrate with external APIs
    # For now, return a placeholder structure
    return {
        'walkability_score': None,
        'transit_score': None,
        'bike_score': None,
        'crime_rate': None,
        'school_rating': None,
        'nearby_amenities': [],
        'demographics': {}
    }


def calculate_roi(purchase_price: float, monthly_rent: float, monthly_expenses: float = 0, 
                 down_payment_percent: float = 0.2) -> Dict[str, float]:
    """
    Calculate return on investment for a property.
    
    Args:
        purchase_price: Property purchase price
        monthly_rent: Expected monthly rental income
        monthly_expenses: Monthly expenses (taxes, insurance, etc.)
        down_payment_percent: Down payment percentage (default: 20%)
        
    Returns:
        dict: ROI calculations
    """
    try:
        down_payment = purchase_price * down_payment_percent
        annual_rent = monthly_rent * 12
        annual_expenses = monthly_expenses * 12
        net_annual_income = annual_rent - annual_expenses
        
        # Cash-on-cash return
        cash_on_cash_return = (net_annual_income / down_payment) * 100 if down_payment > 0 else 0
        
        # Cap rate
        cap_rate = (net_annual_income / purchase_price) * 100
        
        # Gross yield
        gross_yield = (annual_rent / purchase_price) * 100
        
        # 1% rule check
        one_percent_rule = (monthly_rent / purchase_price) * 100
        
        return {
            'cash_on_cash_return': round(cash_on_cash_return, 2),
            'cap_rate': round(cap_rate, 2),
            'gross_yield': round(gross_yield, 2),
            'one_percent_rule': round(one_percent_rule, 4),
            'meets_one_percent': one_percent_rule >= 1.0,
            'annual_cash_flow': round(net_annual_income, 2),
            'monthly_cash_flow': round(net_annual_income / 12, 2)
        }
    except (ZeroDivisionError, TypeError, ValueError):
        return {
            'cash_on_cash_return': 0,
            'cap_rate': 0,
            'gross_yield': 0,
            'one_percent_rule': 0,
            'meets_one_percent': False,
            'annual_cash_flow': 0,
            'monthly_cash_flow': 0
        }


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a percentage value.
    
    Args:
        value: Percentage value
        decimals: Number of decimal places
        
    Returns:
        str: Formatted percentage
    """
    if value is None:
        return "N/A"
    
    try:
        return f"{value:.{decimals}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_square_feet(sqft: Union[int, float]) -> str:
    """
    Format square footage.
    
    Args:
        sqft: Square footage value
        
    Returns:
        str: Formatted square footage
    """
    if sqft is None:
        return "N/A"
    
    try:
        return f"{int(sqft):,} sq ft"
    except (ValueError, TypeError):
        return "N/A"


def format_lot_size(size: Union[int, float], unit: str = 'sqft') -> str:
    """
    Format lot size.
    
    Args:
        size: Lot size value
        unit: Size unit ('sqft', 'acres', 'hectares')
        
    Returns:
        str: Formatted lot size
    """
    if size is None:
        return "N/A"
    
    try:
        if unit == 'sqft':
            return f"{int(size):,} sq ft"
        elif unit == 'acres':
            return f"{size:.2f} acres"
        elif unit == 'hectares':
            return f"{size:.2f} hectares"
        else:
            return f"{size} {unit}"
    except (ValueError, TypeError):
        return "N/A"


def parse_json_safely(json_string: str) -> Dict[str, Any]:
    """
    Safely parse JSON string.
    
    Args:
        json_string: JSON string to parse
        
    Returns:
        dict: Parsed JSON or empty dict if parsing fails
    """
    if not json_string:
        return {}
    
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return {}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        dict: Merged dictionary
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result


def paginate_results(results: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """
    Paginate a list of results.
    
    Args:
        results: List of results to paginate
        page: Page number (1-based)
        per_page: Results per page
        
    Returns:
        dict: Paginated results with metadata
    """
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'results': results[start:end],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': math.ceil(total / per_page) if per_page > 0 else 1,
            'has_prev': page > 1,
            'has_next': end < total,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if end < total else None
        }
    }


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate a URL-friendly slug from text.
    
    Args:
        text: Text to convert to slug
        max_length: Maximum slug length
        
    Returns:
        str: URL-friendly slug
    """
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower() if text else "")
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading and trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug
