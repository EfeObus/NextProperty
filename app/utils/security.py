"""
Security utilities for NextProperty AI platform.
"""

import hashlib
import secrets
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re
import html
from flask import current_app
import bleach
from cryptography.fernet import Fernet
import base64


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password
        hashed: Hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except (ValueError, TypeError):
        return False


def generate_token(user_id: int, expiry_hours: int = 24, token_type: str = 'access') -> str:
    """
    Generate a JWT token for user authentication.
    
    Args:
        user_id: User ID
        expiry_hours: Token expiry in hours
        token_type: Type of token ('access', 'refresh', 'reset')
        
    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'token_type': token_type,
        'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
        'iat': datetime.utcnow()
    }
    
    secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
    return jwt.encode(payload, secret_key, algorithm='HS256')


def verify_token(token: str, token_type: str = 'access') -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        if payload.get('token_type') != token_type:
            return None
            
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.DecodeError):
        return None


def sanitize_html(content: str, allowed_tags: list = None, allowed_attributes: dict = None) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.
    
    Args:
        content: HTML content to sanitize
        allowed_tags: List of allowed HTML tags
        allowed_attributes: Dictionary of allowed attributes per tag
        
    Returns:
        str: Sanitized HTML content
    """
    if not content:
        return ""
    
    if allowed_tags is None:
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote',
            'a', 'img'
        ]
    
    if allowed_attributes is None:
        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            '*': ['class']
        }
    
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)


def escape_sql(value: str) -> str:
    """
    Escape SQL special characters to prevent SQL injection.
    
    Args:
        value: String value to escape
        
    Returns:
        str: Escaped string
    """
    if not isinstance(value, str):
        return str(value)
    
    # Replace single quotes with two single quotes
    escaped = value.replace("'", "''")
    
    # Remove or escape other potentially dangerous characters
    escaped = re.sub(r'[;\-\-\/\*]', '', escaped)
    
    return escaped


def generate_api_key(prefix: str = 'npa', length: int = 32) -> str:
    """
    Generate a secure API key.
    
    Args:
        prefix: Prefix for the API key
        length: Length of the random part
        
    Returns:
        str: Generated API key
    """
    random_part = secrets.token_urlsafe(length)
    return f"{prefix}_{random_part}"


def generate_secure_filename(filename: str) -> str:
    """
    Generate a secure filename for file uploads.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Secure filename
    """
    if not filename:
        return f"file_{secrets.token_hex(8)}"
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove dangerous characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(name) > 50:
        name = name[:50]
    
    # Add timestamp to prevent conflicts
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if ext:
        return f"{name}_{timestamp}.{ext}"
    else:
        return f"{name}_{timestamp}"


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        dict: Password validation results
    """
    if not password:
        return {
            'is_valid': False,
            'score': 0,
            'errors': ['Password is required']
        }
    
    errors = []
    score = 0
    
    # Length check
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    else:
        score += 1
    
    # Uppercase check
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    else:
        score += 1
    
    # Lowercase check
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    else:
        score += 1
    
    # Number check
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')
    else:
        score += 1
    
    # Special character check
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    else:
        score += 1
    
    # Common password check
    common_passwords = [
        'password', '123456', '123456789', 'qwerty', 'abc123',
        'password123', 'admin', 'letmein', 'welcome', 'monkey'
    ]
    if password and password.lower() in common_passwords:
        errors.append('Password is too common')
        score = max(0, score - 2)
    
    # Sequential characters check
    if password and re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower()):
        errors.append('Password should not contain sequential characters')
        score = max(0, score - 1)
    
    return {
        'is_valid': len(errors) == 0,
        'score': min(score, 5),
        'strength': _get_password_strength_label(score),
        'errors': errors
    }


def _get_password_strength_label(score: int) -> str:
    """Get password strength label based on score."""
    if score <= 1:
        return 'Very Weak'
    elif score == 2:
        return 'Weak'
    elif score == 3:
        return 'Fair'
    elif score == 4:
        return 'Good'
    else:
        return 'Strong'


def encrypt_sensitive_data(data: str, key: str = None) -> str:
    """
    Encrypt sensitive data using Fernet symmetric encryption.
    
    Args:
        data: Data to encrypt
        key: Encryption key (will use app config if not provided)
        
    Returns:
        str: Encrypted data (base64 encoded)
    """
    if not data:
        return ""
    
    if not key:
        key = current_app.config.get('ENCRYPTION_KEY')
        if not key:
            # Generate a key if none exists (should be stored securely)
            key = Fernet.generate_key()
    
    if isinstance(key, str):
        key = key.encode()
    
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_sensitive_data(encrypted_data: str, key: str = None) -> str:
    """
    Decrypt sensitive data.
    
    Args:
        encrypted_data: Encrypted data (base64 encoded)
        key: Decryption key (will use app config if not provided)
        
    Returns:
        str: Decrypted data
    """
    if not encrypted_data:
        return ""
    
    try:
        if not key:
            key = current_app.config.get('ENCRYPTION_KEY')
            if not key:
                return ""
        
        if isinstance(key, str):
            key = key.encode()
        
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = fernet.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception:
        return ""


def generate_csrf_token() -> str:
    """
    Generate a CSRF token.
    
    Returns:
        str: CSRF token
    """
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, stored_token: str) -> bool:
    """
    Verify CSRF token.
    
    Args:
        token: Token to verify
        stored_token: Stored token to compare against
        
    Returns:
        bool: True if tokens match, False otherwise
    """
    if not token or not stored_token:
        return False
    
    return secrets.compare_digest(token, stored_token)


def hash_file(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Generate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use
        
    Returns:
        str: File hash
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (FileNotFoundError, IOError):
        return ""


def rate_limit_key(user_id: Optional[int] = None, ip_address: str = None) -> str:
    """
    Generate rate limit key.
    
    Args:
        user_id: User ID
        ip_address: IP address
        
    Returns:
        str: Rate limit key
    """
    if user_id:
        return f"user:{user_id}"
    elif ip_address:
        return f"ip:{ip_address}"
    else:
        return "anonymous"


def mask_sensitive_info(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """
    Mask sensitive information for logging/display.
    
    Args:
        data: Data to mask
        mask_char: Character to use for masking
        visible_chars: Number of characters to leave visible
        
    Returns:
        str: Masked data
    """
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    visible_start = visible_chars // 2
    visible_end = visible_chars - visible_start
    
    if visible_end > 0:
        return data[:visible_start] + mask_char * (len(data) - visible_chars) + data[-visible_end:]
    else:
        return data[:visible_start] + mask_char * (len(data) - visible_start)


def validate_email_security(email: str) -> Dict[str, Any]:
    """
    Validate email for security concerns.
    
    Args:
        email: Email address to validate
        
    Returns:
        dict: Validation results
    """
    issues = []
    
    if not email:
        return {'is_valid': False, 'issues': ['Email is required']}
    
    email = email.lower().strip() if email else ""
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'\.{2,}',  # Multiple consecutive dots
        r'^\.|\.$',  # Leading or trailing dots
        r'[<>"\']',  # HTML/script injection characters
        r'\s',  # Whitespace
        r'[^\x00-\x7F]'  # Non-ASCII characters
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, email):
            issues.append(f'Suspicious pattern detected: {pattern}')
    
    # Check for disposable email domains
    disposable_domains = [
        '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
        'tempmail.org', 'throwaway.email', 'temp-mail.org'
    ]
    
    domain = email.split('@')[-1] if '@' in email else ''
    if domain in disposable_domains:
        issues.append('Disposable email addresses are not allowed')
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'domain': domain
    }
