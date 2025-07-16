#!/usr/bin/env python3
"""
Fix URL encoding issues and test connections
"""

import os
import urllib.parse
from dotenv import load_dotenv

def test_url_encoding():
    """Test different URL encoding approaches."""
    
    print("Testing URL encoding approaches...")
    
    # Method 1: URL encode the password
    password = "Jesutekevwe1@@"
    encoded_password = urllib.parse.quote(password, safe='')
    print(f"Original password: {password}")
    print(f"URL encoded password: {encoded_password}")
    
    # Create properly encoded URLs
    local_url = f"mysql+pymysql://root:{encoded_password}@localhost:3306/nextproperty_ai"
    docker_url = "mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty"
    
    print(f"Local URL: {local_url}")
    print(f"Docker URL: {docker_url}")
    
    return local_url, docker_url

def test_connection_with_fixed_url():
    """Test connection with properly encoded URL."""
    local_url, docker_url = test_url_encoding()
    
    print("\nTesting local database with fixed URL...")
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(local_url, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM properties"))
            count = result.fetchone()[0]
            print(f"✓ Local database connection successful! Found {count} properties.")
            return True
            
    except Exception as e:
        print(f"✗ Local database connection failed: {e}")
        return False

def create_fixed_env_file():
    """Create a fixed .env file with proper URL encoding."""
    
    password = "Jesutekevwe1@@"
    encoded_password = urllib.parse.quote(password, safe='')
    
    env_content = f'''# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=902972f616fc0fd866bb5d5e4fd0eac84b739cc1a6d6db642a8655ec5164deddec77575f9528e5de2393b6869199144ce178ef9b87b7e856d11f90cb2a4bd541
EXPIRY_DATE=2025-08-04

# Database Configuration - Docker MySQL (Primary)
DATABASE_URL=mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty

#MySQL Configuration - Docker
DB_HOST=184.107.4.32
DB_PORT=8002
DB_USER=studentGroup
DB_PASSWORD=juifcdhoifdqw13f
DB_NAME=NextProperty

# Local Database Configuration (Fallback)
DATABASE_URL_LOCAL=mysql+pymysql://root:{encoded_password}@localhost:3306/nextproperty_ai
OLD_DB_HOST=localhost
OLD_DB_PORT=3306
OLD_DB_USER=root
OLD_DB_PASSWORD=Jesutekevwe1@@
OLD_DB_NAME=nextproperty_ai

# Cache Configuration
CACHE_TYPE=simple

# API Keys (optional for development)
BOC_API_KEY=your-boc-api-key
STATCAN_API_KEY=your-statcan-api-key

# Email Configuration (optional for development)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
'''
    
    # Write the fixed .env file
    with open('.env.fixed', 'w') as f:
        f.write(env_content)
    
    print("✓ Created .env.fixed with proper URL encoding")
    return env_content

def main():
    print("=" * 60)
    print("URL Encoding Fix and Database Test")
    print("=" * 60)
    
    # Test URL encoding
    test_url_encoding()
    
    # Test connection with fixed URL
    local_works = test_connection_with_fixed_url()
    
    # Create fixed .env file
    create_fixed_env_file()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    if local_works:
        print("✓ Local database connection works with fixed URL encoding")
        print("\nNext steps:")
        print("1. Replace your .env file with .env.fixed")
        print("2. The Docker database import was successful")
        print("3. Connection to Docker database is blocked (likely network/firewall)")
        print("4. Use local database for development until Docker network is configured")
    else:
        print("✗ Still having connection issues")
        print("Check if MySQL server is running locally")

if __name__ == "__main__":
    main()
