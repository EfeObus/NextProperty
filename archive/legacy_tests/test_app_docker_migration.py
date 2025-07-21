#!/usr/bin/env python3
"""
Test application startup with Docker database
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def test_app_with_docker_db():
    """Test that the application can start with Docker database."""
    
    print("🔄 Testing application with Docker database...")
    load_dotenv()
    
    # Get the main DATABASE_URL (should now be Docker)
    database_url = os.getenv('DATABASE_URL')
    print(f"📊 Using DATABASE_URL: {database_url}")
    
    try:
        # Test SQLAlchemy connection (same as app would use)
        print("\n1. Testing SQLAlchemy Engine Creation...")
        engine = create_engine(database_url, echo=False)
        print("✅ Engine created successfully")
        
        print("\n2. Testing Database Connection...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE() as current_db"))
            current_db = result.fetchone()
            print(f"✅ Connected to database: {current_db[0]}")
            
            # Test basic table access
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"✅ Found {len(tables)} tables")
            
            # Test a sample query if tables exist
            if tables:
                # Try to access a common table
                try:
                    result = conn.execute(text("SELECT COUNT(*) FROM agents LIMIT 1"))
                    count = result.fetchone()
                    print(f"✅ Sample query successful - agents table has {count[0]} records")
                except Exception as e:
                    print(f"ℹ️  Sample query info: {e}")
        
        print("\n🎉 Application should work fine with Docker database!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("⚠️  Application may have issues with current configuration")
        return False

if __name__ == "__main__":
    success = test_app_with_docker_db()
    sys.exit(0 if success else 1)
