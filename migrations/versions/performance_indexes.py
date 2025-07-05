"""Add performance indexes to properties table

Revision ID: performance_indexes
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'performance_indexes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add performance-optimized indexes."""
    # Create indexes for better query performance
    op.create_index('idx_ai_valuation', 'properties', ['ai_valuation'])
    op.create_index('idx_original_price', 'properties', ['original_price'])
    op.create_index('idx_sqft_bedrooms', 'properties', ['sqft', 'bedrooms'])
    op.create_index('idx_city_type_price', 'properties', ['city', 'property_type', 'original_price'])
    op.create_index('idx_investment_score', 'properties', ['investment_score'])
    
    # Improve existing indexes if they don't exist
    try:
        op.create_index('idx_year_built', 'properties', ['year_built'])
    except:
        pass  # Index might already exist

def downgrade():
    """Remove performance indexes."""
    op.drop_index('idx_ai_valuation', 'properties')
    op.drop_index('idx_original_price', 'properties')
    op.drop_index('idx_sqft_bedrooms', 'properties')
    op.drop_index('idx_city_type_price', 'properties')
    op.drop_index('idx_investment_score', 'properties')
    op.drop_index('idx_year_built', 'properties')
