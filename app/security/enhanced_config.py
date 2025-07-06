"""
Enhanced Security Configuration for NextProperty AI.

This module provides configuration settings for the enhanced security features
including behavioral analysis, advanced XSS protection, and CSP management.
"""

# Enhanced XSS Protection Settings
ENHANCED_XSS_SETTINGS = {
    'ENABLED': True,
    'THREAT_SCORING_ENABLED': True,
    'BEHAVIORAL_ANALYSIS_ENABLED': True,
    'CONTENT_ANALYSIS_ENABLED': True,
    
    # Threat detection thresholds
    'CRITICAL_THREAT_THRESHOLD': 20.0,
    'HIGH_THREAT_THRESHOLD': 10.0,
    'MEDIUM_THREAT_THRESHOLD': 5.0,
    
    # Pattern detection weights
    'SCRIPT_INJECTION_WEIGHT': 10,
    'EVENT_HANDLER_WEIGHT': 8,
    'DOM_MANIPULATION_WEIGHT': 6,
    'HTML_INJECTION_WEIGHT': 5,
    'CSS_INJECTION_WEIGHT': 4,
    'ENCODING_EVASION_WEIGHT': 3,
    'SUSPICIOUS_KEYWORDS_WEIGHT': 2,
    
    # Content analysis settings
    'MAX_CONTENT_LENGTH': 100000,
    'ENABLE_BASE64_DETECTION': True,
    'ENABLE_URL_VALIDATION': True,
    'ENABLE_FILE_CONTENT_SCANNING': True,
    
    # Machine learning settings
    'ML_PREDICTION_ENABLED': True,
    'ML_CONFIDENCE_THRESHOLD': 0.7,
    'FEATURE_EXTRACTION_ENABLED': True,
}

# Behavioral Analysis Settings
BEHAVIORAL_ANALYSIS_SETTINGS = {
    'ENABLED': True,
    'WINDOW_SIZE': 300,  # seconds
    'MAX_REQUESTS_PER_IP': 1000,
    
    # Rate limiting thresholds
    'RAPID_REQUEST_THRESHOLD': 50,  # requests per minute
    'BURST_INTERVAL_THRESHOLD': 0.5,  # seconds between requests
    
    # Pattern probing detection
    'PATTERN_TESTING_THRESHOLD': 5,  # different attack patterns tested
    'URL_FUZZING_THRESHOLD': 20,  # different URLs tested
    
    # Risk scoring thresholds
    'BLOCK_RISK_THRESHOLD': 8.0,
    'RATE_LIMIT_RISK_THRESHOLD': 5.0,
    'MONITOR_RISK_THRESHOLD': 2.0,
    
    # Session analysis
    'TRACK_USER_AGENTS': True,
    'TRACK_SESSION_SIGNATURES': True,
    'DETECT_SESSION_ANOMALIES': True,
    
    # IP reputation settings
    'TRACK_IP_REPUTATION': True,
    'IP_TRUST_DECAY_RATE': 0.1,
    'MAX_TRUST_SCORE': 1.0,
    'MIN_TRUST_SCORE': 0.0,
}

# Enhanced CSP Settings
ENHANCED_CSP_SETTINGS = {
    'ENABLED': True,
    'DYNAMIC_POLICY_GENERATION': True,
    'NONCE_GENERATION': True,
    'HASH_CALCULATION': True,
    
    # CSP modes
    'DEFAULT_MODE': 'enforce',  # 'enforce' or 'report-only'
    'STRICT_MODE_CONTEXTS': ['admin', 'upload'],
    
    # Nonce settings
    'NONCE_LENGTH': 16,  # bytes
    'NONCE_CACHE_TIMEOUT': 3600,  # seconds
    
    # Violation reporting
    'VIOLATION_REPORTING_ENABLED': True,
    'VIOLATION_ANALYSIS_ENABLED': True,
    'AUTO_POLICY_ADJUSTMENT': False,  # Set to True for auto-adjustment
    
    # Context-specific policies
    'CONTEXT_POLICIES': {
        'public': {
            'strict': False,
            'allow_unsafe_inline': True,
            'allow_unsafe_eval': True,
        },
        'admin': {
            'strict': True,
            'allow_unsafe_inline': False,
            'allow_unsafe_eval': False,
        },
        'api': {
            'strict': True,
            'allow_unsafe_inline': False,
            'allow_unsafe_eval': False,
            'minimal_directives': True,
        },
        'upload': {
            'strict': True,
            'allow_unsafe_inline': False,
            'allow_unsafe_eval': False,
            'enhanced_file_restrictions': True,
        }
    },
    
    # Trusted domains (add your CDN/external domains here)
    'TRUSTED_DOMAINS': [
        'cdn.jsdelivr.net',
        'cdnjs.cloudflare.com',
        'unpkg.com',
        'fonts.googleapis.com',
        'fonts.gstatic.com',
        'maps.googleapis.com',
        'maps.google.com',
    ],
    
    # Report URI (configure for your environment)
    'REPORT_URI': None,  # Set to your CSP violation report endpoint
    'REPORT_TO': None,   # Set to your report group name
}

# Advanced Input Validation Settings
ADVANCED_VALIDATION_SETTINGS = {
    'ENABLED': True,
    'ML_VALIDATION_ENABLED': True,
    'CONTEXT_AWARE_VALIDATION': True,
    
    # Validation thresholds
    'BLOCK_THRESHOLD': 15.0,
    'MALICIOUS_THRESHOLD': 8.0,
    'SUSPICIOUS_THRESHOLD': 3.0,
    
    # Input type specific settings
    'EMAIL_VALIDATION_STRICT': True,
    'URL_VALIDATION_STRICT': True,
    'PHONE_VALIDATION_ENABLED': True,
    'FILENAME_VALIDATION_STRICT': True,
    
    # Content length limits
    'MAX_TEXT_LENGTH': 10000,
    'MAX_HTML_LENGTH': 50000,
    'MAX_JSON_LENGTH': 100000,
    'MAX_URL_LENGTH': 2048,
    'MAX_EMAIL_LENGTH': 254,
    'MAX_PHONE_LENGTH': 20,
    'MAX_FILENAME_LENGTH': 255,
    
    # File validation settings
    'DANGEROUS_FILE_EXTENSIONS': [
        '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
        '.js', '.vbs', '.ps1', '.sh', '.jar', '.app'
    ],
    'ALLOWED_MIME_TYPES': [
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'text/plain', 'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ],
    
    # Pattern detection settings
    'SQL_INJECTION_DETECTION': True,
    'COMMAND_INJECTION_DETECTION': True,
    'XSS_PATTERN_DETECTION': True,
    'LDAP_INJECTION_DETECTION': True,
    'PATH_TRAVERSAL_DETECTION': True,
}

# Security Integration Settings
SECURITY_INTEGRATION_SETTINGS = {
    'ENABLED': True,
    'COMPREHENSIVE_ANALYSIS': True,
    'REAL_TIME_MONITORING': True,
    
    # Security levels for different contexts
    'CONTEXT_SECURITY_LEVELS': {
        'public': 'STANDARD',
        'admin': 'MAXIMUM',
        'api': 'ENHANCED',
        'upload': 'MAXIMUM',
    },
    
    # Logging and monitoring
    'LOG_ALL_ATTEMPTS': False,
    'LOG_HIGH_THREATS': True,
    'LOG_CRITICAL_THREATS': True,
    'PERFORMANCE_MONITORING': True,
    
    # Response actions
    'BLOCK_CRITICAL_THREATS': True,
    'RATE_LIMIT_SUSPICIOUS': True,
    'QUARANTINE_HIGH_RISK_UPLOADS': True,
    
    # Data retention
    'SECURITY_REPORT_RETENTION': 86400,  # 24 hours
    'VIOLATION_REPORT_RETENTION': 604800,  # 7 days
    'BEHAVIORAL_DATA_RETENTION': 86400,  # 24 hours
    
    # Performance settings
    'MAX_PROCESSING_TIME': 5.0,  # seconds
    'CACHE_ANALYSIS_RESULTS': True,
    'PARALLEL_ANALYSIS': False,  # Set to True for high-traffic sites
}

# Monitoring and Alerting Settings
MONITORING_SETTINGS = {
    'ENABLED': True,
    'REAL_TIME_ALERTS': True,
    'METRICS_COLLECTION': True,
    
    # Alert thresholds
    'CRITICAL_ALERTS_THRESHOLD': 5,  # critical threats per hour
    'HIGH_RISK_ALERTS_THRESHOLD': 20,  # high-risk requests per hour
    'BLOCKED_IP_ALERTS_THRESHOLD': 10,  # blocked IPs per hour
    
    # Metrics
    'COLLECT_PERFORMANCE_METRICS': True,
    'COLLECT_THREAT_METRICS': True,
    'COLLECT_BEHAVIORAL_METRICS': True,
    
    # Dashboard settings
    'ENABLE_SECURITY_DASHBOARD': True,
    'DASHBOARD_REFRESH_INTERVAL': 60,  # seconds
    'DASHBOARD_DATA_RETENTION': 86400,  # 24 hours
}

# Development and Testing Settings
DEVELOPMENT_SETTINGS = {
    'ENABLE_DEBUG_LOGGING': False,
    'DISABLE_SECURITY_IN_DEBUG': False,  # Keep security enabled even in debug
    'MOCK_ML_PREDICTIONS': False,
    'BYPASS_RATE_LIMITING': False,
    'ENABLE_SECURITY_PROFILING': False,
    
    # Testing settings
    'ENABLE_SECURITY_TESTING': False,
    'GENERATE_TEST_REPORTS': False,
    'VALIDATE_CONFIG_ON_STARTUP': True,
}

# Export all settings
ENHANCED_SECURITY_CONFIG = {
    'XSS': ENHANCED_XSS_SETTINGS,
    'BEHAVIORAL': BEHAVIORAL_ANALYSIS_SETTINGS,
    'CSP': ENHANCED_CSP_SETTINGS,
    'VALIDATION': ADVANCED_VALIDATION_SETTINGS,
    'INTEGRATION': SECURITY_INTEGRATION_SETTINGS,
    'MONITORING': MONITORING_SETTINGS,
    'DEVELOPMENT': DEVELOPMENT_SETTINGS,
}


def get_security_config(section: str = None):
    """
    Get security configuration.
    
    Args:
        section: Specific section to retrieve, or None for all
        
    Returns:
        dict: Configuration settings
    """
    if section:
        return ENHANCED_SECURITY_CONFIG.get(section.upper(), {})
    return ENHANCED_SECURITY_CONFIG


def validate_security_config():
    """Validate security configuration settings."""
    errors = []
    
    # Validate XSS settings
    xss_config = ENHANCED_XSS_SETTINGS
    if xss_config['CRITICAL_THREAT_THRESHOLD'] <= xss_config['HIGH_THREAT_THRESHOLD']:
        errors.append("CRITICAL_THREAT_THRESHOLD must be greater than HIGH_THREAT_THRESHOLD")
    
    # Validate behavioral settings
    behavioral_config = BEHAVIORAL_ANALYSIS_SETTINGS
    if behavioral_config['BLOCK_RISK_THRESHOLD'] <= behavioral_config['RATE_LIMIT_RISK_THRESHOLD']:
        errors.append("BLOCK_RISK_THRESHOLD must be greater than RATE_LIMIT_RISK_THRESHOLD")
    
    # Validate CSP settings
    csp_config = ENHANCED_CSP_SETTINGS
    if csp_config['NONCE_LENGTH'] < 8:
        errors.append("NONCE_LENGTH should be at least 8 bytes for security")
    
    # Validate validation settings
    validation_config = ADVANCED_VALIDATION_SETTINGS
    if validation_config['BLOCK_THRESHOLD'] <= validation_config['MALICIOUS_THRESHOLD']:
        errors.append("BLOCK_THRESHOLD must be greater than MALICIOUS_THRESHOLD")
    
    if errors:
        raise ValueError(f"Security configuration validation failed: {'; '.join(errors)}")
    
    return True
