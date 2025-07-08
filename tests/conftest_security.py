"""
Security test configuration that doesn't conflict with main conftest.py
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure pytest for security tests only
def pytest_configure(config):
    """Configure pytest for security tests."""
    # Add custom markers
    config.addinivalue_line("markers", "security: mark test as a security test")
    config.addinivalue_line("markers", "xss: mark test as an XSS protection test")
    config.addinivalue_line("markers", "sqli: mark test as a SQL injection protection test")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "attack_simulation: mark test as an attack simulation")

# Mock fixtures for testing without full app
@pytest.fixture
def mock_app():
    """Mock Flask application for testing."""
    app = Mock()
    app.config = {
        'SECRET_KEY': 'test-secret-key',
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'CSRF_TOKEN_EXPIRY': 3600,
        'XSS_PROTECTION_ENABLED': True,
        'CONTENT_SECURITY_POLICY_ENABLED': True
    }
    app.test_client = Mock()
    return app

@pytest.fixture  
def mock_request():
    """Mock Flask request for testing."""
    request = Mock()
    request.remote_addr = "127.0.0.1"
    request.user_agent = Mock()
    request.user_agent.string = "Test Browser/1.0"
    request.url = "/test"
    request.method = "GET"
    request.args = {}
    request.form = {}
    request.headers = {}
    request.json = None
    return request

@pytest.fixture
def safe_test_inputs():
    """Safe test inputs for validation."""
    return [
        "Hello World",
        "john.doe@example.com",
        "123-456-7890",
        "This is a normal comment",
        "Property search in Toronto"
    ]

@pytest.fixture
def xss_test_payloads():
    """XSS test payloads."""
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>"
    ]

@pytest.fixture
def sqli_test_payloads():
    """SQL injection test payloads."""
    return [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users --",
        "' OR 1=1 --"
    ]
