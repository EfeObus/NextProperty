# Database Documentation

## Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Models](#models)
- [Migrations](#migrations)
- [Indexes and Optimization](#indexes-and-optimization)
- [Data Management](#data-management)
- [Backup and Recovery](#backup-and-recovery)
- [Performance Tuning](#performance-tuning)

## Overview

NextProperty AI uses SQLAlchemy ORM with support for multiple database backends:
- **Development**: SQLite (default)
- **Production**: MySQL/PostgreSQL (recommended)
- **Testing**: In-memory SQLite

## Database Schema

### Core Tables

#### Properties Table
```sql
CREATE TABLE properties (
    listing_id VARCHAR(50) PRIMARY KEY,
    mls VARCHAR(20),
    property_type VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    province VARCHAR(50),
    postal_code VARCHAR(10),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    sold_price DECIMAL(12, 2),
    original_price DECIMAL(12, 2),
    bedrooms INT,
    bathrooms DECIMAL(3, 1),
    kitchens_plus INT,
    rooms INT,
    sqft INT,
    lot_size DECIMAL(8, 4),
    year_built INT,
    sold_date DATE,
    dom INT, -- Days on Market
    taxes DECIMAL(10, 2),
    maintenance_fee DECIMAL(10, 2),
    features TEXT,
    community_features TEXT,
    remarks TEXT,
    agent_id VARCHAR(50),
    ai_valuation DECIMAL(12, 2),
    investment_score DECIMAL(3, 1),
    risk_assessment VARCHAR(20),
    market_trend VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);
```

#### Agents Table
```sql
CREATE TABLE agents (
    agent_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE,
    phone VARCHAR(20),
    license_number VARCHAR(50),
    brokerage VARCHAR(100),
    specialties TEXT, -- JSON array
    years_experience INT,
    languages VARCHAR(200),
    website VARCHAR(200),
    bio TEXT,
    profile_photo VARCHAR(500),
    total_sales INT DEFAULT 0,
    total_volume DECIMAL(15, 2) DEFAULT 0,
    average_rating DECIMAL(3, 2),
    review_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    phone VARCHAR(20),
    preferred_cities TEXT, -- JSON array
    notification_preferences TEXT, -- JSON object
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### Economic Data Tables
```sql
CREATE TABLE economic_indicators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    indicator_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    source VARCHAR(20), -- 'BOC' or 'STATCAN'
    category VARCHAR(50),
    frequency VARCHAR(20), -- 'daily', 'monthly', 'quarterly'
    unit VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE economic_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    indicator_code VARCHAR(50),
    date DATE,
    value DECIMAL(15, 6),
    period_label VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (indicator_code) REFERENCES economic_indicators(indicator_code),
    UNIQUE KEY unique_indicator_date (indicator_code, date)
);
```

#### Property Photos Table
```sql
CREATE TABLE property_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id VARCHAR(50),
    photo_url VARCHAR(500),
    photo_type VARCHAR(50), -- 'exterior', 'interior', 'aerial'
    caption TEXT,
    order_index INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES properties(listing_id) ON DELETE CASCADE
);
```

#### Property Rooms Table
```sql
CREATE TABLE property_rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id VARCHAR(50),
    room_type VARCHAR(50), -- 'bedroom', 'bathroom', 'kitchen', etc.
    level VARCHAR(50), -- 'main', 'upper', 'lower', 'basement'
    dimensions VARCHAR(50),
    features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (listing_id) REFERENCES properties(listing_id) ON DELETE CASCADE
);
```

#### User Saved Properties Table
```sql
CREATE TABLE saved_properties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    listing_id VARCHAR(50),
    is_favorite BOOLEAN DEFAULT FALSE,
    notes TEXT,
    tags TEXT, -- JSON array
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES properties(listing_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_property (user_id, listing_id)
);
```

## Models

### Property Model (`app/models/property.py`)

**Key Features:**
- SQLAlchemy ORM model for property data
- Automatic timestamp management
- JSON serialization methods
- Validation for price, coordinates, and dates
- Relationships with agents, photos, and rooms

**Key Methods:**
```python
def to_dict(self) -> dict
def calculate_price_per_sqft(self) -> float
def get_age(self) -> int
def is_recent_sale(self, days: int = 90) -> bool
```

### Agent Model (`app/models/agent.py`)

**Key Features:**
- Agent profile and contact information
- Performance metrics tracking
- Review system integration
- Specialties as JSON array

**Key Methods:**
```python
def to_dict(self) -> dict
def calculate_average_rating(self) -> float
def get_active_listings_count(self) -> int
```

### User Model (`app/models/user.py`)

**Key Features:**
- User authentication and profile
- Password hashing with werkzeug
- Preferences stored as JSON
- Saved properties relationship

**Key Methods:**
```python
def set_password(self, password: str)
def check_password(self, password: str) -> bool
def to_dict(self, include_sensitive: bool = False) -> dict
```

### Economic Data Models (`app/models/economic_data.py`)

**Key Features:**
- Economic indicators management
- Time series data storage
- Integration with BoC and StatCan APIs

**Key Methods:**
```python
@classmethod
def get_latest_value(cls, indicator_code: str) -> 'EconomicData'
@classmethod
def get_time_series(cls, indicator_code: str, start_date: date, end_date: date) -> List['EconomicData']
```

## Migrations

### Using Flask-Migrate

```bash
# Initialize migrations (first time only)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade if needed
flask db downgrade

# Show migration history
flask db history

# Show current revision
flask db current
```

### Migration Best Practices

1. **Always review migrations** before applying
2. **Backup database** before major migrations
3. **Test migrations** on development/staging first
4. **Use descriptive messages** for migration commits
5. **Handle data migrations** separately from schema changes

### Sample Migration Script

```python
# migrations/versions/xxx_add_economic_data.py
def upgrade():
    # Create economic_indicators table
    op.create_table('economic_indicators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('indicator_code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        # ... other columns
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('indicator_code')
    )
    
    # Create economic_data table
    op.create_table('economic_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('indicator_code', sa.String(50), nullable=True),
        # ... other columns
        sa.ForeignKeyConstraint(['indicator_code'], ['economic_indicators.indicator_code']),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('economic_data')
    op.drop_table('economic_indicators')
```

## Indexes and Optimization

### Performance Indexes

```sql
-- Primary lookup indexes
CREATE INDEX idx_properties_city ON properties(city);
CREATE INDEX idx_properties_property_type ON properties(property_type);
CREATE INDEX idx_properties_price_range ON properties(sold_price);
CREATE INDEX idx_properties_sold_date ON properties(sold_date);
CREATE INDEX idx_properties_bedrooms ON properties(bedrooms);
CREATE INDEX idx_properties_bathrooms ON properties(bathrooms);

-- Geospatial indexes
CREATE INDEX idx_properties_location ON properties(latitude, longitude);

-- Full-text search indexes (MySQL)
CREATE FULLTEXT INDEX idx_properties_features ON properties(features, community_features, remarks);

-- Agent performance indexes
CREATE INDEX idx_agents_active ON agents(is_active);
CREATE INDEX idx_agents_rating ON agents(average_rating);

-- Economic data indexes
CREATE INDEX idx_economic_data_indicator_date ON economic_data(indicator_code, date);
CREATE INDEX idx_economic_data_date ON economic_data(date);

-- User activity indexes
CREATE INDEX idx_saved_properties_user ON saved_properties(user_id);
CREATE INDEX idx_saved_properties_favorites ON saved_properties(user_id, is_favorite);
```

### Composite Indexes

```sql
-- Common filter combinations
CREATE INDEX idx_properties_city_type_price ON properties(city, property_type, sold_price);
CREATE INDEX idx_properties_beds_baths_price ON properties(bedrooms, bathrooms, sold_price);
CREATE INDEX idx_properties_date_price ON properties(sold_date, sold_price);

-- AI analysis optimization
CREATE INDEX idx_properties_ai_analysis ON properties(ai_valuation, investment_score);
```

## Data Management

### Data Import/Export

#### Loading Sample Data
```bash
# Load initial property data
python scripts/load_data.py

# Load specific dataset
python scripts/load_data.py --file Dataset/large_sample_real_estate.csv

# Load with validation
python scripts/load_data.py --validate --clean
```

#### Exporting Data
```python
from app.services.export_service import ExportService

export_service = ExportService()

# Export to Excel
export_service.export_properties_to_excel(
    filename="properties_export.xlsx",
    filters={'city': 'Toronto'}
)

# Export to JSON
export_service.export_to_json(
    model=Property,
    filename="properties.json"
)
```

### Data Validation

#### Property Validation Rules
```python
def validate_property_data(property_data):
    """Validate property data before insertion."""
    errors = []
    
    # Required fields
    required_fields = ['address', 'city', 'province', 'property_type']
    for field in required_fields:
        if not property_data.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Price validation
    if property_data.get('sold_price'):
        if property_data['sold_price'] <= 0:
            errors.append("Sold price must be positive")
    
    # Coordinate validation
    lat = property_data.get('latitude')
    lng = property_data.get('longitude')
    if lat and lng:
        if not (41.7 <= lat <= 83.5):  # Canada latitude bounds
            errors.append("Latitude outside Canada bounds")
        if not (-141.0 <= lng <= -52.6):  # Canada longitude bounds
            errors.append("Longitude outside Canada bounds")
    
    return errors
```

### Data Cleaning

#### Common Cleaning Operations
```python
def clean_property_data(df):
    """Clean and standardize property data."""
    # Remove duplicates
    df = df.drop_duplicates(subset=['listing_id'])
    
    # Standardize city names
    df['city'] = df['city'].str.title().str.strip()
    
    # Clean postal codes
    df['postal_code'] = df['postal_code'].str.upper().str.replace(' ', '')
    
    # Validate and clean prices
    df = df[df['sold_price'] > 0]
    df = df[df['sold_price'] < 50000000]  # Remove outliers
    
    # Clean text fields
    text_fields = ['features', 'community_features', 'remarks']
    for field in text_fields:
        df[field] = df[field].fillna('').str.strip()
    
    return df
```

## Backup and Recovery

### Backup Strategies

#### SQLite Backup
```bash
# Simple file copy
cp instance/nextproperty_dev.db backups/nextproperty_$(date +%Y%m%d_%H%M%S).db

# Using SQLite backup command
sqlite3 instance/nextproperty_dev.db ".backup backups/backup_$(date +%Y%m%d).db"
```

#### MySQL Backup
```bash
# Full database backup
mysqldump -u username -p nextproperty_db > backups/nextproperty_$(date +%Y%m%d).sql

# Structure only
mysqldump -u username -p --no-data nextproperty_db > backups/schema_$(date +%Y%m%d).sql

# Data only
mysqldump -u username -p --no-create-info nextproperty_db > backups/data_$(date +%Y%m%d).sql
```

#### Automated Backup Script
```bash
#!/bin/bash
# backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
DB_NAME="nextproperty_db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/nextproperty_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/nextproperty_$DATE.sql

# Remove backups older than 30 days
find $BACKUP_DIR -name "nextproperty_*.sql.gz" -mtime +30 -delete

echo "Backup completed: nextproperty_$DATE.sql.gz"
```

### Recovery Procedures

#### SQLite Recovery
```bash
# Restore from backup
cp backups/nextproperty_20240101_120000.db instance/nextproperty_dev.db

# Verify database integrity
sqlite3 instance/nextproperty_dev.db "PRAGMA integrity_check;"
```

#### MySQL Recovery
```bash
# Restore full database
mysql -u username -p nextproperty_db < backups/nextproperty_20240101.sql

# Restore specific table
mysql -u username -p nextproperty_db -e "DROP TABLE properties;"
mysql -u username -p nextproperty_db < backups/properties_table.sql
```

## Performance Tuning

### Query Optimization

#### Slow Query Analysis
```python
import time
from app import db
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.5:  # Log queries taking more than 500ms
        app.logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")
```

#### Optimized Query Examples
```python
# Bad: N+1 queries
properties = Property.query.all()
for prop in properties:
    agent_name = prop.agent.name  # Triggers additional query

# Good: Eager loading
properties = Property.query.options(joinedload(Property.agent)).all()
for prop in properties:
    agent_name = prop.agent.name  # No additional query

# Bad: Loading all data
all_properties = Property.query.all()

# Good: Pagination
properties = Property.query.paginate(page=1, per_page=20, error_out=False)
```

### Database Configuration

#### MySQL Optimization
```sql
-- InnoDB settings for performance
SET GLOBAL innodb_buffer_pool_size = 1073741824;  -- 1GB
SET GLOBAL innodb_log_file_size = 268435456;      -- 256MB
SET GLOBAL innodb_flush_log_at_trx_commit = 2;

-- Query cache (if using older MySQL)
SET GLOBAL query_cache_size = 268435456;  -- 256MB
SET GLOBAL query_cache_type = ON;

-- Connection settings
SET GLOBAL max_connections = 200;
SET GLOBAL wait_timeout = 28800;
```

#### PostgreSQL Optimization
```sql
-- Memory settings
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;

-- Apply changes
SELECT pg_reload_conf();
```

### Connection Pooling

#### SQLAlchemy Pool Configuration
```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,          # Number of connections to maintain
    'pool_recycle': 300,      # Recycle connections after 5 minutes
    'pool_pre_ping': True,    # Validate connections before use
    'pool_timeout': 20,       # Timeout for getting connection
    'max_overflow': 0,        # Additional connections beyond pool_size
}
```

### Monitoring and Metrics

#### Database Monitoring
```python
from app.services.database_optimizer import DatabaseOptimizer

optimizer = DatabaseOptimizer()

# Get database health metrics
health = optimizer.get_database_health()
print(f"Connection count: {health['connections']}")
print(f"Table sizes: {health['table_sizes']}")
print(f"Index usage: {health['index_stats']}")

# Performance optimization
optimizer.optimize_for_bulk_operations()
```

#### Performance Metrics to Track
- Query execution time
- Connection pool utilization
- Table sizes and growth rates
- Index usage statistics
- Cache hit rates
- Lock contention

### Best Practices

1. **Use appropriate indexes** for common queries
2. **Limit SELECT fields** to only what's needed
3. **Use LIMIT/pagination** for large result sets
4. **Eager load relationships** to avoid N+1 queries
5. **Cache expensive queries** using Redis
6. **Monitor query performance** and optimize slow queries
7. **Regular maintenance** including ANALYZE and VACUUM
8. **Keep statistics updated** for query planner optimization

## Troubleshooting

### Common Database Issues

#### Connection Issues
```bash
# Check database connection
flask shell
>>> from app import db
>>> db.engine.execute('SELECT 1').scalar()

# Check connection pool status
>>> db.engine.pool.status()
```

#### Migration Issues
```bash
# Reset migrations (development only)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Fix migration conflicts
flask db merge -m "Merge migrations"
```

#### Performance Issues
```sql
-- Check for locked tables (MySQL)
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS;

-- Check for slow queries
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

For more troubleshooting information, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
