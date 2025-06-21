# NextProperty AI - Configuration Documentation

## Table of Contents
- [Overview](#overview)
- [Environment Variables](#environment-variables)
- [Configuration Files](#configuration-files)
- [Environment-Specific Settings](#environment-specific-settings)
- [Security Configuration](#security-configuration)
- [Database Configuration](#database-configuration)
- [API Keys and External Services](#api-keys-and-external-services)
- [Machine Learning Configuration](#machine-learning-configuration)
- [Caching Configuration](#caching-configuration)
- [Logging Configuration](#logging-configuration)
- [File Upload Configuration](#file-upload-configuration)
- [Performance Configuration](#performance-configuration)
- [Deployment Configuration](#deployment-configuration)

## Overview

NextProperty AI uses a flexible configuration system that supports different environments (development, testing, production) through environment variables and configuration classes. The main configuration is managed through the `config/config.py` file and environment-specific `.env` files.

### Configuration Architecture
```
config/
├── config.py           # Main configuration classes
├── .env                # Development environment variables
├── .env.example        # Template for environment variables
├── .env.production     # Production environment variables
└── .env.testing        # Testing environment variables
```

## Environment Variables

### Core Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# =============================================================================
# FLASK CONFIGURATION
# =============================================================================

# Secret key for session management and security
SECRET_KEY=your-super-secret-key-here-change-in-production

# Flask environment: development, production, testing
FLASK_ENV=development

# Enable/disable debug mode
FLASK_DEBUG=1

# Application host and port
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# Database connection URL
# Development (SQLite)
DATABASE_URL=sqlite:///instance/nextproperty_dev.db

# Production (PostgreSQL example)
# DATABASE_URL=postgresql://username:password@localhost:5432/nextproperty_prod

# Database connection pool settings
DB_POOL_SIZE=10
DB_POOL_RECYCLE=120
DB_POOL_TIMEOUT=20
DB_POOL_PRE_PING=true

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# JWT secret for API authentication
JWT_SECRET_KEY=your-jwt-secret-key-here

# Session timeout in seconds (default: 1 hour)
SESSION_TIMEOUT=3600

# Password hashing rounds (higher = more secure but slower)
BCRYPT_LOG_ROUNDS=12

# CORS settings
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# =============================================================================
# API KEYS AND EXTERNAL SERVICES
# =============================================================================

# Bank of Canada API
BANK_OF_CANADA_API_KEY=your-boc-api-key
BOC_API_BASE_URL=https://www.bankofcanada.ca/valet

# Statistics Canada API
STATISTICS_CANADA_API_KEY=your-statcan-api-key
STATCAN_API_BASE_URL=https://www150.statcan.gc.ca/t1/wds/rest

# Google Maps API
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# External API settings
EXTERNAL_API_TIMEOUT=30
API_RATE_LIMIT=100

# =============================================================================
# MACHINE LEARNING CONFIGURATION
# =============================================================================

# ML model settings
MODEL_PATH=models/trained_models/
MODEL_VERSION=1.0
MODEL_FILE=property_price_model_v1.0.pkl

# Prediction settings
PREDICTION_CACHE_TTL=3600
MAX_PREDICTION_BATCH_SIZE=100
PREDICTION_CONFIDENCE_THRESHOLD=0.8

# Feature engineering
FEATURE_SCALING_METHOD=standard
FEATURE_SELECTION_ENABLED=true
FEATURE_IMPORTANCE_THRESHOLD=0.01

# =============================================================================
# CACHING CONFIGURATION
# =============================================================================

# Cache type: simple, redis, memcached
CACHE_TYPE=simple

# Redis configuration (if using Redis)
CACHE_REDIS_HOST=localhost
CACHE_REDIS_PORT=6379
CACHE_REDIS_DB=0
CACHE_REDIS_PASSWORD=

# Cache timeout settings (in seconds)
CACHE_DEFAULT_TIMEOUT=300
PROPERTY_CACHE_TIMEOUT=1800
PREDICTION_CACHE_TIMEOUT=3600
MARKET_DATA_CACHE_TIMEOUT=7200

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file paths
LOG_FILE=logs/nextproperty-ai.log
ERROR_LOG_FILE=logs/nextproperty-ai-errors.log
ACCESS_LOG_FILE=logs/nextproperty-ai-access.log
PERFORMANCE_LOG_FILE=logs/nextproperty-ai-performance.log
SECURITY_LOG_FILE=logs/nextproperty-ai-security.log

# Log rotation settings
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================

# Upload directory
UPLOAD_FOLDER=app/static/images/properties

# File size limits
MAX_CONTENT_LENGTH=67108864  # 64MB total
MAX_PHOTO_SIZE=3145728       # 3MB per photo
MAX_PHOTOS_PER_PROPERTY=20

# Allowed file extensions
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp

# =============================================================================
# PAGINATION AND SEARCH
# =============================================================================

# Pagination settings
PROPERTIES_PER_PAGE=20
AGENTS_PER_PAGE=15
USERS_PER_PAGE=25

# Search limits
MAX_SEARCH_RESULTS=1000
SEARCH_TIMEOUT=10

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================

# Email server settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false

# Email credentials
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Default sender
MAIL_DEFAULT_SENDER=noreply@nextproperty.ai

# =============================================================================
# MONITORING AND ANALYTICS
# =============================================================================

# Performance monitoring
ENABLE_PROFILING=false
PROFILING_SAMPLE_RATE=0.1

# Analytics
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
ENABLE_USER_TRACKING=true

# Health check settings
HEALTH_CHECK_INTERVAL=60
HEALTH_CHECK_TIMEOUT=5

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================

# Debug toolbar
DEBUG_TB_ENABLED=true
DEBUG_TB_INTERCEPT_REDIRECTS=false

# SQL debugging
SQLALCHEMY_ECHO=false
SQLALCHEMY_RECORD_QUERIES=true

# =============================================================================
# PRODUCTION-SPECIFIC SETTINGS
# =============================================================================

# SSL settings
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
FORCE_HTTPS=true

# Gunicorn settings
GUNICORN_WORKERS=4
GUNICORN_WORKER_CLASS=sync
GUNICORN_TIMEOUT=30
GUNICORN_KEEPALIVE=2

# Nginx settings
NGINX_CLIENT_MAX_BODY_SIZE=64m
NGINX_PROXY_TIMEOUT=60s
```

### Environment Variable Validation

The application validates required environment variables on startup:

```python
# Required variables for production
REQUIRED_PRODUCTION_VARS = [
    'SECRET_KEY',
    'DATABASE_URL',
    'JWT_SECRET_KEY'
]

# Required API keys
REQUIRED_API_KEYS = [
    'BANK_OF_CANADA_API_KEY',
    'STATISTICS_CANADA_API_KEY',
    'GOOGLE_MAPS_API_KEY'
]
```

## Configuration Files

### Main Configuration Class

```python
# config/config.py
class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        pass
```

### Configuration Factory

```python
# config/config.py
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration class based on environment."""
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    return config[config_name]
```

## Environment-Specific Settings

### Development Configuration

```python
class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    
    # Development database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///instance/nextproperty_dev.db'
    
    # Relaxed security for development
    BCRYPT_LOG_ROUNDS = 4
    
    # Enable SQL query logging
    SQLALCHEMY_ECHO = True
    
    # Cache settings
    CACHE_TYPE = 'simple'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Development-specific initialization
        if app.debug:
            from flask_debugtoolbar import DebugToolbarExtension
            toolbar = DebugToolbarExtension(app)
```

### Production Configuration

```python
class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    
    # Production database with connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_timeout': 20
    }
    
    # Strong security settings
    BCRYPT_LOG_ROUNDS = 15
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Set up file logging
        file_handler = RotatingFileHandler(
            'logs/nextproperty-ai.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
```

### Testing Configuration

```python
class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    
    # In-memory database for fast tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    # Disable caching for tests
    CACHE_TYPE = 'null'
```

## Security Configuration

### Authentication Settings

```python
# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Session Configuration
SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JS access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

### Password Security

```python
# Password hashing configuration
BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 12))

# Password requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL_CHARS = True
```

### API Security

```python
# Rate limiting
API_RATE_LIMIT = int(os.environ.get('API_RATE_LIMIT', 100))
API_RATE_LIMIT_WINDOW = 3600  # 1 hour

# CORS configuration
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
```

## Database Configuration

### Connection Settings

```python
# Database URL examples
# SQLite (Development)
DATABASE_URL = 'sqlite:///instance/nextproperty.db'

# PostgreSQL (Production)
DATABASE_URL = 'postgresql://user:password@localhost:5432/nextproperty'

# MySQL (Alternative)
DATABASE_URL = 'mysql://user:password@localhost:3306/nextproperty'
```

### Connection Pool Configuration

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,        # Number of connections to maintain
    'pool_recycle': 120,    # Recycle connections after 2 minutes
    'pool_pre_ping': True,  # Validate connections before use
    'pool_timeout': 20,     # Timeout for getting connection
    'max_overflow': 0,      # No additional connections beyond pool_size
}
```

### Migration Configuration

```python
# Alembic configuration
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migrations')
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## API Keys and External Services

### Bank of Canada API

```python
BANK_OF_CANADA_API_KEY = os.environ.get('BANK_OF_CANADA_API_KEY')
BOC_API_BASE_URL = 'https://www.bankofcanada.ca/valet'
BOC_API_TIMEOUT = 30
```

### Statistics Canada API

```python
STATISTICS_CANADA_API_KEY = os.environ.get('STATISTICS_CANADA_API_KEY')
STATCAN_API_BASE_URL = 'https://www150.statcan.gc.ca/t1/wds/rest'
STATCAN_API_TIMEOUT = 30
```

### Google Maps API

```python
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
GOOGLE_MAPS_API_ENDPOINT = 'https://maps.googleapis.com/maps/api'
```

## Machine Learning Configuration

### Model Settings

```python
# Model file paths
MODEL_PATH = os.environ.get('MODEL_PATH', 'models/trained_models/')
MODEL_VERSION = os.environ.get('MODEL_VERSION', '1.0')
MODEL_FILE = f'property_price_model_v{MODEL_VERSION}.pkl'

# Model performance thresholds
PREDICTION_CONFIDENCE_THRESHOLD = 0.8
MAX_PREDICTION_ERROR_RATE = 0.15
```

### Feature Engineering

```python
# Feature processing
FEATURE_SCALING_METHOD = os.environ.get('FEATURE_SCALING_METHOD', 'standard')
FEATURE_SELECTION_ENABLED = os.environ.get('FEATURE_SELECTION_ENABLED', 'true').lower() == 'true'
FEATURE_IMPORTANCE_THRESHOLD = float(os.environ.get('FEATURE_IMPORTANCE_THRESHOLD', 0.01))

# Economic data features
ENABLE_ECONOMIC_FEATURES = True
ECONOMIC_DATA_UPDATE_INTERVAL = 3600  # 1 hour
```

### Prediction Settings

```python
# Prediction caching
PREDICTION_CACHE_TTL = int(os.environ.get('PREDICTION_CACHE_TTL', 3600))
MAX_PREDICTION_BATCH_SIZE = int(os.environ.get('MAX_PREDICTION_BATCH_SIZE', 100))

# Model retraining
AUTO_RETRAIN_ENABLED = False
RETRAIN_THRESHOLD_ACCURACY = 0.85
RETRAIN_MIN_NEW_SAMPLES = 100
```

## Caching Configuration

### Cache Types

```python
# Simple cache (development)
CACHE_TYPE = 'simple'

# Redis cache (production)
CACHE_TYPE = 'redis'
CACHE_REDIS_HOST = os.environ.get('CACHE_REDIS_HOST', 'localhost')
CACHE_REDIS_PORT = int(os.environ.get('CACHE_REDIS_PORT', 6379))
CACHE_REDIS_DB = int(os.environ.get('CACHE_REDIS_DB', 0))
CACHE_REDIS_PASSWORD = os.environ.get('CACHE_REDIS_PASSWORD')

# Memcached (alternative)
CACHE_TYPE = 'memcached'
CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
```

### Cache Timeouts

```python
# Default cache timeout
CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))

# Specific cache timeouts
PROPERTY_CACHE_TIMEOUT = 1800      # 30 minutes
PREDICTION_CACHE_TIMEOUT = 3600    # 1 hour
MARKET_DATA_CACHE_TIMEOUT = 7200   # 2 hours
USER_SESSION_CACHE_TIMEOUT = 1800  # 30 minutes
```

## Logging Configuration

### Log Levels and Files

```python
# Log level
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Log files
LOG_FILE = os.environ.get('LOG_FILE', 'logs/nextproperty-ai.log')
ERROR_LOG_FILE = 'logs/nextproperty-ai-errors.log'
ACCESS_LOG_FILE = 'logs/nextproperty-ai-access.log'
PERFORMANCE_LOG_FILE = 'logs/nextproperty-ai-performance.log'
SECURITY_LOG_FILE = 'logs/nextproperty-ai-security.log'
```

### Log Rotation

```python
# Log rotation settings
LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 10MB
LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
```

### Log Format

```python
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
```

## File Upload Configuration

### Upload Settings

```python
# Upload directory
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/images/properties')

# File size limits
MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 64 * 1024 * 1024))  # 64MB
MAX_PHOTO_SIZE = int(os.environ.get('MAX_PHOTO_SIZE', 3 * 1024 * 1024))  # 3MB
MAX_PHOTOS_PER_PROPERTY = int(os.environ.get('MAX_PHOTOS_PER_PROPERTY', 20))

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
```

### Image Processing

```python
# Image optimization
ENABLE_IMAGE_OPTIMIZATION = True
IMAGE_QUALITY = 85
THUMBNAIL_SIZE = (300, 200)
LARGE_IMAGE_SIZE = (1200, 800)
```

## Performance Configuration

### Application Performance

```python
# Threading and processing
THREAD_POOL_SIZE = 4
PROCESS_POOL_SIZE = 2

# Request timeouts
REQUEST_TIMEOUT = 30
LONG_REQUEST_TIMEOUT = 120  # For ML predictions
```

### Database Performance

```python
# Query optimization
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 300,
    'pool_pre_ping': True,
    'pool_timeout': 20
}

# Query caching
QUERY_CACHE_SIZE = 1000
QUERY_CACHE_TIMEOUT = 300
```

## Deployment Configuration

### Docker Configuration

```dockerfile
# Environment variables in Dockerfile
ENV FLASK_ENV=production
ENV FLASK_APP=app.py
ENV DATABASE_URL=postgresql://user:pass@db:5432/nextproperty
ENV SECRET_KEY=production-secret-key
```

### Kubernetes Configuration

```yaml
# ConfigMap for environment variables
apiVersion: v1
kind: ConfigMap
metadata:
  name: nextproperty-config
data:
  FLASK_ENV: "production"
  DATABASE_URL: "postgresql://user:pass@postgres:5432/nextproperty"
  CACHE_TYPE: "redis"
  CACHE_REDIS_HOST: "redis"
```

### Nginx Configuration

```nginx
# nginx.conf
client_max_body_size 64m;
proxy_connect_timeout 60s;
proxy_send_timeout 60s;
proxy_read_timeout 60s;
```

## Configuration Validation

### Environment Validation

```python
def validate_config():
    """Validate required configuration settings."""
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
```

### Configuration Health Check

```python
def health_check_config():
    """Check configuration health."""
    checks = {
        'database': check_database_connection(),
        'cache': check_cache_connection(),
        'external_apis': check_external_apis(),
        'file_storage': check_file_storage(),
    }
    
    return {
        'status': 'healthy' if all(checks.values()) else 'unhealthy',
        'checks': checks
    }
```

## Configuration Best Practices

### Security Best Practices

1. **Never commit sensitive data** to version control
2. **Use strong, unique secrets** for each environment
3. **Rotate secrets regularly** in production
4. **Use environment-specific configurations**
5. **Validate all configuration values**

### Environment Management

1. **Use `.env` files** for local development
2. **Use environment variables** in production
3. **Document all configuration options**
4. **Provide sensible defaults** where possible
5. **Validate configuration on startup**

### Configuration Organization

1. **Group related settings** together
2. **Use descriptive variable names**
3. **Include units in variable names** (e.g., `TIMEOUT_SECONDS`)
4. **Document complex configurations**
5. **Use configuration classes** for environment-specific settings

## Troubleshooting Configuration Issues

### Common Problems

1. **Missing environment variables**
   ```python
   # Check for missing variables
   required = ['SECRET_KEY', 'DATABASE_URL']
   missing = [var for var in required if not os.environ.get(var)]
   if missing:
       print(f"Missing: {missing}")
   ```

2. **Database connection issues**
   ```python
   # Test database connection
   try:
       db.engine.connect()
       print("Database connection successful")
   except Exception as e:
       print(f"Database connection failed: {e}")
   ```

3. **Cache connection problems**
   ```python
   # Test cache connection
   try:
       cache.get('test')
       print("Cache connection successful")
   except Exception as e:
       print(f"Cache connection failed: {e}")
   ```

### Debug Configuration

```python
def debug_config():
    """Print current configuration for debugging."""
    config_vars = [
        'FLASK_ENV', 'DEBUG', 'DATABASE_URL', 'CACHE_TYPE',
        'LOG_LEVEL', 'MODEL_PATH'
    ]
    
    print("Current Configuration:")
    for var in config_vars:
        value = os.environ.get(var, 'Not Set')
        # Hide sensitive values
        if 'SECRET' in var or 'PASSWORD' in var or 'KEY' in var:
            value = '***' if value != 'Not Set' else 'Not Set'
        print(f"{var}: {value}")
```

## Resources

### Configuration References
- [Flask Configuration Handling](https://flask.palletsprojects.com/en/2.0.x/config/)
- [SQLAlchemy Engine Configuration](https://docs.sqlalchemy.org/en/14/core/engines.html)
- [Redis Configuration](https://redis.io/topics/config)
- [Twelve-Factor App Config](https://12factor.net/config)

### Tools
- **python-dotenv**: Load environment variables from .env files
- **environs**: Parse environment variables with type validation
- **dynaconf**: Dynamic configuration management
- **pydantic**: Data validation for configuration
