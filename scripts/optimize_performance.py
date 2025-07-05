#!/usr/bin/env python3
"""
Performance optimization script for NextProperty AI.
This script optimizes the database and pre-computes expensive calculations.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.property import Property
from app.services.ml_service import MLService
from sqlalchemy import func, text
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_database():
    """Run database optimizations."""
    app = create_app()
    
    with app.app_context():
        try:
            # Analyze tables for better query planning
            logger.info("Analyzing database tables...")
            with db.engine.connect() as conn:
                conn.execute(text("ANALYZE TABLE properties"))
                conn.execute(text("ANALYZE TABLE property_photos"))
                conn.commit()
            logger.info("Database analysis complete")
            
            # Update statistics
            logger.info("Updating table statistics...")
            with db.engine.connect() as conn:
                conn.execute(text("OPTIMIZE TABLE properties"))
                conn.commit()
            logger.info("Table optimization complete")
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")

def precompute_ai_valuations():
    """Pre-compute AI valuations for properties that don't have them."""
    app = create_app()
    ml_service = MLService()
    
    with app.app_context():
        try:
            # Get properties without AI valuations
            properties_without_ai = Property.query.filter(
                Property.ai_valuation.is_(None),
                Property.sold_price.isnot(None),
                Property.sqft.isnot(None)
            ).limit(100).all()  # Process in batches
            
            logger.info(f"Processing {len(properties_without_ai)} properties for AI valuation...")
            
            for i, property_obj in enumerate(properties_without_ai):
                try:
                    # Get AI analysis
                    analysis = ml_service.analyze_property(property_obj)
                    if analysis and 'predicted_price' in analysis:
                        property_obj.ai_valuation = analysis['predicted_price']
                        if 'investment_score' in analysis:
                            property_obj.investment_score = analysis['investment_score']
                    
                    # Commit every 10 properties
                    if (i + 1) % 10 == 0:
                        db.session.commit()
                        logger.info(f"Processed {i + 1} properties...")
                        time.sleep(0.1)  # Small delay to prevent overwhelming the system
                
                except Exception as e:
                    logger.warning(f"Failed to process property {property_obj.listing_id}: {e}")
                    continue
            
            # Final commit
            db.session.commit()
            logger.info("AI valuation pre-computation complete")
            
        except Exception as e:
            logger.error(f"AI valuation pre-computation failed: {e}")
            db.session.rollback()

def update_computed_fields():
    """Update computed fields to improve performance."""
    app = create_app()
    
    with app.app_context():
        try:
            # Update price per sqft for properties that don't have it
            properties_to_update = Property.query.filter(
                Property.price_per_sqft.is_(None),
                Property.sqft.isnot(None),
                Property.sqft > 0,
                Property.sold_price.isnot(None)
            ).all()
            
            logger.info(f"Updating price_per_sqft for {len(properties_to_update)} properties...")
            
            for property_obj in properties_to_update:
                property_obj.price_per_sqft = property_obj.sold_price / property_obj.sqft
            
            db.session.commit()
            logger.info("Computed fields update complete")
            
        except Exception as e:
            logger.error(f"Computed fields update failed: {e}")
            db.session.rollback()

def clean_cache():
    """Clear application cache."""
    app = create_app()
    
    with app.app_context():
        try:
            from app.extensions import cache
            cache.clear()
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")

if __name__ == "__main__":
    logger.info("Starting performance optimization...")
    
    # Run optimizations
    optimize_database()
    update_computed_fields()
    precompute_ai_valuations()
    clean_cache()
    
    logger.info("Performance optimization complete!")
