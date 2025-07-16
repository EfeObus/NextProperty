#!/bin/bash
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
