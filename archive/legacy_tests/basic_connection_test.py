#!/usr/bin/env python3
"""
Basic database connection test without schema queries
"""

import pymysql
import time

def test_basic_connection():
    """Test basic connection to new database."""
    try:
        print("Attempting basic connection to remote database...")
        connection = pymysql.connect(
            host='184.107.4.32',
            port=8001,
            user='studentGroup',
            password='juifcdhoifdqw13f',
            database='NextProperty',
            charset='utf8mb4',
            connect_timeout=30,
            read_timeout=30,
            write_timeout=30
        )
        
        print("✓ Connected successfully!")
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✓ Basic query successful: {result}")
            
            cursor.execute("SELECT DATABASE()")
            result = cursor.fetchone()
            print(f"✓ Connected to database: {result[0]}")
            
        connection.close()
        print("✓ Connection closed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_connection()
