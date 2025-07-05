#!/usr/bin/env python3
"""
Migration script to move from SQLite to MySQL and populate with real estate data.
"""

import os
import sys
import pandas as pd
import pymysql
from datetime import datetime, timedelta
import numpy as np
import random

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.property import Property
from app.models.agent import Agent
from sqlalchemy import text

def create_mysql_database():
    """Create the MySQL database if it doesn't exist."""
    print("Creating MySQL database...")
    
    try:
        # Connect to MySQL server (without database)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Jesutekevwe1@@',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS nextproperty_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print("✓ Database 'nextproperty_ai' created successfully")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False

def clean_currency_value(value):
    """Clean currency values and convert to float."""
    if pd.isna(value) or value == '' or value == 'N/A':
        return None
    
    # Convert to string and clean
    value_str = str(value).replace('$', '').replace(',', '').strip()
    
    try:
        return float(value_str)
    except (ValueError, TypeError):
        return None

def clean_numeric_value(value):
    """Clean numeric values and convert to appropriate type."""
    if pd.isna(value) or value == '' or value == 'N/A':
        return None
    
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_int(value):
    """Safely convert value to integer."""
    if pd.isna(value) or value == '' or value == 'N/A':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None

def safe_date(value):
    """Safely convert value to date."""
    if pd.isna(value) or value == '' or value == 'N/A':
        return None
    
    try:
        if isinstance(value, str):
            # Try different date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%m/%d/%Y', '%d/%m/%Y']:
                try:
                    return datetime.strptime(value.split()[0], fmt).date()
                except ValueError:
                    continue
        return None
    except Exception:
        return None

def generate_synthetic_data(row):
    """Generate realistic sold price and date based on listing price."""
    base_price = clean_currency_value(row.get('Price', 0))
    if not base_price:
        base_price = random.randint(200000, 800000)
    
    # Generate sold price (typically 95-105% of listing price)
    price_factor = random.uniform(0.95, 1.05)
    sold_price = base_price * price_factor
    
    # Generate sold date (within last 2 years)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    random_days = random.randint(0, 730)
    sold_date = start_date + timedelta(days=random_days)
    
    # Generate days on market (7-120 days)
    dom = random.randint(7, 120)
    
    return sold_price, sold_date.date(), dom

def map_csv_to_property(row, index):
    """Map CSV row to Property model fields."""
    # Generate synthetic data
    sold_price, sold_date, dom = generate_synthetic_data(row)
    
    # Extract coordinates
    latitude = clean_numeric_value(row.get('Latitude'))
    longitude = clean_numeric_value(row.get('Longitude'))
    
    # Extract address components
    address = f"{row.get('StreetNumber', '')} {row.get('StreetName', '')} {row.get('StreetSuffix', '')}".strip()
    if not address:
        address = row.get('StreetAddress', f'Address {index}')
    
    # Extract property features
    bedrooms = safe_int(row.get('BedroomsTotal', row.get('BedroomsAboveGround')))
    bathrooms = clean_numeric_value(row.get('BathroomTotal'))
    
    # Calculate square footage from size fields
    sqft = None
    size_fields = ['SizeInterior', 'TotalFinishedArea', 'SizeTotal']
    for field in size_fields:
        size_val = clean_numeric_value(row.get(field))
        if size_val and size_val > 0:
            sqft = int(size_val)
            break
    
    # Extract other numeric fields
    lot_size = clean_numeric_value(row.get('Acreage'))
    year_built = safe_int(row.get('ConstructedDate', row.get('Age')))
    if year_built and year_built < 1800:  # If age was provided instead of year
        year_built = datetime.now().year - year_built
    
    property_data = {
        'listing_id': str(row.get('DdfListingID', f'PROP_{index:06d}')),
        'mls': str(row.get('ListingID', '')),
        'property_type': str(row.get('PropertyType', 'Residential')),
        'address': address,
        'city': str(row.get('City', 'Unknown')).title(),
        'province': str(row.get('Province', 'Ontario')),
        'postal_code': str(row.get('PostalCode', '')),
        'latitude': latitude,
        'longitude': longitude,
        'sold_price': sold_price,
        'original_price': clean_currency_value(row.get('Price')),
        'bedrooms': bedrooms,
        'bathrooms': bathrooms,
        'sqft': sqft,
        'lot_size': lot_size,
        'year_built': year_built,
        'sold_date': sold_date,
        'dom': dom,
        'features': str(row.get('Features', '')),
        'community_features': str(row.get('CommunityFeatures', '')),
        'remarks': str(row.get('PublicRemarks', ''))
    }
    
    return property_data

def load_csv_data():
    """Load and process real estate data from CSV files."""
    print("Loading CSV data...")
    
    # Try to load the large dataset first, then fallback to sample
    csv_files = [
        'Dataset/realEstate.csv',
        'Dataset/large_sample_real_estate.csv',
        'Dataset/sample_real_estate.csv'
    ]
    
    df = None
    for csv_file in csv_files:
        file_path = os.path.join(project_root, csv_file)
        if os.path.exists(file_path):
            try:
                print(f"Loading {csv_file}...")
                df = pd.read_csv(file_path)
                print(f"✓ Successfully loaded {len(df)} records from {csv_file}")
                break
            except Exception as e:
                print(f"✗ Error loading {csv_file}: {e}")
                continue
    
    if df is None:
        print("✗ No valid CSV files found!")
        return []
    
    # Process the data
    properties = []
    for index, row in df.iterrows():
        try:
            property_data = map_csv_to_property(row, index)
            properties.append(property_data)
            
            if (index + 1) % 1000 == 0:
                print(f"Processed {index + 1} records...")
                
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            continue
    
    print(f"✓ Successfully processed {len(properties)} properties")
    return properties

def migrate_data():
    """Migrate data to MySQL database."""
    # Set environment variable explicitly
    os.environ['DATABASE_URL'] = 'mysql+pymysql://root:Jesutekevwe1%40%40@localhost:3306/nextproperty_ai'
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("Setting up database tables...")
        
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("✓ Database tables created")
        
        # Load CSV data
        properties_data = load_csv_data()
        
        if not properties_data:
            print("✗ No data to migrate!")
            return False
        
        print(f"Migrating {len(properties_data)} properties to MySQL...")
        
        # Insert properties in batches
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(properties_data), batch_size):
            batch = properties_data[i:i + batch_size]
            
            try:
                for prop_data in batch:
                    # Check if property already exists
                    existing = Property.query.filter_by(listing_id=prop_data['listing_id']).first()
                    if existing:
                        continue
                    
                    property_obj = Property(**prop_data)
                    db.session.add(property_obj)
                
                db.session.commit()
                total_inserted += len(batch)
                print(f"✓ Inserted batch {i//batch_size + 1}: {total_inserted} properties total")
                
            except Exception as e:
                print(f"✗ Error inserting batch {i//batch_size + 1}: {e}")
                db.session.rollback()
                continue
        
        print(f"✓ Migration completed! {total_inserted} properties inserted")
        
        # Verify data
        count = Property.query.count()
        print(f"✓ Verification: {count} properties in database")
        
        return True

def main():
    """Main migration function."""
    print("🏠 NextProperty AI - SQLite to MySQL Migration")
    print("=" * 50)
    
    # Step 1: Create MySQL database
    if not create_mysql_database():
        print("Failed to create database. Please check your MySQL connection.")
        return
    
    # Step 2: Migrate data
    try:
        success = migrate_data()
        if success:
            print("\n🎉 Migration completed successfully!")
            print("Your application is now using MySQL database with real estate data.")
        else:
            print("\n❌ Migration failed!")
    except Exception as e:
        print(f"\n❌ Migration error: {e}")

if __name__ == '__main__':
    main()
