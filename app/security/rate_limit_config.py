"""
Rate Limiting Configuration for NextProperty AI
Defines rate limiting rules and settings for different types of requests.
"""

# Default rate limiting rules - More lenient for development
RATE_LIMIT_DEFAULTS = {
    'global': {'requests': 10000, 'window': 3600},  # 10000 requests per hour globally
    'ip': {'requests': 2000, 'window': 3600},       # 2000 requests per hour per IP
    'user': {'requests': 5000, 'window': 3600},     # 5000 requests per hour per authenticated user
    'endpoint': {'requests': 500, 'window': 300},   # 500 requests per 5 minutes per endpoint
}

# Sensitive endpoint rate limits (stricter) - Relaxed for development
RATE_LIMIT_SENSITIVE = {
    'auth': {'requests': 50, 'window': 300},        # 50 auth attempts per 5 minutes
    'api': {'requests': 2000, 'window': 3600},      # 2000 API calls per hour
    'upload': {'requests': 100, 'window': 3600},    # 100 uploads per hour
    'admin': {'requests': 500, 'window': 3600},     # 500 admin actions per hour
    'ml_prediction': {'requests': 200, 'window': 300},  # 200 ML predictions per 5 minutes
    'search': {'requests': 1000, 'window': 3600},   # 1000 searches per hour
}

# Burst protection (short-term limits) - More lenient for development
RATE_LIMIT_BURST = {
    'ip': {'requests': 100, 'window': 60},          # 100 requests per minute per IP
    'user': {'requests': 200, 'window': 60},        # 200 requests per minute per user
    'global': {'requests': 1000, 'window': 60},     # 1000 requests per minute globally
}

# Progressive rate limiting for repeated violations
PROGRESSIVE_PENALTIES = {
    'base_penalty': 300,     # 5 minutes base penalty
    'multiplier': 2.0,       # Penalty multiplier for repeated violations
    'max_penalty': 3600,     # Maximum penalty of 1 hour
    'violation_window': 7200, # 2 hour window to track violations
}

# Whitelist configurations
RATE_LIMIT_WHITELIST = {
    'ips': [
        '127.0.0.1',         # Localhost
        '::1',               # IPv6 localhost
        # Add trusted IPs here
    ],
    'user_agents': [
        # Add trusted user agents here (e.g., monitoring tools)
    ],
    'endpoints': [
        '/health',           # Health check endpoint
        '/status',           # Status endpoint
        '/metrics',          # Metrics endpoint (if exists)
    ]
}

# Custom limits for specific endpoints - Relaxed for development
ENDPOINT_SPECIFIC_LIMITS = {
    'api.predict_price': {'requests': 200, 'window': 300},         # ML predictions
    'api.get_properties': {'requests': 1000, 'window': 3600},      # Property listings
    'api.search_properties': {'requests': 500, 'window': 3600},    # Property search
    'auth.login': {'requests': 50, 'window': 300},                 # Login attempts
    'auth.register': {'requests': 30, 'window': 3600},             # Registration
    'api.upload_property_image': {'requests': 50, 'window': 3600}, # Image uploads
    'admin.delete_property': {'requests': 100, 'window': 3600},    # Admin deletions
}

# Rate limiting by user role - More lenient for development
ROLE_BASED_LIMITS = {
    'admin': {
        'requests': 10000,
        'window': 3600,
        'burst': {'requests': 500, 'window': 60}
    },
    'agent': {
        'requests': 8000,
        'window': 3600,
        'burst': {'requests': 400, 'window': 60}
    },
    'user': {
        'requests': 5000,
        'window': 3600,
        'burst': {'requests': 200, 'window': 60}
    },
    'anonymous': {
        'requests': 2000,
        'window': 3600,
        'burst': {'requests': 100, 'window': 60}
    }
}

# Geographic rate limiting (if needed)
GEOGRAPHIC_LIMITS = {
    'enabled': False,  # Set to True to enable geographic rate limiting
    'default_limit': {'requests': 100, 'window': 3600},
    'country_limits': {
        # Example: 'CN': {'requests': 50, 'window': 3600},  # Stricter limits for certain countries
    }
}

# Redis configuration for distributed rate limiting
REDIS_RATE_LIMIT_CONFIG = {
    'enabled': True,           # Use Redis if available
    'key_prefix': 'rl:',      # Prefix for Redis keys
    'default_ttl': 3600,      # Default TTL for rate limit keys
}

# Monitoring and alerting thresholds
RATE_LIMIT_MONITORING = {
    'alert_threshold': 0.8,    # Alert when 80% of limit is reached
    'log_violations': True,     # Log rate limit violations
    'track_patterns': True,     # Track request patterns for analysis
}

# Machine Learning based rate limiting (advanced)
ML_RATE_LIMITING = {
    'enabled': False,          # Set to True to enable ML-based detection
    'anomaly_threshold': 2.0,  # Standard deviations for anomaly detection
    'learning_window': 7200,   # 2 hours of data for learning patterns
    'min_requests': 10,        # Minimum requests needed for ML analysis
}
