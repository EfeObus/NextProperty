#!/usr/bin/env python3
"""
Test MySQL connection and create database if needed.
"""

import pymysql

def test_mysql_connection():
    """Test MySQL connection and create database."""
    print("Testing MySQL connection...")
    
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='your_password_here',
            charset='utf8mb4'
        )
        
        print("✓ Successfully connected to MySQL server")
        
        with connection.cursor() as cursor:
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS nextproperty_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print("✓ Database 'nextproperty_ai' created/verified")
            
            # Show databases
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print("Available databases:")
            for db in databases:
                print(f"  - {db[0]}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"✗ MySQL connection failed: {e}")
        print("\nPlease ensure:")
        print("1. MySQL server is running")
        print("2. Root password is correct (currently set to 'your_password_here')")
        print("3. MySQL is accessible on localhost:3306")
        return False

if __name__ == '__main__':
    test_mysql_connection()
