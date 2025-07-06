#!/usr/bin/env python3
"""
Test MySQL connection with provided credentials.
"""

import pymysql

def test_mysql_connection():
    """Test MySQL connection with the provided credentials."""
    print("Testing MySQL connection...")
    
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Jesutekevwe1@@',
            charset='utf8mb4'
        )
        
        print("✓ Successfully connected to MySQL server")
        
        with connection.cursor() as cursor:
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS nextproperty_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print("✓ Database 'nextproperty_ai' created/verified")
            
            # Test connection to the database
            cursor.execute("USE nextproperty_ai;")
            cursor.execute("SELECT DATABASE();")
            current_db = cursor.fetchone()
            print(f"✓ Connected to database: {current_db[0]}")
            
            # Show current tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"Current tables in database: {len(tables)}")
            for table in tables:
                print(f"  - {table[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        return False

if __name__ == '__main__':
    test_mysql_connection()
