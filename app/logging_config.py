"""
Logging configuration for NextProperty AI platform.
Provides structured logging with different handlers and formatters.
"""

import logging
import logging.handlers
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json
from flask import Flask, request, g, has_request_context
from pythonjsonlogger import jsonlogger


class RequestContextFilter(logging.Filter):
    """Add request context to log records."""
    
    def filter(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            record.user_agent = request.headers.get('User-Agent', '')
            record.user_id = getattr(g, 'current_user', {}).get('id', 'anonymous') if hasattr(g, 'current_user') else 'anonymous'
            record.request_id = getattr(g, 'request_id', 'no-request-id') if hasattr(g, 'request_id') else 'no-request-id'
        else:
            record.url = 'N/A'
            record.remote_addr = 'N/A'
            record.method = 'N/A'
            record.user_agent = 'N/A'
            record.user_id = 'system'
            record.request_id = 'no-request-id'
        
        record.timestamp = datetime.utcnow().isoformat()
        record.application = 'nextproperty-ai'
        
        return True


class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJSONFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add custom fields
        log_record['timestamp'] = getattr(record, 'timestamp', datetime.utcnow().isoformat())
        log_record['application'] = getattr(record, 'application', 'nextproperty-ai')
        log_record['environment'] = os.getenv('FLASK_ENV', 'development')
        log_record['logger_name'] = record.name
        log_record['level'] = record.levelname
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add request context if available
        if hasattr(record, 'url'):
            log_record['request'] = {
                'url': record.url,
                'method': record.method,
                'remote_addr': record.remote_addr,
                'user_agent': record.user_agent,
                'user_id': record.user_id,
                'request_id': record.request_id
            }
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)


class ErrorHandler:
    """Custom error handler for application errors."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Handle and log application errors."""
        context = context or {}
        
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context
        }
        
        if hasattr(error, '__traceback__'):
            import traceback
            error_data['traceback'] = traceback.format_exception(
                type(error), error, error.__traceback__
            )
        
        self.logger.error("Application error occurred", extra=error_data)


def setup_logging(app: Flask) -> Dict[str, logging.Logger]:
    """
    Set up logging configuration for the Flask application.
    
    Args:
        app: Flask application instance
    
    Returns:
        Dict of logger names to logger instances
    """
    # Get configuration
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_dir = app.config.get('LOG_DIR', 'logs')
    app_name = app.config.get('APP_NAME', 'nextproperty-ai')
    
    # Create logs directory
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    json_formatter = CustomJSONFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Create request context filter
    request_filter = RequestContextFilter()
    
    # Console handler for development
    if app.config.get('FLASK_ENV') == 'development':
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(request_filter)
        root_logger.addHandler(console_handler)
    
    # File handler for application logs
    app_log_file = os.path.join(log_dir, f'{app_name}.log')
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(json_formatter)
    file_handler.addFilter(request_filter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = os.path.join(log_dir, f'{app_name}-errors.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    error_handler.addFilter(request_filter)
    root_logger.addHandler(error_handler)
    
    # Access log handler
    access_log_file = os.path.join(log_dir, f'{app_name}-access.log')
    access_handler = logging.handlers.RotatingFileHandler(
        access_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(json_formatter)
    access_handler.addFilter(request_filter)
    
    # Create specialized loggers
    loggers = {}
    
    # Application logger
    app_logger = logging.getLogger('nextproperty.app')
    app_logger.setLevel(getattr(logging, log_level.upper()))
    loggers['app'] = app_logger
    
    # API logger
    api_logger = logging.getLogger('nextproperty.api')
    api_logger.setLevel(getattr(logging, log_level.upper()))
    loggers['api'] = api_logger
    
    # Database logger
    db_logger = logging.getLogger('nextproperty.database')
    db_logger.setLevel(getattr(logging, log_level.upper()))
    loggers['database'] = db_logger
    
    # ML logger
    ml_logger = logging.getLogger('nextproperty.ml')
    ml_logger.setLevel(getattr(logging, log_level.upper()))
    loggers['ml'] = ml_logger
    
    # Cache logger
    cache_logger = logging.getLogger('nextproperty.cache')
    cache_logger.setLevel(getattr(logging, log_level.upper()))
    loggers['cache'] = cache_logger
    
    # External API logger
    external_api_logger = logging.getLogger('nextproperty.external_api')
    external_api_logger.setLevel(getattr(logging, log_level.upper()))
    loggers['external_api'] = external_api_logger
    
    # Performance logger
    performance_logger = logging.getLogger('nextproperty.performance')
    performance_logger.setLevel(logging.INFO)
    performance_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, f'{app_name}-performance.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    performance_handler.setFormatter(json_formatter)
    performance_handler.addFilter(request_filter)
    performance_logger.addHandler(performance_handler)
    loggers['performance'] = performance_logger
    
    # Security logger
    security_logger = logging.getLogger('nextproperty.security')
    security_logger.setLevel(logging.WARNING)
    security_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, f'{app_name}-security.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    security_handler.setFormatter(json_formatter)
    security_handler.addFilter(request_filter)
    security_logger.addHandler(security_handler)
    loggers['security'] = security_logger
    
    # Access logger (separate from root)
    access_logger = logging.getLogger('nextproperty.access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    access_logger.propagate = False  # Don't propagate to root logger
    loggers['access'] = access_logger
    
    # Configure third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    # SQLAlchemy logging
    if app.config.get('SQLALCHEMY_ECHO'):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    app.logger.info(f"Logging configured with level {log_level}")
    
    return loggers


def setup_error_handlers(app: Flask, loggers: Dict[str, logging.Logger]):
    """Set up Flask error handlers."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        loggers['app'].warning(f"404 error: {request.url}")
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        loggers['app'].error(f"500 error: {error}")
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        loggers['app'].warning(f"400 error: {error}")
        return {'error': 'Bad request'}, 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        loggers['security'].warning(f"401 error: Unauthorized access attempt from {request.remote_addr}")
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        loggers['security'].warning(f"403 error: Forbidden access attempt from {request.remote_addr}")
        return {'error': 'Forbidden'}, 403


def log_request_start():
    """Log request start."""
    g.request_start_time = datetime.utcnow()
    g.request_id = f"req_{int(g.request_start_time.timestamp() * 1000)}"
    
    access_logger = logging.getLogger('nextproperty.access')
    access_logger.info("Request started", extra={
        'event_type': 'request_start',
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'content_type': request.headers.get('Content-Type', ''),
        'content_length': request.headers.get('Content-Length', 0)
    })


def log_request_end(response):
    """Log request end."""
    if hasattr(g, 'request_start_time'):
        duration = (datetime.utcnow() - g.request_start_time).total_seconds()
        
        access_logger = logging.getLogger('nextproperty.access')
        performance_logger = logging.getLogger('nextproperty.performance')
        
        log_data = {
            'event_type': 'request_end',
            'status_code': response.status_code,
            'duration_seconds': duration,
            'response_size': 0  # Simplified for now
        }
        
        access_logger.info("Request completed", extra=log_data)
        
        # Log slow requests
        if duration > 2.0:  # Log requests slower than 2 seconds
            performance_logger.warning("Slow request detected", extra={
                **log_data,
                'threshold_exceeded': '2s'
            })
    
    return response


class PerformanceMonitor:
    """Monitor application performance."""
    
    def __init__(self):
        self.logger = logging.getLogger('nextproperty.performance')
    
    def log_db_query(self, query: str, duration: float, params: Optional[Dict] = None):
        """Log database query performance."""
        log_data = {
            'event_type': 'db_query',
            'query': query[:500],  # Truncate long queries
            'duration_seconds': duration,
            'params_count': len(params) if params else 0
        }
        
        if duration > 1.0:  # Log slow queries
            self.logger.warning("Slow database query", extra=log_data)
        else:
            self.logger.debug("Database query", extra=log_data)
    
    def log_cache_operation(self, operation: str, key: str, duration: float, hit: bool = None):
        """Log cache operation performance."""
        log_data = {
            'event_type': 'cache_operation',
            'operation': operation,
            'cache_key': key[:100],  # Truncate long keys
            'duration_seconds': duration
        }
        
        if hit is not None:
            log_data['cache_hit'] = hit
        
        self.logger.debug("Cache operation", extra=log_data)
    
    def log_external_api_call(self, api_name: str, endpoint: str, duration: float, status_code: int):
        """Log external API call performance."""
        log_data = {
            'event_type': 'external_api_call',
            'api_name': api_name,
            'endpoint': endpoint,
            'duration_seconds': duration,
            'status_code': status_code
        }
        
        if duration > 5.0:  # Log slow API calls
            self.logger.warning("Slow external API call", extra=log_data)
        elif status_code >= 400:
            self.logger.error("External API error", extra=log_data)
        else:
            self.logger.info("External API call", extra=log_data)
    
    def log_ml_operation(self, operation: str, duration: float, input_size: int = None):
        """Log ML operation performance."""
        log_data = {
            'event_type': 'ml_operation',
            'operation': operation,
            'duration_seconds': duration
        }
        
        if input_size:
            log_data['input_size'] = input_size
        
        if duration > 10.0:  # Log slow ML operations
            self.logger.warning("Slow ML operation", extra=log_data)
        else:
            self.logger.info("ML operation", extra=log_data)


class SecurityLogger:
    """Logger for security events."""
    
    def __init__(self):
        self.logger = logging.getLogger('nextproperty.security')
    
    def log_login_attempt(self, email: str, success: bool, ip_address: str):
        """Log login attempt."""
        self.logger.info("Login attempt", extra={
            'event_type': 'login_attempt',
            'email': email,
            'success': success,
            'ip_address': ip_address
        })
    
    def log_failed_authentication(self, reason: str, ip_address: str):
        """Log failed authentication."""
        self.logger.warning("Authentication failed", extra={
            'event_type': 'authentication_failed',
            'reason': reason,
            'ip_address': ip_address
        })
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activity."""
        self.logger.warning("Suspicious activity detected", extra={
            'event_type': 'suspicious_activity',
            'activity_type': activity_type,
            'details': details
        })
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str):
        """Log rate limit exceeded."""
        self.logger.warning("Rate limit exceeded", extra={
            'event_type': 'rate_limit_exceeded',
            'ip_address': ip_address,
            'endpoint': endpoint
        })


# Global instances
performance_monitor = PerformanceMonitor()
security_logger = SecurityLogger()
