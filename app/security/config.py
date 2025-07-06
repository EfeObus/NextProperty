"""
Security configuration for NextProperty AI.
"""

# CSRF Protection Configuration
CSRF_SETTINGS = {
    'CSRF_ENABLED': True,
    'CSRF_SESSION_KEY': '_csrf_token',
    'CSRF_TIME_LIMIT': 3600,  # 1 hour
    'CSRF_DISABLE_VALIDATION': False,
    'CSRF_CHECK_DEFAULT': True,
    'WTF_CSRF_CHECK_DEFAULT': True,
    'WTF_CSRF_TIME_LIMIT': 3600,
    'WTF_CSRF_SSL_STRICT': True,
    'WTF_CSRF_ENABLED': True
}

# XSS Protection Configuration
XSS_SETTINGS = {
    'XSS_PROTECTION_ENABLED': True,
    'HTML_SANITIZATION_ENABLED': True,
    'ALLOWED_HTML_TAGS': [
        'p', 'br', 'strong', 'em', 'u', 'b', 'i',
        'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre', 'div', 'span'
    ],
    'ALLOWED_HTML_ATTRIBUTES': {
        '*': ['class', 'id'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'blockquote': ['cite'],
        'code': ['class'],
        'div': ['class', 'id'],
        'span': ['class', 'id']
    },
    'MAX_INPUT_LENGTH': 10000,
    'VALIDATE_INPUT_PATTERNS': True
}

# Content Security Policy Configuration
CSP_SETTINGS = {
    'CONTENT_SECURITY_POLICY_ENABLED': True,
    'CSP_DEFAULT_SRC': ["'self'"],
    'CSP_SCRIPT_SRC': [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "https://unpkg.com",
        "https://maps.googleapis.com"
    ],
    'CSP_STYLE_SRC': [
        "'self'",
        "'unsafe-inline'",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "https://unpkg.com",
        "https://fonts.googleapis.com"
    ],
    'CSP_FONT_SRC': [
        "'self'",
        "https://fonts.gstatic.com",
        "https://cdnjs.cloudflare.com"
    ],
    'CSP_IMG_SRC': [
        "'self'",
        "data:",
        "https:",
        "blob:"
    ],
    'CSP_CONNECT_SRC': [
        "'self'",
        "https://api.numlookupapi.com"
    ],
    'CSP_FRAME_SRC': [
        "'self'",
        "https://maps.google.com"
    ],
    'CSP_OBJECT_SRC': ["'none'"],
    'CSP_BASE_URI': ["'self'"]
}

# Security Headers Configuration
SECURITY_HEADERS = {
    'X_XSS_PROTECTION': '1; mode=block',
    'X_CONTENT_TYPE_OPTIONS': 'nosniff',
    'X_FRAME_OPTIONS': 'SAMEORIGIN',
    'REFERRER_POLICY': 'strict-origin-when-cross-origin',
    'PERMISSIONS_POLICY': (
        'geolocation=(), microphone=(), camera=(), '
        'payment=(), usb=(), magnetometer=(), gyroscope=()'
    ),
    'STRICT_TRANSPORT_SECURITY': 'max-age=31536000; includeSubDomains',
    'X_PERMITTED_CROSS_DOMAIN_POLICIES': 'none'
}

# Input Validation Configuration
VALIDATION_SETTINGS = {
    'MAX_FORM_DATA_SIZE': 16 * 1024 * 1024,  # 16MB
    'MAX_JSON_SIZE': 1024 * 1024,  # 1MB
    'MAX_STRING_LENGTH': 10000,
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_FILE_EXTENSIONS': {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt'],
        'data': ['.csv', '.xlsx', '.json']
    },
    'VALIDATE_FILE_SIGNATURES': True,
    'SCAN_UPLOADS_FOR_MALWARE': False  # Set to True in production
}

# Rate Limiting Configuration
RATE_LIMITING = {
    'ENABLED': True,
    'GLOBAL_RATE_LIMIT': '1000 per hour',
    'API_RATE_LIMIT': '100 per minute',
    'AUTH_RATE_LIMIT': '10 per minute',
    'UPLOAD_RATE_LIMIT': '5 per minute',
    'STORAGE_URI': 'redis://localhost:6379',
    'STRATEGY': 'fixed-window'
}

# Session Security Configuration
SESSION_SETTINGS = {
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'PERMANENT_SESSION_LIFETIME': 3600,  # 1 hour
    'SESSION_REFRESH_EACH_REQUEST': True,
    'SESSION_PROTECTION': 'strong'
}

# Logging and Monitoring Configuration
SECURITY_LOGGING = {
    'LOG_SECURITY_EVENTS': True,
    'LOG_FAILED_AUTH_ATTEMPTS': True,
    'LOG_SUSPICIOUS_ACTIVITY': True,
    'LOG_XSS_ATTEMPTS': True,
    'LOG_CSRF_FAILURES': True,
    'ALERT_ON_MULTIPLE_FAILURES': True,
    'ALERT_THRESHOLD': 5,
    'ALERT_TIME_WINDOW': 300  # 5 minutes
}

# Whitelist Configuration
SECURITY_WHITELIST = {
    'TRUSTED_HOSTS': [
        'localhost',
        '127.0.0.1',
        'nextproperty.ai',
        '*.nextproperty.ai'
    ],
    'TRUSTED_PROXIES': [],
    'ALLOWED_ORIGINS': [
        'https://nextproperty.ai',
        'https://www.nextproperty.ai'
    ],
    'BYPASS_PATHS': [
        '/health',
        '/metrics',
        '/static'
    ]
}

def get_security_config():
    """
    Get complete security configuration.
    
    Returns:
        dict: Complete security configuration
    """
    config = {}
    config.update(CSRF_SETTINGS)
    config.update(XSS_SETTINGS)
    config.update(CSP_SETTINGS)
    config.update(VALIDATION_SETTINGS)
    config.update(SESSION_SETTINGS)
    config.update(SECURITY_LOGGING)
    
    return config


def get_csp_header():
    """
    Generate Content Security Policy header.
    
    Returns:
        str: CSP header value
    """
    policies = []
    
    # Default source
    policies.append(f"default-src {' '.join(CSP_SETTINGS['CSP_DEFAULT_SRC'])}")
    
    # Script source
    policies.append(f"script-src {' '.join(CSP_SETTINGS['CSP_SCRIPT_SRC'])}")
    
    # Style source
    policies.append(f"style-src {' '.join(CSP_SETTINGS['CSP_STYLE_SRC'])}")
    
    # Font source
    policies.append(f"font-src {' '.join(CSP_SETTINGS['CSP_FONT_SRC'])}")
    
    # Image source
    policies.append(f"img-src {' '.join(CSP_SETTINGS['CSP_IMG_SRC'])}")
    
    # Connect source
    policies.append(f"connect-src {' '.join(CSP_SETTINGS['CSP_CONNECT_SRC'])}")
    
    # Frame source
    policies.append(f"frame-src {' '.join(CSP_SETTINGS['CSP_FRAME_SRC'])}")
    
    # Object source
    policies.append(f"object-src {' '.join(CSP_SETTINGS['CSP_OBJECT_SRC'])}")
    
    # Base URI
    policies.append(f"base-uri {' '.join(CSP_SETTINGS['CSP_BASE_URI'])}")
    
    return '; '.join(policies)


def is_safe_url(url: str, host: str) -> bool:
    """
    Check if URL is safe for redirects.
    
    Args:
        url: URL to check
        host: Trusted host
        
    Returns:
        bool: True if URL is safe
    """
    if not url:
        return False
    
    # Import here to avoid circular imports
    from urllib.parse import urlparse, urljoin
    
    # Parse the URL
    parsed = urlparse(urljoin(host, url))
    
    # Check if it's a relative URL or same host
    return not parsed.netloc or parsed.netloc == host


def validate_file_upload(file, allowed_extensions: list = None) -> tuple:
    """
    Validate uploaded file for security.
    
    Args:
        file: Uploaded file object
        allowed_extensions: List of allowed file extensions
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file or not file.filename:
        return False, "No file provided"
    
    # Check file extension
    if allowed_extensions:
        file_ext = '.' + file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in allowed_extensions:
            return False, f"File type not allowed: {file_ext}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > VALIDATION_SETTINGS['MAX_FILE_SIZE']:
        return False, "File too large"
    
    # Additional security checks would go here
    # - File signature validation
    # - Malware scanning
    # - Content analysis
    
    return True, None
