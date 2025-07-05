"""
Simple performance optimization for NextProperty AI.
"""
from app import create_app, db
from app.models.property import Property
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    app = create_app()
    
    with app.app_context():
        # Clear cache
        try:
            from app.extensions import cache
            cache.clear()
            logger.info("Cache cleared")
        except:
            logger.info("Cache clear skipped")
        
        # Update missing price_per_sqft values
        try:
            properties = Property.query.filter(
                Property.price_per_sqft.is_(None),
                Property.sqft.isnot(None),
                Property.sqft > 0,
                Property.sold_price.isnot(None)
            ).limit(100).all()
            
            count = 0
            for prop in properties:
                prop.price_per_sqft = prop.sold_price / prop.sqft
                count += 1
            
            db.session.commit()
            logger.info(f"Updated price_per_sqft for {count} properties")
            
        except Exception as e:
            logger.error(f"Error updating price_per_sqft: {e}")
        
        # Run basic database maintenance
        try:
            with db.engine.connect() as conn:
                # Get table status
                result = conn.execute(text("SHOW TABLE STATUS LIKE 'properties'"))
                table_info = result.fetchone()
                logger.info(f"Properties table has {table_info[4]} rows")
                
                # Basic optimization
                conn.execute(text("ANALYZE TABLE properties"))
                logger.info("Table analysis complete")
                
        except Exception as e:
            logger.error(f"Database optimization error: {e}")

if __name__ == "__main__":
    main()
    print("Quick optimization complete!")
