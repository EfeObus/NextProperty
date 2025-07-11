#!/usr/bin/env python3
"""
Test script to verify property upload functionality
"""

from app import create_app
from app.models.property import Property, PropertyPhoto
from app import db
import uuid
import random
from datetime import datetime

app = create_app()

# Test property upload simulation
with app.app_context():
    # Create a test property like the upload form would
    listing_id = f'NPTest{str(uuid.uuid4()).replace("-", "")[:6].upper()}'
    
    test_property = Property(
        listing_id=listing_id,
        mls=f'MLS{random.randint(100000, 999999)}',
        property_type='Detached',
        address='123 Test Upload Street',
        city='Toronto',
        province='ON',
        postal_code='M1M1M1',
        latitude=43.6532 + random.uniform(-0.05, 0.05),
        longitude=-79.3832 + random.uniform(-0.05, 0.05),
        original_price=750000.00,
        bedrooms=3,
        bathrooms=2.5,
        sqft=1800,
        lot_size=5000,
        features='Modern kitchen, hardwood floors, garage',
        remarks='Beautiful test property with updated features',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        # Add property to database
        db.session.add(test_property)
        db.session.commit()
        
        print(f'✅ Test property {listing_id} successfully uploaded to MySQL database!')
        print(f'Address: {test_property.address}, {test_property.city}')
        print(f'Price: ${test_property.original_price:,.2f}')
        print(f'Features: {test_property.features}')
        
        # Verify it exists
        check_property = Property.query.filter_by(listing_id=listing_id).first()
        if check_property:
            print('✅ Property verified in database')
        else:
            print('❌ Property not found after upload')
            
        # Clean up test property
        db.session.delete(test_property)
        db.session.commit()
        print('✅ Test cleanup completed')
        
    except Exception as e:
        print(f'❌ Error uploading test property: {e}')
        db.session.rollback()
