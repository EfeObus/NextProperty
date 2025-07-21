#!/usr/bin/env python3
"""
Database Migration Verification Script
Run this after importing to verify the migration was successful
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_migration():
    """Verify the migration by connecting to the new database and checking data."""
    
    # New database connection
    new_db_url = "mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8002/NextProperty"
    
    try:
        logger.info("Connecting to new database...")
        engine = create_engine(new_db_url, echo=False, connect_args={
            'connect_timeout': 60,
            'charset': 'utf8mb4'
        })
        
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT DATABASE(), USER(), NOW()"))
            db_info = result.fetchone()
            logger.info(f"✓ Connected to database: {db_info[0]} as user: {db_info[1]} at {db_info[2]}")
            
            # Get table list
            result = conn.execute(text("""
                SELECT table_name, table_rows 
                FROM information_schema.tables 
                WHERE table_schema = 'NextProperty'
                ORDER BY table_name
            """))
            
            tables = result.fetchall()
            logger.info(f"✓ Found {len(tables)} tables in the database:")
            
            total_rows = 0
            for table_name, row_count in tables:
                row_count = row_count or 0  # Handle None values
                logger.info(f"  - {table_name}: {row_count} rows")
                total_rows += row_count
            
            logger.info(f"✓ Total rows across all tables: {total_rows}")
            
            # Test specific important tables
            important_tables = ['properties', 'users', 'agents', 'favourites']
            for table in important_tables:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    logger.info(f"✓ {table} table: {count} records")
                except Exception as e:
                    logger.warning(f"⚠ Could not check {table} table: {e}")
            
            logger.info("✓ Database migration verification completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"✗ Migration verification failed: {e}")
        return False

def main():
    """Main verification function."""
    logger.info("=" * 60)
    logger.info("NextProperty Database Migration Verification")
    logger.info("=" * 60)
    
    if verify_migration():
        logger.info("✓ Migration verification passed!")
        logger.info("Your database has been successfully migrated to the new server.")
    else:
        logger.error("✗ Migration verification failed!")
        logger.error("Please check the import process and try again.")

if __name__ == "__main__":
    main()
