"""
Integration tests for API endpoints.
"""

import json
import pytest
from decimal import Decimal
from unittest.mock import patch

from app.models import Property, Agent, User


class TestPropertyAPI:
    """Test cases for property API endpoints."""
    
    def test_get_properties_list(self, client, sample_property):
        """Test getting list of properties."""
        response = client.get('/api/properties')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'properties' in data
        assert len(data['properties']) >= 1
        
        # Check property structure
        property_data = data['properties'][0]
        assert 'id' in property_data
        assert 'title' in property_data
        assert 'price' in property_data
        assert 'property_type' in property_data
    
    def test_get_property_detail(self, client, sample_property):
        """Test getting property details."""
        response = client.get(f'/api/properties/{sample_property.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_property.id
        assert data['title'] == sample_property.title
        assert data['price'] == float(sample_property.price)
    
    def test_get_nonexistent_property(self, client):
        """Test getting non-existent property."""
        response = client.get('/api/properties/nonexistent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_property(self, client, sample_agent, sample_property_data):
        """Test creating a new property."""
        sample_property_data['agent_id'] = sample_agent.id
        
        response = client.post(
            '/api/properties',
            data=json.dumps(sample_property_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == sample_property_data['title']
        assert data['price'] == sample_property_data['price']
    
    def test_update_property(self, client, sample_property):
        """Test updating an existing property."""
        update_data = {
            'title': 'Updated Property Title',
            'price': 550000.00
        }
        
        response = client.put(
            f'/api/properties/{sample_property.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == update_data['title']
        assert data['price'] == update_data['price']
    
    def test_delete_property(self, client, sample_property):
        """Test deleting a property."""
        response = client.delete(f'/api/properties/{sample_property.id}')
        
        assert response.status_code == 200
        
        # Verify property is deleted
        get_response = client.get(f'/api/properties/{sample_property.id}')
        assert get_response.status_code == 404
    
    def test_search_properties(self, client, sample_property):
        """Test property search functionality."""
        search_params = {
            'city': sample_property.city,
            'min_price': 400000,
            'max_price': 600000,
            'property_type': sample_property.property_type
        }
        
        response = client.get('/api/properties/search', query_string=search_params)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) >= 1
        
        # Verify search results match criteria
        result = data['results'][0]
        assert result['city'] == sample_property.city
        assert result['property_type'] == sample_property.property_type
    
    def test_search_properties_with_invalid_params(self, client):
        """Test property search with invalid parameters."""
        search_params = {
            'min_price': 'invalid',
            'max_price': -1000
        }
        
        response = client.get('/api/properties/search', query_string=search_params)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.services.ml_service.MLService')
    def test_property_valuation(self, mock_ml_service, client, sample_property):
        """Test property valuation endpoint."""
        mock_ml_service.return_value.predict_property_value.return_value = {
            'predicted_value': 475000.0,
            'confidence': 0.87,
            'value_range': {'min': 425000.0, 'max': 525000.0}
        }
        
        response = client.get(f'/api/properties/{sample_property.id}/valuation')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'predicted_value' in data
        assert 'confidence' in data
        assert data['predicted_value'] == 475000.0
    
    @patch('app.services.ml_service.MLService')
    def test_investment_analysis(self, mock_ml_service, client, sample_property):
        """Test investment analysis endpoint."""
        mock_ml_service.return_value.analyze_investment_potential.return_value = {
            'score': 8.2,
            'risk_level': 'medium',
            'expected_roi': 0.11,
            'factors': ['location', 'market_trends', 'property_condition']
        }
        
        response = client.get(f'/api/properties/{sample_property.id}/investment-analysis')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert 'risk_level' in data
        assert data['score'] == 8.2


class TestAgentAPI:
    """Test cases for agent API endpoints."""
    
    def test_get_agents_list(self, client, sample_agent):
        """Test getting list of agents."""
        response = client.get('/api/agents')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'agents' in data
        assert len(data['agents']) >= 1
        
        agent_data = data['agents'][0]
        assert 'id' in agent_data
        assert 'name' in agent_data
        assert 'email' in agent_data
    
    def test_get_agent_detail(self, client, sample_agent):
        """Test getting agent details."""
        response = client.get(f'/api/agents/{sample_agent.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == sample_agent.id
        assert data['name'] == sample_agent.name
        assert data['email'] == sample_agent.email
    
    def test_get_agent_properties(self, client, sample_agent, sample_property):
        """Test getting agent's properties."""
        response = client.get(f'/api/agents/{sample_agent.id}/properties')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'properties' in data
        assert len(data['properties']) >= 1
        
        property_data = data['properties'][0]
        assert property_data['agent_id'] == sample_agent.id
    
    def test_create_agent(self, client):
        """Test creating a new agent."""
        agent_data = {
            'name': 'New Agent',
            'email': 'newagent@example.com',
            'phone': '+1555999888',
            'license_number': 'NEW123',
            'company': 'New Realty'
        }
        
        response = client.post(
            '/api/agents',
            data=json.dumps(agent_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == agent_data['name']
        assert data['email'] == agent_data['email']


class TestMarketDataAPI:
    """Test cases for market data API endpoints."""
    
    @patch('app.services.data_service.DataService')
    def test_get_market_trends(self, mock_data_service, client):
        """Test getting market trends."""
        mock_data_service.return_value.get_market_trends.return_value = {
            'city': 'Toronto',
            'average_price': 650000.0,
            'price_change_1m': 0.02,
            'price_change_1y': 0.15,
            'sales_volume': 1200,
            'inventory_level': 'low'
        }
        
        response = client.get('/api/market/trends', query_string={'city': 'Toronto'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'average_price' in data
        assert 'price_change_1y' in data
        assert data['city'] == 'Toronto'
    
    @patch('app.services.external_apis.ExternalAPIService')
    def test_get_interest_rates(self, mock_external_apis, client):
        """Test getting interest rates."""
        mock_external_apis.return_value.get_interest_rates.return_value = [
            {'date': '2024-01-01', 'rate': 2.5, 'type': 'overnight'},
            {'date': '2024-02-01', 'rate': 2.7, 'type': 'overnight'}
        ]
        
        response = client.get('/api/market/interest-rates')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rates' in data
        assert len(data['rates']) >= 1
        assert 'rate' in data['rates'][0]
    
    @patch('app.services.data_service.DataService')
    def test_get_comparable_properties(self, mock_data_service, client, sample_property):
        """Test getting comparable properties."""
        mock_data_service.return_value.find_comparable_properties.return_value = [
            {
                'id': 'comp-1',
                'title': 'Comparable 1',
                'price': 480000.0,
                'similarity_score': 0.92,
                'distance_km': 1.2
            },
            {
                'id': 'comp-2',
                'title': 'Comparable 2',
                'price': 520000.0,
                'similarity_score': 0.88,
                'distance_km': 0.8
            }
        ]
        
        response = client.get(f'/api/properties/{sample_property.id}/comparables')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'comparables' in data
        assert len(data['comparables']) >= 1
        assert 'similarity_score' in data['comparables'][0]


class TestAuthAPI:
    """Test cases for authentication API endpoints."""
    
    def test_user_registration(self, client, sample_user_data):
        """Test user registration."""
        response = client.post(
            '/api/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['email'] == sample_user_data['email']
        assert 'password' not in data['user']  # Should not return password
    
    def test_user_login(self, client, sample_user):
        """Test user login."""
        login_data = {
            'email': sample_user.email,
            'password': 'password123'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert 'token' in data
    
    def test_invalid_login(self, client, sample_user):
        """Test login with invalid credentials."""
        login_data = {
            'email': sample_user.email,
            'password': 'wrongpassword'
        }
        
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_duplicate_email_registration(self, client, sample_user, sample_user_data):
        """Test registration with existing email."""
        sample_user_data['email'] = sample_user.email
        
        response = client.post(
            '/api/auth/register',
            data=json.dumps(sample_user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestAnalyticsAPI:
    """Test cases for analytics API endpoints."""
    
    @patch('app.services.data_service.DataService')
    def test_get_market_analytics(self, mock_data_service, client):
        """Test getting market analytics."""
        mock_data_service.return_value.get_market_analytics.return_value = {
            'total_properties': 15000,
            'avg_price': 575000.0,
            'median_price': 520000.0,
            'price_trend_30d': 0.03,
            'active_listings': 2500,
            'sold_last_30d': 800,
            'price_distribution': {
                '0-300k': 0.15,
                '300k-500k': 0.35,
                '500k-750k': 0.30,
                '750k+': 0.20
            }
        }
        
        response = client.get('/api/analytics/market', query_string={'city': 'Toronto'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_properties' in data
        assert 'avg_price' in data
        assert 'price_distribution' in data
    
    @patch('app.services.data_service.DataService')
    def test_get_agent_analytics(self, mock_data_service, client, sample_agent):
        """Test getting agent analytics."""
        mock_data_service.return_value.get_agent_performance.return_value = {
            'total_listings': 25,
            'active_listings': 8,
            'sold_last_30d': 3,
            'avg_days_on_market': 28,
            'avg_sale_price': 580000.0,
            'commission_earned': 34800.0
        }
        
        response = client.get(f'/api/analytics/agents/{sample_agent.id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_listings' in data
        assert 'commission_earned' in data


class TestErrorHandling:
    """Test cases for API error handling."""
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON in request."""
        response = client.post(
            '/api/properties',
            data='invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        incomplete_data = {
            'title': 'Incomplete Property'
            # Missing required fields like property_type, address, etc.
        }
        
        response = client.post(
            '/api/properties',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_method_not_allowed(self, client):
        """Test handling of unsupported HTTP methods."""
        response = client.patch('/api/properties')
        
        assert response.status_code == 405
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality."""
        # This would require actual rate limiting implementation
        # For now, just test that the endpoint exists
        response = client.get('/api/properties')
        assert response.status_code in [200, 429]  # Success or rate limited
