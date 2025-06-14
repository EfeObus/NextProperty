"""
Performance tests for NextProperty AI application.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from app.models import Property, Agent
from app.services.data_service import DataService
from app.services.ml_service import MLService


class TestDatabasePerformance:
    """Test database query performance."""
    
    def test_property_search_performance(self, client, test_factory, db_session):
        """Test property search performance with large dataset."""
        # Create a larger dataset for testing
        properties = []
        for i in range(100):
            prop = test_factory.create_property(
                title=f'Property {i}',
                price=400000 + (i * 1000),
                city='Toronto' if i % 2 == 0 else 'Vancouver',
                property_type='house' if i % 3 == 0 else 'condo'
            )
            properties.append(prop)
        
        db_session.add_all(properties)
        db_session.commit()
        
        # Measure search performance
        start_time = time.time()
        
        response = client.get('/api/properties/search', query_string={
            'city': 'Toronto',
            'min_price': 400000,
            'max_price': 500000
        })
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert response.status_code == 200
        assert query_time < 1.0  # Should complete within 1 second
    
    def test_agent_listing_performance(self, client, test_factory, db_session):
        """Test agent listing performance."""
        # Create agents with properties
        for i in range(20):
            agent = test_factory.create_agent(
                name=f'Agent {i}',
                email=f'agent{i}@example.com'
            )
            db_session.add(agent)
            db_session.flush()
            
            # Add properties for each agent
            for j in range(10):
                prop = test_factory.create_property(
                    title=f'Agent {i} Property {j}',
                    agent_id=agent.id
                )
                db_session.add(prop)
        
        db_session.commit()
        
        start_time = time.time()
        response = client.get('/api/agents')
        end_time = time.time()
        
        query_time = end_time - start_time
        
        assert response.status_code == 200
        assert query_time < 0.5  # Should complete within 0.5 seconds
    
    def test_market_analytics_performance(self, client, test_factory, db_session):
        """Test market analytics calculation performance."""
        # Create properties for analytics
        cities = ['Toronto', 'Vancouver', 'Montreal', 'Calgary']
        
        for city in cities:
            for i in range(50):
                prop = test_factory.create_property(
                    title=f'{city} Property {i}',
                    city=city,
                    price=300000 + (i * 5000)
                )
                db_session.add(prop)
        
        db_session.commit()
        
        start_time = time.time()
        response = client.get('/api/analytics/market', query_string={'city': 'Toronto'})
        end_time = time.time()
        
        query_time = end_time - start_time
        
        assert response.status_code == 200
        assert query_time < 2.0  # Complex analytics should complete within 2 seconds


class TestCachePerformance:
    """Test caching system performance."""
    
    @patch('app.cache.cache_manager.redis_client')
    def test_cache_hit_performance(self, mock_redis, client):
        """Test cache hit performance."""
        # Mock cache hit
        mock_redis.get.return_value = b'{"cached": "data"}'
        mock_redis.exists.return_value = True
        
        start_time = time.time()
        
        # Multiple requests to same endpoint
        for _ in range(10):
            response = client.get('/api/properties')
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # With caching, 10 requests should be very fast
        assert total_time < 0.1  # Less than 100ms for 10 cached requests
    
    @patch('app.cache.cache_manager.redis_client')
    def test_cache_miss_performance(self, mock_redis, client, sample_property):
        """Test cache miss performance."""
        # Mock cache miss
        mock_redis.get.return_value = None
        mock_redis.exists.return_value = False
        mock_redis.set.return_value = True
        
        start_time = time.time()
        response = client.get('/api/properties')
        end_time = time.time()
        
        query_time = end_time - start_time
        
        assert response.status_code == 200
        assert query_time < 1.0  # Should still be reasonably fast
    
    def test_cache_warming_performance(self, db_session, test_factory):
        """Test cache warming performance."""
        from app.cache.cache_warming import CacheWarmer
        
        # Create test data
        for i in range(20):
            prop = test_factory.create_property(
                title=f'Warm Property {i}',
                city='Toronto'
            )
            db_session.add(prop)
        
        db_session.commit()
        
        cache_warmer = CacheWarmer()
        
        start_time = time.time()
        with patch.object(cache_warmer, '_warm_popular_searches'):
            cache_warmer.warm_property_caches()
        end_time = time.time()
        
        warming_time = end_time - start_time
        
        # Cache warming should be efficient
        assert warming_time < 5.0  # Should complete within 5 seconds


class TestConcurrencyPerformance:
    """Test application performance under concurrent load."""
    
    def test_concurrent_property_requests(self, client, sample_property):
        """Test concurrent property API requests."""
        def make_request():
            response = client.get('/api/properties')
            return response.status_code
        
        # Simulate concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        total_time = end_time - start_time
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        
        # Should handle 20 concurrent requests efficiently
        assert total_time < 5.0
    
    def test_concurrent_search_requests(self, client, test_factory, db_session):
        """Test concurrent search requests."""
        # Create test data
        for i in range(50):
            prop = test_factory.create_property(
                title=f'Concurrent Property {i}',
                city='Toronto' if i % 2 == 0 else 'Vancouver'
            )
            db_session.add(prop)
        
        db_session.commit()
        
        def search_properties(city):
            response = client.get('/api/properties/search', query_string={'city': city})
            return response.status_code, len(response.get_json().get('results', []))
        
        # Concurrent searches for different cities
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [
                executor.submit(search_properties, 'Toronto'),
                executor.submit(search_properties, 'Vancouver'),
                executor.submit(search_properties, 'Toronto'),
                executor.submit(search_properties, 'Vancouver'),
                executor.submit(search_properties, 'Toronto')
            ]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        total_time = end_time - start_time
        
        # All searches should succeed
        assert all(status == 200 for status, _ in results)
        
        # Should handle concurrent searches efficiently
        assert total_time < 3.0


class TestMLServicePerformance:
    """Test ML service performance."""
    
    @patch('app.services.ml_service.joblib')
    def test_property_valuation_performance(self, mock_joblib, sample_property):
        """Test property valuation performance."""
        from unittest.mock import Mock
        
        # Mock ML model
        mock_model = Mock()
        mock_model.predict.return_value = [450000.0]
        mock_joblib.load.return_value = mock_model
        
        ml_service = MLService()
        
        # Measure prediction time
        start_time = time.time()
        
        with patch.object(ml_service, '_load_valuation_model', return_value=mock_model):
            result = ml_service.predict_property_value(sample_property.to_dict())
        
        end_time = time.time()
        prediction_time = end_time - start_time
        
        assert 'predicted_value' in result
        assert prediction_time < 0.1  # Should be very fast with mocked model
    
    @patch('app.services.ml_service.joblib')
    def test_batch_valuation_performance(self, mock_joblib, test_factory, db_session):
        """Test batch property valuation performance."""
        from unittest.mock import Mock
        
        # Create multiple properties for batch processing
        properties = []
        for i in range(10):
            prop = test_factory.create_property(title=f'Batch Property {i}')
            properties.append(prop.to_dict())
        
        # Mock ML model
        mock_model = Mock()
        mock_model.predict.return_value = [400000 + (i * 10000) for i in range(10)]
        mock_joblib.load.return_value = mock_model
        
        ml_service = MLService()
        
        start_time = time.time()
        
        with patch.object(ml_service, '_load_valuation_model', return_value=mock_model):
            results = []
            for prop in properties:
                result = ml_service.predict_property_value(prop)
                results.append(result)
        
        end_time = time.time()
        batch_time = end_time - start_time
        
        assert len(results) == 10
        assert batch_time < 1.0  # Batch processing should be efficient


class TestExternalAPIPerformance:
    """Test external API integration performance."""
    
    @patch('app.services.external_apis.requests')
    def test_bank_of_canada_api_performance(self, mock_requests):
        """Test Bank of Canada API response time."""
        from app.services.external_apis import ExternalAPIService
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'observations': [
                {'d': '2024-01-01', 'v': '2.5'}
            ]
        }
        mock_requests.get.return_value = mock_response
        
        api_service = ExternalAPIService()
        
        start_time = time.time()
        rates = api_service.get_interest_rates()
        end_time = time.time()
        
        api_time = end_time - start_time
        
        assert len(rates) >= 1
        assert api_time < 0.1  # Mocked API should be very fast
    
    @patch('app.services.external_apis.requests')
    def test_multiple_api_calls_performance(self, mock_requests):
        """Test performance of multiple external API calls."""
        from app.services.external_apis import ExternalAPIService
        
        # Mock responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_requests.get.return_value = mock_response
        
        api_service = ExternalAPIService()
        
        start_time = time.time()
        
        # Multiple API calls
        api_service.get_interest_rates()
        api_service.get_housing_data('Toronto')
        api_service.get_economic_indicators(['gdp'])
        
        end_time = time.time()
        total_api_time = end_time - start_time
        
        # Multiple API calls should complete quickly when mocked
        assert total_api_time < 0.5


class TestDataServicePerformance:
    """Test data service performance."""
    
    def test_market_trends_calculation_performance(self, db_session, test_factory):
        """Test market trends calculation performance."""
        # Create substantial dataset
        for i in range(200):
            prop = test_factory.create_property(
                title=f'Trends Property {i}',
                city='Toronto',
                price=300000 + (i * 1000)
            )
            db_session.add(prop)
        
        db_session.commit()
        
        data_service = DataService(db_session)
        
        start_time = time.time()
        trends = data_service.get_market_trends('Toronto')
        end_time = time.time()
        
        calculation_time = end_time - start_time
        
        assert 'average_price' in trends
        assert calculation_time < 1.0  # Should calculate trends efficiently
    
    def test_comparable_properties_performance(self, db_session, test_factory):
        """Test comparable properties finding performance."""
        # Create properties in same area
        base_property = test_factory.create_property(
            title='Base Property',
            latitude=43.6532,
            longitude=-79.3832,
            city='Toronto'
        )
        db_session.add(base_property)
        db_session.flush()
        
        # Create comparable properties nearby
        for i in range(50):
            comp_prop = test_factory.create_property(
                title=f'Comparable {i}',
                latitude=43.6532 + (i * 0.001),  # Slightly different coordinates
                longitude=-79.3832 + (i * 0.001),
                city='Toronto'
            )
            db_session.add(comp_prop)
        
        db_session.commit()
        
        data_service = DataService(db_session)
        
        start_time = time.time()
        comparables = data_service.find_comparable_properties(
            base_property.id,
            radius_km=5,
            limit=10
        )
        end_time = time.time()
        
        search_time = end_time - start_time
        
        assert len(comparables) >= 1
        assert search_time < 2.0  # Geospatial search should be efficient


class TestMemoryPerformance:
    """Test memory usage and efficiency."""
    
    def test_large_dataset_memory_usage(self, db_session, test_factory):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large dataset
        properties = []
        for i in range(1000):
            prop = test_factory.create_property(
                title=f'Memory Test Property {i}',
                description='A' * 500  # Larger description
            )
            properties.append(prop)
        
        db_session.add_all(properties)
        db_session.commit()
        
        # Query all properties
        all_properties = db_session.query(Property).all()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        assert len(all_properties) == 1000
        # Memory increase should be reasonable (less than 100MB for 1000 properties)
        assert memory_increase < 100 * 1024 * 1024


@pytest.mark.slow
class TestStressTests:
    """Stress tests for the application."""
    
    def test_high_volume_property_creation(self, client, test_factory):
        """Test creating many properties rapidly."""
        property_data = {
            'title': 'Stress Test Property',
            'property_type': 'house',
            'price': 500000,
            'address': '123 Stress St',
            'city': 'Toronto',
            'province': 'ON'
        }
        
        start_time = time.time()
        
        successful_requests = 0
        for i in range(50):
            property_data['title'] = f'Stress Test Property {i}'
            response = client.post(
                '/api/properties',
                json=property_data
            )
            if response.status_code == 201:
                successful_requests += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle rapid property creation
        assert successful_requests >= 40  # At least 80% success rate
        assert total_time < 10.0  # Should complete within 10 seconds
    
    def test_search_stress_test(self, client, test_factory, db_session):
        """Test search functionality under stress."""
        # Create diverse dataset
        cities = ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa']
        property_types = ['house', 'condo', 'townhouse']
        
        for city in cities:
            for prop_type in property_types:
                for i in range(20):
                    prop = test_factory.create_property(
                        title=f'{city} {prop_type} {i}',
                        city=city,
                        property_type=prop_type,
                        price=200000 + (i * 10000)
                    )
                    db_session.add(prop)
        
        db_session.commit()
        
        # Perform multiple complex searches
        search_params = [
            {'city': 'Toronto', 'property_type': 'house'},
            {'min_price': 300000, 'max_price': 500000},
            {'city': 'Vancouver', 'min_bedrooms': 2},
            {'property_type': 'condo'},
            {'city': 'Montreal', 'max_price': 400000}
        ]
        
        start_time = time.time()
        
        successful_searches = 0
        for params in search_params * 10:  # Repeat each search 10 times
            response = client.get('/api/properties/search', query_string=params)
            if response.status_code == 200:
                successful_searches += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should handle multiple complex searches efficiently
        assert successful_searches >= 45  # At least 90% success rate
        assert total_time < 15.0  # Should complete within 15 seconds
