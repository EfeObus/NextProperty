"""
Test configuration and fixtures for NextProperty AI tests.
"""

import os
import pytest
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from app import create_app
from app.models import db, User, Property, Agent, EconomicData
from app.utils.security import generate_password_hash
from config.config import TestConfig


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Override the database URL for testing
    TestConfig.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    app = create_app(TestConfig)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['LOGIN_DISABLED'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for testing."""
    with app.app_context():
        # Begin a transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use the transaction
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        db.session = session
        
        yield session
        
        # Rollback the transaction
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        id='user-123',
        email='test@example.com',
        username='testuser',
        password_hash=generate_password_hash('password123'),
        first_name='John',
        last_name='Doe',
        phone='+1234567890',
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_agent(db_session):
    """Create a sample agent for testing."""
    agent = Agent(
        id='agent-123',
        name='Jane Smith',
        email='agent@example.com',
        phone='+1987654321',
        license_number='LIC123456',
        company='Real Estate Co.',
        bio='Experienced real estate agent',
        specialties=['residential', 'commercial'],
        rating=4.5,
        total_sales=50,
        years_experience=10,
        commission_rate=Decimal('2.5'),
        is_active=True
    )
    db_session.add(agent)
    db_session.commit()
    return agent


@pytest.fixture
def sample_property(db_session, sample_agent):
    """Create a sample property for testing."""
    property_obj = Property(
        id='prop-123',
        title='Beautiful Family Home',
        description='A lovely 3-bedroom house in a quiet neighborhood',
        property_type='house',
        status='active',
        price=Decimal('500000.00'),
        bedrooms=3,
        bathrooms=2,
        square_feet=1800,
        lot_size=0.25,
        year_built=2010,
        address='123 Main St',
        city='Toronto',
        province='ON',
        postal_code='M5V 3A8',
        country='Canada',
        latitude=43.6532,
        longitude=-79.3832,
        features=['garage', 'garden', 'hardwood floors'],
        agent_id=sample_agent.id,
        listing_date=datetime.utcnow().date(),
        last_updated=datetime.utcnow()
    )
    db_session.add(property_obj)
    db_session.commit()
    return property_obj


@pytest.fixture
def sample_economic_data(db_session):
    """Create sample economic data for testing."""
    economic_data = EconomicData(
        id='econ-123',
        indicator='interest_rate',
        value=Decimal('2.5'),
        date=datetime.utcnow().date(),
        source='Bank of Canada',
        frequency='monthly',
        unit='percent',
        description='Bank of Canada overnight rate'
    )
    db_session.add(economic_data)
    db_session.commit()
    return economic_data


@pytest.fixture
def auth_headers():
    """Create authentication headers for API testing."""
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token'
    }


@pytest.fixture
def mock_redis():
    """Mock Redis for caching tests."""
    with patch('app.cache.cache_manager.redis_client') as mock_redis:
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.delete.return_value = True
        mock_redis.exists.return_value = False
        mock_redis.ping.return_value = True
        yield mock_redis


@pytest.fixture
def mock_ml_service():
    """Mock ML service for testing."""
    with patch('app.services.ml_service.MLService') as mock_ml:
        mock_instance = Mock()
        mock_instance.predict_property_value.return_value = {
            'predicted_value': 450000.0,
            'confidence': 0.85,
            'value_range': {'min': 400000.0, 'max': 500000.0}
        }
        mock_instance.analyze_investment_potential.return_value = {
            'score': 8.5,
            'risk_level': 'medium',
            'expected_roi': 0.12,
            'factors': ['location', 'market_trends']
        }
        mock_ml.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_external_apis():
    """Mock external APIs for testing."""
    with patch('app.services.external_apis.ExternalAPIService') as mock_api:
        mock_instance = Mock()
        mock_instance.get_interest_rates.return_value = [
            {'date': '2024-01-01', 'rate': 2.5, 'type': 'overnight'}
        ]
        mock_instance.get_housing_data.return_value = {
            'average_price': 650000.0,
            'price_change': 0.05,
            'sales_volume': 1500
        }
        mock_api.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_property_data():
    """Sample property data for testing."""
    return {
        'title': 'Test Property',
        'description': 'A test property for unit testing',
        'property_type': 'condo',
        'price': 350000.00,
        'bedrooms': 2,
        'bathrooms': 1,
        'square_feet': 900,
        'address': '456 Test Ave',
        'city': 'Vancouver',
        'province': 'BC',
        'postal_code': 'V6B 1A1',
        'features': ['balcony', 'gym']
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'securepassword123',
        'first_name': 'Alice',
        'last_name': 'Johnson',
        'phone': '+1555123456'
    }


@pytest.fixture
def sample_search_params():
    """Sample search parameters for testing."""
    return {
        'city': 'Toronto',
        'min_price': 300000,
        'max_price': 700000,
        'property_type': 'house',
        'min_bedrooms': 2,
        'max_bedrooms': 4,
        'features': ['garage']
    }


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_user(**kwargs):
        """Create a user with default or custom attributes."""
        defaults = {
            'email': 'factory@example.com',
            'username': 'factoryuser',
            'password_hash': generate_password_hash('password'),
            'first_name': 'Factory',
            'last_name': 'User',
            'is_active': True,
            'is_verified': True
        }
        defaults.update(kwargs)
        return User(**defaults)
    
    @staticmethod
    def create_property(**kwargs):
        """Create a property with default or custom attributes."""
        defaults = {
            'title': 'Factory Property',
            'description': 'A property created by the test factory',
            'property_type': 'house',
            'status': 'active',
            'price': Decimal('400000.00'),
            'bedrooms': 3,
            'bathrooms': 2,
            'square_feet': 1500,
            'address': '789 Factory St',
            'city': 'Toronto',
            'province': 'ON',
            'postal_code': 'M1M 1M1',
            'listing_date': datetime.utcnow().date()
        }
        defaults.update(kwargs)
        return Property(**defaults)
    
    @staticmethod
    def create_agent(**kwargs):
        """Create an agent with default or custom attributes."""
        defaults = {
            'name': 'Factory Agent',
            'email': 'factoryagent@example.com',
            'phone': '+1999888777',
            'license_number': 'FAC123',
            'company': 'Factory Realty',
            'rating': 4.0,
            'is_active': True
        }
        defaults.update(kwargs)
        return Agent(**defaults)


@pytest.fixture
def test_factory():
    """Provide the test data factory."""
    return TestDataFactory
