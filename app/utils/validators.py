"""
Validation utilities for NextProperty AI platform.
"""

import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
import phonenumbers
from phonenumbers import NumberParseException
from werkzeug.datastructures import FileStorage


class ValidationError(Exception):
    """Custom validation error exception."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If email is invalid
    """
    if not email or not isinstance(email, str):
        raise ValidationError("Email is required", "email")
    
    email = email.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format", "email")
    
    if len(email) > 254:
        raise ValidationError("Email too long", "email")
    
    return True


def validate_phone(phone: str, country: str = 'CA') -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        country: Country code (default: Canada)
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If phone number is invalid
    """
    if not phone or not isinstance(phone, str):
        raise ValidationError("Phone number is required", "phone")
    
    try:
        parsed_number = phonenumbers.parse(phone, country)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError("Invalid phone number", "phone")
        return True
    except NumberParseException:
        raise ValidationError("Invalid phone number format", "phone")


def validate_postal_code(postal_code: str, country: str = 'CA') -> bool:
    """
    Validate postal code format.
    
    Args:
        postal_code: Postal code to validate
        country: Country code (default: Canada)
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If postal code is invalid
    """
    if not postal_code or not isinstance(postal_code, str):
        raise ValidationError("Postal code is required", "postal_code")
    
    postal_code = postal_code.strip().upper().replace(' ', '')
    
    if country == 'CA':
        # Canadian postal code format: A1A1A1
        pattern = r'^[A-Z]\d[A-Z]\d[A-Z]\d$'
        if not re.match(pattern, postal_code):
            raise ValidationError("Invalid Canadian postal code format", "postal_code")
    elif country == 'US':
        # US ZIP code format: 12345 or 12345-6789
        pattern = r'^\d{5}(-\d{4})?$'
        if not re.match(pattern, postal_code):
            raise ValidationError("Invalid US ZIP code format", "postal_code")
    
    return True


def validate_price(price: Union[str, int, float, Decimal], min_price: float = 0, max_price: float = 100000000) -> bool:
    """
    Validate property price.
    
    Args:
        price: Price to validate
        min_price: Minimum allowed price
        max_price: Maximum allowed price
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If price is invalid
    """
    if price is None:
        raise ValidationError("Price is required", "price")
    
    try:
        price_decimal = Decimal(str(price))
        if price_decimal < min_price:
            raise ValidationError(f"Price must be at least ${min_price:,.2f}", "price")
        if price_decimal > max_price:
            raise ValidationError(f"Price cannot exceed ${max_price:,.2f}", "price")
        return True
    except (InvalidOperation, ValueError):
        raise ValidationError("Invalid price format", "price")


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate geographic coordinates.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If coordinates are invalid
    """
    if latitude is None or longitude is None:
        raise ValidationError("Coordinates are required", "coordinates")
    
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if not (-90 <= lat <= 90):
            raise ValidationError("Latitude must be between -90 and 90", "latitude")
        if not (-180 <= lng <= 180):
            raise ValidationError("Longitude must be between -180 and 180", "longitude")
        
        return True
    except (ValueError, TypeError):
        raise ValidationError("Invalid coordinate format", "coordinates")


def validate_date_range(start_date: Union[str, date, datetime], 
                       end_date: Union[str, date, datetime]) -> bool:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If date range is invalid
    """
    try:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date).date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
            
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date).date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        
        if start_date > end_date:
            raise ValidationError("Start date cannot be after end date", "date_range")
        
        # Check if dates are not too far in the future
        today = date.today()
        max_future_date = date(today.year + 10, today.month, today.day)
        
        if start_date > max_future_date or end_date > max_future_date:
            raise ValidationError("Dates cannot be more than 10 years in the future", "date_range")
        
        return True
    except (ValueError, TypeError):
        raise ValidationError("Invalid date format", "date_range")


def validate_property_type(property_type: str) -> bool:
    """
    Validate property type.
    
    Args:
        property_type: Property type to validate
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If property type is invalid
    """
    valid_types = {
        'house', 'condo', 'townhouse', 'apartment', 'duplex', 'triplex',
        'fourplex', 'mobile_home', 'manufactured_home', 'land', 'commercial',
        'office', 'retail', 'warehouse', 'industrial', 'mixed_use', 'other'
    }
    
    if not property_type or not isinstance(property_type, str):
        raise ValidationError("Property type is required", "property_type")
    
    if property_type.lower() not in valid_types:
        raise ValidationError(f"Invalid property type. Must be one of: {', '.join(valid_types)}", "property_type")
    
    return True


def validate_file_upload(file: FileStorage, allowed_extensions: List[str] = None, 
                        max_size: int = 3 * 1024 * 1024) -> bool:
    """
    Validate file upload.
    
    Args:
        file: Uploaded file
        allowed_extensions: List of allowed file extensions
        max_size: Maximum file size in bytes (default: 3MB)
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If file is invalid
    """
    if not file or not file.filename:
        raise ValidationError("File is required", "file")
    
    if allowed_extensions is None:
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx']
    
    # Check file extension
    filename = file.filename.lower() if file.filename else ""
    if '.' not in filename:
        raise ValidationError("File must have an extension", "file")
    
    extension = filename.rsplit('.', 1)[1]
    if extension not in allowed_extensions:
        raise ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}", "file")
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if size > max_size:
        raise ValidationError(f"File too large. Maximum size: {max_size / (1024 * 1024):.1f}MB", "file")
    
    return True


def validate_property_photos(files: List[FileStorage], max_photos: int = 20, 
                            max_size_per_photo: int = 3 * 1024 * 1024) -> bool:
    """
    Validate property photo uploads.
    
    Args:
        files: List of uploaded photo files
        max_photos: Maximum number of photos allowed (default: 20)
        max_size_per_photo: Maximum size per photo in bytes (default: 3MB)
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValidationError: If photos are invalid
    """
    if len(files) > max_photos:
        raise ValidationError(f"Too many photos. Maximum allowed: {max_photos}", "photos")
    
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    
    for i, file in enumerate(files):
        if not file or not file.filename:
            continue  # Skip empty file inputs
            
        try:
            validate_file_upload(file, allowed_extensions, max_size_per_photo)
        except ValidationError as e:
            raise ValidationError(f"Photo {i+1}: {str(e)}", "photos")
    
    return True


def validate_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize search parameters.
    
    Args:
        params: Search parameters dictionary
        
    Returns:
        dict: Validated and sanitized parameters
        
    Raises:
        ValidationError: If parameters are invalid
    """
    validated = {}
    
    # Price range validation
    if 'min_price' in params and params['min_price'] is not None:
        try:
            validated['min_price'] = max(0, float(params['min_price']))
        except (ValueError, TypeError):
            raise ValidationError("Invalid minimum price", "min_price")
    
    if 'max_price' in params and params['max_price'] is not None:
        try:
            validated['max_price'] = min(100000000, float(params['max_price']))
        except (ValueError, TypeError):
            raise ValidationError("Invalid maximum price", "max_price")
    
    # Bedrooms and bathrooms validation
    for field in ['bedrooms', 'bathrooms']:
        if field in params and params[field] is not None:
            try:
                value = int(params[field])
                if value < 0 or value > 20:
                    raise ValidationError(f"Invalid {field} count", field)
                validated[field] = value
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid {field} format", field)
    
    # Square footage validation
    for field in ['min_sqft', 'max_sqft']:
        if field in params and params[field] is not None:
            try:
                value = float(params[field])
                if value < 0 or value > 50000:
                    raise ValidationError(f"Invalid {field}", field)
                validated[field] = value
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid {field} format", field)
    
    # Property type validation
    if 'property_type' in params and params['property_type']:
        try:
            validate_property_type(params['property_type'])
            validated['property_type'] = params['property_type'].lower() if params['property_type'] else None
        except ValidationError:
            raise
    
    # Location validation
    if 'city' in params and params['city']:
        validated['city'] = params['city'].strip()
    
    if 'province' in params and params['province']:
        validated['province'] = params['province'].strip()
    
    if 'postal_code' in params and params['postal_code']:
        try:
            validate_postal_code(params['postal_code'])
            validated['postal_code'] = params['postal_code'].strip().upper().replace(' ', '')
        except ValidationError:
            raise
    
    # Sort validation
    valid_sorts = ['price_asc', 'price_desc', 'date_asc', 'date_desc', 'sqft_asc', 'sqft_desc']
    if 'sort' in params and params['sort']:
        if params['sort'] not in valid_sorts:
            raise ValidationError(f"Invalid sort option. Must be one of: {', '.join(valid_sorts)}", "sort")
        validated['sort'] = params['sort']
    
    # Page and limit validation
    if 'page' in params:
        try:
            validated['page'] = max(1, int(params['page']))
        except (ValueError, TypeError):
            validated['page'] = 1
    
    if 'limit' in params:
        try:
            validated['limit'] = min(100, max(1, int(params['limit'])))
        except (ValueError, TypeError):
            validated['limit'] = 20
    
    return validated


def validate_user_input(data: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
    """
    Validate user input data.
    
    Args:
        data: Input data dictionary
        required_fields: List of required field names
        
    Returns:
        dict: Validated data
        
    Raises:
        ValidationError: If validation fails
    """
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}", "required_fields")
    
    validated = {}
    
    # Copy and sanitize string fields
    for key, value in data.items():
        if isinstance(value, str):
            validated[key] = value.strip()
        else:
            validated[key] = value
    
    return validated
