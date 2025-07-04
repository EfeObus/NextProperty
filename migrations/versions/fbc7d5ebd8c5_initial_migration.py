"""Initial migration

Revision ID: fbc7d5ebd8c5
Revises: 
Create Date: 2025-06-07 15:32:47.861518

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbc7d5ebd8c5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agents',
    sa.Column('agent_id', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('license_number', sa.String(length=50), nullable=True),
    sa.Column('brokerage', sa.String(length=100), nullable=True),
    sa.Column('specialties', sa.Text(), nullable=True),
    sa.Column('years_experience', sa.Integer(), nullable=True),
    sa.Column('languages', sa.String(length=200), nullable=True),
    sa.Column('website', sa.String(length=200), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('profile_photo', sa.String(length=500), nullable=True),
    sa.Column('total_sales', sa.Integer(), nullable=True),
    sa.Column('total_volume', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('average_dom', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('client_satisfaction', sa.Numeric(precision=3, scale=2), nullable=True),
    sa.Column('service_areas', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('agent_id')
    )
    with op.batch_alter_table('agents', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_agents_email'), ['email'], unique=True)

    op.create_table('economic_data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('indicator_name', sa.String(length=100), nullable=False),
    sa.Column('indicator_code', sa.String(length=50), nullable=False),
    sa.Column('source', sa.String(length=50), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('value', sa.Numeric(precision=15, scale=6), nullable=True),
    sa.Column('unit', sa.String(length=50), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('frequency', sa.String(length=20), nullable=True),
    sa.Column('seasonal_adjustment', sa.String(length=50), nullable=True),
    sa.Column('is_preliminary', sa.Boolean(), nullable=True),
    sa.Column('is_revised', sa.Boolean(), nullable=True),
    sa.Column('data_quality', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('economic_data', schema=None) as batch_op:
        batch_op.create_index('idx_indicator_date', ['indicator_code', 'date'], unique=False)
        batch_op.create_index('idx_name_date', ['indicator_name', 'date'], unique=False)
        batch_op.create_index('idx_source_date', ['source', 'date'], unique=False)
        batch_op.create_index(batch_op.f('ix_economic_data_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_economic_data_indicator_code'), ['indicator_code'], unique=False)
        batch_op.create_index(batch_op.f('ix_economic_data_indicator_name'), ['indicator_name'], unique=False)

    op.create_table('economic_indicators',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('indicator_code', sa.String(length=50), nullable=False),
    sa.Column('indicator_name', sa.String(length=200), nullable=False),
    sa.Column('source', sa.String(length=50), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('frequency', sa.String(length=20), nullable=True),
    sa.Column('unit', sa.String(length=50), nullable=True),
    sa.Column('seasonal_adjustment', sa.String(length=50), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('update_frequency', sa.String(length=20), nullable=True),
    sa.Column('priority', sa.Integer(), nullable=True),
    sa.Column('ml_relevance', sa.Numeric(precision=3, scale=2), nullable=True),
    sa.Column('property_impact', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('economic_indicators', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_economic_indicators_indicator_code'), ['indicator_code'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('profile_picture', sa.String(length=500), nullable=True),
    sa.Column('preferred_cities', sa.Text(), nullable=True),
    sa.Column('preferred_property_types', sa.Text(), nullable=True),
    sa.Column('price_range_min', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('price_range_max', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('agent_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('agent_id', sa.String(length=50), nullable=False),
    sa.Column('reviewer_name', sa.String(length=100), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('review_text', sa.Text(), nullable=True),
    sa.Column('transaction_type', sa.String(length=20), nullable=True),
    sa.Column('property_type', sa.String(length=50), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.agent_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('properties',
    sa.Column('listing_id', sa.String(length=50), nullable=False),
    sa.Column('mls', sa.String(length=20), nullable=True),
    sa.Column('property_type', sa.String(length=50), nullable=True),
    sa.Column('address', sa.String(length=255), nullable=True),
    sa.Column('city', sa.String(length=100), nullable=True),
    sa.Column('province', sa.String(length=50), nullable=True),
    sa.Column('postal_code', sa.String(length=10), nullable=True),
    sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
    sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
    sa.Column('sold_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('original_price', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('price_per_sqft', sa.Numeric(precision=8, scale=2), nullable=True),
    sa.Column('bedrooms', sa.Integer(), nullable=True),
    sa.Column('bathrooms', sa.Numeric(precision=3, scale=1), nullable=True),
    sa.Column('kitchens_plus', sa.Integer(), nullable=True),
    sa.Column('rooms', sa.Integer(), nullable=True),
    sa.Column('sqft', sa.Integer(), nullable=True),
    sa.Column('lot_size', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('sold_date', sa.Date(), nullable=True),
    sa.Column('dom', sa.Integer(), nullable=True),
    sa.Column('taxes', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('maintenance_fee', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('features', sa.Text(), nullable=True),
    sa.Column('community_features', sa.Text(), nullable=True),
    sa.Column('remarks', sa.Text(), nullable=True),
    sa.Column('ai_valuation', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('investment_score', sa.Numeric(precision=3, scale=2), nullable=True),
    sa.Column('risk_assessment', sa.String(length=20), nullable=True),
    sa.Column('market_trend', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('agent_id', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.agent_id'], ),
    sa.PrimaryKeyConstraint('listing_id'),
    mysql_charset='utf8mb4'
    )
    with op.batch_alter_table('properties', schema=None) as batch_op:
        batch_op.create_index('idx_date_type', ['sold_date', 'property_type'], unique=False)
        batch_op.create_index('idx_location', ['latitude', 'longitude'], unique=False)
        batch_op.create_index('idx_price_range', ['sold_price'], unique=False)
        batch_op.create_index('idx_property_search', ['city', 'property_type', 'sold_price'], unique=False)
        batch_op.create_index(batch_op.f('ix_properties_city'), ['city'], unique=False)
        batch_op.create_index(batch_op.f('ix_properties_mls'), ['mls'], unique=False)
        batch_op.create_index(batch_op.f('ix_properties_property_type'), ['property_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_properties_sold_date'), ['sold_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_properties_sold_price'), ['sold_price'], unique=False)

    op.create_table('search_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('search_query', sa.String(length=500), nullable=True),
    sa.Column('search_filters', sa.Text(), nullable=True),
    sa.Column('results_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('property_photos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.String(length=50), nullable=False),
    sa.Column('photo_url', sa.String(length=500), nullable=False),
    sa.Column('photo_type', sa.String(length=50), nullable=True),
    sa.Column('order_index', sa.Integer(), nullable=True),
    sa.Column('caption', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['listing_id'], ['properties.listing_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('property_rooms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.String(length=50), nullable=False),
    sa.Column('room_type', sa.String(length=50), nullable=True),
    sa.Column('level', sa.String(length=20), nullable=True),
    sa.Column('dimensions', sa.String(length=50), nullable=True),
    sa.Column('features', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['listing_id'], ['properties.listing_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('saved_properties',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.String(length=50), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('tags', sa.String(length=200), nullable=True),
    sa.Column('is_favorite', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['listing_id'], ['properties.listing_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'listing_id', name='unique_user_property')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('saved_properties')
    op.drop_table('property_rooms')
    op.drop_table('property_photos')
    op.drop_table('search_history')
    with op.batch_alter_table('properties', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_properties_sold_price'))
        batch_op.drop_index(batch_op.f('ix_properties_sold_date'))
        batch_op.drop_index(batch_op.f('ix_properties_property_type'))
        batch_op.drop_index(batch_op.f('ix_properties_mls'))
        batch_op.drop_index(batch_op.f('ix_properties_city'))
        batch_op.drop_index('idx_property_search')
        batch_op.drop_index('idx_price_range')
        batch_op.drop_index('idx_location')
        batch_op.drop_index('idx_date_type')

    op.drop_table('properties')
    op.drop_table('agent_reviews')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('economic_indicators', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_economic_indicators_indicator_code'))

    op.drop_table('economic_indicators')
    with op.batch_alter_table('economic_data', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_economic_data_indicator_name'))
        batch_op.drop_index(batch_op.f('ix_economic_data_indicator_code'))
        batch_op.drop_index(batch_op.f('ix_economic_data_date'))
        batch_op.drop_index('idx_source_date')
        batch_op.drop_index('idx_name_date')
        batch_op.drop_index('idx_indicator_date')

    op.drop_table('economic_data')
    with op.batch_alter_table('agents', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_agents_email'))

    op.drop_table('agents')
    # ### end Alembic commands ###
