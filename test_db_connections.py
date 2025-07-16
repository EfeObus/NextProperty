#!/usr/bin/env python3
"""
Simple database connection test
"""

import pymysql
import sys

def test_old_database():
    """Test connection to old database."""
    try:
        print("Testing old database connection...")
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Jesutekevwe1@@',
            database='nextproperty_ai',
            charset='utf8mb4',
            connect_timeout=30
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'nextproperty_ai'")
            result = cursor.fetchone()
            print(f"✓ Old database connected successfully. Found {result[0]} tables.")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ Old database connection failed: {e}")
        return False

def test_new_database():
    """Test connection to new database."""
    try:
        print("Testing new database connection...")
        connection = pymysql.connect(
            host='184.107.4.32',
            port=8002,
            user='studentGroup',
            password='juifcdhoifdqw13f',
            database='NextProperty',
            charset='utf8mb4',
            connect_timeout=60
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'NextProperty'")
            result = cursor.fetchone()
            print(f"✓ New database connected successfully. Found {result[0]} tables.")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ New database connection failed: {e}")
        return False

def main():
    print("=" * 50)
    print("Database Connection Test")
    print("=" * 50)
    
    old_ok = test_old_database()
    new_ok = test_new_database()
    
    if old_ok and new_ok:
        print("\n✓ Both database connections successful!")
        return True
    else:
        print("\n✗ One or more database connections failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
