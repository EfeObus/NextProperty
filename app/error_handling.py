"""
Error handling utilities for NextProperty AI platform.
Provides custom exception classes and error handling mechanisms.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime
from flask import request, g, has_request_context
import sys

logger = logging.getLogger(__name__)


class BaseApplicationError(Exception):
    """Base exception class for application errors."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        """
        Initialize base application error.
        
        Args:
            message: Error message
            code: Error code for categorization
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        
        # Add request context if available
        if has_request_context():
            self.request_context = {
                'url': request.url,
                'method': request.method,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'user_id': getattr(g, 'current_user', {}).get('id') if hasattr(g, 'current_user') else None
            }
        else:
            self.request_context = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'details': self.details,
            'timestamp': self.timestamp,
            'request_context': self.request_context
        }


class ValidationError(BaseApplicationError):
    """Error for input validation failures."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        """
        Initialize validation error.
        
        Args:
            field: Field that failed validation
            message: Validation error message
            value: Invalid value (sanitized)
        """
        super().__init__(f"Validation error in field '{field}': {message}")
        self.field = field
        self.details = {
            'field': field,
            'validation_message': message,
            'value_type': type(value).__name__ if value is not None else None
        }


class DatabaseError(BaseApplicationError):
    """Error for database operations."""
    
    def __init__(self, operation: str, message: str, table: str = None, 
                 query: str = None, original_error: Exception = None):
        """
        Initialize database error.
        
        Args:
            operation: Database operation that failed
            message: Error message
            table: Table involved in the operation
            query: SQL query that failed (sanitized)
            original_error: Original database exception
        """
        super().__init__(f"Database {operation} error: {message}")
        self.operation = operation
        self.table = table
        self.query = query[:500] if query else None  # Truncate long queries
        self.original_error = str(original_error) if original_error else None
        
        self.details = {
            'operation': operation,
            'table': table,
            'query_preview': self.query,
            'original_error': self.original_error
        }


class ExternalAPIError(BaseApplicationError):
    """Error for external API calls."""
    
    def __init__(self, api_name: str, endpoint: str, status_code: int = None,
                 message: str = None, response_data: Any = None):
        """
        Initialize external API error.
        
        Args:
            api_name: Name of the external API
            endpoint: API endpoint that failed
            status_code: HTTP status code
            message: Error message
            response_data: API response data (sanitized)
        """
        error_msg = message or f"External API error: {api_name} {endpoint}"
        super().__init__(error_msg)
        
        self.api_name = api_name
        self.endpoint = endpoint
        self.status_code = status_code
        
        self.details = {
            'api_name': api_name,
            'endpoint': endpoint,
            'status_code': status_code,
            'response_preview': str(response_data)[:200] if response_data else None
        }


class AuthenticationError(BaseApplicationError):
    """Error for authentication failures."""
    
    def __init__(self, message: str, auth_type: str = None, user_id: str = None):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            auth_type: Type of authentication (login, token, etc.)
            user_id: User ID if available
        """
        super().__init__(f"Authentication error: {message}")
        self.auth_type = auth_type
        self.user_id = user_id
        
        self.details = {
            'auth_type': auth_type,
            'user_id': user_id
        }


class AuthorizationError(BaseApplicationError):
    """Error for authorization failures."""
    
    def __init__(self, message: str, required_permission: str = None, 
                 user_id: str = None, resource: str = None):
        """
        Initialize authorization error.
        
        Args:
            message: Error message
            required_permission: Required permission
            user_id: User ID
            resource: Resource being accessed
        """
        super().__init__(f"Authorization error: {message}")
        self.required_permission = required_permission
        self.user_id = user_id
        self.resource = resource
        
        self.details = {
            'required_permission': required_permission,
            'user_id': user_id,
            'resource': resource
        }


class CacheError(BaseApplicationError):
    """Error for cache operations."""
    
    def __init__(self, operation: str, cache_key: str, message: str):
        """
        Initialize cache error.
        
        Args:
            operation: Cache operation that failed
            cache_key: Cache key involved
            message: Error message
        """
        super().__init__(f"Cache {operation} error: {message}")
        self.operation = operation
        self.cache_key = cache_key
        
        self.details = {
            'operation': operation,
            'cache_key': cache_key[:100]  # Truncate long keys
        }


class MLModelError(BaseApplicationError):
    """Error for ML model operations."""
    
    def __init__(self, model_name: str, operation: str, message: str,
                 input_data: Any = None):
        """
        Initialize ML model error.
        
        Args:
            model_name: Name of the ML model
            operation: Model operation (predict, train, etc.)
            message: Error message
            input_data: Input data that caused error (sanitized)
        """
        super().__init__(f"ML model error ({model_name}): {message}")
        self.model_name = model_name
        self.operation = operation
        
        self.details = {
            'model_name': model_name,
            'operation': operation,
            'input_preview': str(input_data)[:200] if input_data else None
        }


class DataProcessingError(BaseApplicationError):
    """Error for data processing operations."""
    
    def __init__(self, processor: str, stage: str, message: str,
                 data_sample: Any = None):
        """
        Initialize data processing error.
        
        Args:
            processor: Name of the data processor
            stage: Processing stage that failed
            message: Error message
            data_sample: Sample of data that caused error
        """
        super().__init__(f"Data processing error ({processor}): {message}")
        self.processor = processor
        self.stage = stage
        
        self.details = {
            'processor': processor,
            'stage': stage,
            'data_sample': str(data_sample)[:200] if data_sample else None
        }


class ConfigurationError(BaseApplicationError):
    """Error for configuration issues."""
    
    def __init__(self, config_key: str, message: str, expected_type: str = None):
        """
        Initialize configuration error.
        
        Args:
            config_key: Configuration key that's problematic
            message: Error message
            expected_type: Expected configuration type
        """
        super().__init__(f"Configuration error ({config_key}): {message}")
        self.config_key = config_key
        self.expected_type = expected_type
        
        self.details = {
            'config_key': config_key,
            'expected_type': expected_type
        }


class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self):
        self.logger = logging.getLogger('nextproperty.errors')
        # Ensure the logger has handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle and log an error.
        
        Args:
            error: Exception to handle
            context: Additional context information
        
        Returns:
            Error information dictionary
        """
        context = context or {}
        
        # Create error info
        error_info = {
            'error_id': self._generate_error_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'context': context
        }
        
        if isinstance(error, BaseApplicationError):
            # Custom application error
            error_info.update(error.to_dict())
            self._log_application_error(error, error_info)
        else:
            # System/third-party error
            error_info.update({
                'error_type': type(error).__name__,
                'message': str(error),
                'code': 'SYSTEM_ERROR',
                'traceback': self._get_traceback(error)
            })
            self._log_system_error(error, error_info)
        
        return error_info
    
    def handle_validation_errors(self, errors: List[ValidationError]) -> Dict[str, Any]:
        """
        Handle multiple validation errors.
        
        Args:
            errors: List of validation errors
        
        Returns:
            Aggregated error information
        """
        error_info = {
            'error_id': self._generate_error_id(),
            'error_type': 'ValidationErrors',
            'message': f"Multiple validation errors: {len(errors)} fields failed",
            'code': 'VALIDATION_FAILED',
            'timestamp': datetime.utcnow().isoformat(),
            'validation_errors': []
        }
        
        for error in errors:
            error_info['validation_errors'].append({
                'field': error.field,
                'message': error.message,
                'details': error.details
            })
        
        self.logger.warning("Multiple validation errors", extra=error_info)
        
        return error_info
    
    def _log_application_error(self, error: BaseApplicationError, error_info: Dict[str, Any]):
        """Log application-specific error."""
        if isinstance(error, (ValidationError,)):
            self.logger.warning("Application validation error", extra=error_info)
        elif isinstance(error, (AuthenticationError, AuthorizationError)):
            self.logger.warning("Application security error", extra=error_info)
        elif isinstance(error, (DatabaseError, ExternalAPIError)):
            self.logger.error("Application infrastructure error", extra=error_info)
        else:
            self.logger.error("Application error", extra=error_info)
    
    def _log_system_error(self, error: Exception, error_info: Dict[str, Any]):
        """Log system/third-party error."""
        # Remove 'message' key from error_info to avoid LogRecord conflict
        log_extra = {k: v for k, v in error_info.items() if k != 'message'}
        self.logger.error(f"System error: {error_info.get('message', str(error))}", extra=log_extra, exc_info=error)
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID."""
        import uuid
        return f"err_{int(datetime.utcnow().timestamp())}_{str(uuid.uuid4())[:8]}"
    
    def _get_traceback(self, error: Exception) -> List[str]:
        """Get formatted traceback."""
        return traceback.format_exception(type(error), error, error.__traceback__)


class ErrorMetrics:
    """Track error metrics and patterns."""
    
    def __init__(self):
        self.logger = logging.getLogger('nextproperty.metrics')
        self.error_counts = {}
        self.error_patterns = {}
    
    def record_error(self, error_type: str, error_code: str = None, 
                    context: Dict[str, Any] = None):
        """
        Record error occurrence for metrics.
        
        Args:
            error_type: Type of error
            error_code: Error code
            context: Error context
        """
        context = context or {}
        
        # Count errors by type
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Track patterns
        pattern_key = f"{error_type}:{error_code}" if error_code else error_type
        self.error_patterns[pattern_key] = self.error_patterns.get(pattern_key, 0) + 1
        
        # Log metrics
        self.logger.info("Error metrics updated", extra={
            'event_type': 'error_recorded',
            'error_type': error_type,
            'error_code': error_code,
            'total_count': self.error_counts[error_type],
            'pattern_count': self.error_patterns[pattern_key],
            'context': context
        })
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary statistics."""
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_errors': total_errors,
            'error_counts': dict(sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )),
            'error_patterns': dict(sorted(
                self.error_patterns.items(), 
                key=lambda x: x[1], 
                reverse=True
            )),
            'top_errors': list(sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            ))[:10]
        }


def setup_global_error_handler():
    """Set up global exception handler."""
    error_handler = ErrorHandler()
    error_metrics = ErrorMetrics()
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Global exception handler."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_info = error_handler.handle_error(exc_value)
        error_metrics.record_error(
            error_info['error_type'], 
            error_info.get('code'),
            error_info.get('context')
        )
    
    sys.excepthook = handle_exception
    
    return error_handler, error_metrics


# Global instances
global_error_handler, global_error_metrics = setup_global_error_handler()


class AdvancedErrorHandler:
    """Advanced error handling with monitoring and recovery capabilities."""
    
    def __init__(self):
        """Initialize the advanced error handler."""
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        self.error_counts = {}
        self.circuit_breakers = {}
    
    def _setup_logging(self):
        """Setup comprehensive logging configuration."""
        if not self.logger.handlers:
            # Create handlers
            error_handler = logging.FileHandler('logs/nextproperty-ai-errors.log')
            performance_handler = logging.FileHandler('logs/nextproperty-ai-performance.log')
            security_handler = logging.FileHandler('logs/nextproperty-ai-security.log')
            
            # Create formatters
            detailed_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s - '
                '[%(filename)s:%(lineno)d] - [%(funcName)s]'
            )
            
            # Configure handlers
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            
            performance_handler.setLevel(logging.WARNING)
            performance_handler.setFormatter(detailed_formatter)
            
            security_handler.setLevel(logging.CRITICAL)
            security_handler.setFormatter(detailed_formatter)
            
            # Add handlers to logger
            self.logger.addHandler(error_handler)
            self.logger.addHandler(performance_handler)
            self.logger.addHandler(security_handler)
            self.logger.setLevel(logging.DEBUG)
    
    def handle_with_retry(self, func, max_retries: int = 3, backoff_factor: float = 1.0):
        """
        Execute function with automatic retry on failure.
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            
        Returns:
            Function result or raises last exception
        """
        import time
        import random
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                last_exception = e
                
                if attempt < max_retries:
                    # Calculate backoff time with jitter
                    backoff_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {backoff_time:.2f} seconds."
                    )
                    
                    time.sleep(backoff_time)
                else:
                    self.logger.error(
                        f"All {max_retries + 1} attempts failed for {func.__name__}: {str(e)}"
                    )
        
        raise last_exception
    
    def circuit_breaker(self, service_name: str, failure_threshold: int = 5, timeout: int = 60):
        """
        Circuit breaker pattern implementation for service calls.
        
        Args:
            service_name: Name of the service
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before trying to close circuit
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                now = datetime.utcnow()
                
                # Initialize circuit breaker for this service
                if service_name not in self.circuit_breakers:
                    self.circuit_breakers[service_name] = {
                        'state': 'closed',  # closed, open, half-open
                        'failure_count': 0,
                        'last_failure_time': None,
                        'success_count': 0
                    }
                
                circuit = self.circuit_breakers[service_name]
                
                # Check if circuit is open and timeout has passed
                if circuit['state'] == 'open':
                    if circuit['last_failure_time'] and \
                       (now - circuit['last_failure_time']).seconds >= timeout:
                        circuit['state'] = 'half-open'
                        circuit['success_count'] = 0
                        self.logger.info(f"Circuit breaker for {service_name} moved to half-open state")
                    else:
                        raise ServiceUnavailableError(
                            f"Service {service_name} is currently unavailable (circuit open)"
                        )
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Success - reset failure count
                    if circuit['state'] == 'half-open':
                        circuit['success_count'] += 1
                        if circuit['success_count'] >= 3:  # Require 3 successes to close
                            circuit['state'] = 'closed'
                            circuit['failure_count'] = 0
                            self.logger.info(f"Circuit breaker for {service_name} closed")
                    elif circuit['state'] == 'closed':
                        circuit['failure_count'] = 0
                    
                    return result
                    
                except Exception as e:
                    # Failure - increment failure count
                    circuit['failure_count'] += 1
                    circuit['last_failure_time'] = now
                    
                    if circuit['failure_count'] >= failure_threshold:
                        circuit['state'] = 'open'
                        self.logger.error(
                            f"Circuit breaker for {service_name} opened after "
                            f"{failure_threshold} failures"
                        )
                    
                    raise e
            
            return wrapper
        return decorator
    
    def monitor_performance(self, func_name: str = None):
        """
        Performance monitoring decorator.
        
        Args:
            func_name: Optional name for the function (uses actual name if not provided)
        """
        def decorator(func):
            import time
            import functools
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                name = func_name or func.__name__
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Log slow operations
                    if execution_time > 5.0:  # 5 seconds threshold
                        self.logger.warning(
                            f"Slow operation detected: {name} took {execution_time:.2f}s"
                        )
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.logger.error(
                        f"Function {name} failed after {execution_time:.2f}s: {str(e)}"
                    )
                    raise e
            
            return wrapper
        return decorator
    
    def handle_database_errors(self, operation: str):
        """
        Database-specific error handling decorator.
        
        Args:
            operation: Description of the database operation
        """
        def decorator(func):
            import functools
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Handle specific database errors
                    error_type = type(e).__name__
                    
                    if 'IntegrityError' in error_type:
                        raise DataValidationError(
                            f"Data integrity violation in {operation}: {str(e)}"
                        )
                    elif 'OperationalError' in error_type:
                        raise DatabaseConnectionError(
                            f"Database connection issue in {operation}: {str(e)}"
                        )
                    elif 'TimeoutError' in error_type or 'timeout' in str(e).lower() if str(e) else False:
                        raise DatabaseTimeoutError(
                            f"Database operation timeout in {operation}: {str(e)}"
                        )
                    else:
                        raise DatabaseError(
                            f"Database error in {operation}: {str(e)}"
                        )
            
            return wrapper
        return decorator
    
    def validate_and_sanitize(self, validation_rules: Dict[str, Any]):
        """
        Input validation and sanitization decorator.
        
        Args:
            validation_rules: Dictionary of validation rules
        """
        def decorator(func):
            import functools
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Validate inputs based on rules
                for param_name, rules in validation_rules.items():
                    if param_name in kwargs:
                        value = kwargs[param_name]
                        
                        # Required check
                        if rules.get('required', False) and value is None:
                            raise ValidationError(f"Parameter {param_name} is required")
                        
                        # Type check
                        if value is not None and 'type' in rules:
                            expected_type = rules['type']
                            if not isinstance(value, expected_type):
                                raise ValidationError(
                                    f"Parameter {param_name} must be of type {expected_type.__name__}"
                                )
                        
                        # Range check for numbers
                        if value is not None and isinstance(value, (int, float)):
                            if 'min' in rules and value < rules['min']:
                                raise ValidationError(
                                    f"Parameter {param_name} must be >= {rules['min']}"
                                )
                            if 'max' in rules and value > rules['max']:
                                raise ValidationError(
                                    f"Parameter {param_name} must be <= {rules['max']}"
                                )
                        
                        # Length check for strings
                        if value is not None and isinstance(value, str):
                            if 'min_length' in rules and len(value) < rules['min_length']:
                                raise ValidationError(
                                    f"Parameter {param_name} must have at least {rules['min_length']} characters"
                                )
                            if 'max_length' in rules and len(value) > rules['max_length']:
                                raise ValidationError(
                                    f"Parameter {param_name} must have at most {rules['max_length']} characters"
                                )
                        
                        # Sanitize string inputs
                        if value is not None and isinstance(value, str) and rules.get('sanitize', False):
                            import html
                            import re
                            # Basic HTML escaping and script removal
                            value = html.escape(value)
                            value = re.sub(r'<script.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
                            kwargs[param_name] = value
                
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error statistics."""
        return {
            'error_counts': self.error_counts.copy(),
            'circuit_breakers': {
                name: {
                    'state': cb['state'],
                    'failure_count': cb['failure_count']
                }
                for name, cb in self.circuit_breakers.items()
            },
            'timestamp': datetime.utcnow().isoformat()
        }


# Global error handler instance
advanced_error_handler = AdvancedErrorHandler()
