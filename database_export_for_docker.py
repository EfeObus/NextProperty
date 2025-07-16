#!/usr/bin/env python3
"""
Database Export Script for Docker MySQL Migration
Since the target database is in a Docker container, we'll export to SQL files
that can be imported via phpMyAdmin or docker exec commands.
"""

import os
import sys
import pymysql
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_export.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DatabaseExporter:
    def __init__(self):
        # Old database connection (source)
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'Jesutekevwe1@@',
            'database': 'nextproperty_ai'
        }
        
        # Create export directory
        self.export_dir = 'database_export'
        os.makedirs(self.export_dir, exist_ok=True)

    def test_connection(self):
        """Test database connection."""
        try:
            connection = pymysql.connect(**self.db_config, charset='utf8mb4')
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", 
                             (self.db_config['database'],))
                table_count = cursor.fetchone()[0]
                logger.info(f"✓ Connected to source database. Found {table_count} tables.")
            connection.close()
            return True
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False

    def get_table_list(self):
        """Get list of tables from the database."""
        try:
            connection = pymysql.connect(**self.db_config, charset='utf8mb4')
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                logger.info(f"Found tables: {tables}")
            connection.close()
            return tables
        except Exception as e:
            logger.error(f"Error getting table list: {e}")
            return []

    def export_database_structure(self):
        """Export database structure (CREATE TABLE statements)."""
        try:
            structure_file = os.path.join(self.export_dir, 'database_structure.sql')
            
            cmd = [
                'mysqldump',
                f'--host={self.db_config["host"]}',
                f'--port={self.db_config["port"]}',
                f'--user={self.db_config["user"]}',
                f'--password={self.db_config["password"]}',
                '--no-data',  # Structure only
                '--routines',
                '--triggers',
                '--single-transaction',
                '--add-drop-table',
                '--add-drop-database',
                '--create-options',
                self.db_config['database']
            ]
            
            logger.info("Exporting database structure...")
            with open(structure_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode == 0:
                logger.info(f"✓ Database structure exported to {structure_file}")
                return True
            else:
                logger.error(f"✗ Structure export failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting structure: {e}")
            return False

    def export_database_data(self):
        """Export database data."""
        try:
            data_file = os.path.join(self.export_dir, 'database_data.sql')
            
            cmd = [
                'mysqldump',
                f'--host={self.db_config["host"]}',
                f'--port={self.db_config["port"]}',
                f'--user={self.db_config["user"]}',
                f'--password={self.db_config["password"]}',
                '--no-create-info',  # Data only
                '--single-transaction',
                '--extended-insert',
                '--complete-insert',
                '--disable-keys',
                '--lock-tables=false',
                self.db_config['database']
            ]
            
            logger.info("Exporting database data...")
            with open(data_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode == 0:
                logger.info(f"✓ Database data exported to {data_file}")
                return True
            else:
                logger.error(f"✗ Data export failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return False

    def export_complete_database(self):
        """Export complete database (structure + data)."""
        try:
            complete_file = os.path.join(self.export_dir, 'complete_database.sql')
            
            cmd = [
                'mysqldump',
                f'--host={self.db_config["host"]}',
                f'--port={self.db_config["port"]}',
                f'--user={self.db_config["user"]}',
                f'--password={self.db_config["password"]}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--extended-insert',
                '--complete-insert',
                '--add-drop-table',
                '--disable-keys',
                self.db_config['database']
            ]
            
            logger.info("Exporting complete database...")
            with open(complete_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
            if result.returncode == 0:
                logger.info(f"✓ Complete database exported to {complete_file}")
                return True
            else:
                logger.error(f"✗ Complete export failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting complete database: {e}")
            return False

    def create_docker_import_script(self):
        """Create a script to import the database into Docker container."""
        script_content = '''#!/bin/bash
# Docker MySQL Import Script
# This script helps import the exported database into a Docker MySQL container

echo "NextProperty Database Import for Docker MySQL"
echo "============================================="

# Check if SQL files exist
if [ ! -f "database_export/complete_database.sql" ]; then
    echo "Error: complete_database.sql not found in database_export directory"
    exit 1
fi

echo "Choose import method:"
echo "1. Import via Docker exec (requires Docker container name)"
echo "2. Import via phpMyAdmin (manual process)"
echo "3. Import via MySQL client (if accessible)"

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        read -p "Enter Docker container name/ID: " container_name
        echo "Copying SQL file to container..."
        docker cp database_export/complete_database.sql $container_name:/tmp/
        
        echo "Importing database..."
        docker exec -i $container_name mysql -u studentGroup -p'juifcdhoifdqw13f' NextProperty < database_export/complete_database.sql
        
        if [ $? -eq 0 ]; then
            echo "✓ Database imported successfully!"
        else
            echo "✗ Import failed. Check Docker container logs."
        fi
        ;;
    2)
        echo "Manual phpMyAdmin Import Process:"
        echo "1. Open phpMyAdmin in your browser"
        echo "2. Select the 'NextProperty' database"
        echo "3. Go to 'Import' tab"
        echo "4. Choose the file: database_export/complete_database.sql"
        echo "5. Set format to 'SQL'"
        echo "6. Click 'Go' to import"
        echo ""
        echo "Note: If the file is too large, use the structure and data files separately:"
        echo "   - First import: database_export/database_structure.sql"
        echo "   - Then import: database_export/database_data.sql"
        ;;
    3)
        echo "Using MySQL client:"
        echo "mysql -h 184.107.4.32 -P 8002 -u studentGroup -p'juifcdhoifdqw13f' NextProperty < database_export/complete_database.sql"
        
        read -p "Execute this command now? (y/n): " execute
        if [ "$execute" = "y" ]; then
            mysql -h 184.107.4.32 -P 8002 -u studentGroup -p'juifcdhoifdqw13f' NextProperty < database_export/complete_database.sql
        fi
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
'''
        
        script_file = os.path.join(self.export_dir, 'import_to_docker.sh')
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(script_file, 0o755)
        logger.info(f"✓ Docker import script created: {script_file}")

    def create_import_instructions(self):
        """Create detailed import instructions."""
        instructions = f'''
# NextProperty Database Migration Instructions
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Files Created:
- `complete_database.sql` - Complete database dump (structure + data)
- `database_structure.sql` - Database structure only (tables, indexes, etc.)
- `database_data.sql` - Data only (INSERT statements)
- `import_to_docker.sh` - Automated import script

## Import Methods:

### Method 1: phpMyAdmin (Recommended for Docker)
1. Open phpMyAdmin in your browser (usually http://184.107.4.32:8080 or similar)
2. Login with your credentials
3. Select or create the 'NextProperty' database
4. Go to 'Import' tab
5. Choose file: `complete_database.sql`
6. Set format to 'SQL'
7. Click 'Go'

### Method 2: Docker Exec Command
If you have direct access to the Docker container:
```bash
# Copy SQL file to container
docker cp database_export/complete_database.sql <container_name>:/tmp/

# Import into database
docker exec -i <container_name> mysql -u studentGroup -p'juifcdhoifdqw13f' NextProperty < /tmp/complete_database.sql
```

### Method 3: MySQL Client (if accessible)
```bash
mysql -h 184.107.4.32 -P 8002 -u studentGroup -p'juifcdhoifdqw13f' NextProperty < database_export/complete_database.sql
```

### Method 4: Split Import (for large files)
If the complete file is too large:
1. First import structure: `database_structure.sql`
2. Then import data: `database_data.sql`

## After Import:
1. Update your .env file to use the new database
2. Test your application connection
3. Verify data integrity

## Troubleshooting:
- If import fails due to existing tables, the structure file includes DROP TABLE statements
- For character encoding issues, ensure UTF8MB4 is used
- Check Docker container logs for detailed error messages

## Current Database Configuration:
- Source: localhost:3306/nextproperty_ai
- Target: 184.107.4.32:8002/NextProperty
- Tables exported: Check the export log for details
'''
        
        instructions_file = os.path.join(self.export_dir, 'IMPORT_INSTRUCTIONS.md')
        with open(instructions_file, 'w') as f:
            f.write(instructions)
        
        logger.info(f"✓ Import instructions created: {instructions_file}")

    def export_database(self):
        """Main export function."""
        logger.info("Starting database export for Docker migration...")
        
        if not self.test_connection():
            logger.error("Cannot connect to source database. Aborting export.")
            return False
        
        success_count = 0
        
        # Export complete database
        if self.export_complete_database():
            success_count += 1
        
        # Export structure only
        if self.export_database_structure():
            success_count += 1
            
        # Export data only
        if self.export_database_data():
            success_count += 1
        
        # Create import helpers
        self.create_docker_import_script()
        self.create_import_instructions()
        
        logger.info(f"Export completed: {success_count}/3 operations successful")
        logger.info(f"Files saved in: {os.path.abspath(self.export_dir)}")
        
        return success_count == 3

def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("NextProperty Database Export for Docker Migration")
    logger.info("=" * 60)
    
    exporter = DatabaseExporter()
    
    if exporter.export_database():
        logger.info("✓ Database export completed successfully!")
        logger.info("Check the database_export directory for SQL files and instructions.")
    else:
        logger.error("✗ Database export failed!")
        
    logger.info("Export script completed.")

if __name__ == "__main__":
    main()
