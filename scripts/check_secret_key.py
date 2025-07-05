#!/usr/bin/env python3
"""
Secret Key Status Checker
Check the current SECRET_KEY expiry status without generating a new key.
"""

import os
import re
from datetime import datetime
from pathlib import Path

def check_secret_key_status(env_path):
    """Check and display the current secret key status."""
    try:
        with open(env_path, 'r') as file:
            content = file.read()
        
        # Extract SECRET_KEY
        secret_match = re.search(r'^SECRET_KEY=(.+)$', content, re.MULTILINE)
        if not secret_match:
            print("❌ No SECRET_KEY found in .env file")
            return False
        
        secret_key = secret_match.group(1).strip()
        print(f"Secret Key Length: {len(secret_key)} characters")
        print(f"Secret Key (first 16 chars): {secret_key[:16]}...")
        
        # Extract EXPIRY_DATE
        expiry_match = re.search(r'^EXPIRY_DATE=(.+)$', content, re.MULTILINE)
        if not expiry_match:
            print("❌ No EXPIRY_DATE found in .env file")
            return False
        
        expiry_date_str = expiry_match.group(1).strip()
        
        # Handle shell command format
        if expiry_date_str.startswith('$(date'):
            print("⚠️  EXPIRY_DATE is in shell command format")
            print("   Run the generator script to set a proper date")
            return False
        
        try:
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
            current_date = datetime.now()
            
            days_until_expiry = (expiry_date - current_date).days
            
            print(f"Expiry Date: {expiry_date_str}")
            print(f"Current Date: {current_date.strftime('%Y-%m-%d')}")
            
            if days_until_expiry < 0:
                print(f"🔴 SECRET_KEY EXPIRED {abs(days_until_expiry)} days ago!")
                print("   Run the generator script immediately")
                return False
            elif days_until_expiry == 0:
                print("🟡 SECRET_KEY expires TODAY!")
                print("   Consider running the generator script")
                return True
            elif days_until_expiry <= 7:
                print(f"🟡 SECRET_KEY expires in {days_until_expiry} days")
                print("   Consider running the generator script soon")
                return True
            else:
                print(f"🟢 SECRET_KEY is valid for {days_until_expiry} more days")
                return True
                
        except ValueError:
            print(f"❌ Invalid date format in EXPIRY_DATE: {expiry_date_str}")
            return False
    
    except Exception as e:
        print(f"❌ Error checking secret key status: {e}")
        return False

def main():
    """Main function to check secret key status."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    env_path = project_root / '.env'
    
    print("=== NextProperty AI Secret Key Status ===")
    print(f"Environment file: {env_path}")
    print()
    
    # Check if .env file exists
    if not env_path.exists():
        print(f"❌ .env file not found at {env_path}")
        return False
    
    # Check secret key status
    is_valid = check_secret_key_status(env_path)
    
    print()
    if not is_valid:
        print("🔧 To generate a new secret key, run:")
        print("   python3 scripts/generate_secret_key.py")
        print("   or")
        print("   ./scripts/generate_secret_key.sh")
    
    return is_valid

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
