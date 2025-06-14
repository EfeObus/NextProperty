"""
Unit tests for service classes.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, date

from app.services.ml_service import MLService
from app.services.data_service import DataService
from app.services.external_apis import ExternalAPIService
from app.services.geospatial_service import GeospatialService


class TestMLService:
    """Test cases for ML Service."""
    
    def test_ml_service_initialization(self):
        """Test ML service initialization."""
        ml_service = MLService()
        assert ml_service is not None
    
    @patch('app.services.ml_service.joblib')
    def test_predict_property_value(self, mock_joblib, sample_property):
        """Test property value prediction."""
        # Mock the model
        mock_model = Mock()
        mock_model.predict.return_value = [450000.0]
        mock_joblib.load.return_value = mock_model
        
        ml_service = MLService()
        
        # Mock model loading
        with patch.object(ml_service, '_load_valuation_model', return_value=mock_model):
            result = ml_service.predict_property_value(sample_property.to_dict())
        
        assert 'predicted_value' in result
        assert 'confidence' in result
        assert 'value_range' in result
        assert isinstance(result['predicted_value'], float)
        assert 0 <= result['confidence'] <= 1
    
    @patch('app.services.ml_service.joblib')
    def test_analyze_investment_potential(self, mock_joblib, sample_property):
        """Test investment potential analysis."""
        mock_model = Mock()
        mock_model.predict_proba.return_value = [[0.1, 0.3, 0.6]]
        mock_joblib.load.return_value = mock_model
        
        ml_service = MLService()
        
        with patch.object(ml_service, '_load_investment_model', return_value=mock_model):
            result = ml_service.analyze_investment_potential(sample_property.to_dict())
        
        assert 'score' in result
        assert 'risk_level' in result
        assert 'expected_roi' in result
        assert 'factors' in result
        assert 0 <= result['score'] <= 10
        assert result['risk_level'] in ['low', 'medium', 'high']
    
    def test_prepare_property_features(self, sample_property):
        """Test property feature preparation for ML models."""
        ml_service = MLService()
        features = ml_service._prepare_property_features(sample_property.to_dict())
        
        assert isinstance(features, dict)
        assert 'bedrooms' in features
        assert 'bathrooms' in features
        assert 'square_feet' in features
        assert 'age' in features
    
    @patch('app.services.ml_service.requests')
    def test_market_trend_prediction(self, mock_requests):
        """Test market trend prediction."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'prediction': 'upward',
            'confidence': 0.78,
            'factors': ['low_inventory', 'economic_growth']
        }
        mock_requests.post.return_value = mock_response
        
        ml_service = MLService()
        result = ml_service.predict_market_trends('Toronto', 'quarterly')
        
        assert 'prediction' in result
        assert 'confidence' in result
        assert result['prediction'] in ['upward', 'downward', 'stable']
    
    def test_calculate_property_score(self, sample_property):
        """Test property scoring algorithm."""
        ml_service = MLService()
        
        property_data = sample_property.to_dict()
        score = ml_service._calculate_property_score(property_data)
        
        assert isinstance(score, (int, float))
        assert 0 <= score <= 10


class TestDataService:
    """Test cases for Data Service."""
    
    def test_data_service_initialization(self, db_session):
        """Test data service initialization."""
        data_service = DataService(db_session)
        assert data_service.db == db_session
    
    def test_get_market_trends(self, db_session, sample_property):
        """Test market trends calculation."""
        data_service = DataService(db_session)
        
        trends = data_service.get_market_trends('Toronto')
        
        assert 'average_price' in trends
        assert 'median_price' in trends
        assert 'total_properties' in trends
        assert isinstance(trends['average_price'], (int, float))
    
    def test_get_property_insights(self, db_session, sample_property):
        """Test property insights generation."""
        data_service = DataService(db_session)
        
        insights = data_service.get_property_insights(sample_property.id)
        
        assert 'price_analysis' in insights
        assert 'market_position' in insights
        assert 'investment_metrics' in insights
    
    def test_calculate_roi(self, db_session):
        """Test ROI calculation."""
        data_service = DataService(db_session)
        
        roi = data_service.calculate_roi(
            purchase_price=500000,
            rental_income=2500,
            expenses=800,
            appreciation_rate=0.05
        )
        
        assert 'monthly_cash_flow' in roi
        assert 'annual_roi' in roi
        assert 'cap_rate' in roi
        assert isinstance(roi['annual_roi'], (int, float))
    
    def test_find_comparable_properties(self, db_session, sample_property):
        """Test finding comparable properties."""
        data_service = DataService(db_session)
        
        comparables = data_service.find_comparable_properties(
            sample_property.id,
            radius_km=5,
            limit=10
        )
        
        assert isinstance(comparables, list)
        for comp in comparables:
            assert 'id' in comp
            assert 'similarity_score' in comp
            assert 'distance_km' in comp
    
    def test_get_price_history(self, db_session, sample_property):
        """Test price history retrieval."""
        data_service = DataService(db_session)
        
        history = data_service.get_price_history(sample_property.id)
        
        assert isinstance(history, list)
        assert 'price' in history[0] if history else True
        assert 'date' in history[0] if history else True
    
    def test_get_market_analytics(self, db_session):
        """Test market analytics calculation."""
        data_service = DataService(db_session)
        
        analytics = data_service.get_market_analytics('Toronto')
        
        assert 'total_properties' in analytics
        assert 'price_distribution' in analytics
        assert 'inventory_levels' in analytics
        assert isinstance(analytics['total_properties'], int)
    
    def test_get_agent_performance(self, db_session, sample_agent):
        """Test agent performance metrics."""
        data_service = DataService(db_session)
        
        performance = data_service.get_agent_performance(sample_agent.id)
        
        assert 'total_listings' in performance
        assert 'avg_days_on_market' in performance
        assert 'success_rate' in performance
        assert isinstance(performance['total_listings'], int)


class TestExternalAPIService:
    """Test cases for External API Service."""
    
    def test_external_api_service_initialization(self):
        """Test external API service initialization."""
        api_service = ExternalAPIService()
        assert api_service is not None
    
    @patch('app.services.external_apis.requests')
    def test_get_interest_rates(self, mock_requests):
        """Test Bank of Canada interest rates API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'observations': [
                {'d': '2024-01-01', 'v': '2.5'},
                {'d': '2024-02-01', 'v': '2.7'}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        api_service = ExternalAPIService()
        rates = api_service.get_interest_rates()
        
        assert isinstance(rates, list)
        assert len(rates) >= 1
        assert 'date' in rates[0]
        assert 'rate' in rates[0]
    
    @patch('app.services.external_apis.requests')
    def test_get_housing_data(self, mock_requests):
        """Test Statistics Canada housing data API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'object': [
                {
                    'vectorDataPoint': [
                        {'refPer': '2024-01', 'value': 650000}
                    ]
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        api_service = ExternalAPIService()
        housing_data = api_service.get_housing_data('Toronto')
        
        assert 'average_price' in housing_data
        assert 'date' in housing_data
        assert isinstance(housing_data['average_price'], (int, float))
    
    @patch('app.services.external_apis.requests')
    def test_get_economic_indicators(self, mock_requests):
        """Test economic indicators API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'observations': [
                {'d': '2024-01-01', 'v': '2.1'}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        api_service = ExternalAPIService()
        indicators = api_service.get_economic_indicators(['gdp_growth'])
        
        assert isinstance(indicators, dict)
        assert 'gdp_growth' in indicators
    
    def test_api_error_handling(self):
        """Test API error handling."""
        api_service = ExternalAPIService()
        
        with patch('app.services.external_apis.requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            # Should handle gracefully and return empty data
            result = api_service.get_interest_rates()
            assert result == []
    
    @patch('app.services.external_apis.requests')
    def test_rate_limiting(self, mock_requests):
        """Test API rate limiting handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_requests.get.return_value = mock_response
        
        api_service = ExternalAPIService()
        
        # Should handle rate limiting gracefully
        result = api_service.get_interest_rates()
        assert result == []


class TestGeospatialService:
    """Test cases for Geospatial Service."""
    
    def test_geospatial_service_initialization(self):
        """Test geospatial service initialization."""
        geo_service = GeospatialService()
        assert geo_service is not None
    
    def test_calculate_distance(self):
        """Test distance calculation between coordinates."""
        geo_service = GeospatialService()
        
        # Distance between Toronto and Vancouver (approximately 3300km)
        distance = geo_service.calculate_distance(
            43.6532, -79.3832,  # Toronto
            49.2827, -123.1207  # Vancouver
        )
        
        assert isinstance(distance, float)
        assert 3000 < distance < 4000  # Approximate distance
    
    @patch('app.services.geospatial_service.requests')
    def test_geocode_address(self, mock_requests):
        """Test address geocoding."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'geometry': {
                    'location': {'lat': 43.6532, 'lng': -79.3832}
                },
                'formatted_address': '123 Main St, Toronto, ON, Canada'
            }]
        }
        mock_requests.get.return_value = mock_response
        
        geo_service = GeospatialService()
        result = geo_service.geocode_address('123 Main St, Toronto, ON')
        
        assert 'latitude' in result
        assert 'longitude' in result
        assert 'formatted_address' in result
        assert isinstance(result['latitude'], float)
        assert isinstance(result['longitude'], float)
    
    @patch('app.services.geospatial_service.requests')
    def test_reverse_geocode(self, mock_requests):
        """Test reverse geocoding (coordinates to address)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'formatted_address': 'Toronto, ON, Canada',
                'address_components': [
                    {'long_name': 'Toronto', 'types': ['locality']},
                    {'long_name': 'Ontario', 'types': ['administrative_area_level_1']},
                    {'long_name': 'Canada', 'types': ['country']}
                ]
            }]
        }
        mock_requests.get.return_value = mock_response
        
        geo_service = GeospatialService()
        result = geo_service.reverse_geocode(43.6532, -79.3832)
        
        assert 'address' in result
        assert 'city' in result
        assert 'province' in result
        assert 'country' in result
    
    def test_find_properties_nearby(self, db_session, sample_property):
        """Test finding properties within radius."""
        geo_service = GeospatialService()
        
        nearby = geo_service.find_properties_nearby(
            db_session,
            43.6532, -79.3832,  # Toronto coordinates
            radius_km=10
        )
        
        assert isinstance(nearby, list)
        for prop in nearby:
            assert 'id' in prop
            assert 'distance_km' in prop
    
    def test_get_neighborhood_info(self):
        """Test neighborhood information retrieval."""
        geo_service = GeospatialService()
        
        with patch.object(geo_service, '_fetch_neighborhood_data') as mock_fetch:
            mock_fetch.return_value = {
                'name': 'Downtown Toronto',
                'population': 250000,
                'median_income': 75000,
                'amenities': ['subway', 'shopping', 'restaurants']
            }
            
            info = geo_service.get_neighborhood_info(43.6532, -79.3832)
            
            assert 'name' in info
            assert 'population' in info
            assert 'amenities' in info
    
    def test_calculate_commute_time(self):
        """Test commute time calculation."""
        geo_service = GeospatialService()
        
        with patch('app.services.geospatial_service.requests') as mock_requests:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'routes': [{
                    'legs': [{
                        'duration': {'value': 1800, 'text': '30 mins'},
                        'distance': {'value': 15000, 'text': '15 km'}
                    }]
                }]
            }
            mock_requests.get.return_value = mock_response
            
            commute = geo_service.calculate_commute_time(
                43.6532, -79.3832,  # Origin
                43.7532, -79.2832,  # Destination
                mode='driving'
            )
            
            assert 'duration_minutes' in commute
            assert 'distance_km' in commute
            assert isinstance(commute['duration_minutes'], (int, float))
    
    def test_validate_coordinates(self):
        """Test coordinate validation."""
        geo_service = GeospatialService()
        
        # Valid coordinates
        assert geo_service.validate_coordinates(43.6532, -79.3832) is True
        
        # Invalid coordinates
        assert geo_service.validate_coordinates(200, -300) is False
        assert geo_service.validate_coordinates('invalid', 'coords') is False
