"""
Unit tests for utility functions and helpers.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal

from app.utils.validators import (
    validate_email, validate_phone, validate_postal_code,
    validate_price, validate_coordinates, validate_date_range
)
from app.utils.helpers import (
    generate_uuid, sanitize_input, parse_coordinates,
    format_currency, format_address, calculate_distance,
    extract_property_features, calculate_roi
)
from app.utils.security import (
    generate_password_hash, check_password_hash,
    generate_token, verify_token, sanitize_html,
    generate_api_key
)
from app.utils.formatters import (
    format_property_data, format_search_results,
    format_market_data, format_agent_data, format_user_data
)


class TestValidators:
    """Test cases for validation functions."""
    
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email('test@example.com') is True
        assert validate_email('user.name+tag@domain.co.uk') is True
        assert validate_email('user123@test-domain.com') is True
        
        # Invalid emails
        assert validate_email('invalid-email') is False
        assert validate_email('@domain.com') is False
        assert validate_email('user@') is False
        assert validate_email('') is False
        assert validate_email(None) is False
    
    def test_validate_phone(self):
        """Test phone number validation."""
        # Valid phone numbers
        assert validate_phone('+1234567890') is True
        assert validate_phone('+1 (234) 567-8900') is True
        assert validate_phone('234-567-8900') is True
        assert validate_phone('2345678900') is True
        
        # Invalid phone numbers
        assert validate_phone('123') is False
        assert validate_phone('invalid-phone') is False
        assert validate_phone('') is False
        assert validate_phone(None) is False
    
    def test_validate_postal_code(self):
        """Test postal code validation."""
        # Valid Canadian postal codes
        assert validate_postal_code('M5V 3A8') is True
        assert validate_postal_code('K1A0A6') is True
        assert validate_postal_code('m5v3a8') is True  # Case insensitive
        
        # Valid US ZIP codes
        assert validate_postal_code('12345') is True
        assert validate_postal_code('12345-6789') is True
        
        # Invalid postal codes
        assert validate_postal_code('invalid') is False
        assert validate_postal_code('12') is False
        assert validate_postal_code('') is False
        assert validate_postal_code(None) is False
    
    def test_validate_price(self):
        """Test price validation."""
        # Valid prices
        assert validate_price(100000) is True
        assert validate_price(500000.50) is True
        assert validate_price(Decimal('750000.00')) is True
        assert validate_price('250000') is True
        
        # Invalid prices
        assert validate_price(-1000) is False
        assert validate_price(0) is False
        assert validate_price('invalid') is False
        assert validate_price(None) is False
    
    def test_validate_coordinates(self):
        """Test coordinate validation."""
        # Valid coordinates
        assert validate_coordinates(43.6532, -79.3832) is True
        assert validate_coordinates(0, 0) is True
        assert validate_coordinates(90, 180) is True
        assert validate_coordinates(-90, -180) is True
        
        # Invalid coordinates
        assert validate_coordinates(91, 0) is False  # Latitude out of range
        assert validate_coordinates(0, 181) is False  # Longitude out of range
        assert validate_coordinates('invalid', 0) is False
        assert validate_coordinates(None, None) is False
    
    def test_validate_date_range(self):
        """Test date range validation."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Valid date range
        assert validate_date_range(start_date, end_date) is True
        assert validate_date_range(start_date, start_date) is True  # Same date
        
        # Invalid date range
        assert validate_date_range(end_date, start_date) is False  # End before start
        assert validate_date_range(None, end_date) is False
        assert validate_date_range(start_date, None) is False


class TestHelpers:
    """Test cases for helper functions."""
    
    def test_generate_uuid(self):
        """Test UUID generation."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        
        assert isinstance(uuid1, str)
        assert isinstance(uuid2, str)
        assert uuid1 != uuid2  # Should be unique
        assert len(uuid1) > 0
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Normal text should pass through
        assert sanitize_input('normal text') == 'normal text'
        
        # HTML should be stripped
        assert sanitize_input('<script>alert("xss")</script>') == 'alert("xss")'
        assert sanitize_input('<b>bold</b> text') == 'bold text'
        
        # SQL injection attempts should be handled
        dangerous_input = "'; DROP TABLE users; --"
        sanitized = sanitize_input(dangerous_input)
        assert sanitized != dangerous_input
    
    def test_parse_coordinates(self):
        """Test coordinate parsing."""
        # Valid coordinate strings
        lat, lng = parse_coordinates('43.6532,-79.3832')
        assert lat == 43.6532
        assert lng == -79.3832
        
        lat, lng = parse_coordinates('43.6532, -79.3832')  # With space
        assert lat == 43.6532
        assert lng == -79.3832
        
        # Invalid coordinate strings
        assert parse_coordinates('invalid') == (None, None)
        assert parse_coordinates('') == (None, None)
        assert parse_coordinates('43.6532') == (None, None)  # Missing longitude
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(500000) == '$500,000'
        assert format_currency(500000.50) == '$500,000.50'
        assert format_currency(Decimal('750000.00')) == '$750,000'
        assert format_currency(1000000) == '$1,000,000'
        
        # Test different currencies
        assert format_currency(500000, currency='EUR') == '€500,000'
        assert format_currency(500000, currency='GBP') == '£500,000'
    
    def test_format_address(self):
        """Test address formatting."""
        address_components = {
            'street': '123 Main St',
            'city': 'Toronto',
            'province': 'ON',
            'postal_code': 'M5V 3A8',
            'country': 'Canada'
        }
        
        formatted = format_address(address_components)
        assert '123 Main St' in formatted
        assert 'Toronto' in formatted
        assert 'ON' in formatted
        assert 'M5V 3A8' in formatted
    
    def test_calculate_distance(self):
        """Test distance calculation."""
        # Distance between Toronto and Vancouver
        distance = calculate_distance(
            43.6532, -79.3832,  # Toronto
            49.2827, -123.1207  # Vancouver
        )
        
        assert isinstance(distance, float)
        assert 3000 < distance < 4000  # Approximate distance in km
        
        # Distance between same point should be 0
        distance_same = calculate_distance(43.6532, -79.3832, 43.6532, -79.3832)
        assert distance_same == 0.0
    
    def test_extract_property_features(self):
        """Test property feature extraction."""
        property_data = {
            'description': 'Beautiful home with garage, hardwood floors, and garden',
            'features': ['parking', 'balcony']
        }
        
        features = extract_property_features(property_data)
        
        assert isinstance(features, list)
        assert 'garage' in features
        assert 'hardwood floors' in features
        assert 'garden' in features
        assert 'parking' in features
        assert 'balcony' in features
    
    def test_calculate_roi(self):
        """Test ROI calculation."""
        roi_data = calculate_roi(
            purchase_price=500000,
            rental_income=2500,
            monthly_expenses=800,
            annual_appreciation=0.05
        )
        
        assert 'monthly_cash_flow' in roi_data
        assert 'annual_cash_flow' in roi_data
        assert 'cap_rate' in roi_data
        assert 'total_annual_return' in roi_data
        
        assert roi_data['monthly_cash_flow'] == 1700  # 2500 - 800
        assert roi_data['annual_cash_flow'] == 20400  # 1700 * 12


class TestSecurity:
    """Test cases for security utilities."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = 'test_password123'
        
        # Hash password
        password_hash = generate_password_hash(password)
        assert password_hash is not None
        assert password_hash != password  # Should not be plain text
        
        # Verify correct password
        assert check_password_hash(password_hash, password) is True
        
        # Verify incorrect password
        assert check_password_hash(password_hash, 'wrong_password') is False
    
    def test_token_generation_and_verification(self):
        """Test token generation and verification."""
        data = {'user_id': 'user-123', 'email': 'test@example.com'}
        
        # Generate token
        token = generate_token(data)
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token
        verified_data = verify_token(token)
        assert verified_data is not None
        assert verified_data['user_id'] == 'user-123'
        assert verified_data['email'] == 'test@example.com'
        
        # Verify invalid token
        invalid_data = verify_token('invalid_token')
        assert invalid_data is None
    
    def test_html_sanitization(self):
        """Test HTML sanitization."""
        # Safe HTML should pass through
        safe_html = '<p>This is safe content</p>'
        sanitized = sanitize_html(safe_html)
        assert '<p>' in sanitized
        
        # Dangerous HTML should be stripped
        dangerous_html = '<script>alert("xss")</script><p>Content</p>'
        sanitized = sanitize_html(dangerous_html)
        assert '<script>' not in sanitized
        assert '<p>Content</p>' in sanitized
        
        # Test with complex dangerous content
        complex_dangerous = '<img src="x" onerror="alert(1)"><div onclick="steal()">Click me</div>'
        sanitized = sanitize_html(complex_dangerous)
        assert 'onerror' not in sanitized
        assert 'onclick' not in sanitized
    
    def test_api_key_generation(self):
        """Test API key generation."""
        api_key1 = generate_api_key()
        api_key2 = generate_api_key()
        
        assert isinstance(api_key1, str)
        assert isinstance(api_key2, str)
        assert api_key1 != api_key2  # Should be unique
        assert len(api_key1) >= 32  # Should be reasonably long


class TestFormatters:
    """Test cases for data formatters."""
    
    def test_format_property_data(self, sample_property):
        """Test property data formatting."""
        formatted = format_property_data(sample_property)
        
        assert 'id' in formatted
        assert 'title' in formatted
        assert 'price' in formatted
        assert 'formatted_price' in formatted
        assert 'bedrooms' in formatted
        assert 'bathrooms' in formatted
        assert 'address' in formatted
        assert 'agent' in formatted
        
        # Check that price is properly formatted
        assert isinstance(formatted['price'], (int, float))
        assert '$' in formatted['formatted_price']
    
    def test_format_search_results(self):
        """Test search results formatting."""
        mock_properties = [
            {
                'id': 'prop-1',
                'title': 'Property 1',
                'price': 500000,
                'city': 'Toronto'
            },
            {
                'id': 'prop-2',
                'title': 'Property 2',
                'price': 600000,
                'city': 'Vancouver'
            }
        ]
        
        formatted = format_search_results(mock_properties, total=2, page=1, per_page=10)
        
        assert 'results' in formatted
        assert 'pagination' in formatted
        assert 'summary' in formatted
        
        assert len(formatted['results']) == 2
        assert formatted['pagination']['total'] == 2
        assert formatted['pagination']['page'] == 1
    
    def test_format_market_data(self):
        """Test market data formatting."""
        market_data = {
            'average_price': 650000.0,
            'median_price': 580000.0,
            'total_properties': 1500,
            'price_change_1m': 0.02,
            'price_change_1y': 0.15
        }
        
        formatted = format_market_data(market_data, 'Toronto')
        
        assert 'city' in formatted
        assert 'average_price' in formatted
        assert 'formatted_average_price' in formatted
        assert 'price_trends' in formatted
        assert 'market_indicators' in formatted
        
        assert formatted['city'] == 'Toronto'
        assert '$' in formatted['formatted_average_price']
    
    def test_format_agent_data(self, sample_agent):
        """Test agent data formatting."""
        formatted = format_agent_data(sample_agent)
        
        assert 'id' in formatted
        assert 'name' in formatted
        assert 'email' in formatted
        assert 'phone' in formatted
        assert 'rating' in formatted
        assert 'experience_years' in formatted
        assert 'total_sales' in formatted
        
        # Should not include sensitive data
        assert 'password' not in formatted
        assert 'internal_notes' not in formatted
    
    def test_format_user_data(self, sample_user):
        """Test user data formatting."""
        formatted = format_user_data(sample_user)
        
        assert 'id' in formatted
        assert 'email' in formatted
        assert 'username' in formatted
        assert 'full_name' in formatted
        assert 'profile_completion' in formatted
        
        # Should not include sensitive data
        assert 'password_hash' not in formatted
        assert 'password' not in formatted


class TestCacheUtilities:
    """Test cases for cache utilities."""
    
    @pytest.fixture
    def mock_cache(self):
        """Mock cache for testing."""
        from unittest.mock import Mock
        cache = Mock()
        cache.get.return_value = None
        cache.set.return_value = True
        cache.delete.return_value = True
        return cache
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        from app.utils.cache import generate_cache_key
        
        key1 = generate_cache_key('properties', city='Toronto', type='house')
        key2 = generate_cache_key('properties', city='Vancouver', type='house')
        key3 = generate_cache_key('properties', city='Toronto', type='condo')
        
        assert key1 != key2  # Different cities
        assert key1 != key3  # Different types
        assert isinstance(key1, str)
    
    def test_cache_ttl_calculation(self):
        """Test cache TTL calculation."""
        from app.utils.cache import calculate_ttl
        
        # High priority data should have longer TTL
        ttl_high = calculate_ttl('high')
        ttl_medium = calculate_ttl('medium')
        ttl_low = calculate_ttl('low')
        
        assert ttl_high > ttl_medium > ttl_low
        assert all(isinstance(ttl, int) for ttl in [ttl_high, ttl_medium, ttl_low])


class TestErrorHandling:
    """Test cases for error handling utilities."""
    
    def test_custom_exceptions(self):
        """Test custom exception classes."""
        from app.utils.errors import ValidationError, AuthenticationError, APIError
        
        # ValidationError
        validation_error = ValidationError("Invalid input", field="email")
        assert str(validation_error) == "Invalid input"
        assert validation_error.field == "email"
        
        # AuthenticationError
        auth_error = AuthenticationError("Invalid credentials")
        assert str(auth_error) == "Invalid credentials"
        
        # APIError
        api_error = APIError("External API failed", status_code=503)
        assert str(api_error) == "External API failed"
        assert api_error.status_code == 503
    
    def test_error_logging(self):
        """Test error logging functionality."""
        from app.utils.errors import log_error
        from unittest.mock import patch
        
        with patch('app.utils.errors.logger') as mock_logger:
            error = Exception("Test error")
            log_error(error, context={'user_id': 'user-123'})
            
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert 'Test error' in str(call_args)
            assert 'user-123' in str(call_args)
