"""
Comprehensive Error Handlers for Rate Limiting Features
NextProperty AI Platform

This module provides specialized error handling for all rate limiting scenarios,
including proper HTTP responses, logging, monitoring, and user feedback.
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from flask import (
    request, jsonify, render_template, current_app, g, 
    has_request_context, session, redirect, url_for
)
from werkzeug.exceptions import TooManyRequests
from app.error_handling import BaseApplicationError
from app.security.rate_limiter import RateLimitExceeded

logger = logging.getLogger(__name__)


class RateLimitError(BaseApplicationError):
    """Base class for rate limiting errors."""
    
    def __init__(self, message: str, limit_type: str = 'unknown', 
                 retry_after: int = 60, endpoint: str = None, 
                 client_id: str = None, details: Dict[str, Any] = None):
        super().__init__(message, 'RATE_LIMIT_ERROR', details)
        self.limit_type = limit_type
        self.retry_after = retry_after
        self.endpoint = endpoint
        self.client_id = client_id


class GlobalRateLimitError(RateLimitError):
    """Error for global rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, details: Dict[str, Any] = None):
        super().__init__(
            "Global rate limit exceeded. Too many requests across the platform.",
            limit_type='global',
            retry_after=retry_after,
            details=details
        )


class IPRateLimitError(RateLimitError):
    """Error for IP-based rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, ip_address: str = None, 
                 details: Dict[str, Any] = None):
        super().__init__(
            f"IP rate limit exceeded for {ip_address or 'unknown IP'}.",
            limit_type='ip',
            retry_after=retry_after,
            details=details or {'ip_address': ip_address}
        )


class UserRateLimitError(RateLimitError):
    """Error for user-specific rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, user_id: str = None, 
                 details: Dict[str, Any] = None):
        super().__init__(
            f"User rate limit exceeded for user {user_id or 'unknown'}.",
            limit_type='user',
            retry_after=retry_after,
            details=details or {'user_id': user_id}
        )


class EndpointRateLimitError(RateLimitError):
    """Error for endpoint-specific rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, endpoint: str = None, 
                 details: Dict[str, Any] = None):
        super().__init__(
            f"Endpoint rate limit exceeded for {endpoint or 'unknown endpoint'}.",
            limit_type='endpoint',
            retry_after=retry_after,
            endpoint=endpoint,
            details=details
        )


class BurstRateLimitError(RateLimitError):
    """Error for burst protection rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, details: Dict[str, Any] = None):
        super().__init__(
            "Burst rate limit exceeded. Too many requests in a short time.",
            limit_type='burst',
            retry_after=retry_after,
            details=details
        )


class CategoryRateLimitError(RateLimitError):
    """Error for category-specific rate limit exceeded."""
    
    def __init__(self, category: str, retry_after: int = 60, 
                 details: Dict[str, Any] = None):
        super().__init__(
            f"{category.title()} rate limit exceeded.",
            limit_type='category',
            retry_after=retry_after,
            details=details or {'category': category}
        )


class APIRateLimitError(CategoryRateLimitError):
    """Error for API rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, api_key: str = None, 
                 details: Dict[str, Any] = None):
        super().__init__(
            'api',
            retry_after=retry_after,
            details=details or {'api_key': api_key}
        )
        self.message = "API rate limit exceeded. Please reduce request frequency."


class AuthRateLimitError(CategoryRateLimitError):
    """Error for authentication rate limit exceeded."""
    
    def __init__(self, retry_after: int = 300, details: Dict[str, Any] = None):
        super().__init__(
            'auth',
            retry_after=retry_after,
            details=details
        )
        self.message = "Authentication rate limit exceeded. Too many login attempts."


class UploadRateLimitError(CategoryRateLimitError):
    """Error for upload rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, details: Dict[str, Any] = None):
        super().__init__(
            'upload',
            retry_after=retry_after,
            details=details
        )
        self.message = "Upload rate limit exceeded. Please wait before uploading again."


class SearchRateLimitError(CategoryRateLimitError):
    """Error for search rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60, details: Dict[str, Any] = None):
        super().__init__(
            'search',
            retry_after=retry_after,
            details=details
        )
        self.message = "Search rate limit exceeded. Please reduce search frequency."


class AbuseDetectionRateLimitError(RateLimitError):
    """Error for abuse detection rate limit exceeded."""
    
    def __init__(self, abuse_type: str, confidence: float, retry_after: int = 300, 
                 details: Dict[str, Any] = None):
        super().__init__(
            f"Request blocked due to suspected abuse: {abuse_type}.",
            limit_type='abuse_detection',
            retry_after=retry_after,
            details=details or {'abuse_type': abuse_type, 'confidence': confidence}
        )
        self.abuse_type = abuse_type
        self.confidence = confidence


class GeographicRateLimitError(RateLimitError):
    """Error for geographic rate limit exceeded."""
    
    def __init__(self, location: str, retry_after: int = 60, 
                 details: Dict[str, Any] = None):
        super().__init__(
            f"Geographic rate limit exceeded for {location}.",
            limit_type='geographic',
            retry_after=retry_after,
            details=details or {'location': location}
        )
        self.location = location


class RateLimitErrorHandler:
    """Comprehensive handler for all rate limiting errors."""
    
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger(f"{__name__}.RateLimitErrorHandler")
        
        # Error response templates
        self.error_templates = {
            'api': self._create_api_response,
            'web': self._create_web_response,
            'mobile': self._create_mobile_response
        }
        
        # Rate limit metrics for monitoring
        self.metrics = {
            'total_blocks': 0,
            'blocks_by_type': {},
            'blocks_by_endpoint': {},
            'recent_blocks': []
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize error handler with Flask app."""
        self.app = app
        
        # Register error handlers
        self._register_error_handlers(app)
        
        # Set up monitoring hooks
        self._setup_monitoring_hooks(app)
        
        self.logger.info("Rate limit error handlers initialized")
    
    def register_handlers(self):
        """Public method to register error handlers."""
        if self.app:
            self._register_error_handlers(self.app)
            self._setup_monitoring_hooks(self.app)
        else:
            raise RuntimeError("No Flask app instance available. Call init_app() first.")
    
    def handle_rate_limit_error(self, error: RateLimitError):
        """Public method to handle rate limit errors."""
        return self._handle_custom_rate_limit_error(error)
    
    def _register_error_handlers(self, app):
        """Register all rate limit error handlers."""
        
        # Handle RateLimitExceeded from rate_limiter.py
        @app.errorhandler(RateLimitExceeded)
        def handle_rate_limit_exceeded(error):
            return self._handle_rate_limit_exceeded(error)
        
        # Handle Flask-Limiter TooManyRequests
        @app.errorhandler(TooManyRequests)
        def handle_too_many_requests(error):
            return self._handle_too_many_requests(error)
        
        # Handle 429 status code directly
        @app.errorhandler(429)
        def handle_429_error(error):
            return self._handle_429_error(error)
        
        # Handle custom rate limit errors
        for error_class in [
            GlobalRateLimitError, IPRateLimitError, UserRateLimitError,
            EndpointRateLimitError, BurstRateLimitError, CategoryRateLimitError,
            APIRateLimitError, AuthRateLimitError, UploadRateLimitError,
            SearchRateLimitError, AbuseDetectionRateLimitError, GeographicRateLimitError
        ]:
            app.errorhandler(error_class)(self._handle_custom_rate_limit_error)
    
    def _setup_monitoring_hooks(self, app):
        """Set up monitoring and metrics collection."""
        
        @app.before_request
        def track_rate_limit_context():
            """Track context for rate limit monitoring."""
            g.rate_limit_start_time = time.time()
            g.rate_limit_context = {
                'endpoint': request.endpoint,
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'user_id': getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
            }
        
        @app.after_request
        def log_rate_limit_metrics(response):
            """Log rate limit metrics after request."""
            if response.status_code == 429:
                self._log_rate_limit_incident(response)
            return response
    
    def _handle_rate_limit_exceeded(self, error: RateLimitExceeded):
        """Handle RateLimitExceeded from rate limiter."""
        self.logger.warning(
            f"Rate limit exceeded: {error.limit_type} - {error.message}",
            extra={'retry_after': error.retry_after, 'limit_type': error.limit_type}
        )
        
        return self._create_rate_limit_response(
            message=error.message,
            limit_type=error.limit_type,
            retry_after=error.retry_after
        )
    
    def _handle_too_many_requests(self, error):
        """Handle Flask-Limiter TooManyRequests."""
        retry_after = getattr(error, 'retry_after', 60)
        
        self.logger.warning(
            f"Flask-Limiter rate limit exceeded",
            extra={'retry_after': retry_after}
        )
        
        return self._create_rate_limit_response(
            message="Rate limit exceeded",
            limit_type="flask_limiter",
            retry_after=retry_after
        )
    
    def _handle_429_error(self, error):
        """Handle generic 429 errors."""
        self.logger.warning(f"429 error: {error}")
        
        return self._create_rate_limit_response(
            message="Too many requests",
            limit_type="generic",
            retry_after=60
        )
    
    def _handle_custom_rate_limit_error(self, error: RateLimitError):
        """Handle custom rate limit errors."""
        self.logger.warning(
            f"Custom rate limit error: {error.__class__.__name__} - {error.message}",
            extra={
                'limit_type': error.limit_type,
                'retry_after': error.retry_after,
                'endpoint': error.endpoint,
                'client_id': error.client_id,
                'details': error.details
            }
        )
        
        return self._create_rate_limit_response(
            message=error.message,
            limit_type=error.limit_type,
            retry_after=error.retry_after,
            details=error.details
        )
    
    def _create_rate_limit_response(self, message: str, limit_type: str, 
                                  retry_after: int, details: Dict[str, Any] = None):
        """Create appropriate rate limit response based on request type."""
        
        # Update metrics
        self._update_metrics(limit_type, retry_after)
        
        # Determine response type
        response_type = self._determine_response_type()
        
        # Create response headers
        headers = self._create_response_headers(limit_type, retry_after)
        
        # Create response based on type
        if response_type == 'api':
            response = self._create_api_response(message, limit_type, retry_after, details)
        elif response_type == 'mobile':
            response = self._create_mobile_response(message, limit_type, retry_after, details)
        else:
            response = self._create_web_response(message, limit_type, retry_after, details)
        
        # Add headers
        for header, value in headers.items():
            response.headers[header] = value
        
        return response
    
    def _determine_response_type(self) -> str:
        """Determine the appropriate response type."""
        if request.is_json or request.path.startswith('/api/'):
            return 'api'
        elif 'mobile' in request.headers.get('User-Agent', '').lower():
            return 'mobile'
        else:
            return 'web'
    
    def _create_response_headers(self, limit_type: str, retry_after: int) -> Dict[str, str]:
        """Create standard rate limit response headers."""
        return {
            'Retry-After': str(retry_after),
            'X-RateLimit-Type': limit_type,
            'X-RateLimit-Retry-After': str(retry_after),
            'X-RateLimit-Reset': str(int(time.time()) + retry_after),
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    
    def _create_api_response(self, message: str, limit_type: str, 
                           retry_after: int, details: Dict[str, Any] = None):
        """Create JSON API response for rate limit."""
        response_data = {
            'error': True,
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'message': message,
            'limit_type': limit_type,
            'retry_after': retry_after,
            'retry_after_human': self._format_retry_time(retry_after),
            'timestamp': datetime.utcnow().isoformat(),
            'documentation': 'https://docs.nextproperty.ai/rate-limits'
        }
        
        if details:
            response_data['details'] = details
        
        # Add helpful guidance based on limit type
        response_data['guidance'] = self._get_guidance_for_limit_type(limit_type)
        
        response = jsonify(response_data)
        response.status_code = 429
        return response
    
    def _create_web_response(self, message: str, limit_type: str, 
                           retry_after: int, details: Dict[str, Any] = None):
        """Create HTML web response for rate limit."""
        try:
            response = current_app.make_response(
                render_template(
                    'errors/rate_limit.html',
                    message=message,
                    limit_type=limit_type,
                    retry_after=retry_after,
                    retry_after_human=self._format_retry_time(retry_after),
                    current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    guidance=self._get_guidance_for_limit_type(limit_type),
                    details=details or {}
                )
            )
        except Exception as e:
            # Fallback to simple response if template fails
            self.logger.error(f"Failed to render rate limit template: {e}")
            response = current_app.make_response(
                self._get_fallback_html_response(message, retry_after)
            )
        
        response.status_code = 429
        return response
    
    def _create_mobile_response(self, message: str, limit_type: str, 
                              retry_after: int, details: Dict[str, Any] = None):
        """Create mobile-optimized response for rate limit."""
        # For mobile, we'll use JSON but with mobile-specific guidance
        response_data = {
            'error': True,
            'error_code': 'RATE_LIMIT_EXCEEDED',
            'message': message,
            'limit_type': limit_type,
            'retry_after': retry_after,
            'retry_after_human': self._format_retry_time(retry_after),
            'mobile_guidance': self._get_mobile_guidance_for_limit_type(limit_type),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if details:
            response_data['details'] = details
        
        response = jsonify(response_data)
        response.status_code = 429
        return response
    
    def _format_retry_time(self, retry_after: int) -> str:
        """Format retry time in human-readable format."""
        if retry_after < 60:
            return f"{retry_after} seconds"
        elif retry_after < 3600:
            minutes = retry_after // 60
            seconds = retry_after % 60
            return f"{minutes} minute{'s' if minutes != 1 else ''}" + \
                   (f" and {seconds} second{'s' if seconds != 1 else ''}" if seconds > 0 else "")
        else:
            hours = retry_after // 3600
            minutes = (retry_after % 3600) // 60
            return f"{hours} hour{'s' if hours != 1 else ''}" + \
                   (f" and {minutes} minute{'s' if minutes != 1 else ''}" if minutes > 0 else "")
    
    def _get_guidance_for_limit_type(self, limit_type: str) -> str:
        """Get user guidance based on limit type."""
        guidance = {
            'global': "The system is experiencing high load. Please reduce your request frequency.",
            'ip': "Your IP address has made too many requests. Please wait before trying again.",
            'user': "Your user account has exceeded the rate limit. Please wait before making more requests.",
            'endpoint': "This specific endpoint has been accessed too frequently. Try using other features.",
            'burst': "You're making requests too quickly. Please add delays between your requests.",
            'api': "API rate limit exceeded. Consider implementing request batching or caching.",
            'auth': "Too many authentication attempts. Please wait before trying to log in again.",
            'upload': "Upload limit exceeded. Please wait before uploading more files.",
            'search': "Search limit exceeded. Please refine your searches or wait before searching again.",
            'abuse_detection': "Suspicious activity detected. Please contact support if you believe this is an error.",
            'geographic': "Geographic rate limit exceeded for your region. Please try again later."
        }
        return guidance.get(limit_type, "Rate limit exceeded. Please wait before trying again.")
    
    def _get_mobile_guidance_for_limit_type(self, limit_type: str) -> str:
        """Get mobile-specific user guidance based on limit type."""
        guidance = {
            'global': "High system load. Please wait and try again.",
            'ip': "Too many requests from your device. Please wait.",
            'user': "Account rate limit reached. Please wait.",
            'endpoint': "Feature temporarily limited. Try other features.",
            'burst': "Slow down your requests. Add delays between actions.",
            'api': "API limit reached. Reduce request frequency.",
            'auth': "Too many login attempts. Please wait.",
            'upload': "Upload limit reached. Please wait.",
            'search': "Search limit reached. Please wait.",
            'abuse_detection': "Suspicious activity detected. Contact support if needed.",
            'geographic': "Regional limit reached. Please try again later."
        }
        return guidance.get(limit_type, "Rate limit reached. Please wait.")
    
    def _get_fallback_html_response(self, message: str, retry_after: int) -> str:
        """Get fallback HTML response when template rendering fails."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rate Limit Exceeded - NextProperty AI</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .error-code {{ font-size: 2em; color: #ff6b6b; margin-bottom: 20px; }}
                .message {{ font-size: 1.2em; margin-bottom: 20px; }}
                .retry-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-code">429 - Rate Limit Exceeded</div>
                <div class="message">{message}</div>
                <div class="retry-info">
                    <p>Please wait {self._format_retry_time(retry_after)} before trying again.</p>
                    <p>If you continue to experience issues, please contact support.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _update_metrics(self, limit_type: str, retry_after: int):
        """Update rate limit metrics for monitoring."""
        self.metrics['total_blocks'] += 1
        
        if limit_type not in self.metrics['blocks_by_type']:
            self.metrics['blocks_by_type'][limit_type] = 0
        self.metrics['blocks_by_type'][limit_type] += 1
        
        endpoint = request.endpoint or request.path
        if endpoint not in self.metrics['blocks_by_endpoint']:
            self.metrics['blocks_by_endpoint'][endpoint] = 0
        self.metrics['blocks_by_endpoint'][endpoint] += 1
        
        # Keep recent blocks for analysis (last 100)
        self.metrics['recent_blocks'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'limit_type': limit_type,
            'retry_after': retry_after,
            'endpoint': endpoint,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')[:100]  # Truncate
        })
        
        # Keep only last 100 entries
        if len(self.metrics['recent_blocks']) > 100:
            self.metrics['recent_blocks'] = self.metrics['recent_blocks'][-100:]
    
    def _log_rate_limit_incident(self, response):
        """Log rate limit incident for monitoring and analysis."""
        context = getattr(g, 'rate_limit_context', {})
        
        incident_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'status_code': response.status_code,
            'endpoint': context.get('endpoint'),
            'method': context.get('method'),
            'ip': context.get('ip'),
            'user_agent': context.get('user_agent'),
            'user_id': context.get('user_id'),
            'response_headers': dict(response.headers),
            'request_duration': time.time() - getattr(g, 'rate_limit_start_time', time.time())
        }
        
        self.logger.info(
            "Rate limit incident",
            extra=incident_data
        )
        
        # Log to security logger if it's a potential abuse case
        if response.headers.get('X-RateLimit-Type') in ['abuse_detection', 'burst']:
            security_logger = logging.getLogger('security')
            security_logger.warning(
                f"Potential abuse detected: {incident_data['ip']} at {incident_data['endpoint']}",
                extra=incident_data
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current rate limit metrics."""
        return {
            'total_blocks': self.metrics['total_blocks'],
            'blocks_by_type': dict(self.metrics['blocks_by_type']),
            'blocks_by_endpoint': dict(self.metrics['blocks_by_endpoint']),
            'recent_blocks_count': len(self.metrics['recent_blocks']),
            'top_blocked_endpoints': self._get_top_blocked_endpoints(),
            'top_blocked_types': self._get_top_blocked_types()
        }
    
    def _get_top_blocked_endpoints(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get top blocked endpoints."""
        return sorted(
            self.metrics['blocks_by_endpoint'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def _get_top_blocked_types(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get top blocked limit types."""
        return sorted(
            self.metrics['blocks_by_type'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def clear_metrics(self):
        """Clear all metrics (for testing or reset)."""
        self.metrics = {
            'total_blocks': 0,
            'blocks_by_type': {},
            'blocks_by_endpoint': {},
            'recent_blocks': []
        }
        self.logger.info("Rate limit metrics cleared")


# Utility functions for specific rate limit scenarios

def handle_api_key_rate_limit(api_key: str, requests_per_hour: int, 
                             current_usage: int) -> APIRateLimitError:
    """Handle API key rate limit scenarios."""
    retry_after = 3600  # 1 hour
    details = {
        'api_key': api_key[:8] + '...' if api_key else 'unknown',
        'requests_per_hour': requests_per_hour,
        'current_usage': current_usage,
        'limit_reset': datetime.utcnow() + timedelta(hours=1)
    }
    return APIRateLimitError(retry_after=retry_after, details=details)


def handle_geographic_rate_limit(country: str, region: str = None, 
                                city: str = None) -> GeographicRateLimitError:
    """Handle geographic rate limit scenarios."""
    location_parts = [city, region, country]
    location = ', '.join(filter(None, location_parts))
    
    details = {
        'country': country,
        'region': region,
        'city': city,
        'location_string': location
    }
    return GeographicRateLimitError(location=location, details=details)


def handle_abuse_detection_rate_limit(abuse_type: str, confidence: float, 
                                     severity: str = 'medium') -> AbuseDetectionRateLimitError:
    """Handle abuse detection rate limit scenarios."""
    # Determine retry time based on severity
    retry_times = {
        'low': 60,      # 1 minute
        'medium': 300,  # 5 minutes
        'high': 900,    # 15 minutes
        'critical': 3600  # 1 hour
    }
    
    retry_after = retry_times.get(severity, 300)
    
    details = {
        'abuse_type': abuse_type,
        'confidence': confidence,
        'severity': severity,
        'detection_time': datetime.utcnow().isoformat()
    }
    
    return AbuseDetectionRateLimitError(
        abuse_type=abuse_type,
        confidence=confidence,
        retry_after=retry_after,
        details=details
    )


# Global instance
rate_limit_error_handler = RateLimitErrorHandler()


def init_rate_limit_error_handlers(app):
    """Initialize rate limit error handlers with the Flask app."""
    rate_limit_error_handler.init_app(app)
    return rate_limit_error_handler
