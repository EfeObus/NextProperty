#!/usr/bin/env python3

from app import create_app, db
from app.models.property import Property
from app.services.ml_service import MLService
from datetime import datetime
import random

def test_real_time_analytics():
    """Test that analytics update in real-time when new properties are added."""
    
    app = create_app()
    with app.app_context():
        ml_service = MLService()
        
        print("=== Real-Time Analytics Test ===")
        
        # Get initial analytics
        print("\n1. Getting initial analytics...")
        initial_analytics = ml_service.get_price_analytics_by_location()
        
        if not initial_analytics.get('success'):
            print(f"❌ Initial analytics failed: {initial_analytics.get('error')}")
            return
        
        initial_cities = initial_analytics['data']['cities']
        print(f"✅ Initial analytics: {len(initial_cities)} cities")
        
        # Find a test city or create one - use existing city with good data
        test_city = None
        initial_test_city_data = None
        for city_data in initial_cities:
            if city_data['property_count'] > 10:  # Use a city with multiple properties
                test_city = city_data['name']
                initial_test_city_data = city_data
                break
        
        if not test_city:
            print("❌ No suitable test city found")
            return
        
        print(f"   Using {test_city}: ${initial_test_city_data['avg_price']:,.2f} avg, {initial_test_city_data['property_count']} properties")
        
        # Add a new property to the test city
        print(f"\n2. Adding new property to {test_city}...")
        
        new_property = Property(
            listing_id=f"TEST_ANALYTICS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            address=f"{random.randint(100, 999)} Test Analytics St",
            city=test_city,
            province="ON",
            postal_code="T3S7A1",
            property_type="House",
            bedrooms=3,
            bathrooms=2,
            sqft=1800,
            lot_size=0.25,
            rooms=7,
            sold_price=750000.00,  # Set a specific price for testing
            original_price=775000.00,
            year_built=2015,
            dom=25,
            taxes=8500.00,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(new_property)
            db.session.commit()
            print(f"✅ Property added: {new_property.listing_id}")
            print(f"   Price: ${new_property.sold_price:,.2f}")
            
        except Exception as e:
            print(f"❌ Failed to add property: {str(e)}")
            db.session.rollback()
            return
        
        # Get updated analytics
        print("\n3. Getting updated analytics...")
        updated_analytics = ml_service.get_price_analytics_by_location()
        
        if not updated_analytics.get('success'):
            print(f"❌ Updated analytics failed: {updated_analytics.get('error')}")
            return
        
        updated_cities = updated_analytics['data']['cities']
        print(f"✅ Updated analytics: {len(updated_cities)} cities")
        
        # Check if our test city appears in updated data
        updated_test_city_data = None
        for city_data in updated_cities:
            if city_data['name'] == test_city:
                updated_test_city_data = city_data
                break
        
        # Verify real-time update
        print("\n4. Verifying real-time update...")
        
        if updated_test_city_data:
            print(f"✅ {test_city} found in updated data:")
            print(f"   Avg Price: ${updated_test_city_data['avg_price']:,.2f}")
            print(f"   Property Count: {updated_test_city_data['property_count']}")
            
            if initial_test_city_data:
                # Compare with initial data
                price_diff = updated_test_city_data['avg_price'] - initial_test_city_data['avg_price']
                count_diff = updated_test_city_data['property_count'] - initial_test_city_data['property_count']
                print(f"   Changes: Price ${price_diff:+.2f}, Count {count_diff:+d}")
                
                if count_diff > 0:
                    print("✅ REAL-TIME UPDATE CONFIRMED: Property count increased!")
                else:
                    print("⚠️  Property count didn't change as expected")
            else:
                print("✅ REAL-TIME UPDATE CONFIRMED: New city appeared in analytics!")
        else:
            print(f"⚠️  {test_city} not found in updated analytics (might need minimum property threshold)")
        
        # Clean up test property
        print("\n5. Cleaning up test property...")
        try:
            db.session.delete(new_property)
            db.session.commit()
            print("✅ Test property cleaned up")
        except Exception as e:
            print(f"⚠️  Cleanup failed: {str(e)}")
        
        print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_real_time_analytics()
