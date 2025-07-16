#!/usr/bin/env python3
"""
Simple test to force local database connection
"""

import os
import sys

# Force local database URL
os.environ['DATABASE_URL'] = 'mysql+pymysql://root:Jesutekevwe1%40%40@localhost:3306/nextproperty_ai'

# Add project root to path
sys.path.insert(0, '/Users/efeobukohwo/Desktop/Nextproperty Real Estate')

try:
    from sqlalchemy import create_engine, text
    
    # Test direct connection with forced URL
    engine = create_engine(os.environ['DATABASE_URL'], echo=False)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM properties"))
        count = result.fetchone()[0]
        print(f"✓ Direct connection successful! Found {count} properties.")
    
    # Test with Flask app
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        from app.extensions import db
        
        # Check what URL the app is actually using
        print(f"App database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        result = db.session.execute(text("SELECT COUNT(*) FROM properties"))
        count = result.fetchone()[0]
        print(f"✓ Flask app connection successful! Found {count} properties.")
        
except Exception as e:
    print(f"✗ Error: {e}")
    
    # Let's check what the app config actually contains
    try:
        from app import create_app
        app = create_app('development')
        print(f"App is trying to use: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
    except Exception as config_error:
        print(f"Config error: {config_error}")
