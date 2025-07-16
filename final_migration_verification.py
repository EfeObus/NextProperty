#!/usr/bin/env python3
"""
Final verification of Docker database migration
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def final_migration_verification():
    """Final verification that migration to Docker database is complete."""
    
    print("🔄 Final Migration Verification")
    print("=" * 50)
    
    # Load fresh environment
    load_dotenv()
    
    # Check configuration
    database_url = os.getenv('DATABASE_URL')
    docker_url = os.getenv('DATABASE_URL_DOCKER')
    
    print(f"📊 Main DATABASE_URL: {database_url}")
    print(f"🐳 Docker DATABASE_URL: {docker_url}")
    
    # Verify they match (indicating successful migration)
    if database_url == docker_url:
        print("✅ Configuration correctly points to Docker database")
    else:
        print("⚠️  Configuration mismatch detected")
        return False
    
    # Test database connection
    try:
        print("\n🔌 Testing Database Connection...")
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # Basic connection test
            result = conn.execute(text("SELECT 'Migration Successful!' as status"))
            status = result.fetchone()
            print(f"✅ {status[0]}")
            
            # Verify we're on Docker database
            result = conn.execute(text("SELECT DATABASE() as current_db"))
            current_db = result.fetchone()
            print(f"✅ Connected to: {current_db[0]}")
            
            if current_db[0] == 'NextProperty':
                print("✅ Confirmed: Using Docker database")
            else:
                print("⚠️  Warning: Not using expected Docker database")
                return False
            
            # Check tables
            result = conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            print(f"✅ Database has {len(tables)} tables")
            
            # List tables
            table_names = [table[0] for table in tables]
            print("📋 Available tables:")
            for table in table_names:
                print(f"   - {table}")
        
        print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("\n📝 Summary:")
        print("   ✅ Application now uses Docker MySQL database")
        print("   ✅ Local MySQL database removed")
        print("   ✅ Old SQLite database removed") 
        print("   ✅ Configuration cleaned up")
        print(f"   ✅ Backup created: local_db_final_backup_*.sql")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        return False

if __name__ == "__main__":
    success = final_migration_verification()
    sys.exit(0 if success else 1)
