#!/usr/bin/env python3
"""
Secret Key Generator Script
Automatically generates a new SECRET_KEY with 30-day expiry and updates the .env file.
"""

import os
import secrets
import re
from datetime import datetime, timedelta
from pathlib import Path

def generate_secret_key(length=64):
    """Generate a cryptographically secure random secret key."""
    return secrets.token_hex(length)

def get_expiry_date(days=30):
    """Calculate expiry date (30 days from now)."""
    expiry = datetime.now() + timedelta(days=days)
    return expiry.strftime("%Y-%m-%d")

def update_env_file(env_path, new_secret_key, new_expiry_date):
    """Update the .env file with new SECRET_KEY and EXPIRY_DATE."""
    try:
        # Read the current .env file
        with open(env_path, 'r') as file:
            content = file.read()
        
        # Update SECRET_KEY
        secret_key_pattern = r'^SECRET_KEY=.*$'
        new_secret_line = f'SECRET_KEY={new_secret_key}'
        content = re.sub(secret_key_pattern, new_secret_line, content, flags=re.MULTILINE)
        
        # Update EXPIRY_DATE
        expiry_pattern = r'^EXPIRY_DATE=.*$'
        new_expiry_line = f'EXPIRY_DATE={new_expiry_date}'
        content = re.sub(expiry_pattern, new_expiry_line, content, flags=re.MULTILINE)
        
        # Write the updated content back to .env file
        with open(env_path, 'w') as file:
            file.write(content)
        
        return True
    except Exception as e:
        print(f"Error updating .env file: {e}")
        return False

def check_key_expiry(env_path):
    """Check if the current secret key has expired."""
    try:
        with open(env_path, 'r') as file:
            content = file.read()
        
        # Extract EXPIRY_DATE
        expiry_match = re.search(r'^EXPIRY_DATE=(.+)$', content, re.MULTILINE)
        if not expiry_match:
            print("No EXPIRY_DATE found in .env file")
            return True  # Assume expired if no date found
        
        expiry_date_str = expiry_match.group(1).strip()
        
        # Handle shell command format
        if expiry_date_str.startswith('$(date'):
            print("EXPIRY_DATE is in shell command format, treating as expired")
            return True
        
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
            current_date = datetime.now()
            
            if current_date >= expiry_date:
                print(f"Secret key expired on {expiry_date_str}")
                return True
            else:
                print(f"Secret key is valid until {expiry_date_str}")
                return False
        except ValueError:
            print(f"Invalid date format in EXPIRY_DATE: {expiry_date_str}")
            return True
    
    except Exception as e:
        print(f"Error checking key expiry: {e}")
        return True

def main():
    """Main function to generate and update secret key."""
    # Get the project root directory (parent of scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_path = project_root / '.env'
    
    print("=== NextProperty AI Secret Key Generator ===")
    print(f"Environment file: {env_path}")
    
    # Check if .env file exists
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return False
    
    # Check if current key has expired
    is_expired = check_key_expiry(env_path)
    
    if not is_expired:
        print("Current secret key is still valid.")
        response = input("Do you want to generate a new key anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Keeping current secret key.")
            return True
    
    # Generate new secret key and expiry date
    print("Generating new secret key...")
    new_secret_key = generate_secret_key()
    new_expiry_date = get_expiry_date()
    
    print(f"New secret key generated (64 characters)")
    print(f"Expiry date: {new_expiry_date}")
    
    # Update .env file
    print("Updating .env file...")
    success = update_env_file(env_path, new_secret_key, new_expiry_date)
    
    if success:
        print("✅ Secret key updated successfully!")
        print("⚠️  Important: Restart your application for changes to take effect.")
        return True
    else:
        print("❌ Failed to update secret key.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
