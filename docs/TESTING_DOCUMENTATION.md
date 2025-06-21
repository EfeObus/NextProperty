# NextProperty AI - Testing Documentation

## Table of Contents
- [Overview](#overview)
- [Test Strategy](#test-strategy)
- [Test Types](#test-types)
- [Test Environment Setup](#test-environment-setup)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Continuous Integration](#continuous-integration)
- [Performance Testing](#performance-testing)
- [Test Data Management](#test-data-management)

## Overview

The NextProperty AI project uses a comprehensive testing strategy to ensure code quality, reliability, and maintainability. Our testing approach includes unit tests, integration tests, performance tests, and end-to-end tests.

### Testing Framework
- **Primary Framework**: pytest
- **Coverage Tool**: pytest-cov
- **Mocking**: unittest.mock
- **Database Testing**: SQLAlchemy with in-memory SQLite
- **API Testing**: Flask test client
- **Performance Testing**: pytest-benchmark

## Test Strategy

### Testing Pyramid
```
                    /\
                   /  \
                  / E2E \ (Few)
                 /______\
                /        \
               /Integration\ (Some)
              /____________\
             /              \
            /   Unit Tests   \ (Many)
           /________________\
```

### Quality Gates
- **Minimum Coverage**: 80% overall, 90% for critical components
- **All Tests Pass**: CI/CD pipeline requirement
- **Performance Benchmarks**: API response times < 200ms
- **Security Tests**: No critical vulnerabilities

## Test Types

### Unit Tests
Test individual functions, methods, and classes in isolation.

**Location**: `tests/unit/`

**Example**:
```python
# tests/unit/test_property_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.property_service import PropertyService
from app.models.property import Property

class TestPropertyService:
    def test_calculate_property_price_success(self):
        """Test successful property price calculation."""
        # Arrange
        property_data = {
            "location": "Toronto",
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1500
        }
        
        # Act
        result = PropertyService.calculate_price(property_data)
        
        # Assert
        assert result is not None
        assert result["price"] > 0
        assert "confidence" in result
    
    def test_calculate_property_price_invalid_data(self):
        """Test property price calculation with invalid data."""
        # Arrange
        invalid_data = {"location": ""}
        
        # Act & Assert
        with pytest.raises(ValidationError):
            PropertyService.calculate_price(invalid_data)
    
    @patch('app.services.ml_service.MLService.predict')
    def test_calculate_property_price_ml_failure(self, mock_predict):
        """Test handling of ML service failure."""
        # Arrange
        mock_predict.side_effect = Exception("Model loading failed")
        property_data = {"location": "Toronto", "bedrooms": 3}
        
        # Act & Assert
        with pytest.raises(MLServiceError):
            PropertyService.calculate_price(property_data)
```

### Integration Tests
Test interactions between components, modules, and external services.

**Location**: `tests/integration/`

**Example**:
```python
# tests/integration/test_api_integration.py
import pytest
import json
from app import create_app
from app.models import db, Property

class TestPropertyAPIIntegration:
    def test_create_and_retrieve_property(self, client, auth_headers):
        """Test creating a property and retrieving it via API."""
        # Create property
        property_data = {
            "address": "123 Main St",
            "city": "Toronto",
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1500
        }
        
        response = client.post(
            '/api/properties',
            data=json.dumps(property_data),
            headers=auth_headers
        )
        
        assert response.status_code == 201
        created_property = response.get_json()
        
        # Retrieve property
        response = client.get(f'/api/properties/{created_property["id"]}')
        assert response.status_code == 200
        
        retrieved_property = response.get_json()
        assert retrieved_property["address"] == property_data["address"]
```

### End-to-End Tests
Test complete user workflows from frontend to backend.

**Location**: `tests/e2e/`

**Example**:
```python
# tests/e2e/test_property_search_flow.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestPropertySearchFlow:
    def test_property_search_and_prediction(self, driver):
        """Test complete property search and price prediction flow."""
        # Navigate to search page
        driver.get("http://localhost:5000/search")
        
        # Enter search criteria
        location_input = driver.find_element(By.ID, "location")
        location_input.send_keys("Toronto")
        
        bedrooms_select = driver.find_element(By.ID, "bedrooms")
        bedrooms_select.send_keys("3")
        
        # Submit search
        search_button = driver.find_element(By.ID, "search-btn")
        search_button.click()
        
        # Wait for results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-card"))
        )
        
        # Click on first property
        first_property = driver.find_element(By.CLASS_NAME, "property-card")
        first_property.click()
        
        # Wait for prediction page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "predicted-price"))
        )
        
        # Verify prediction is displayed
        predicted_price = driver.find_element(By.ID, "predicted-price")
        assert predicted_price.text.startswith("$")
```

## Test Environment Setup

### Configuration
```python
# config/config.py
class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = True
    CACHE_TYPE = 'simple'
    ML_MODEL_PATH = 'tests/fixtures/test_model.pkl'
```

### Test Database Setup
```python
# tests/conftest.py
import pytest
import tempfile
from app import create_app
from app.models import db
from config.config import TestConfig

@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app(TestConfig)
    return app

@pytest.fixture(scope='session')
def database(app):
    """Create database for testing."""
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()
```

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestPropertyAPI

# Run specific test method
pytest tests/test_api.py::TestPropertyAPI::test_get_property

# Run tests with pattern matching
pytest -k "test_prediction"

# Run tests with markers
pytest -m "slow"
pytest -m "not slow"
```

### Test Output Options
```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l

# Capture method: no, sys, fd
pytest --capture=no
```

### Parallel Test Execution
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Use all available CPUs
pytest -n 4     # Use 4 processes
```

## Writing Tests

### Test Structure (AAA Pattern)
```python
def test_function_name():
    """Test description."""
    # Arrange - Set up test data and conditions
    input_data = {"key": "value"}
    expected_result = "expected_output"
    
    # Act - Execute the function under test
    result = function_under_test(input_data)
    
    # Assert - Verify the result
    assert result == expected_result
```

### Fixtures
```python
# tests/conftest.py
@pytest.fixture
def sample_property():
    """Create a sample property for testing."""
    return Property(
        address="123 Test St",
        city="Toronto",
        bedrooms=3,
        bathrooms=2,
        square_feet=1500,
        price=750000
    )

@pytest.fixture
def auth_headers():
    """Create authentication headers for API tests."""
    token = generate_test_token()
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
```

### Parameterized Tests
```python
@pytest.mark.parametrize("bedrooms,bathrooms,expected_min_price", [
    (1, 1, 300000),
    (2, 2, 500000),
    (3, 2, 700000),
    (4, 3, 900000),
])
def test_property_price_by_rooms(bedrooms, bathrooms, expected_min_price):
    """Test property price calculation for different room configurations."""
    property_data = {
        "location": "Toronto",
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "square_feet": 1500
    }
    
    result = PropertyService.calculate_price(property_data)
    assert result["price"] >= expected_min_price
```

### Mocking External Services
```python
@patch('app.services.external_api.requests.get')
def test_fetch_economic_data(mock_get):
    """Test fetching economic data from external API."""
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {"interest_rate": 2.5}
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    # Act
    result = EconomicDataService.fetch_current_rates()
    
    # Assert
    assert result["interest_rate"] == 2.5
    mock_get.assert_called_once()
```

### Database Testing
```python
def test_create_property_in_database(client, database):
    """Test creating a property in the database."""
    # Arrange
    property_data = {
        "address": "123 Test St",
        "city": "Toronto",
        "bedrooms": 3
    }
    
    # Act
    property_obj = Property(**property_data)
    database.session.add(property_obj)
    database.session.commit()
    
    # Assert
    saved_property = Property.query.filter_by(address="123 Test St").first()
    assert saved_property is not None
    assert saved_property.city == "Toronto"
```

## Test Coverage

### Generating Coverage Reports
```bash
# Run tests with coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Generate XML coverage report (for CI)
pytest --cov=app --cov-report=xml

# Show missing lines
pytest --cov=app --cov-report=term-missing

# Set minimum coverage threshold
pytest --cov=app --cov-fail-under=80
```

### Coverage Configuration
```ini
# .coveragerc or pyproject.toml
[tool.coverage.run]
source = app
omit = 
    */venv/*
    */tests/*
    */migrations/*
    app/__init__.py

[tool.coverage.report]
exclude_lines = 
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[tool.coverage.html]
directory = htmlcov
```

### Coverage Targets
- **Overall Coverage**: Minimum 80%
- **Critical Components**: Minimum 90%
  - ML prediction services
  - API endpoints
  - Data validation functions
  - Security components

## Continuous Integration

### GitHub Actions Configuration
```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
```

## Performance Testing

### Load Testing with pytest-benchmark
```python
import pytest
from app.services.prediction import PredictionService

@pytest.mark.benchmark
def test_prediction_performance(benchmark):
    """Benchmark property price prediction performance."""
    property_data = {
        "location": "Toronto",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500
    }
    
    result = benchmark(PredictionService.predict_price, property_data)
    assert result["price"] > 0

def test_bulk_prediction_performance(benchmark):
    """Benchmark bulk property predictions."""
    properties = [
        {"location": "Toronto", "bedrooms": i, "bathrooms": 1, "square_feet": 1000}
        for i in range(1, 6)
    ]
    
    result = benchmark(PredictionService.predict_bulk, properties)
    assert len(result) == 5
```

### API Performance Testing
```python
def test_api_response_time(client):
    """Test API endpoint response time."""
    import time
    
    start_time = time.time()
    response = client.get('/api/properties')
    end_time = time.time()
    
    response_time = end_time - start_time
    assert response_time < 0.2  # 200ms threshold
    assert response.status_code == 200
```

## Test Data Management

### Test Fixtures
```python
# tests/fixtures/property_data.py
SAMPLE_PROPERTIES = [
    {
        "address": "123 Main St",
        "city": "Toronto",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500,
        "price": 750000
    },
    {
        "address": "456 Oak Ave",
        "city": "Vancouver",
        "bedrooms": 2,
        "bathrooms": 1,
        "square_feet": 1200,
        "price": 650000
    }
]

@pytest.fixture
def sample_properties():
    """Provide sample property data for tests."""
    return SAMPLE_PROPERTIES.copy()
```

### Factory Pattern
```python
# tests/factories.py
import factory
from app.models import Property

class PropertyFactory(factory.Factory):
    class Meta:
        model = Property
    
    address = factory.Sequence(lambda n: f"{n} Test Street")
    city = factory.Faker('city')
    bedrooms = factory.Faker('random_int', min=1, max=5)
    bathrooms = factory.Faker('random_int', min=1, max=3)
    square_feet = factory.Faker('random_int', min=800, max=3000)
    price = factory.LazyAttribute(lambda obj: obj.square_feet * 300)

# Usage in tests
def test_property_creation():
    property_obj = PropertyFactory()
    assert property_obj.address is not None
    assert property_obj.price > 0
```

### Database Seeding
```python
# tests/seed_data.py
def seed_test_data(db):
    """Seed database with test data."""
    properties = [
        Property(address="123 Test St", city="Toronto", bedrooms=3),
        Property(address="456 Test Ave", city="Vancouver", bedrooms=2),
    ]
    
    for prop in properties:
        db.session.add(prop)
    
    db.session.commit()
    return properties
```

## Test Markers

### Custom Markers
```python
# pytest.ini
[tool:pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
    ml: marks tests as machine learning tests
    external: marks tests that require external services
```

### Using Markers
```python
@pytest.mark.slow
def test_complex_calculation():
    """Test that takes a long time to run."""
    pass

@pytest.mark.external
def test_api_integration():
    """Test that requires external API."""
    pass

# Run specific markers
# pytest -m "unit"
# pytest -m "not slow"
# pytest -m "api and not external"
```

## Debugging Tests

### Debug Mode
```python
# Add to test for debugging
import pdb; pdb.set_trace()

# Or use pytest's built-in debugger
pytest --pdb
pytest --pdb-trace
```

### Logging in Tests
```python
import logging

def test_with_logging(caplog):
    """Test with log capture."""
    with caplog.at_level(logging.INFO):
        function_that_logs()
    
    assert "Expected log message" in caplog.text
```

## Best Practices

### Test Organization
- One test class per module/service
- Descriptive test names
- Use fixtures for common setup
- Keep tests independent
- Test edge cases and error conditions

### Test Data
- Use realistic test data
- Avoid hardcoded values
- Clean up after tests
- Use factories for complex objects

### Assertions
- Use specific assertions
- Include helpful error messages
- Test both positive and negative cases
- Verify all important attributes

### Maintenance
- Regularly review and update tests
- Remove obsolete tests
- Refactor duplicated test code
- Keep tests simple and focused

## Common Testing Patterns

### Testing Exceptions
```python
def test_invalid_input_raises_exception():
    """Test that invalid input raises appropriate exception."""
    with pytest.raises(ValidationError, match="Invalid property data"):
        PropertyService.validate({})
```

### Testing Async Code
```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test asynchronous function."""
    result = await async_property_fetch()
    assert result is not None
```

### Testing with Context Managers
```python
def test_file_processing():
    """Test file processing with context manager."""
    with patch('builtins.open', mock_open(read_data="test data")):
        result = process_file("test.txt")
        assert result == "processed"
```

## Resources

### Documentation
- [pytest Documentation](https://pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

### Tools
- **pytest**: Primary testing framework
- **pytest-cov**: Coverage reporting
- **pytest-xdist**: Parallel test execution
- **pytest-benchmark**: Performance testing
- **factory-boy**: Test data factories
- **responses**: HTTP mocking
- **freezegun**: Time mocking
