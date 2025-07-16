#!/usr/bin/env python3
"""
Test Docker MySQL connection with various settings
"""

import pymysql
import time
from sqlalchemy import create_engine, text
import sys

def test_pymysql_direct():
    """Test direct PyMySQL connection with minimal settings."""
    print("Testing direct PyMySQL connection...")
    try:
        connection = pymysql.connect(
            host='184.107.4.32',
            port=8002,
            user='studentGroup',
            password='juifcdhoifdqw13f',
            database='NextProperty',
            charset='utf8mb4',
            connect_timeout=10,
            autocommit=True
        )
        
        print("✓ Connected with PyMySQL")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"✓ Basic query successful: {result}")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ PyMySQL connection failed: {e}")
        return False

def test_sqlalchemy_minimal():
    """Test SQLAlchemy with minimal settings."""
    print("\nTesting SQLAlchemy with minimal settings...")
    try:
        db_url = "mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty"
        
        engine = create_engine(
            db_url, 
            echo=False,
            pool_pre_ping=False,
            connect_args={
                'connect_timeout': 10,
                'charset': 'utf8mb4',
                'autocommit': True
            }
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✓ SQLAlchemy minimal connection successful: {row}")
            
        return True
        
    except Exception as e:
        print(f"✗ SQLAlchemy minimal connection failed: {e}")
        return False

def test_with_app_config():
    """Test with your app's configuration."""
    print("\nTesting with app configuration...")
    try:
        db_url = "mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty"
        
        engine_options = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'pool_timeout': 60,
            'echo': False,
            'connect_args': {
                'charset': 'utf8mb4',
                'connect_timeout': 60,
                'read_timeout': 60,
                'write_timeout': 60,
                'autocommit': False
            }
        }
        
        engine = create_engine(db_url, **engine_options)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'NextProperty'"))
            count = result.fetchone()[0]
            print(f"✓ App config connection successful. Found {count} tables.")
            
        return True
        
    except Exception as e:
        print(f"✗ App config connection failed: {e}")
        return False

def test_flask_app_connection():
    """Test using actual Flask app configuration."""
    print("\nTesting Flask app connection...")
    try:
        # Add project root to path
        sys.path.insert(0, '/Users/efeobukohwo/Desktop/Nextproperty Real Estate')
        
        from dotenv import load_dotenv
        load_dotenv()
        
        from app import create_app
        
        app = create_app('development')
        
        with app.app_context():
            from app.extensions import db
            
            # Test database connection
            result = db.session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✓ Flask app connection successful: {row}")
            
            # Test table count
            result = db.session.execute(text("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'NextProperty'"))
            count = result.fetchone()[0]
            print(f"✓ Found {count} tables in NextProperty database")
            
        return True
        
    except Exception as e:
        print(f"✗ Flask app connection failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Docker MySQL Connection Testing")
    print("=" * 60)
    
    tests = [
        test_pymysql_direct,
        test_sqlalchemy_minimal,
        test_with_app_config,
        test_flask_app_connection
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print("-" * 40)
    
    print(f"\nResults: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ All tests passed! Your app should work with the Docker database.")
    elif passed > 0:
        print("⚠️  Some tests passed. There may be configuration issues to resolve.")
    else:
        print("❌ All tests failed. The Docker database may not be accessible.")

if __name__ == "__main__":
    main()
