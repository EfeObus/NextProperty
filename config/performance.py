"""
Performance configuration for NextProperty AI.
Apply these settings to maximize application performance.
"""

# Template performance improvements
TEMPLATE_AUTO_RELOAD = False  # Disable in production
SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files

# Database query optimizations
SQLALCHEMY_RECORD_QUERIES = False  # Disable query logging in production
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_recycle': 300,
    'pool_pre_ping': True,
    'pool_timeout': 30,
    'echo': False,
    'connect_args': {
        'charset': 'utf8mb4',
        'connect_timeout': 30,
        'read_timeout': 30,
        'write_timeout': 30,
        'autocommit': False
    }
}

# Caching configuration
CACHE_TYPE = 'simple'  # Use Redis in production
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
CACHE_THRESHOLD = 1000  # Maximum number of cached items

# Application performance settings
PROPERTIES_PER_PAGE = 12  # Reduced pagination
MAX_SEARCH_RESULTS = 100
QUERY_TIMEOUT = 30
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload

# Security optimizations
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Static file optimizations
STATIC_FOLDER = 'static'
STATIC_URL_PATH = '/static'
