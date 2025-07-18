import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database Configuration - Updated for Docker MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,              # Reduced for Docker container
        'max_overflow': 20,           # Reduced overflow connections
        'pool_recycle': 3600,         # Increased for stability
        'pool_pre_ping': True,
        'pool_timeout': 60,           # Increased timeout for Docker
        'echo': False,                # Disable SQL logging
        'connect_args': {
            'charset': 'utf8mb4',
            'connect_timeout': 60,    # Increased for Docker
            'read_timeout': 60,       # Increased for Docker  
            'write_timeout': 60,      # Increased for Docker
            'autocommit': False,
            'sql_mode': 'TRADITIONAL'
        }
    }
    
    # Performance Configuration
    PROPERTIES_PER_PAGE = 12      # Reduced from 20 for faster loading
    MAX_SEARCH_RESULTS = 100      # Limit search results
    QUERY_TIMEOUT = 30            # Query timeout in seconds
    
    # API Keys
    BANK_OF_CANADA_API_KEY = os.environ.get('BANK_OF_CANADA_API_KEY')
    STATISTICS_CANADA_API_KEY = os.environ.get('STATISTICS_CANADA_API_KEY')
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # ML Model Configuration
    MODEL_PATH = os.environ.get('MODEL_PATH', 'models/trained_models/')
    MODEL_VERSION = os.environ.get('MODEL_VERSION', '1.0')
    PREDICTION_CACHE_TTL = int(os.environ.get('PREDICTION_CACHE_TTL', 3600))
    
    # Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))
    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))
    
    # External APIs
    BOC_API_BASE_URL = os.environ.get('BOC_API_BASE_URL', 'https://www.bankofcanada.ca/valet')
    STATCAN_API_BASE_URL = os.environ.get('STATCAN_API_BASE_URL', 'https://www150.statcan.gc.ca/t1/wds/rest')
    EXTERNAL_API_TIMEOUT = int(os.environ.get('EXTERNAL_API_TIMEOUT', 30))
    API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))
    
    # Caching
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.environ.get('CACHE_REDIS_PORT', 6379))
    CACHE_REDIS_DB = int(os.environ.get('CACHE_REDIS_DB', 0))
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Redis Configuration for Rate Limiting
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 1))  # Use different DB for rate limiting
    
    # Rate Limiting Configuration
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_STORAGE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Import rate limiting configuration
    from app.security.rate_limit_config import (
        RATE_LIMIT_DEFAULTS, RATE_LIMIT_SENSITIVE, RATE_LIMIT_BURST,
        ENDPOINT_SPECIFIC_LIMITS, ROLE_BASED_LIMITS
    )
    
    RATE_LIMIT_DEFAULTS = RATE_LIMIT_DEFAULTS
    RATE_LIMIT_SENSITIVE = RATE_LIMIT_SENSITIVE
    RATE_LIMIT_BURST = RATE_LIMIT_BURST
    ENDPOINT_SPECIFIC_LIMITS = ENDPOINT_SPECIFIC_LIMITS
    ROLE_BASED_LIMITS = ROLE_BASED_LIMITS
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/images/properties')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 64 * 1024 * 1024))  # 64MB (20 photos × 3MB each)
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    MAX_PHOTOS_PER_PROPERTY = int(os.environ.get('MAX_PHOTOS_PER_PROPERTY', 20))
    MAX_PHOTO_SIZE = int(os.environ.get('MAX_PHOTO_SIZE', 3 * 1024 * 1024))  # 3MB per photo
    
    # Pagination
    PROPERTIES_PER_PAGE = int(os.environ.get('PROPERTIES_PER_PAGE', 20))
    MAX_SEARCH_RESULTS = int(os.environ.get('MAX_SEARCH_RESULTS', 1000))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Override with more secure settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_timeout': 20
    }
    
    # Production logging
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
