"""
Enhanced Rate Limit Error Handler for NextProperty AI
Handles abuse detection and all rate limiting scenarios with user-friendly responses.
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from flask import (
    request, jsonify, render_template, current_app, g, 
    has_request_context, make_response
)
from werkzeug.exceptions import TooManyRequests

logger = logging.getLogger(__name__)


class EnhancedRateLimitErrorHandler:
    """Enhanced error handler for rate limiting with comprehensive abuse detection support."""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(f"{__name__}.EnhancedRateLimitErrorHandler")
        
        # Abuse type mappings to user-friendly messages
        self.abuse_type_messages = {
            'resource_exhaustion': {
                'title': 'System Resources Overloaded',
                'message': 'Our servers are currently experiencing high load. Please wait and try again.',
                'icon': '⚡',
                'color': '#ff6b6b',
                'guidance': 'Reduce request frequency and wait for the specified time before retrying.'
            },
            'rapid_requests': {
                'title': 'Too Many Requests',
                'message': 'You are making requests too quickly. Please slow down.',
                'icon': '🚀',
                'color': '#ffa726',
                'guidance': 'Space out your requests and avoid rapid-fire API calls.'
            },
            'brute_force': {
                'title': 'Suspicious Login Activity',
                'message': 'Multiple failed authentication attempts detected.',
                'icon': '🔒',
                'color': '#e74c3c',
                'guidance': 'Verify your credentials and contact support if you need help.'
            },
            'scraping': {
                'title': 'Automated Activity Detected',
                'message': 'Automated data collection is not permitted.',
                'icon': '🤖',
                'color': '#9b59b6',
                'guidance': 'Use our official API for data access or contact us for legitimate business needs.'
            },
            'api_abuse': {
                'title': 'API Usage Limit Exceeded',
                'message': 'Your API usage has exceeded acceptable limits.',
                'icon': '📡',
                'color': '#3498db',
                'guidance': 'Review our API documentation for proper usage patterns.'
            },
            'suspicious_patterns': {
                'title': 'Unusual Activity Detected',
                'message': 'Unusual request patterns have been detected from your account.',
                'icon': '🔍',
                'color': '#f39c12',
                'guidance': 'If this is legitimate traffic, please contact our support team.'
            }
        }
        
        # Severity level configurations
        self.severity_configs = {
            1: {'retry_multiplier': 1.0, 'base_retry': 300, 'max_retry': 900},     # 5-15 minutes
            2: {'retry_multiplier': 1.5, 'base_retry': 600, 'max_retry': 1800},   # 10-30 minutes
            3: {'retry_multiplier': 2.0, 'base_retry': 900, 'max_retry': 3600},   # 15-60 minutes
            4: {'retry_multiplier': 3.0, 'base_retry': 1800, 'max_retry': 7200},  # 30-120 minutes
            5: {'retry_multiplier': 4.0, 'base_retry': 3600, 'max_retry': 14400}  # 60-240 minutes
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handler with Flask application."""
        self.app = app
        self.register_handlers(app)
    
    def register_handlers(self, app):
        """Register all error handlers with the Flask application."""
        
        @app.errorhandler(429)
        def handle_rate_limit_error(error):
            """Handle 429 Too Many Requests errors."""
            return self.handle_abuse_detection_error(error)
        
        @app.errorhandler(TooManyRequests)
        def handle_flask_limiter_error(error):
            """Handle Flask-Limiter TooManyRequests exceptions."""
            return self.handle_flask_limiter_error(error)
    
    def handle_abuse_detection_error(self, error_data):
        """
        Handle abuse detection rate limit errors.
        
        Args:
            error_data: Can be an exception, dict, or direct parameters
        """
        
        # Parse error data from various sources
        if isinstance(error_data, dict):
            # Direct abuse detection response (like the one you received)
            abuse_type = error_data.get('abuse_type', 'unknown')
            retry_after = error_data.get('retry_after', 300)
            level = error_data.get('level', 1)
            incident_id = error_data.get('incident_id')
        elif hasattr(error_data, 'abuse_type'):
            # Custom abuse detection error object
            abuse_type = error_data.abuse_type
            retry_after = error_data.retry_after
            level = getattr(error_data, 'level', 1)
            incident_id = getattr(error_data, 'incident_id', None)
        else:
            # Generic error - apply default abuse detection handling
            abuse_type = 'resource_exhaustion'
            retry_after = 300
            level = 1
            incident_id = int(time.time())
        
        # Get configuration for this abuse type
        abuse_config = self.abuse_type_messages.get(
            abuse_type, 
            self.abuse_type_messages['resource_exhaustion']
        )
        
        # Log the incident
        self.logger.warning(
            f"Abuse detection triggered - Type: {abuse_type}, Level: {level}, "
            f"Retry After: {retry_after}s, Incident: {incident_id}"
        )
        
        # Create response based on request type
        if self._is_api_request():
            return self._create_api_error_response(
                abuse_type, abuse_config, retry_after, level, incident_id
            )
        else:
            return self._create_web_error_response(
                abuse_type, abuse_config, retry_after, level, incident_id
            )
    
    def handle_flask_limiter_error(self, error):
        """Handle Flask-Limiter errors."""
        retry_after = getattr(error, 'retry_after', 60)
        
        # Treat as rate limiting rather than abuse
        if self._is_api_request():
            return jsonify({
                'error': True,
                'error_code': 'RATE_LIMIT_EXCEEDED',
                'type': 'rate_limit',
                'message': 'Rate limit exceeded',
                'retry_after': retry_after,
                'timestamp': datetime.utcnow().isoformat()
            }), 429
        else:
            return self._create_web_error_response(
                'rate_limit', 
                {
                    'title': 'Rate Limit Exceeded',
                    'message': 'You have exceeded the allowed request rate.',
                    'icon': '⏱️',
                    'color': '#2196f3',
                    'guidance': 'Please wait before making more requests.'
                },
                retry_after, 
                1, 
                None
            )
    
    def _is_api_request(self):
        """Determine if the request is an API request."""
        return (
            request.is_json or 
            request.path.startswith('/api/') or
            'application/json' in request.headers.get('Accept', '')
        )
    
    def _create_api_error_response(self, abuse_type, abuse_config, retry_after, level, incident_id):
        """Create JSON API error response."""
        response_data = {
            'error': True,
            'error_code': 'ABUSE_RATE_LIMIT',
            'type': 'abuse_rate_limit',
            'abuse_type': abuse_type,
            'level': level,
            'message': abuse_config['message'],
            'retry_after': retry_after,
            'retry_after_human': self._format_time_duration(retry_after),
            'incident_id': incident_id,
            'timestamp': datetime.utcnow().isoformat(),
            'guidance': abuse_config['guidance'],
            'support': {
                'contact': 'support@nextproperty.ai',
                'documentation': 'https://docs.nextproperty.ai/rate-limits',
                'appeal_process': 'https://docs.nextproperty.ai/appeals'
            }
        }
        
        response = jsonify(response_data)
        response.status_code = 429
        response.headers['Retry-After'] = str(retry_after)
        response.headers['X-RateLimit-Type'] = 'abuse_detection'
        response.headers['X-RateLimit-Abuse-Type'] = abuse_type
        response.headers['X-RateLimit-Level'] = str(level)
        response.headers['X-Incident-ID'] = str(incident_id) if incident_id else ''
        
        return response
    
    def _create_web_error_response(self, abuse_type, abuse_config, retry_after, level, incident_id):
        """Create HTML web error response."""
        try:
            response = make_response(
                render_template(
                    'errors/enhanced_rate_limit.html',
                    abuse_type=abuse_type,
                    title=abuse_config['title'],
                    message=abuse_config['message'],
                    icon=abuse_config['icon'],
                    color=abuse_config['color'],
                    guidance=abuse_config['guidance'],
                    retry_after=retry_after,
                    retry_after_human=self._format_time_duration(retry_after),
                    level=level,
                    incident_id=incident_id,
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    severity_description=self._get_severity_description(level),
                    next_action=self._get_next_action(abuse_type, level)
                )
            )
        except Exception as e:
            # Fallback to built-in template or simple response
            self.logger.error(f"Failed to render enhanced template: {e}")
            response = make_response(
                self._get_fallback_html_response(abuse_config, retry_after, incident_id)
            )
        
        response.status_code = 429
        response.headers['Retry-After'] = str(retry_after)
        response.headers['X-RateLimit-Type'] = 'abuse_detection'
        response.headers['X-RateLimit-Abuse-Type'] = abuse_type
        response.headers['X-RateLimit-Level'] = str(level)
        if incident_id:
            response.headers['X-Incident-ID'] = str(incident_id)
        
        return response
    
    def _format_time_duration(self, seconds):
        """Format seconds into human-readable duration."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds > 0:
                return f"{minutes} minutes and {remaining_seconds} seconds"
            return f"{minutes} minutes"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes > 0:
                return f"{hours} hours and {remaining_minutes} minutes"
            return f"{hours} hours"
    
    def _get_severity_description(self, level):
        """Get human-readable severity description."""
        descriptions = {
            1: 'Low severity - Minor rate limit violation',
            2: 'Medium severity - Moderate rate limit violation',
            3: 'High severity - Significant rate limit violation',
            4: 'Very High severity - Serious abuse detected',
            5: 'Critical severity - Severe abuse requiring immediate action'
        }
        return descriptions.get(level, 'Unknown severity level')
    
    def _get_next_action(self, abuse_type, level):
        """Get recommended next action based on abuse type and level."""
        if level >= 4:
            return "Contact our support team if you believe this is an error."
        elif abuse_type == 'brute_force':
            return "Verify your credentials and ensure you're using the correct login information."
        elif abuse_type in ['scraping', 'api_abuse']:
            return "Review our API documentation and ensure you're following rate limit guidelines."
        else:
            return "Wait for the specified time period and then retry your request."
    
    def _get_fallback_html_response(self, abuse_config, retry_after, incident_id):
        """Generate a simple HTML fallback response."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rate Limit Exceeded - NextProperty AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .icon {{
                    font-size: 48px;
                    margin-bottom: 20px;
                }}
                .title {{
                    color: {abuse_config['color']};
                    margin-bottom: 15px;
                }}
                .message {{
                    color: #666;
                    margin-bottom: 20px;
                    line-height: 1.5;
                }}
                .retry-info {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .incident-id {{
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">{abuse_config['icon']}</div>
                <h1 class="title">{abuse_config['title']}</h1>
                <p class="message">{abuse_config['message']}</p>
                <div class="retry-info">
                    <strong>Please wait {self._format_time_duration(retry_after)} before retrying.</strong>
                </div>
                <p>{abuse_config['guidance']}</p>
                {f'<div class="incident-id">Incident ID: {incident_id}</div>' if incident_id else ''}
            </div>
            <script>
                // Auto-refresh after retry period
                setTimeout(function() {{
                    window.location.reload();
                }}, {retry_after * 1000});
            </script>
        </body>
        </html>
        """


# Global instance
enhanced_rate_limit_handler = EnhancedRateLimitErrorHandler()
