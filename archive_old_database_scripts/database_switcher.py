#!/usr/bin/env python3
"""
Database Configuration Switcher
Easily switch between local and Docker databases
"""

import os
import shutil
from datetime import datetime

def backup_current_env():
    """Backup current .env file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f".env.backup.{timestamp}"
    shutil.copy('.env', backup_name)
    print(f"✓ Current .env backed up as {backup_name}")

def switch_to_local():
    """Switch to local database."""
    env_content = '''# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=902972f616fc0fd866bb5d5e4fd0eac84b739cc1a6d6db642a8655ec5164deddec77575f9528e5de2393b6869199144ce178ef9b87b7e856d11f90cb2a4bd541
EXPIRY_DATE=2025-08-04

# Database Configuration - LOCAL DATABASE
DATABASE_URL=mysql+pymysql://root:Jesutekevwe1%40%40@localhost:3306/nextproperty_ai

# Current Database Details
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Jesutekevwe1@@
DB_NAME=nextproperty_ai

# Alternative: Docker Database (when accessible)
DATABASE_URL_DOCKER=mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty

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
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✓ Switched to LOCAL database configuration")

def switch_to_docker():
    """Switch to Docker database."""
    env_content = '''# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=902972f616fc0fd866bb5d5e4fd0eac84b739cc1a6d6db642a8655ec5164deddec77575f9528e5de2393b6869199144ce178ef9b87b7e856d11f90cb2a4bd541
EXPIRY_DATE=2025-08-04

# Database Configuration - DOCKER DATABASE
DATABASE_URL=mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty

# Current Database Details
DB_HOST=184.107.4.32
DB_PORT=8002
DB_USER=studentGroup
DB_PASSWORD=juifcdhoifdqw13f
DB_NAME=NextProperty

# Alternative: Local Database
DATABASE_URL_LOCAL=mysql+pymysql://root:Jesutekevwe1%40%40@localhost:3306/nextproperty_ai

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
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✓ Switched to DOCKER database configuration")

def show_current_config():
    """Show current database configuration."""
    try:
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'localhost:3306' in content and 'nextproperty_ai' in content:
            if content.find('DATABASE_URL=mysql+pymysql://root:') != -1:
                print("📍 Current configuration: LOCAL DATABASE")
                print("   Database: nextproperty_ai on localhost:3306")
            else:
                print("📍 Current configuration: MIXED")
        elif '184.107.4.32:8002' in content and 'NextProperty' in content:
            if content.find('DATABASE_URL=mysql+pymysql://studentGroup:') != -1:
                print("📍 Current configuration: DOCKER DATABASE")
                print("   Database: NextProperty on 184.107.4.32:8002")
            else:
                print("📍 Current configuration: MIXED")
        else:
            print("📍 Current configuration: UNKNOWN")
            
    except FileNotFoundError:
        print("❌ .env file not found")

def main():
    print("=" * 50)
    print("NextProperty Database Configuration Switcher")
    print("=" * 50)
    
    show_current_config()
    
    print("\nOptions:")
    print("1. Switch to LOCAL database (recommended)")
    print("2. Switch to DOCKER database (if accessible)")
    print("3. Show current configuration")
    print("4. Backup current .env file")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        backup_current_env()
        switch_to_local()
        print("\n✅ Switched to local database!")
        print("   Restart your application to apply changes.")
        
    elif choice == '2':
        backup_current_env()
        switch_to_docker()
        print("\n⚠️  Switched to Docker database!")
        print("   Note: External access may not work.")
        print("   Restart your application to apply changes.")
        
    elif choice == '3':
        show_current_config()
        
    elif choice == '4':
        backup_current_env()
        
    elif choice == '5':
        print("Goodbye!")
        
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
