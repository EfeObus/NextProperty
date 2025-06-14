"""
Custom error classes for NextProperty AI platform.
"""

from typing import Optional, Dict, Any, List


class NextPropertyError(Exception):
    """Base exception class for NextProperty AI platform."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        error_dict = {
            'message': self.message,
            'code': self.code,
            'type': self.__class__.__name__
        }
        
        if self.details:
            error_dict['details'] = self.details
        
        return error_dict


class ValidationError(NextPropertyError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, errors: Dict[str, List[str]] = None):
        self.field = field
        self.errors = errors or {}
        
        details = {}
        if field:
            details['field'] = field
        if errors:
            details['validation_errors'] = errors
        
        super().__init__(message, 'VALIDATION_ERROR', details)


class AuthenticationError(NextPropertyError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", reason: str = None):
        details = {}
        if reason:
            details['reason'] = reason
        
        super().__init__(message, 'AUTHENTICATION_ERROR', details)


class AuthorizationError(NextPropertyError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", required_permission: str = None):
        details = {}
        if required_permission:
            details['required_permission'] = required_permission
        
        super().__init__(message, 'AUTHORIZATION_ERROR', details)


class DataNotFoundError(NextPropertyError):
    """Raised when requested data is not found."""
    
    def __init__(self, message: str = "Data not found", resource_type: str = None, 
                 resource_id: str = None):
        details = {}
        if resource_type:
            details['resource_type'] = resource_type
        if resource_id:
            details['resource_id'] = resource_id
        
        super().__init__(message, 'DATA_NOT_FOUND', details)


class ExternalAPIError(NextPropertyError):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str = "External API error", api_name: str = None,
                 status_code: int = None, response_body: str = None):
        details = {}
        if api_name:
            details['api_name'] = api_name
        if status_code:
            details['status_code'] = status_code
        if response_body:
            details['response_body'] = response_body
        
        super().__init__(message, 'EXTERNAL_API_ERROR', details)


class DatabaseError(NextPropertyError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database error", operation: str = None,
                 table: str = None, original_error: str = None):
        details = {}
        if operation:
            details['operation'] = operation
        if table:
            details['table'] = table
        if original_error:
            details['original_error'] = original_error
        
        super().__init__(message, 'DATABASE_ERROR', details)


class ConfigurationError(NextPropertyError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str = "Configuration error", config_key: str = None):
        details = {}
        if config_key:
            details['config_key'] = config_key
        
        super().__init__(message, 'CONFIGURATION_ERROR', details)


class FileUploadError(NextPropertyError):
    """Raised when file upload fails."""
    
    def __init__(self, message: str = "File upload error", filename: str = None,
                 file_size: int = None, allowed_types: List[str] = None):
        details = {}
        if filename:
            details['filename'] = filename
        if file_size:
            details['file_size'] = file_size
        if allowed_types:
            details['allowed_types'] = allowed_types
        
        super().__init__(message, 'FILE_UPLOAD_ERROR', details)


class RateLimitError(NextPropertyError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", limit: int = None,
                 window: int = None, retry_after: int = None):
        details = {}
        if limit:
            details['limit'] = limit
        if window:
            details['window'] = window
        if retry_after:
            details['retry_after'] = retry_after
        
        super().__init__(message, 'RATE_LIMIT_ERROR', details)


class GeospatialError(NextPropertyError):
    """Raised when geospatial operations fail."""
    
    def __init__(self, message: str = "Geospatial error", coordinates: tuple = None,
                 operation: str = None):
        details = {}
        if coordinates:
            details['coordinates'] = coordinates
        if operation:
            details['operation'] = operation
        
        super().__init__(message, 'GEOSPATIAL_ERROR', details)


class MLModelError(NextPropertyError):
    """Raised when ML model operations fail."""
    
    def __init__(self, message: str = "ML model error", model_name: str = None,
                 operation: str = None, input_data: Dict[str, Any] = None):
        details = {}
        if model_name:
            details['model_name'] = model_name
        if operation:
            details['operation'] = operation
        if input_data:
            details['input_data'] = input_data
        
        super().__init__(message, 'ML_MODEL_ERROR', details)


class CacheError(NextPropertyError):
    """Raised when cache operations fail."""
    
    def __init__(self, message: str = "Cache error", operation: str = None,
                 cache_key: str = None):
        details = {}
        if operation:
            details['operation'] = operation
        if cache_key:
            details['cache_key'] = cache_key
        
        super().__init__(message, 'CACHE_ERROR', details)


class PropertyAnalysisError(NextPropertyError):
    """Raised when property analysis fails."""
    
    def __init__(self, message: str = "Property analysis error", property_id: int = None,
                 analysis_type: str = None):
        details = {}
        if property_id:
            details['property_id'] = property_id
        if analysis_type:
            details['analysis_type'] = analysis_type
        
        super().__init__(message, 'PROPERTY_ANALYSIS_ERROR', details)


class SearchError(NextPropertyError):
    """Raised when search operations fail."""
    
    def __init__(self, message: str = "Search error", search_params: Dict[str, Any] = None,
                 search_type: str = None):
        details = {}
        if search_params:
            details['search_params'] = search_params
        if search_type:
            details['search_type'] = search_type
        
        super().__init__(message, 'SEARCH_ERROR', details)


class EmailError(NextPropertyError):
    """Raised when email operations fail."""
    
    def __init__(self, message: str = "Email error", email_type: str = None,
                 recipient: str = None, smtp_error: str = None):
        details = {}
        if email_type:
            details['email_type'] = email_type
        if recipient:
            details['recipient'] = recipient
        if smtp_error:
            details['smtp_error'] = smtp_error
        
        super().__init__(message, 'EMAIL_ERROR', details)


class NotificationError(NextPropertyError):
    """Raised when notification operations fail."""
    
    def __init__(self, message: str = "Notification error", notification_type: str = None,
                 user_id: int = None, channel: str = None):
        details = {}
        if notification_type:
            details['notification_type'] = notification_type
        if user_id:
            details['user_id'] = user_id
        if channel:
            details['channel'] = channel
        
        super().__init__(message, 'NOTIFICATION_ERROR', details)


class PaymentError(NextPropertyError):
    """Raised when payment operations fail."""
    
    def __init__(self, message: str = "Payment error", payment_method: str = None,
                 amount: float = None, transaction_id: str = None):
        details = {}
        if payment_method:
            details['payment_method'] = payment_method
        if amount:
            details['amount'] = amount
        if transaction_id:
            details['transaction_id'] = transaction_id
        
        super().__init__(message, 'PAYMENT_ERROR', details)


class BusinessLogicError(NextPropertyError):
    """Raised when business logic constraints are violated."""
    
    def __init__(self, message: str = "Business logic error", rule: str = None,
                 context: Dict[str, Any] = None):
        details = {}
        if rule:
            details['rule'] = rule
        if context:
            details['context'] = context
        
        super().__init__(message, 'BUSINESS_LOGIC_ERROR', details)


# Error handler utility functions
def handle_database_error(e: Exception, operation: str = None, table: str = None) -> DatabaseError:
    """Convert database exceptions to DatabaseError."""
    return DatabaseError(
        message=f"Database operation failed: {str(e)}",
        operation=operation,
        table=table,
        original_error=str(e)
    )


def handle_external_api_error(e: Exception, api_name: str = None, 
                             status_code: int = None) -> ExternalAPIError:
    """Convert external API exceptions to ExternalAPIError."""
    return ExternalAPIError(
        message=f"External API call failed: {str(e)}",
        api_name=api_name,
        status_code=status_code,
        response_body=str(e)
    )


def format_error_response(error: NextPropertyError, include_traceback: bool = False) -> Dict[str, Any]:
    """Format error for API response."""
    response = {
        'status': 'error',
        'error': error.to_dict()
    }
    
    if include_traceback:
        import traceback
        response['error']['traceback'] = traceback.format_exc()
    
    return response


def get_http_status_for_error(error: NextPropertyError) -> int:
    """Get appropriate HTTP status code for error type."""
    error_status_map = {
        'ValidationError': 400,
        'AuthenticationError': 401,
        'AuthorizationError': 403,
        'DataNotFoundError': 404,
        'RateLimitError': 429,
        'ExternalAPIError': 502,
        'DatabaseError': 500,
        'ConfigurationError': 500,
        'FileUploadError': 400,
        'GeospatialError': 400,
        'MLModelError': 500,
        'CacheError': 500,
        'PropertyAnalysisError': 422,
        'SearchError': 400,
        'EmailError': 500,
        'NotificationError': 500,
        'PaymentError': 402,
        'BusinessLogicError': 422
    }
    
    return error_status_map.get(error.__class__.__name__, 500)


class ErrorCollector:
    """Utility class to collect multiple errors."""
    
    def __init__(self):
        self.errors: List[NextPropertyError] = []
    
    def add_error(self, error: NextPropertyError):
        """Add an error to the collection."""
        self.errors.append(error)
    
    def add_validation_error(self, message: str, field: str = None):
        """Add a validation error."""
        self.add_error(ValidationError(message, field))
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[Dict[str, Any]]:
        """Get all errors as dictionaries."""
        return [error.to_dict() for error in self.errors]
    
    def raise_if_errors(self, message: str = "Multiple validation errors occurred"):
        """Raise ValidationError if there are any errors."""
        if self.has_errors():
            error_details = {
                'errors': self.get_errors(),
                'count': len(self.errors)
            }
            raise ValidationError(message, details=error_details)
    
    def clear(self):
        """Clear all errors."""
        self.errors.clear()
