#!/usr/bin/env python3
"""
Database fallback configuration test
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_app_with_local_db():
    """Test app with local database to ensure it still works."""
    print("Testing app with local database...")
    
    # Temporarily override database URL
    os.environ['DATABASE_URL'] = 'mysql+pymysql://root:Jesutekevwe1@@localhost:3306/nextproperty_ai'
    
    try:
        from app import create_app
        from app.extensions import db
        from sqlalchemy import text
        
        app = create_app('development')
        
        with app.app_context():
            # Test connection
            result = db.session.execute(text("SELECT COUNT(*) FROM properties"))
            count = result.fetchone()[0]
            print(f"✓ Local database connection successful. Found {count} properties.")
            
            return True
            
    except Exception as e:
        print(f"✗ Local database test failed: {e}")
        return False

def create_hybrid_config():
    """Create a configuration that can switch between databases."""
    config_content = '''# Hybrid Database Configuration
# This allows switching between local and Docker databases

# Primary database (Docker) - use when available
DATABASE_URL_DOCKER=mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty

# Fallback database (Local) - use when Docker is unavailable  
DATABASE_URL_LOCAL=mysql+pymysql://root:Jesutekevwe1@@localhost:3306/nextproperty_ai

# Current active database (change this to switch)
DATABASE_URL=mysql+pymysql://root:Jesutekevwe1@@localhost:3306/nextproperty_ai

# Instructions:
# To use Docker database: Set DATABASE_URL to DATABASE_URL_DOCKER
# To use Local database:  Set DATABASE_URL to DATABASE_URL_LOCAL
'''
    
    with open('.env.hybrid', 'w') as f:
        f.write(config_content)
    
    print("✓ Created .env.hybrid configuration file")

def main():
    print("=" * 60)
    print("Database Configuration Testing")
    print("=" * 60)
    
    # Test with local database
    local_works = test_app_with_local_db()
    
    # Create hybrid configuration
    create_hybrid_config()
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    
    if local_works:
        print("✓ Your app works with the local database")
        print("\nSince the Docker database is not accessible from your machine:")
        print("1. The data was successfully imported via phpMyAdmin")
        print("2. The Docker database is working (phpMyAdmin can access it)")
        print("3. The issue is network connectivity from your machine to Docker")
        print("\nOptions:")
        print("A. Deploy your app to the same network as the Docker container")
        print("B. Configure Docker to allow external connections")
        print("C. Use local database for development, Docker for production")
        print("D. Set up port forwarding or network bridge")
    else:
        print("✗ Local database connection also failed")
        print("This suggests a broader configuration issue")

if __name__ == "__main__":
    main()
