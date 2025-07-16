
# NextProperty Database Migration Instructions
Generated on: 2025-07-11 20:38:58

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
