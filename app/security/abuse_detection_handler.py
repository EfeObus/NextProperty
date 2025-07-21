"""
Abuse Detection Response Handler
Specifically handles the JSON response format you received from the abuse detection system.
"""

from flask import request, jsonify
from app.security.enhanced_rate_limit_error_handler import enhanced_rate_limit_handler


def handle_abuse_detection_response(response_data):
    """
    Handle the specific abuse detection response format.
    
    Example response:
    {
        "abuse_type": "resource_exhaustion",
        "error": "Request blocked due to abuse detection",
        "incident_id": 1753105363.67304,
        "level": 4,
        "retry_after": 504,
        "type": "abuse_rate_limit"
    }
    """
    return enhanced_rate_limit_handler.handle_abuse_detection_error(response_data)


def create_abuse_detection_middleware():
    """
    Create middleware to intercept and handle abuse detection responses.
    This can be used to automatically handle abuse detection throughout the app.
    """
    def abuse_detection_middleware(response):
        # Check if response contains abuse detection data
        if (response.status_code == 429 and 
            response.is_json and 
            hasattr(response, 'json') and 
            response.json.get('type') == 'abuse_rate_limit'):
            
            # Handle the abuse detection response
            return handle_abuse_detection_response(response.json)
        
        return response
    
    return abuse_detection_middleware


def simulate_abuse_detection_error():
    """
    Simulate the abuse detection error you received for testing purposes.
    """
    test_abuse_data = {
        "abuse_type": "resource_exhaustion",
        "error": "Request blocked due to abuse detection",
        "incident_id": 1753105363.67304,
        "level": 4,
        "retry_after": 504,
        "type": "abuse_rate_limit"
    }
    
    return handle_abuse_detection_response(test_abuse_data)


# Flask route for testing the abuse detection error page
def register_test_routes(app):
    """Register test routes for abuse detection error handling."""
    
    @app.route('/test/abuse-detection')
    def test_abuse_detection():
        """Test route to see the abuse detection error page."""
        return simulate_abuse_detection_error()
    
    @app.route('/test/abuse-detection/<abuse_type>')
    def test_specific_abuse_type(abuse_type):
        """Test route for specific abuse types."""
        test_data = {
            "abuse_type": abuse_type,
            "error": f"Request blocked due to {abuse_type} detection",
            "incident_id": 1753105363.67304,
            "level": 3,
            "retry_after": 300,
            "type": "abuse_rate_limit"
        }
        return handle_abuse_detection_response(test_data)
    
    @app.route('/test/abuse-detection/api')
    def test_abuse_detection_api():
        """Test API response for abuse detection."""
        test_data = {
            "abuse_type": "resource_exhaustion",
            "error": "Request blocked due to abuse detection",
            "incident_id": 1753105363.67304,
            "level": 4,
            "retry_after": 504,
            "type": "abuse_rate_limit"
        }
        
        # Simulate API request
        request.environ['CONTENT_TYPE'] = 'application/json'
        return handle_abuse_detection_response(test_data)
