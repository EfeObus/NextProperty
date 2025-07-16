#!/usr/bin/env python3
"""
Final validation of Docker MySQL connection with updated port
"""

import os
import sys
from dotenv import load_dotenv
import pymysql
from sqlalchemy import create_engine, text

def test_comprehensive_docker_connection():
    """Comprehensive test of Docker database connection."""
    
    print("🔄 Loading environment variables...")
    load_dotenv()
    
    # Get configuration
    host = os.getenv('DB_HOST_DOCKER')
    port = int(os.getenv('DB_PORT_DOCKER'))
    user = os.getenv('DB_USER_DOCKER')
    password = os.getenv('DB_PASSWORD_DOCKER')
    database = os.getenv('DB_NAME_DOCKER')
    database_url = os.getenv('DATABASE_URL_DOCKER')
    
    print("=== Docker MySQL Connection Test ===")
    print(f"🏠 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"👤 User: {user}")
    print(f"📁 Database: {database}")
    print(f"🔗 Full URL: {database_url}")
    print()
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Basic Connection
    try:
        print("Test 1: Basic PyMySQL Connection")
        print("  Connecting...")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=30
        )
        
        print("  ✅ Connection established")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"  ✅ Test query result: {result}")
            
        connection.close()
        print("  ✅ Connection closed cleanly")
        success_count += 1
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    print()
    
    # Test 2: Database Information
    try:
        print("Test 2: Database Information")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"  ✅ MySQL Version: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()
            print(f"  ✅ Current Database: {current_db[0]}")
            
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = %s", (database,))
            table_count = cursor.fetchone()
            print(f"  ✅ Number of tables: {table_count[0]}")
            
        connection.close()
        success_count += 1
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    print()
    
    # Test 3: SQLAlchemy Connection
    try:
        print("Test 3: SQLAlchemy Connection")
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'SQLAlchemy Works!' as message"))
            message = result.fetchone()
            print(f"  ✅ {message[0]}")
            
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"  ✅ Found {len(tables)} tables via SQLAlchemy")
            
        success_count += 1
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    print()
    
    # Test 4: Table Access
    try:
        print("Test 4: Table Access Test")
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"  ✅ Can access tables: {len(tables)} tables found")
                for table in tables[:5]:  # Show first 5 tables
                    print(f"    - {table[0]}")
                if len(tables) > 5:
                    print(f"    ... and {len(tables) - 5} more")
            else:
                print("  ⚠️  No tables found in database")
            
        connection.close()
        success_count += 1
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
    
    print()
    print("=== Summary ===")
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Docker MySQL connection is fully functional.")
        return True
    else:
        print(f"⚠️  {total_tests - success_count} test(s) failed.")
        return False

if __name__ == "__main__":
    success = test_comprehensive_docker_connection()
    sys.exit(0 if success else 1)
