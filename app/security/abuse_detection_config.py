"""
Configuration for Abuse Detection System
"""

# Abuse detection rate limiting configuration
ABUSE_DETECTION_CONFIG = {
    'enabled': True,
    'log_incidents': True,
    'real_time_blocking': True,
    'progressive_penalties': True,
}

# Rate limits for different abuse levels
ABUSE_RATE_LIMITS = {
    'low_abuse': {
        'requests': 50,
        'window': 300,  # 5 minutes
        'description': 'Low-level abuse detection'
    },
    'medium_abuse': {
        'requests': 20,
        'window': 300,  # 5 minutes
        'description': 'Medium-level abuse detection'
    },
    'high_abuse': {
        'requests': 5,
        'window': 300,  # 5 minutes
        'description': 'High-level abuse detection'
    },
    'critical_abuse': {
        'requests': 1,
        'window': 600,  # 10 minutes
        'description': 'Critical abuse detection'
    }
}

# Pattern-specific rate limits
PATTERN_RATE_LIMITS = {
    'rapid_requests': {
        'requests': 100,
        'window': 60,  # 1 minute
        'description': 'Rapid request pattern detection'
    },
    'auth_attempts': {
        'requests': 10,
        'window': 300,  # 5 minutes
        'description': 'Authentication attempt limiting'
    },
    'api_calls': {
        'requests': 200,
        'window': 3600,  # 1 hour
        'description': 'API call rate limiting'
    },
    'search_queries': {
        'requests': 50,
        'window': 300,  # 5 minutes
        'description': 'Search query rate limiting'
    },
    'form_submissions': {
        'requests': 20,
        'window': 300,  # 5 minutes
        'description': 'Form submission rate limiting'
    }
}

# Detection thresholds for different abuse types
ABUSE_DETECTION_THRESHOLDS = {
    'rapid_requests': {
        'count': 50,
        'window': 60,  # 1 minute
        'description': 'Threshold for rapid request detection'
    },
    'error_rate': {
        'threshold': 0.5,  # 50% error rate
        'min_requests': 10,
        'description': 'Error rate threshold for abuse detection'
    },
    'auth_failure_rate': {
        'threshold': 0.8,  # 80% failure rate
        'min_attempts': 5,
        'description': 'Authentication failure rate threshold'
    },
    'unique_endpoints': {
        'threshold': 20,
        'window': 300,  # 5 minutes
        'description': 'Unique endpoint access threshold'
    },
    'parameter_variations': {
        'threshold': 15,
        'window': 300,  # 5 minutes
        'description': 'Parameter variation threshold'
    },
    'user_agent_switches': {
        'threshold': 5,
        'window': 300,  # 5 minutes
        'description': 'User agent switching threshold'
    },
    'suspicious_pattern_score': {
        'threshold': 0.7,  # 70% suspicion threshold
        'description': 'Overall suspicion score threshold'
    }
}

# Progressive penalty escalation
PENALTY_ESCALATION = {
    1: {
        'duration': 300,     # 5 minutes
        'multiplier': 1.0,   # Normal rate
        'description': 'First violation - warning'
    },
    2: {
        'duration': 900,     # 15 minutes
        'multiplier': 0.5,   # Half rate
        'description': 'Second violation - moderate restriction'
    },
    3: {
        'duration': 1800,    # 30 minutes
        'multiplier': 0.2,   # 20% rate
        'description': 'Third violation - strict restriction'
    },
    4: {
        'duration': 3600,    # 1 hour
        'multiplier': 0.1,   # 10% rate
        'description': 'Fourth violation - severe restriction'
    },
    5: {
        'duration': 7200,    # 2 hours
        'multiplier': 0.05,  # 5% rate
        'description': 'Fifth+ violation - maximum restriction'
    }
}

# Whitelist for abuse detection (trusted sources)
ABUSE_DETECTION_WHITELIST = {
    'ips': [
        '127.0.0.1',
        '::1',
        # Add trusted IP addresses here
    ],
    'user_agents': [
        # Add trusted user agents here (monitoring tools, etc.)
    ],
    'endpoints': [
        '/health',
        '/status',
        '/metrics'
    ]
}

# Redis configuration for abuse detection
ABUSE_REDIS_CONFIG = {
    'key_prefix': 'abuse_rl:',
    'default_ttl': 3600,  # 1 hour
    'cleanup_interval': 300,  # 5 minutes
}

# Monitoring and alerting configuration
ABUSE_MONITORING = {
    'enable_alerts': True,
    'alert_threshold': {
        'incidents_per_hour': 10,
        'unique_clients_per_hour': 5,
        'critical_incidents': 1
    },
    'log_level': 'INFO',
    'detailed_logging': True,
    'statistics_retention': 86400,  # 24 hours
}

# Machine learning enhancement (future)
ML_ABUSE_DETECTION = {
    'enabled': False,  # Set to True when ML models are ready
    'model_threshold': 0.8,
    'feature_extraction': {
        'temporal_patterns': True,
        'behavioral_analysis': True,
        'network_analysis': True
    },
    'adaptive_thresholds': False,
    'online_learning': False
}

# Integration with existing security systems
SECURITY_INTEGRATION = {
    'xss_protection': True,
    'csrf_protection': True,
    'behavioral_analysis': True,
    'rate_limiter': True,
    'shared_blacklist': True
}

# Performance optimization settings
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'cache_ttl': 300,  # 5 minutes
    'async_processing': False,  # Set to True for high-traffic scenarios
    'batch_analysis': False,
    'memory_limit': 100,  # MB
    'max_incidents_per_client': 100
}
