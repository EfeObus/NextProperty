"""
Security middleware for XSS and CSRF protection.
"""

from flask import request, g, session, current_app, abort, jsonify
from werkzeug.exceptions import BadRequest
import secrets
import re
from functools import wraps
from typing import Optional, Any, Dict
import bleach
import html
from markupsafe import Markup
import time


class SecurityMiddleware:
    """Middleware for comprehensive security protection."""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app."""
        app.config.setdefault('CSRF_TOKEN_EXPIRY', 3600)  # 1 hour
        app.config.setdefault('CSRF_SECRET_KEY', app.secret_key)
        app.config.setdefault('XSS_PROTECTION_ENABLED', True)
        app.config.setdefault('CONTENT_SECURITY_POLICY_ENABLED', True)
        
        # Register security headers
        app.after_request(add_security_headers)
        
        # Register template filters and functions (enhanced versions)
        app.jinja_env.filters['safe_html'] = enhanced_safe_html_filter
        app.jinja_env.filters['escape_js'] = enhanced_escape_js_filter
        app.jinja_env.globals['csrf_token'] = generate_enhanced_csrf_token
        app.jinja_env.globals['csrf_meta_tag'] = enhanced_csrf_meta_tag


class XSSProtection:
    """XSS Protection utilities."""
    
    # Allowed HTML tags for content sanitization
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'b', 'i',
        'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre', 'div', 'span'
    ]
    
    # Allowed attributes per tag
    ALLOWED_ATTRIBUTES = {
        '*': ['class', 'id'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'blockquote': ['cite'],
        'code': ['class'],
        'div': ['class', 'id'],
        'span': ['class', 'id']
    }
    
    @staticmethod
    def sanitize_html(content: str, allowed_tags: Optional[list] = None, 
                     allowed_attributes: Optional[dict] = None) -> str:
        """
        Sanitize HTML content to prevent XSS attacks.
        
        Args:
            content: HTML content to sanitize
            allowed_tags: List of allowed HTML tags
            allowed_attributes: Dictionary of allowed attributes per tag
            
        Returns:
            str: Sanitized HTML content
        """
        if not content:
            return ""
        
        if allowed_tags is None:
            allowed_tags = XSSProtection.ALLOWED_TAGS
        
        if allowed_attributes is None:
            allowed_attributes = XSSProtection.ALLOWED_ATTRIBUTES
        
        # Clean the content with bleach
        cleaned = bleach.clean(
            content, 
            tags=allowed_tags, 
            attributes=allowed_attributes,
            strip=True,
            strip_comments=True
        )
        
        return cleaned
    
    @staticmethod
    def escape_html(content: str) -> str:
        """
        Escape HTML special characters.
        
        Args:
            content: Content to escape
            
        Returns:
            str: HTML-escaped content
        """
        if not content:
            return ""
        
        return html.escape(str(content), quote=True)
    
    @staticmethod
    def escape_javascript(content: str) -> str:
        """
        Escape content for safe inclusion in JavaScript.
        
        Args:
            content: Content to escape
            
        Returns:
            str: JavaScript-safe content
        """
        if not content:
            return ""
        
        # Escape quotes and special characters
        content = str(content)
        content = content.replace('\\', '\\\\')
        content = content.replace('"', '\\"')
        content = content.replace("'", "\\'")
        content = content.replace('\n', '\\n')
        content = content.replace('\r', '\\r')
        content = content.replace('\t', '\\t')
        content = content.replace('<', '\\u003c')
        content = content.replace('>', '\\u003e')
        content = content.replace('&', '\\u0026')
        
        return content
    
    @staticmethod
    def validate_input(data: Any, max_length: int = 10000) -> bool:
        """
        Validate input for suspicious patterns.
        
        Args:
            data: Input data to validate
            max_length: Maximum allowed length
            
        Returns:
            bool: True if input is safe, False otherwise
        """
        if data is None:
            return True
        
        content = str(data)
        
        # Check length
        if len(content) > max_length:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'onfocus\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<applet[^>]*>',
            r'<meta[^>]*>',
            r'<link[^>]*>',
            r'<style[^>]*>.*?</style>',
            r'expression\s*\(',
            r'@import',
            r'document\.cookie',
            r'document\.write',
            r'window\.location',
            r'eval\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\('
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True


class CSRFProtection:
    """CSRF Protection utilities."""
    
    @staticmethod
    def generate_token() -> str:
        """
        Generate a CSRF token.
        
        Returns:
            str: CSRF token
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(token: str, session_token: str) -> bool:
        """
        Validate CSRF token.
        
        Args:
            token: Token from request
            session_token: Token from session
            
        Returns:
            bool: True if tokens match, False otherwise
        """
        if not token or not session_token:
            return False
        
        return secrets.compare_digest(token, session_token)
    
    @staticmethod
    def get_token_from_request() -> Optional[str]:
        """
        Get CSRF token from request.
        
        Returns:
            str: CSRF token or None
        """
        # Check form data
        token = request.form.get('csrf_token')
        if token:
            return token
        
        # Check headers
        token = request.headers.get('X-CSRFToken')
        if token:
            return token
        
        # Check JSON data
        if request.is_json:
            json_data = request.get_json(silent=True)
            if json_data and 'csrf_token' in json_data:
                return json_data['csrf_token']
        
        return None


def csrf_protect(f):
    """
    Decorator to protect routes with CSRF validation.
    
    Args:
        f: Function to protect
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Get tokens
            request_token = CSRFProtection.get_token_from_request()
            session_token = session.get('csrf_token')
            
            # Validate token
            if not CSRFProtection.validate_token(request_token, session_token):
                if request.is_json:
                    return jsonify({'error': 'CSRF token validation failed'}), 403
                else:
                    abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def xss_protect(f):
    """
    Decorator to protect routes with XSS validation.
    
    Args:
        f: Function to protect
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validate form data
        if request.form:
            for key, value in request.form.items():
                if not XSSProtection.validate_input(value):
                    current_app.logger.warning(f"XSS attempt detected in form field {key}")
                    if request.is_json:
                        return jsonify({'error': 'Invalid input detected'}), 400
                    else:
                        abort(400)
        
        # Validate JSON data
        if request.is_json:
            json_data = request.get_json(silent=True)
            if json_data:
                def validate_json_recursive(data):
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, (dict, list)):
                                validate_json_recursive(value)
                            elif not XSSProtection.validate_input(value):
                                return False
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, (dict, list)):
                                validate_json_recursive(item)
                            elif not XSSProtection.validate_input(item):
                                return False
                    return True
                
                if not validate_json_recursive(json_data):
                    current_app.logger.warning("XSS attempt detected in JSON data")
                    return jsonify({'error': 'Invalid input detected'}), 400
        
        return f(*args, **kwargs)
    
    return decorated_function


def add_security_headers(response):
    """
    Add security headers to response with enhanced CSP management.
    
    Args:
        response: Flask response object
        
    Returns:
        Modified response object
    """
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Type Options
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Frame Options
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Enhanced Content Security Policy
    if current_app.config.get('CONTENT_SECURITY_POLICY_ENABLED', True):
        # Check if enhanced CSP policy is available
        if hasattr(g, 'csp_policy'):
            try:
                from .enhanced_csp import csp_manager
                csp_header = csp_manager.policy_to_header(g.csp_policy)
                header_name = csp_manager.get_header_name(g.csp_policy)
                response.headers[header_name] = csp_header
            except ImportError:
                # Fallback to basic CSP
                csp = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                    "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                    "https://unpkg.com https://maps.googleapis.com; "
                    "style-src 'self' 'unsafe-inline' "
                    "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                    "https://unpkg.com https://fonts.googleapis.com; "
                    "font-src 'self' https://fonts.gstatic.com "
                    "https://cdnjs.cloudflare.com; "
                    "img-src 'self' data: https: blob:; "
                    "connect-src 'self' https://api.numlookupapi.com; "
                    "frame-src 'self' https://maps.google.com; "
                    "object-src 'none'; "
                    "base-uri 'self';"
                )
                response.headers['Content-Security-Policy'] = csp
        else:
            # Default CSP
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                "https://unpkg.com https://maps.googleapis.com; "
                "style-src 'self' 'unsafe-inline' "
                "https://cdn.jsdelivr.net https://cdnjs.cloudflare.com "
                "https://unpkg.com https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com "
                "https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https://api.numlookupapi.com; "
                "frame-src 'self' https://maps.google.com; "
                "object-src 'none'; "
                "base-uri 'self';"
            )
            response.headers['Content-Security-Policy'] = csp
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions Policy
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), '
        'payment=(), usb=(), magnetometer=(), gyroscope=()'
    )
    
    return response


def enhanced_xss_protect(f):
    """
    Enhanced XSS protection decorator using advanced threat analysis.
    
    Args:
        f: Function to protect
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            from .enhanced_integration import enhanced_security
            
            # Perform enhanced security analysis
            security_report = enhanced_security.analyze_request('public')
            
            # Store report in g for access in route
            g.security_report = security_report
            
            # Block critical threats
            if security_report.overall_threat_level.name == 'CRITICAL':
                current_app.logger.error(f"Critical XSS threat blocked: {security_report.recommendation}")
                if request.is_json:
                    return jsonify({'error': 'Request blocked due to security policy'}), 403
                else:
                    abort(403)
            
            # Log high threats
            if security_report.overall_threat_level.name == 'HIGH':
                current_app.logger.warning(f"High XSS threat detected: {security_report.recommendation}")
        
        except ImportError:
            # Fallback to standard XSS protection
            return xss_protect(f)(*args, **kwargs)
        except Exception as e:
            current_app.logger.error(f"Enhanced XSS protection error: {e}")
            # Continue with request but log the error
        
        return f(*args, **kwargs)
    
    return decorated_function


def enhanced_csrf_protect(f):
    """
    Enhanced CSRF protection with behavioral analysis.
    
    Args:
        f: Function to protect
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Standard CSRF validation first
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Get tokens
            request_token = CSRFProtection.get_token_from_request()
            session_token = session.get('csrf_token')
            
            # Validate token
            if not CSRFProtection.validate_token(request_token, session_token):
                current_app.logger.warning(f"CSRF token validation failed for IP: {request.remote_addr}")
                
                # Try enhanced behavioral analysis
                try:
                    from .enhanced_integration import enhanced_security
                    
                    # Check if this might be a legitimate request from behavioral perspective
                    security_report = enhanced_security.analyze_request('api')
                    
                    # If behavioral analysis shows very low risk, log but allow (with caution)
                    if (security_report.behavior_analysis and 
                        security_report.behavior_analysis.risk_score < 1.0 and
                        not security_report.behavior_analysis.patterns_detected):
                        current_app.logger.info("CSRF failed but low behavioral risk - potential legitimate request")
                    
                except ImportError:
                    pass
                
                if request.is_json:
                    return jsonify({'error': 'CSRF token validation failed'}), 403
                else:
                    abort(403)
        
        return f(*args, **kwargs)
    
    return decorated_function


# Enhanced template filters and functions
def enhanced_safe_html_filter(content):
    """
    Enhanced Jinja2 filter for safe HTML content using advanced sanitization.
    
    Args:
        content: Content to sanitize
        
    Returns:
        Markup: Safe HTML content
    """
    if not content:
        return Markup("")
    
    try:
        from .advanced_xss import advanced_xss, Context
        
        # Use advanced XSS analysis for sanitization
        analysis = advanced_xss.analyze_content(str(content), Context.HTML)
        
        if analysis.blocked:
            # Content is too dangerous, return empty
            return Markup("")
        else:
            # Use sanitized content
            return Markup(analysis.sanitized_content)
            
    except ImportError:
        # Fallback to standard sanitization
        return safe_html_filter(content)


def enhanced_escape_js_filter(content):
    """
    Enhanced Jinja2 filter for JavaScript-safe content.
    
    Args:
        content: Content to escape
        
    Returns:
        str: JavaScript-safe content
    """
    try:
        from .advanced_xss import advanced_xss, Context
        
        # Use advanced XSS analysis for JavaScript context
        analysis = advanced_xss.analyze_content(str(content), Context.JAVASCRIPT)
        
        if analysis.blocked:
            return ""  # Block dangerous content
        else:
            return analysis.sanitized_content
            
    except ImportError:
        # Fallback to standard escaping
        return escape_js_filter(content)


def generate_enhanced_csrf_token():
    """
    Generate CSRF token with enhanced tracking.
    
    Returns:
        str: CSRF token
    """
    token = generate_csrf_token()
    
    # Track token generation for behavioral analysis
    try:
        from .behavioral_analysis import behavioral_analyzer
        
        # This helps track token generation patterns
        if hasattr(g, 'security_report'):
            g.security_report.actions_taken.append("csrf_token_generated")
            
    except ImportError:
        pass
    
    return token


def enhanced_csrf_meta_tag():
    """
    Generate CSRF meta tag with nonce if available.
    
    Returns:
        Markup: CSRF meta tag
    """
    token = generate_enhanced_csrf_token()
    
    # Try to add nonce if CSP is active
    nonce_attr = ""
    try:
        from .enhanced_csp import csp_manager
        nonce = csp_manager.get_current_nonce()
        if nonce:
            nonce_attr = f' nonce="{nonce}"'
    except ImportError:
        pass
    
    return Markup(f'<meta name="csrf-token" content="{token}"{nonce_attr}>')


# Original template filters and functions (now enhanced versions available)
def safe_html_filter(content):
    """
    Jinja2 filter for safe HTML content.
    
    Args:
        content: Content to sanitize
        
    Returns:
        Markup: Safe HTML content
    """
    if not content:
        return Markup("")
    
    sanitized = XSSProtection.sanitize_html(str(content))
    return Markup(sanitized)


def escape_js_filter(content):
    """
    Jinja2 filter for JavaScript-safe content.
    
    Args:
        content: Content to escape
        
    Returns:
        str: JavaScript-safe content
    """
    return XSSProtection.escape_javascript(content)


def generate_csrf_token():
    """
    Generate and store CSRF token in session.
    
    Returns:
        str: CSRF token
    """
    if 'csrf_token' not in session:
        session['csrf_token'] = CSRFProtection.generate_token()
    
    return session['csrf_token']


def csrf_meta_tag():
    """
    Generate CSRF meta tag for HTML head.
    
    Returns:
        Markup: CSRF meta tag
    """
    token = generate_csrf_token()
    return Markup(f'<meta name="csrf-token" content="{token}">')


# Initialize security middleware instance
security_middleware = SecurityMiddleware()
