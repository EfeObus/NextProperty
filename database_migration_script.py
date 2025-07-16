#!/usr/bin/env python3
"""
Database Migration Script
Migrates all data from local MySQL database to remote MySQL database
"""

import os
import sys
import pymysql
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self):
        # Old database connection (source)
        self.old_db_config = {
            'host': os.getenv('OLD_DB_HOST', 'localhost'),
            'port': int(os.getenv('OLD_DB_PORT', 3306)),
            'user': os.getenv('OLD_DB_USER', 'root'),
            'password': 'Jesutekevwe1@@',
            'database': os.getenv('OLD_DB_NAME', 'nextproperty_ai'),
            'charset': 'utf8mb4'
        }
        
        # New database connection (destination)
        self.new_db_config = {
            'host': '184.107.4.32',
            'port': 8001,
            'user': 'studentGroup',
            'password': 'juifcdhoifdqw13f',
            'database': 'NextProperty',
            'charset': 'utf8mb4'
        }
        
        # SQLAlchemy engines with connection settings
        old_db_url = f"mysql+pymysql://{self.old_db_config['user']}:Jesutekevwe1%40%40@{self.old_db_config['host']}:{self.old_db_config['port']}/{self.old_db_config['database']}"
        new_db_url = f"mysql+pymysql://{self.new_db_config['user']}:{self.new_db_config['password']}@{self.new_db_config['host']}:{self.new_db_config['port']}/{self.new_db_config['database']}"
        
        engine_options = {
            'pool_recycle': 3600,
            'pool_pre_ping': True,
            'connect_args': {
                'connect_timeout': 60,
                'read_timeout': 60,
                'write_timeout': 60,
                'charset': 'utf8mb4'
            }
        }
        
        self.old_engine = create_engine(old_db_url, echo=False, **engine_options)
        self.new_engine = create_engine(new_db_url, echo=False, **engine_options)

    def test_connections(self):
        """Test both database connections."""
        logger.info("Testing database connections...")
        
        try:
            # Test old database
            with self.old_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✓ Successfully connected to old database")
                
            # Test new database
            with self.new_engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✓ Successfully connected to new database")
                
            return True
            
        except Exception as e:
            logger.error(f"✗ Connection test failed: {e}")
            return False

    def get_table_list(self):
        """Get list of tables from the old database."""
        try:
            with self.old_engine.connect() as conn:
                result = conn.execute(text("SHOW TABLES"))
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"Found {len(tables)} tables in old database: {tables}")
                return tables
        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            return []

    def get_table_structure(self, table_name):
        """Get the CREATE TABLE statement for a table."""
        try:
            with self.old_engine.connect() as conn:
                result = conn.execute(text(f"SHOW CREATE TABLE `{table_name}`"))
                create_statement = result.fetchone()[1]
                return create_statement
        except Exception as e:
            logger.error(f"Error getting structure for table {table_name}: {e}")
            return None

    def create_table_in_new_db(self, table_name, create_statement):
        """Create table in new database."""
        try:
            with self.new_engine.connect() as conn:
                # Drop table if exists
                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
                # Create table
                conn.execute(text(create_statement))
                conn.commit()
                logger.info(f"✓ Created table {table_name} in new database")
                return True
        except Exception as e:
            logger.error(f"✗ Error creating table {table_name}: {e}")
            return False

    def migrate_table_data(self, table_name):
        """Migrate data from old table to new table."""
        try:
            # Get data from old database
            logger.info(f"Reading data from table {table_name}...")
            df = pd.read_sql(f"SELECT * FROM `{table_name}`", self.old_engine)
            
            if df.empty:
                logger.info(f"Table {table_name} is empty, skipping data migration")
                return True
                
            logger.info(f"Found {len(df)} rows in table {table_name}")
            
            # Insert data into new database
            logger.info(f"Inserting data into new table {table_name}...")
            df.to_sql(table_name, self.new_engine, if_exists='append', index=False, method='multi')
            
            # Verify data migration
            with self.new_engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                new_count = result.fetchone()[0]
                
            if new_count == len(df):
                logger.info(f"✓ Successfully migrated {new_count} rows for table {table_name}")
                return True
            else:
                logger.error(f"✗ Data count mismatch for table {table_name}: {len(df)} vs {new_count}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error migrating data for table {table_name}: {e}")
            return False

    def migrate_database(self):
        """Main migration function."""
        logger.info("Starting database migration...")
        
        # Test connections
        if not self.test_connections():
            logger.error("Connection test failed. Aborting migration.")
            return False
            
        # Get table list
        tables = self.get_table_list()
        if not tables:
            logger.error("No tables found in old database.")
            return False
            
        success_count = 0
        total_tables = len(tables)
        
        for table_name in tables:
            logger.info(f"Processing table {table_name} ({success_count + 1}/{total_tables})...")
            
            # Get table structure
            create_statement = self.get_table_structure(table_name)
            if not create_statement:
                logger.error(f"Could not get structure for table {table_name}")
                continue
                
            # Create table in new database
            if not self.create_table_in_new_db(table_name, create_statement):
                logger.error(f"Could not create table {table_name} in new database")
                continue
                
            # Migrate data
            if self.migrate_table_data(table_name):
                success_count += 1
            else:
                logger.error(f"Data migration failed for table {table_name}")
                
        logger.info(f"Migration completed: {success_count}/{total_tables} tables migrated successfully")
        
        if success_count == total_tables:
            logger.info("✓ All tables migrated successfully!")
            return True
        else:
            logger.error(f"✗ Migration incomplete: {total_tables - success_count} tables failed")
            return False

    def verify_migration(self):
        """Verify the migration by comparing row counts."""
        logger.info("Verifying migration...")
        
        tables = self.get_table_list()
        verification_passed = True
        
        for table_name in tables:
            try:
                # Count rows in old database
                with self.old_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                    old_count = result.fetchone()[0]
                    
                # Count rows in new database
                with self.new_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                    new_count = result.fetchone()[0]
                    
                if old_count == new_count:
                    logger.info(f"✓ {table_name}: {old_count} rows (verified)")
                else:
                    logger.error(f"✗ {table_name}: {old_count} vs {new_count} rows (mismatch)")
                    verification_passed = False
                    
            except Exception as e:
                logger.error(f"✗ Error verifying table {table_name}: {e}")
                verification_passed = False
                
        return verification_passed

def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("NextProperty Database Migration Script")
    logger.info("=" * 60)
    
    migrator = DatabaseMigrator()
    
    # Perform migration
    if migrator.migrate_database():
        logger.info("Migration completed successfully!")
        
        # Verify migration
        if migrator.verify_migration():
            logger.info("✓ Migration verification passed!")
        else:
            logger.error("✗ Migration verification failed!")
            
    else:
        logger.error("Migration failed!")
        
    logger.info("Migration script completed.")

if __name__ == "__main__":
    main()
