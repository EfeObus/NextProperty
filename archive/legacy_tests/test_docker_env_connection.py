#!/usr/bin/env python3
"""
Test Docker MySQL connection using .env configuration
"""

import os
from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine, text

def test_docker_connection_with_env():
    """Test Docker database connection using environment variables."""
    
    # Load environment variables
    load_dotenv()
    
    # Get Docker database configuration
    host = os.getenv('DB_HOST_DOCKER')
    port = int(os.getenv('DB_PORT_DOCKER'))
    user = os.getenv('DB_USER_DOCKER')
    password = os.getenv('DB_PASSWORD_DOCKER')
    database = os.getenv('DB_NAME_DOCKER')
    database_url = os.getenv('DATABASE_URL_DOCKER')
    
    print("=== Testing Docker Database Connection ===")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {database}")
    print(f"Database URL: {database_url}")
    print()
    
    # Test 1: Direct PyMySQL connection
    try:
        print("Test 1: Direct PyMySQL connection...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=30
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✓ MySQL Version: {version[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s", (database,))
            table_count = cursor.fetchone()
            print(f"✓ Tables in database: {table_count[0]}")
            
        connection.close()
        print("✓ Direct PyMySQL connection successful!")
        
    except Exception as e:
        print(f"✗ Direct PyMySQL connection failed: {e}")
        return False
    
    # Test 2: SQLAlchemy connection
    try:
        print("\nTest 2: SQLAlchemy connection...")
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"✓ SQLAlchemy query successful: {result.fetchone()}")
            
            result = conn.execute(text("SELECT DATABASE()"))
            current_db = result.fetchone()
            print(f"✓ Current database: {current_db[0]}")
            
        print("✓ SQLAlchemy connection successful!")
        
    except Exception as e:
        print(f"✗ SQLAlchemy connection failed: {e}")
        return False
    
    print("\n🎉 All Docker database connection tests passed!")
    return True

if __name__ == "__main__":
    test_docker_connection_with_env()
