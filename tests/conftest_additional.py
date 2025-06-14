"""
Pytest configuration and test runner setup.
"""

import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure pytest markers
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "external: marks tests that require external services"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically add markers based on test file names and content."""
    for item in items:
        # Add slow marker to performance tests
        if "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.performance)
        
        # Add integration marker to API tests
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add unit marker to model and utility tests
        if any(test_type in item.nodeid for test_type in ["test_models", "test_utils", "test_services"]):
            item.add_marker(pytest.mark.unit)
        
        # Add external marker to tests that use external APIs
        if "external_api" in item.nodeid.lower() or "test_external" in item.nodeid:
            item.add_marker(pytest.mark.external)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Set test environment variables
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    
    # Disable external API calls during testing
    os.environ['DISABLE_EXTERNAL_APIS'] = 'true'
    
    # Set up test logging
    import logging
    logging.getLogger('app').setLevel(logging.WARNING)
    

@pytest.fixture(autouse=True)
def isolate_tests():
    """Ensure test isolation."""
    yield
    # Clean up any global state after each test
    import importlib
    
    # Reload modules that might have been modified
    modules_to_reload = [
        'app.cache.cache_manager',
        'app.services.ml_service',
        'app.services.external_apis'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])


def pytest_runtest_setup(item):
    """Set up before each test."""
    # Skip external API tests if not in CI environment
    if item.get_closest_marker("external") and not os.getenv('CI'):
        pytest.skip("External API tests skipped in local environment")


def pytest_runtest_teardown(item, nextitem):
    """Clean up after each test."""
    # Clear any caches
    try:
        from app.cache.cache_manager import cache_manager
        cache_manager.clear_all()
    except ImportError:
        pass


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        'TESTING': True,
        'DEBUG': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'REDIS_URL': 'redis://localhost:6379/1',  # Use different DB for tests
        'CACHE_ENABLED': False,  # Disable caching in most tests
        'ML_MODELS_PATH': 'tests/fixtures/models',
        'EXTERNAL_API_TIMEOUT': 1,  # Short timeout for tests
        'RATE_LIMITING_ENABLED': False
    }


# Custom pytest options
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-slow", 
        action="store_true", 
        default=False, 
        help="run slow tests"
    )
    parser.addoption(
        "--run-external", 
        action="store_true", 
        default=False, 
        help="run tests that require external services"
    )
    parser.addoption(
        "--benchmark", 
        action="store_true", 
        default=False, 
        help="run performance benchmarks"
    )


def pytest_collection_modifyitems_hook(config, items):
    """Modify test collection based on command line options."""
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
    
    if not config.getoption("--run-external"):
        skip_external = pytest.mark.skip(reason="need --run-external option to run")
        for item in items:
            if "external" in item.keywords:
                item.add_marker(skip_external)


# Performance test helpers
class PerformanceTracker:
    """Track performance metrics during tests."""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, name):
        """Start timing an operation."""
        import time
        self.metrics[name] = {'start': time.time()}
    
    def end_timer(self, name):
        """End timing an operation."""
        import time
        if name in self.metrics:
            self.metrics[name]['end'] = time.time()
            self.metrics[name]['duration'] = (
                self.metrics[name]['end'] - self.metrics[name]['start']
            )
    
    def get_duration(self, name):
        """Get the duration of an operation."""
        return self.metrics.get(name, {}).get('duration', 0)
    
    def assert_performance(self, name, max_duration):
        """Assert that an operation completed within the expected time."""
        duration = self.get_duration(name)
        assert duration <= max_duration, (
            f"Operation '{name}' took {duration:.3f}s, "
            f"expected <= {max_duration}s"
        )


@pytest.fixture
def performance_tracker():
    """Provide a performance tracker for tests."""
    return PerformanceTracker()


# Mock helpers for external services
class MockExternalServices:
    """Mock external services for testing."""
    
    @staticmethod
    def mock_bank_of_canada():
        """Mock Bank of Canada API responses."""
        return {
            'observations': [
                {'d': '2024-01-01', 'v': '2.5'},
                {'d': '2024-02-01', 'v': '2.7'}
            ]
        }
    
    @staticmethod
    def mock_statistics_canada():
        """Mock Statistics Canada API responses."""
        return {
            'object': [{
                'vectorDataPoint': [
                    {'refPer': '2024-01', 'value': 650000}
                ]
            }]
        }
    
    @staticmethod
    def mock_geocoding_service():
        """Mock geocoding service responses."""
        return {
            'results': [{
                'geometry': {
                    'location': {'lat': 43.6532, 'lng': -79.3832}
                },
                'formatted_address': '123 Main St, Toronto, ON, Canada'
            }]
        }


@pytest.fixture
def mock_external_services():
    """Provide mock external services."""
    return MockExternalServices()


# API test helpers
class APITestHelper:
    """Helper class for API testing."""
    
    @staticmethod
    def assert_json_response(response, expected_status=200):
        """Assert that response is valid JSON with expected status."""
        assert response.status_code == expected_status
        assert response.content_type == 'application/json'
        return response.get_json()
    
    @staticmethod
    def assert_property_structure(property_data):
        """Assert that property data has the expected structure."""
        required_fields = ['id', 'title', 'price', 'property_type', 'city']
        for field in required_fields:
            assert field in property_data, f"Missing field: {field}"
    
    @staticmethod
    def assert_pagination_structure(data):
        """Assert that paginated response has the expected structure."""
        assert 'results' in data
        assert 'pagination' in data
        
        pagination = data['pagination']
        required_pagination_fields = ['page', 'per_page', 'total', 'pages']
        for field in required_pagination_fields:
            assert field in pagination, f"Missing pagination field: {field}"


@pytest.fixture
def api_helper():
    """Provide API test helper."""
    return APITestHelper()
