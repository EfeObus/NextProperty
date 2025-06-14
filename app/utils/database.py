"""
Database initialization and migration utilities for NextProperty AI platform.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import logging
from datetime import datetime
from sqlalchemy import text

logger = logging.getLogger(__name__)


def init_database(app: Flask, db: SQLAlchemy):
    """
    Initialize database with Flask-Migrate.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    migrate = Migrate(app, db)
    return migrate


def create_tables(db: SQLAlchemy):
    """
    Create all database tables.
    
    Args:
        db: SQLAlchemy database instance
    """
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False


def drop_tables(db: SQLAlchemy):
    """
    Drop all database tables.
    
    Args:
        db: SQLAlchemy database instance
    """
    try:
        db.drop_all()
        logger.info("Database tables dropped successfully")
        return True
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        return False


def reset_database(db: SQLAlchemy):
    """
    Reset database by dropping and recreating all tables.
    
    Args:
        db: SQLAlchemy database instance
    """
    try:
        drop_tables(db)
        create_tables(db)
        logger.info("Database reset successfully")
        return True
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False


def create_indexes(db: SQLAlchemy):
    """
    Create additional database indexes for performance.
    
    Args:
        db: SQLAlchemy database instance
    """
    try:
        # Property indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(city, province);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_type_status ON properties(property_type, status);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_coordinates ON properties(latitude, longitude);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_bedrooms_bathrooms ON properties(bedrooms, bathrooms);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_square_feet ON properties(square_feet);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_properties_listed_date ON properties(listed_date);
        """))
        
        # Property price history indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_price_history_property_date ON property_price_history(property_id, date);
        """))
        
        # Property views indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_property_views_property_date ON property_views(property_id, viewed_at);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_property_views_user_date ON property_views(user_id, viewed_at);
        """))
        
        # Saved searches indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_saved_searches_user_active ON saved_searches(user_id, is_active);
        """))
        
        # Price alerts indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_price_alerts_user_active ON price_alerts(user_id, is_active);
        """))
        
        # Agent indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_agents_brokerage ON agents(brokerage);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_agents_active_rating ON agents(is_active, average_rating);
        """))
        
        # User indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_active_verified ON users(is_active, is_verified);
        """))
        
        # Economic data indexes
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_economic_data_indicator_date ON economic_data(indicator_name, date);
        """))
        
        db.engine.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_economic_data_region_category ON economic_data(region, category);
        """))
        
        logger.info("Database indexes created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")
        return False


def optimize_database(db: SQLAlchemy):
    """
    Optimize database performance.
    
    Args:
        db: SQLAlchemy database instance
    """
    try:
        # Update table statistics for MySQL
        if 'mysql' in str(db.engine.url):
            db.engine.execute(text("ANALYZE TABLE properties;"))
            db.engine.execute(text("ANALYZE TABLE agents;"))
            db.engine.execute(text("ANALYZE TABLE users;"))
            db.engine.execute(text("ANALYZE TABLE economic_data;"))
            db.engine.execute(text("ANALYZE TABLE property_price_history;"))
            db.engine.execute(text("ANALYZE TABLE property_views;"))
            db.engine.execute(text("ANALYZE TABLE saved_searches;"))
            db.engine.execute(text("ANALYZE TABLE price_alerts;"))
        
        # Vacuum for PostgreSQL
        elif 'postgresql' in str(db.engine.url):
            db.engine.execute(text("VACUUM ANALYZE;"))
        
        logger.info("Database optimization completed")
        return True
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return False


def backup_database(db: SQLAlchemy, backup_path: str = None):
    """
    Create database backup.
    
    Args:
        db: SQLAlchemy database instance
        backup_path: Path to save backup file
    """
    if not backup_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"backup_{timestamp}.sql"
    
    try:
        if 'mysql' in str(db.engine.url):
            # MySQL backup using mysqldump
            import subprocess
            
            url = db.engine.url
            command = [
                'mysqldump',
                '-h', url.host or 'localhost',
                '-P', str(url.port or 3306),
                '-u', url.username,
                f'-p{url.password}',
                url.database
            ]
            
            with open(backup_path, 'w') as f:
                subprocess.run(command, stdout=f, check=True)
        
        elif 'postgresql' in str(db.engine.url):
            # PostgreSQL backup using pg_dump
            import subprocess
            
            url = db.engine.url
            env = os.environ.copy()
            env['PGPASSWORD'] = url.password
            
            command = [
                'pg_dump',
                '-h', url.host or 'localhost',
                '-p', str(url.port or 5432),
                '-U', url.username,
                '-d', url.database,
                '-f', backup_path
            ]
            
            subprocess.run(command, env=env, check=True)
        
        else:
            # SQLite backup
            import shutil
            shutil.copy2(url.database, backup_path)
        
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creating database backup: {e}")
        return None


def check_database_health(db: SQLAlchemy) -> dict:
    """
    Check database health and return status.
    
    Args:
        db: SQLAlchemy database instance
        
    Returns:
        dict: Database health status
    """
    health_status = {
        'connected': False,
        'tables_exist': False,
        'indexes_exist': False,
        'sample_data': False,
        'error': None
    }
    
    try:
        # Check connection
        db.engine.execute(text("SELECT 1"))
        health_status['connected'] = True
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = ['properties', 'agents', 'users', 'economic_data']
        tables_exist = all(table in tables for table in required_tables)
        health_status['tables_exist'] = tables_exist
        
        if tables_exist:
            # Check if indexes exist
            property_indexes = inspector.get_indexes('properties')
            health_status['indexes_exist'] = len(property_indexes) > 0
            
            # Check for sample data
            result = db.engine.execute(text("SELECT COUNT(*) FROM properties"))
            property_count = result.fetchone()[0]
            health_status['sample_data'] = property_count > 0
            health_status['property_count'] = property_count
            
            # Get table sizes
            health_status['table_counts'] = {}
            for table in required_tables:
                try:
                    result = db.engine.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    health_status['table_counts'][table] = result.fetchone()[0]
                except Exception:
                    health_status['table_counts'][table] = 0
    
    except Exception as e:
        health_status['error'] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_status


def seed_sample_data(db: SQLAlchemy):
    """
    Seed database with sample data for development.
    
    Args:
        db: SQLAlchemy database instance
    """
    try:
        from app.models.user import User
        from app.models.agent import Agent
        from app.models.property import Property
        from app.models.economic_data import EconomicData
        from datetime import date, datetime
        import json
        
        # Create sample users
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@nextproperty.ai',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                is_verified=True
            )
            admin_user.set_password('admin123')
            
            demo_user = User(
                username='demo',
                email='demo@nextproperty.ai',
                first_name='Demo',
                last_name='User',
                is_verified=True
            )
            demo_user.set_password('demo123')
            
            db.session.add(admin_user)
            db.session.add(demo_user)
        
        # Create sample agent
        if Agent.query.count() == 0:
            sample_agent = Agent(
                first_name='John',
                last_name='Smith',
                license_number='A123456',
                brokerage='NextProperty Realty',
                phone='(416) 555-0123',
                email='john.smith@nextproperty.ai',
                bio='Experienced real estate agent specializing in Toronto properties.',
                specialties=json.dumps(['Residential', 'Condos', 'First-time buyers']),
                languages=json.dumps(['English', 'French']),
                years_experience=8,
                average_rating=4.8,
                review_count=156
            )
            db.session.add(sample_agent)
        
        # Create sample properties
        if Property.query.count() == 0:
            sample_properties = [
                {
                    'mls_number': 'C5123456',
                    'street_number': '123',
                    'street_name': 'Main Street',
                    'city': 'Toronto',
                    'province': 'ON',
                    'postal_code': 'M5V3A1',
                    'price': 850000,
                    'property_type': 'condo',
                    'bedrooms': 2,
                    'bathrooms': 2,
                    'square_feet': 1200,
                    'year_built': 2018,
                    'description': 'Beautiful modern condo in downtown Toronto with stunning city views.',
                    'latitude': 43.6532,
                    'longitude': -79.3832,
                    'status': 'active',
                    'listed_date': date(2024, 12, 1)
                },
                {
                    'mls_number': 'H5789012',
                    'street_number': '456',
                    'street_name': 'Oak Avenue',
                    'city': 'Vancouver',
                    'province': 'BC',
                    'postal_code': 'V6B1A1',
                    'price': 1250000,
                    'property_type': 'house',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'square_feet': 1800,
                    'lot_size': 5000,
                    'year_built': 2015,
                    'description': 'Spacious family home with large backyard in desirable neighborhood.',
                    'latitude': 49.2827,
                    'longitude': -123.1207,
                    'status': 'active',
                    'listed_date': date(2024, 11, 15)
                }
            ]
            
            for prop_data in sample_properties:
                property_obj = Property(**prop_data)
                if Agent.query.first():
                    property_obj.agent_id = Agent.query.first().id
                db.session.add(property_obj)
        
        # Create sample economic data
        if EconomicData.query.count() == 0:
            sample_economic_data = [
                {
                    'indicator_name': 'Bank Rate',
                    'value': 5.0,
                    'unit': 'Percent',
                    'date': date(2024, 12, 1),
                    'frequency': 'Daily',
                    'source': 'Bank of Canada',
                    'region': 'Canada',
                    'category': 'Interest Rates'
                },
                {
                    'indicator_name': 'Consumer Price Index',
                    'value': 138.2,
                    'unit': 'Index',
                    'date': date(2024, 11, 1),
                    'frequency': 'Monthly',
                    'source': 'Statistics Canada',
                    'region': 'Canada',
                    'category': 'Inflation'
                }
            ]
            
            for econ_data in sample_economic_data:
                economic_obj = EconomicData(**econ_data)
                db.session.add(economic_obj)
        
        db.session.commit()
        logger.info("Sample data seeded successfully")
        return True
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error seeding sample data: {e}")
        return False


def get_migration_status(migrate):
    """
    Get current migration status.
    
    Args:
        migrate: Flask-Migrate instance
        
    Returns:
        dict: Migration status information
    """
    try:
        from flask_migrate import current, heads, history
        
        current_rev = current()
        head_rev = heads()
        migration_history = list(history())
        
        return {
            'current_revision': current_rev,
            'head_revision': head_rev,
            'is_up_to_date': current_rev == head_rev,
            'pending_migrations': len(migration_history),
            'migration_history': [
                {
                    'revision': rev.revision,
                    'description': rev.doc,
                    'down_revision': rev.down_revision
                }
                for rev in migration_history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting migration status: {e}")
        return {'error': str(e)}
