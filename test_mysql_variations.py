#!/usr/bin/env python3
"""
Test MySQL connection with different password scenarios.
"""

import pymysql

def test_mysql_variations():
    """Test MySQL connection with different password scenarios."""
    print("Testing MySQL connection variations...")
    
    # Test scenarios
    scenarios = [
        ("no password", "", ""),
        ("empty password", "root", ""),
        ("default password", "root", "your_password_here"),
        ("common password", "root", "root"),
        ("mysql password", "root", "mysql")
    ]
    
    for name, user, password in scenarios:
        try:
            print(f"\nTrying {name}...")
            connection = pymysql.connect(
                host='localhost',
                user=user,
                password=password,
                charset='utf8mb4'
            )
            
            print(f"✓ Successfully connected with {name}")
            
            with connection.cursor() as cursor:
                # Create database
                cursor.execute("CREATE DATABASE IF NOT EXISTS nextproperty_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                print("✓ Database 'nextproperty_ai' created/verified")
                
                # Test connection to the database
                cursor.execute("USE nextproperty_ai;")
                print("✓ Successfully connected to nextproperty_ai database")
            
            connection.close()
            print(f"\n🎉 SUCCESS: Use user='{user}' password='{password}'")
            return user, password
            
        except Exception as e:
            print(f"✗ Failed with {name}: {e}")
            continue
    
    print("\n❌ Could not connect with any scenario")
    return None, None

if __name__ == '__main__':
    user, password = test_mysql_variations()
