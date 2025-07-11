#!/usr/bin/env python3
"""
Test script to verify the enhanced feature importance analysis
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ml_service import MLService
import json

def test_feature_analysis():
    """Test the enhanced feature importance analysis"""
    print("Testing Enhanced Feature Importance Analysis...")
    print("=" * 60)
    
    # Initialize ML service
    ml_service = MLService()
    
    # Get feature importance analysis
    analysis = ml_service.get_feature_importance_analysis()
    
    if analysis.get('success'):
        print("✅ Feature importance analysis successful!")
        print(f"📊 Model type: {analysis['model_type']}")
        print(f"🔢 Total features: {analysis['total_features']}")
        print(f"📈 Categories found: {len(analysis['category_importance'])}")
        
        print("\n🏆 Top 10 Most Important Features:")
        print("-" * 50)
        for i, feature in enumerate(analysis['top_10_features'][:10], 1):
            print(f"{i:2d}. {feature['feature']:<25} | {feature['importance_percent']:6.2f}% | {feature['category']}")
        
        print("\n📊 Feature Categories by Importance:")
        print("-" * 40)
        for category in analysis['category_importance']:
            print(f"{category['category']:<25} | {category['importance_percent']:6.1f}%")
        
        print("\n🔍 All 26 Features Summary:")
        print("-" * 60)
        for feature in analysis['all_features']:
            status = "🔥" if feature['importance_percent'] > 5 else "📈" if feature['importance_percent'] > 2 else "📊"
            print(f"#{feature['rank']:2d} {status} {feature['feature']:<25} | {feature['importance_percent']:6.2f}% | {feature['category']}")
        
        # Verify we have exactly 26 features
        if len(analysis['all_features']) == 26:
            print("\n✅ Confirmed: All 26 features are present!")
        else:
            print(f"\n⚠️  Warning: Expected 26 features, found {len(analysis['all_features'])}")
        
        # Check if importance scores sum to reasonable total
        total_importance = sum(f['importance_percent'] for f in analysis['all_features'])
        print(f"📈 Total importance percentage: {total_importance:.1f}%")
        
        if 95 <= total_importance <= 105:
            print("✅ Importance scores are properly normalized!")
        else:
            print("⚠️  Warning: Importance scores may not be properly normalized")
        
        return True
        
    else:
        print(f"❌ Feature importance analysis failed: {analysis.get('error', 'Unknown error')}")
        return False

def test_model_prediction():
    """Test model prediction to ensure it's working"""
    print("\n" + "=" * 60)
    print("Testing Model Prediction Capability...")
    print("=" * 60)
    
    ml_service = MLService()
    
    # Test with sample property data
    test_property = {
        'bedrooms': 3,
        'bathrooms': 2,
        'square_feet': 1500,
        'lot_size': 6000,
        'city': 'Toronto',
        'property_type': 'Detached',
        'year_built': 2010
    }
    
    result = ml_service.predict_property_price(test_property)
    
    if result.get('predicted_price'):
        print("✅ Model prediction successful!")
        print(f"🏠 Sample property prediction: ${result['predicted_price']:,.0f}")
        print(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
        print(f"📊 Method: {result.get('prediction_method', 'unknown')}")
        return True
    else:
        print(f"❌ Model prediction failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    print("🚀 NextProperty AI - Enhanced Feature Analysis Test")
    print("=" * 60)
    
    try:
        # Test feature analysis
        feature_test = test_feature_analysis()
        
        # Test prediction
        prediction_test = test_model_prediction()
        
        print("\n" + "=" * 60)
        print("📋 Test Summary:")
        print("=" * 60)
        print(f"Feature Analysis: {'✅ PASS' if feature_test else '❌ FAIL'}")
        print(f"Model Prediction: {'✅ PASS' if prediction_test else '❌ FAIL'}")
        
        if feature_test and prediction_test:
            print("\n🎉 All tests passed! The enhanced feature analysis is ready!")
            print("🌐 Visit: http://localhost:5007/dashboard/analytics/insights")
        else:
            print("\n⚠️  Some tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        import traceback
        traceback.print_exc()
