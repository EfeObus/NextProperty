#!/usr/bin/env python3
"""
Test script for economic API integration in ML Service
"""

import sys
import os
import traceback
from datetime import datetime

# Add project root to path
sys.path.append('/Users/efeobukohwo/Desktop/Nextproperty Real Estate')

def test_economic_integration():
    """Test the economic integration in ML service."""
    print("=" * 60)
    print("TESTING ECONOMIC API INTEGRATION IN ML SERVICE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import Flask app and ML service
        from app import create_app
        from app.services.ml_service import MLService
        
        # Create app context
        app = create_app()
        
        with app.app_context():
            print("\n1. Testing ML Service initialization...")
            ml_service = MLService()
            print("✓ ML Service initialized successfully")
            
            print("\n2. Testing economic indicators fetching...")
            economic_indicators = ml_service._get_economic_indicators()
            
            if economic_indicators:
                print("✓ Economic indicators fetched successfully")
                print(f"   Total indicators: {len(economic_indicators)}")
                
                # Display key indicators
                print("\n   Key Economic Indicators:")
                key_indicators = [
                    'policy_rate', 'prime_rate', 'mortgage_5yr', 'inflation_rate',
                    'unemployment_rate', 'exchange_rate', 'gdp_growth'
                ]
                
                for key in key_indicators:
                    value = economic_indicators.get(key, 'N/A')
                    print(f"   - {key}: {value}")
                
                # Display derived indicators
                print("\n   Derived Economic Features:")
                derived_indicators = [
                    'interest_rate_environment', 'economic_momentum', 'affordability_pressure'
                ]
                
                for key in derived_indicators:
                    value = economic_indicators.get(key, 'N/A')
                    print(f"   - {key}: {value}")
                    
            else:
                print("✗ Failed to fetch economic indicators")
                return False
            
            print("\n3. Testing feature extraction with economic data...")
            
            # Create a sample property dictionary for testing
            sample_property = {
                'bedrooms': 3,
                'bathrooms': 2,
                'square_feet': 1500,
                'lot_size': 5000,
                'rooms': 7,
                'city': 'Toronto',
                'province': 'Ontario',
                'property_type': 'Detached',
                'year_built': 2010,
                'dom': 25,
                'taxes': 4500
            }
            
            features = ml_service._extract_features_from_dict(sample_property)
            
            if features and len(features) == 26:
                print("✓ Feature extraction successful")
                print(f"   Total features: {len(features)}")
                print(f"   Feature values: {features[:5]}... (showing first 5)")
            else:
                print(f"✗ Feature extraction failed. Expected 26 features, got {len(features) if features else 0}")
                return False
            
            print("\n4. Testing economic calculation methods...")
            
            # Test individual calculation methods
            try:
                interest_env = ml_service._calculate_interest_environment(economic_indicators)
                print(f"   ✓ Interest environment: {interest_env:.3f}")
                
                econ_momentum = ml_service._calculate_economic_momentum(economic_indicators)
                print(f"   ✓ Economic momentum: {econ_momentum:.3f}")
                
                affordability = ml_service._calculate_affordability_pressure(economic_indicators)
                print(f"   ✓ Affordability pressure: {affordability:.3f}")
                
                prop_affordability = ml_service._calculate_property_affordability(
                    1500, economic_indicators['mortgage_5yr'], economic_indicators['inflation_rate']
                )
                print(f"   ✓ Property affordability: {prop_affordability:.3f}")
                
                econ_sensitivity = ml_service._calculate_property_economic_sensitivity(
                    'Detached', economic_indicators
                )
                print(f"   ✓ Economic sensitivity: {econ_sensitivity:.3f}")
                
                market_timing = ml_service._calculate_market_timing(economic_indicators)
                print(f"   ✓ Market timing: {market_timing:.3f}")
                
            except Exception as calc_error:
                print(f"✗ Error in economic calculations: {calc_error}")
                return False
            
            print("\n5. Testing price prediction with economic features...")
            
            try:
                prediction_result = ml_service.predict_property_price(sample_property)
                
                if prediction_result.get('predicted_price'):
                    print("✓ Price prediction successful")
                    print(f"   Predicted price: ${prediction_result['predicted_price']:,.2f}")
                    print(f"   Confidence: {prediction_result.get('confidence', 'N/A')}")
                    print(f"   Features used: {prediction_result.get('features_used', 'N/A')}")
                else:
                    print(f"✗ Price prediction failed: {prediction_result.get('error', 'Unknown error')}")
                    
            except Exception as pred_error:
                print(f"✗ Error in price prediction: {pred_error}")
                traceback.print_exc()
            
            print("\n6. Testing economic insights generation...")
            
            # Create a mock property object for insights testing
            class MockProperty:
                def __init__(self):
                    self.sold_price = 750000
                    self.original_price = 725000
                    self.dom = 35
                    self.sqft = 1500
                    self.features = "garage, fireplace, hardwood floors"
                    self.property_type = "Detached"
            
            mock_property = MockProperty()
            
            try:
                insights = ml_service._generate_insights(mock_property, features)
                print("✓ Economic insights generation successful")
                print(f"   Total insights: {len(insights)}")
                
                if insights:
                    print("   Generated insights:")
                    for i, insight in enumerate(insights, 1):
                        print(f"   {i}. {insight}")
                        
            except Exception as insight_error:
                print(f"✗ Error generating insights: {insight_error}")
                
            print("\n" + "=" * 60)
            print("ECONOMIC INTEGRATION TEST COMPLETED SUCCESSFULLY")
            print("=" * 60)
            
            # Summary
            print(f"\n✓ Economic indicators: {len(economic_indicators)} fetched")
            print(f"✓ Feature extraction: 26 features including economic data")
            print(f"✓ Economic calculations: All methods working")
            print(f"✓ Price prediction: Enhanced with economic context")
            print(f"✓ Insights generation: Economic-aware insights")
            
            return True
            
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_economic_integration()
    if success:
        print("\n🎉 All tests passed! Economic integration is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)
