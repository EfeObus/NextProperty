#!/usr/bin/env python3
"""
Test script for Analytics Insights functionality
Demonstrates the new analytics features with sample data
"""

from app import create_app
from app.services.ml_service import MLService

def test_analytics_functionality():
    """Test all analytics features"""
    app = create_app()
    
    with app.app_context():
        ml_service = MLService()
        
        print("🔍 NEXTPROPERTY AI - ANALYTICS INSIGHTS TEST")
        print("=" * 50)
        
        # Test 1: Feature Importance Analysis
        print("\n📊 Testing Feature Importance Analysis...")
        feature_result = ml_service.get_feature_importance_analysis()
        
        if feature_result.get('success'):
            top_features = feature_result.get('top_features', [])
            print(f"✅ Feature analysis successful!")
            print(f"   Model Type: {feature_result.get('model_type')}")
            print(f"   Total Features: {feature_result.get('total_features')}")
            print(f"   Top 5 Features:")
            for i, feature in enumerate(top_features[:5], 1):
                print(f"      {i}. {feature['feature']}: {feature['importance_percent']:.2f}%")
        else:
            print(f"⚠️  Feature analysis unavailable: {feature_result.get('error')}")
        
        # Test 2: Price Analytics by Location
        print("\n🏙️  Testing Price Analytics by Location...")
        price_result = ml_service.get_price_analytics_by_location()
        
        if price_result.get('success'):
            data = price_result.get('data', {})
            summary = price_result.get('summary', {})
            
            print(f"✅ Price analytics successful!")
            print(f"   Cities analyzed: {len(data.get('cities', []))}")
            print(f"   Provinces: {len(data.get('provinces', []))}")
            print(f"   Property types: {len(data.get('property_types', []))}")
            print(f"   Postal zones: {len(data.get('zones', []))}")
            
            # Show top 3 cities by price
            cities = data.get('cities', [])[:3]
            if cities:
                print(f"   Top 3 Cities by Average Price:")
                for i, city in enumerate(cities, 1):
                    price = city['avg_price']
                    count = city['property_count']
                    print(f"      {i}. {city['name']}: ${price:,.0f} ({count} properties)")
            
            # Show property types
            prop_types = data.get('property_types', [])[:3]
            if prop_types:
                print(f"   Top 3 Property Types by Average Price:")
                for i, prop_type in enumerate(prop_types, 1):
                    price = prop_type['avg_price']
                    count = prop_type['property_count']
                    print(f"      {i}. {prop_type['name']}: ${price:,.0f} ({count} properties)")
                    
        else:
            print(f"⚠️  Price analytics failed: {price_result.get('error')}")
        
        # Test 3: Neighbourhood Analysis
        print("\n🏘️  Testing Neighbourhood Analysis...")
        
        # Test with a major city
        test_cities = ['Toronto', 'Vancouver', 'Montreal']
        for city in test_cities:
            neighbourhood_result = ml_service.get_neighbourhood_price_analysis(city)
            
            if neighbourhood_result.get('success'):
                neighbourhoods = neighbourhood_result.get('neighbourhoods', [])
                print(f"   {city}: {len(neighbourhoods)} neighbourhoods analyzed")
                if neighbourhoods:
                    top_neighbourhood = neighbourhoods[0]
                    print(f"      Top area: {top_neighbourhood['neighbourhood']} (${top_neighbourhood['avg_price']:,.0f})")
            else:
                print(f"   {city}: No neighbourhood data available")
                
        # Test 4: URL Routes
        print("\n🌐 Testing URL Routes...")
        from flask import url_for
        
        with app.test_request_context():
            analytics_url = url_for('dashboard.analytics')
            insights_url = url_for('dashboard.analytics_insights')
            
            print(f"   Main Analytics: {analytics_url}")
            print(f"   Deep Insights: {insights_url}")
            print("   ✅ URL routes working correctly")
        
        print("\n" + "=" * 50)
        print("🎉 ANALYTICS INSIGHTS TESTING COMPLETE!")
        print("\nFeatures Available:")
        print("• Feature Importance Analysis with ML model insights")
        print("• Geographic Price Analysis (Cities, Provinces, Zones)")
        print("• Interactive Charts and Visualizations")
        print("• Responsive Design with Bootstrap 5")
        print("• Navigation Integration")
        print("\nAccess via:")
        print("• Main Navigation → Analytics → Advanced Analytics")
        print("• Main Navigation → Analytics → Deep Insights")
        print("• Direct URLs: /dashboard/analytics and /dashboard/analytics/insights")

if __name__ == '__main__':
    test_analytics_functionality()
