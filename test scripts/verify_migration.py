#!/usr/bin/env python3
"""
Verify the MySQL database and show sample data.
"""

import pymysql
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.property import Property

def verify_mysql_data():
    """Verify the data in MySQL database."""
    print("🔍 Verifying MySQL Database Contents")
    print("=" * 50)
    
    # Create Flask app context
    os.environ['DATABASE_URL'] = 'mysql+pymysql://root:Jesutekevwe1%40%40@localhost:3306/nextproperty_ai'
    app = create_app()
    
    with app.app_context():
        # Basic counts
        total_properties = Property.query.count()
        print(f"📊 Total Properties: {total_properties:,}")
        
        # Count by property type
        print("\n📋 Properties by Type:")
        property_types = db.session.query(
            Property.property_type, 
            db.func.count(Property.listing_id)
        ).group_by(Property.property_type).all()
        
        for prop_type, count in property_types:
            print(f"  • {prop_type}: {count:,}")
        
        # Count by city (top 10)
        print("\n🏙️ Top 10 Cities:")
        cities = db.session.query(
            Property.city, 
            db.func.count(Property.listing_id)
        ).group_by(Property.city).order_by(
            db.func.count(Property.listing_id).desc()
        ).limit(10).all()
        
        for city, count in cities:
            print(f"  • {city}: {count:,}")
        
        # Price statistics
        print("\n💰 Price Statistics:")
        price_stats = db.session.query(
            db.func.min(Property.sold_price).label('min_price'),
            db.func.max(Property.sold_price).label('max_price'),
            db.func.avg(Property.sold_price).label('avg_price')
        ).filter(Property.sold_price.isnot(None)).first()
        
        if price_stats:
            print(f"  • Minimum Price: ${price_stats.min_price:,.2f}")
            print(f"  • Maximum Price: ${price_stats.max_price:,.2f}")
            print(f"  • Average Price: ${price_stats.avg_price:,.2f}")
        
        # Sample properties
        print("\n🏠 Sample Properties:")
        sample_properties = Property.query.filter(
            Property.sold_price.isnot(None)
        ).limit(5).all()
        
        for prop in sample_properties:
            print(f"  • ID: {prop.listing_id}")
            print(f"    Address: {prop.address}, {prop.city}")
            print(f"    Type: {prop.property_type}")
            print(f"    Price: ${prop.sold_price:,.2f}")
            print(f"    Bedrooms: {prop.bedrooms}, Bathrooms: {prop.bathrooms}")
            print()

def verify_direct_mysql():
    """Verify data using direct MySQL connection."""
    print("\n🔗 Direct MySQL Verification")
    print("=" * 30)
    
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Jesutekevwe1@@',
            database='nextproperty_ai',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Show tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("📋 Database Tables:")
            for table in tables:
                print(f"  • {table[0]}")
            
            # Count records in properties table
            cursor.execute("SELECT COUNT(*) FROM properties;")
            count = cursor.fetchone()[0]
            print(f"\n📊 Total records in properties table: {count:,}")
            
            # Sample data
            cursor.execute("""
                SELECT listing_id, address, city, property_type, sold_price 
                FROM properties 
                WHERE sold_price IS NOT NULL 
                LIMIT 3;
            """)
            
            rows = cursor.fetchall()
            print("\n🏠 Sample Records:")
            for row in rows:
                listing_id, address, city, prop_type, price = row
                print(f"  • {listing_id}: {address}, {city} - {prop_type} - ${price:,.2f}")
        
        connection.close()
        print("\n✅ Direct MySQL verification successful!")
        
    except Exception as e:
        print(f"❌ Direct MySQL verification failed: {e}")

if __name__ == '__main__':
    verify_mysql_data()
    verify_direct_mysql()
