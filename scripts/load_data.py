#!/usr/bin/env python3
"""
Data loading script to populate the database with real estate data from CSV files.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.property import Property
from app.models.agent import Agent


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


def generate_synthetic_sold_data(row):
    """Generate realistic sold price and date based on listing price."""
    base_price = clean_currency_value(row.get('Price', 0))
    
    if not base_price or base_price <= 0:
        # Generate realistic price based on property type and location
        if 'Condo' in str(row.get('PropertyType', '')):
            base_price = random.uniform(300000, 800000)
        elif 'Detached' in str(row.get('PropertyType', '')):
            base_price = random.uniform(500000, 1500000)
        else:
            base_price = random.uniform(400000, 1000000)
    
    # Generate sold price (typically 95-105% of listing price)
    price_variation = random.uniform(0.95, 1.05)
    sold_price = base_price * price_variation
    
    # Generate sold date (within last 2 years)
    days_ago = random.randint(30, 730)
    sold_date = datetime.now() - timedelta(days=days_ago)
    
    # Generate days on market (typically 15-90 days)
    dom = random.randint(15, 90)
    
    return sold_price, sold_date.date(), dom


def create_default_agent():
    """Create a default agent for properties without agent info."""
    agent = Agent(
        agent_id='AGT001',
        name='Default Agent',
        email='default@nextproperty.ai',
        phone='(555) 123-4567',
        brokerage='NextProperty Real Estate',
        license_number='LIC001',
        bio='Default agent for imported properties',
        specialties='Residential, Commercial',
        years_experience=5,
        languages='English',
        service_areas='GTA'
    )
    return agent


def load_property_data(csv_file_path):
    """Load property data from CSV file into the database."""
    print(f"Loading property data from {csv_file_path}...")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Found {len(df)} properties in CSV file")
        
        # Create default agent if not exists
        default_agent = Agent.query.filter_by(agent_id='AGT001').first()
        if not default_agent:
            default_agent = create_default_agent()
            db.session.add(default_agent)
            db.session.commit()
            print("Created default agent")
        
        # Process each property
        properties_added = 0
        
        for index, row in df.iterrows():
            try:
                # Generate unique listing ID
                listing_id = f"NP{str(uuid.uuid4()).replace('-', '')[:8].upper()}"
                
                # Check if property already exists
                if Property.query.filter_by(listing_id=listing_id).first():
                    continue
                
                # Extract basic property information
                address = str(row.get('StreetAddress', '')).strip() if pd.notna(row.get('StreetAddress')) else f"{index + 1} Sample Street"
                city = str(row.get('City', 'Unknown')).strip().title()
                province = str(row.get('Province', 'ON')).strip().upper()
                postal_code = str(row.get('PostalCode', 'M1M1M1')).strip().upper()
                
                # Clean coordinates
                latitude = clean_numeric_value(row.get('Latitude'))
                longitude = clean_numeric_value(row.get('Longitude'))
                
                # If no coordinates, generate some for GTA area
                if not latitude or not longitude:
                    latitude = round(random.uniform(43.6, 43.8), 6)
                    longitude = round(random.uniform(-79.5, -79.2), 6)
                
                # Extract property features
                bedrooms = clean_numeric_value(row.get('BedroomsTotal', 0))
                if not bedrooms:
                    bedrooms = random.randint(2, 5)
                
                bathrooms = clean_numeric_value(row.get('BathroomTotal', 0))
                if not bathrooms:
                    bathrooms = random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4])
                
                # Generate square footage if not available
                sqft = clean_numeric_value(row.get('SizeInterior'))
                if not sqft:
                    # Estimate based on bedrooms
                    sqft = int(bedrooms * random.uniform(300, 400) + random.uniform(200, 500))
                
                # Property type
                property_type = str(row.get('PropertyType', 'Detached')).strip()
                if not property_type or property_type == 'nan':
                    property_type = random.choice(['Detached', 'Semi-Detached', 'Townhouse', 'Condo', 'Apartment'])
                
                # Generate sold data
                sold_price, sold_date, dom = generate_synthetic_sold_data(row)
                
                # Extract additional features
                lot_size = clean_numeric_value(row.get('SizeTotal'))
                if not lot_size and property_type in ['Detached', 'Semi-Detached']:
                    lot_size = random.uniform(3000, 8000)
                
                # Get features and remarks
                features = str(row.get('Features', '')).strip() if pd.notna(row.get('Features')) else None
                community_features = str(row.get('CommunityFeatures', '')).strip() if pd.notna(row.get('CommunityFeatures')) else None
                remarks = str(row.get('PublicRemarks', '')).strip() if pd.notna(row.get('PublicRemarks')) else None
                
                # Generate property taxes
                taxes = random.uniform(3000, 8000)
                
                # Generate year_built if not available
                year_built = None
                if pd.notna(row.get('YearBuilt')):
                    year_built = int(row.get('YearBuilt'))
                else:
                    # Generate realistic year_built based on property type and price
                    current_year = 2024
                    if property_type in ['Condo', 'Apartment']:
                        # Condos tend to be newer
                        year_built = random.randint(1980, current_year)
                    elif sold_price > 800000:
                        # Higher priced properties might be newer or well-maintained older homes
                        year_built = random.randint(1950, current_year)
                    else:
                        # General range for residential properties
                        year_built = random.randint(1940, current_year)
                
                # Create property object
                property_obj = Property(
                    listing_id=listing_id,
                    mls=f"MLS{random.randint(100000, 999999)}",
                    property_type=property_type,
                    address=address,
                    city=city,
                    province=province,
                    postal_code=postal_code,
                    latitude=latitude,
                    longitude=longitude,
                    sold_price=sold_price,
                    original_price=sold_price * random.uniform(0.95, 1.05),  # Generate original price
                    bedrooms=int(bedrooms),
                    bathrooms=bathrooms,
                    sqft=int(sqft),
                    lot_size=lot_size,
                    year_built=year_built,
                    sold_date=sold_date,
                    dom=dom,
                    taxes=taxes,
                    features=features,
                    community_features=community_features,
                    remarks=remarks,
                    agent_id=default_agent.agent_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(property_obj)
                properties_added += 1
                
                # Commit in batches
                if properties_added % 50 == 0:
                    db.session.commit()
                    print(f"Added {properties_added} properties...")
                    
            except Exception as e:
                print(f"Error processing row {index}: {str(e)}")
                continue
        
        # Final commit
        db.session.commit()
        print(f"Successfully loaded {properties_added} properties into the database")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error loading data: {str(e)}")
        raise


def main():
    """Main function to load all data."""
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Load sample data
        csv_file = os.path.join(project_root, 'Dataset', 'sample_real_estate.csv')
        
        if os.path.exists(csv_file):
            load_property_data(csv_file)
        else:
            print(f"CSV file not found: {csv_file}")
            
        # Try loading large sample if available
        large_csv_file = os.path.join(project_root, 'Dataset', 'large_sample_real_estate.csv')
        if os.path.exists(large_csv_file):
            print("\nLoading large dataset...")
            load_property_data(large_csv_file)
        
        print("\nData loading completed!")


if __name__ == '__main__':
    main()
