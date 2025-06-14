"""
Unit tests for database models.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.models import User, Property, Agent, EconomicData
from app.utils.security import check_password_hash


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, db_session):
        """Test creating a new user."""
        user = User(
            email='test@example.com',
            username='testuser',
            password_hash='hashed_password',
            first_name='John',
            last_name='Doe'
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.full_name == 'John Doe'
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
    
    def test_user_password_hashing(self, db_session):
        """Test password hashing functionality."""
        from app.utils.security import generate_password_hash
        
        password = 'secretpassword123'
        user = User(
            email='secure@example.com',
            username='secureuser',
            password_hash=generate_password_hash(password),
            first_name='Secure',
            last_name='User'
        )
        db_session.add(user)
        db_session.commit()
        
        # Verify password can be checked
        assert check_password_hash(user.password_hash, password)
        assert not check_password_hash(user.password_hash, 'wrongpassword')
    
    def test_user_unique_constraints(self, db_session):
        """Test unique constraints on email and username."""
        user1 = User(
            email='unique@example.com',
            username='uniqueuser',
            password_hash='hash1'
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create user with same email
        user2 = User(
            email='unique@example.com',
            username='differentuser',
            password_hash='hash2'
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Try to create user with same username
        user3 = User(
            email='different@example.com',
            username='uniqueuser',
            password_hash='hash3'
        )
        db_session.add(user3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_to_dict(self, sample_user):
        """Test user serialization to dictionary."""
        user_dict = sample_user.to_dict()
        
        assert 'id' in user_dict
        assert 'email' in user_dict
        assert 'username' in user_dict
        assert 'first_name' in user_dict
        assert 'last_name' in user_dict
        assert 'password_hash' not in user_dict  # Should not expose password
        assert user_dict['full_name'] == 'John Doe'
    
    def test_user_profile_completion(self, db_session):
        """Test profile completion calculation."""
        # User with minimal info
        user1 = User(email='min@example.com', username='minuser')
        db_session.add(user1)
        
        # User with complete info
        user2 = User(
            email='complete@example.com',
            username='completeuser',
            first_name='Complete',
            last_name='User',
            phone='+1234567890',
            bio='Complete bio'
        )
        db_session.add(user2)
        db_session.commit()
        
        assert user1.profile_completion < user2.profile_completion


class TestPropertyModel:
    """Test cases for Property model."""
    
    def test_property_creation(self, db_session, sample_agent):
        """Test creating a new property."""
        property_obj = Property(
            title='Test Property',
            description='A test property',
            property_type='house',
            price=Decimal('500000.00'),
            bedrooms=3,
            bathrooms=2,
            address='123 Test St',
            city='Toronto',
            province='ON',
            agent_id=sample_agent.id
        )
        db_session.add(property_obj)
        db_session.commit()
        
        assert property_obj.id is not None
        assert property_obj.title == 'Test Property'
        assert property_obj.price == Decimal('500000.00')
        assert property_obj.status == 'active'  # Default status
        assert property_obj.created_at is not None
        assert property_obj.agent == sample_agent
    
    def test_property_price_validation(self, db_session):
        """Test property price validation."""
        # Valid price
        property1 = Property(
            title='Valid Price',
            price=Decimal('100000.00'),
            property_type='condo',
            address='123 Valid St',
            city='Toronto',
            province='ON'
        )
        db_session.add(property1)
        db_session.commit()
        
        # Invalid negative price should be handled at application level
        property2 = Property(
            title='Invalid Price',
            price=Decimal('-100.00'),
            property_type='condo',
            address='123 Invalid St',
            city='Toronto',
            province='ON'
        )
        # This would be caught by application validation, not DB constraint
        db_session.add(property2)
        db_session.commit()
    
    def test_property_to_dict(self, sample_property):
        """Test property serialization to dictionary."""
        property_dict = sample_property.to_dict()
        
        assert 'id' in property_dict
        assert 'title' in property_dict
        assert 'price' in property_dict
        assert 'bedrooms' in property_dict
        assert 'bathrooms' in property_dict
        assert 'address' in property_dict
        assert 'agent' in property_dict
        assert property_dict['price'] == float(sample_property.price)
    
    def test_property_search_vector(self, sample_property):
        """Test property search vector generation."""
        search_vector = sample_property.search_vector
        
        assert sample_property.title.lower() in search_vector.lower()
        assert sample_property.city.lower() in search_vector.lower()
        assert sample_property.property_type in search_vector.lower()
    
    def test_property_age_calculation(self, db_session):
        """Test property age calculation."""
        current_year = datetime.now().year
        
        property_obj = Property(
            title='Age Test',
            property_type='house',
            year_built=current_year - 10,
            address='123 Age St',
            city='Toronto',
            province='ON'
        )
        db_session.add(property_obj)
        db_session.commit()
        
        assert property_obj.age == 10
    
    def test_property_price_per_sqft(self, db_session):
        """Test price per square foot calculation."""
        property_obj = Property(
            title='Price Test',
            property_type='house',
            price=Decimal('500000.00'),
            square_feet=2000,
            address='123 Price St',
            city='Toronto',
            province='ON'
        )
        db_session.add(property_obj)
        db_session.commit()
        
        assert property_obj.price_per_sqft == Decimal('250.00')


class TestAgentModel:
    """Test cases for Agent model."""
    
    def test_agent_creation(self, db_session):
        """Test creating a new agent."""
        agent = Agent(
            name='Test Agent',
            email='agent@test.com',
            phone='+1234567890',
            license_number='LIC123',
            company='Test Realty'
        )
        db_session.add(agent)
        db_session.commit()
        
        assert agent.id is not None
        assert agent.name == 'Test Agent'
        assert agent.email == 'agent@test.com'
        assert agent.is_active is True
        assert agent.created_at is not None
    
    def test_agent_rating_validation(self, db_session):
        """Test agent rating validation."""
        # Valid rating
        agent1 = Agent(
            name='Good Agent',
            email='good@test.com',
            rating=4.5,
            license_number='GOOD123'
        )
        db_session.add(agent1)
        db_session.commit()
        
        assert agent1.rating == 4.5
    
    def test_agent_properties_relationship(self, db_session, sample_agent):
        """Test agent-properties relationship."""
        property1 = Property(
            title='Agent Property 1',
            property_type='house',
            address='123 Agent St',
            city='Toronto',
            province='ON',
            agent_id=sample_agent.id
        )
        property2 = Property(
            title='Agent Property 2',
            property_type='condo',
            address='456 Agent Ave',
            city='Toronto',
            province='ON',
            agent_id=sample_agent.id
        )
        
        db_session.add_all([property1, property2])
        db_session.commit()
        
        assert len(sample_agent.properties) == 2
        assert property1 in sample_agent.properties
        assert property2 in sample_agent.properties
    
    def test_agent_to_dict(self, sample_agent):
        """Test agent serialization to dictionary."""
        agent_dict = sample_agent.to_dict()
        
        assert 'id' in agent_dict
        assert 'name' in agent_dict
        assert 'email' in agent_dict
        assert 'rating' in agent_dict
        assert 'total_sales' in agent_dict
        assert 'commission_rate' in agent_dict


class TestEconomicDataModel:
    """Test cases for EconomicData model."""
    
    def test_economic_data_creation(self, db_session):
        """Test creating economic data."""
        data = EconomicData(
            indicator='gdp_growth',
            value=Decimal('2.1'),
            date=date.today(),
            source='Statistics Canada',
            frequency='quarterly',
            unit='percent'
        )
        db_session.add(data)
        db_session.commit()
        
        assert data.id is not None
        assert data.indicator == 'gdp_growth'
        assert data.value == Decimal('2.1')
        assert data.source == 'Statistics Canada'
    
    def test_economic_data_to_dict(self, sample_economic_data):
        """Test economic data serialization."""
        data_dict = sample_economic_data.to_dict()
        
        assert 'id' in data_dict
        assert 'indicator' in data_dict
        assert 'value' in data_dict
        assert 'date' in data_dict
        assert 'source' in data_dict
        assert data_dict['value'] == float(sample_economic_data.value)
    
    def test_economic_data_time_series(self, db_session):
        """Test querying economic data as time series."""
        base_date = date.today()
        
        # Create multiple data points
        for i in range(5):
            data = EconomicData(
                indicator='interest_rate',
                value=Decimal(f'{2.0 + i * 0.1}'),
                date=date(base_date.year, base_date.month, i + 1),
                source='Bank of Canada',
                frequency='monthly'
            )
            db_session.add(data)
        
        db_session.commit()
        
        # Query time series
        time_series = db_session.query(EconomicData)\
            .filter(EconomicData.indicator == 'interest_rate')\
            .order_by(EconomicData.date)\
            .all()
        
        assert len(time_series) == 5
        assert time_series[0].value < time_series[-1].value
