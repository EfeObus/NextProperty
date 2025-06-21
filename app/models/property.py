from app import db
from datetime import datetime
from sqlalchemy import Index, text
from flask import current_app

class Property(db.Model):
    """Property model representing real estate listings."""
    
    __tablename__ = 'properties'
    
    # Primary key
    listing_id = db.Column(db.String(50), primary_key=True)
    
    # Basic property information
    mls = db.Column(db.String(20), index=True)
    property_type = db.Column(db.String(50), index=True)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100), index=True)
    province = db.Column(db.String(50))
    postal_code = db.Column(db.String(10))
    
    # Location coordinates
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    
    # Pricing information
    sold_price = db.Column(db.Numeric(12, 2), index=True)
    original_price = db.Column(db.Numeric(12, 2))
    price_per_sqft = db.Column(db.Numeric(8, 2))
    
    # Property features
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Numeric(3, 1))
    kitchens_plus = db.Column(db.Integer)
    rooms = db.Column(db.Integer)
    sqft = db.Column(db.Integer)
    lot_size = db.Column(db.Numeric(10, 2))
    year_built = db.Column(db.Integer, index=True)  # Year the property was built
    
    # Transaction details
    sold_date = db.Column(db.Date, index=True)
    dom = db.Column(db.Integer)  # Days on market
    taxes = db.Column(db.Numeric(10, 2))
    maintenance_fee = db.Column(db.Numeric(10, 2))
    
    # Descriptive features
    features = db.Column(db.Text)
    community_features = db.Column(db.Text)
    remarks = db.Column(db.Text)
    
    # AI-generated fields
    ai_valuation = db.Column(db.Numeric(12, 2))
    investment_score = db.Column(db.Numeric(3, 2))  # 0-10 scale
    risk_assessment = db.Column(db.String(20))  # Low, Medium, High
    market_trend = db.Column(db.String(20))  # Rising, Stable, Declining
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agent_id = db.Column(db.String(50), db.ForeignKey('agents.agent_id'))
    photos = db.relationship('PropertyPhoto', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    rooms_detail = db.relationship('PropertyRoom', backref='property', lazy='dynamic', cascade='all, delete-orphan')
    
    # Database indexes
    __table_args__ = (
        Index('idx_location', 'latitude', 'longitude'),
        Index('idx_price_range', 'sold_price'),
        Index('idx_property_search', 'city', 'property_type', 'sold_price'),
        Index('idx_date_type', 'sold_date', 'property_type'),
        # Full-text search index for MySQL
        {'mysql_charset': 'utf8mb4'}
    )
    
    def __repr__(self):
        return f'<Property {self.listing_id}: {self.address}>'
    
    @property
    def images(self):
        """Alias for photos to maintain template compatibility."""
        return self.photos.all() if self.photos else []
    
    @property
    def title(self):
        """Generate a title for the property."""
        return f"{self.address}" if self.address else f"Property {self.listing_id}"
    
    @property
    def description(self):
        """Get property description from remarks."""
        return self.remarks or "No description available"
    
    @property
    def status(self):
        """Property status - all properties are available for purchase."""
        return "Available"
    
    def to_dict(self):
        """Convert property to dictionary for JSON serialization."""
        return {
            'listing_id': self.listing_id,
            'mls': self.mls,
            'property_type': self.property_type,
            'address': self.address,
            'city': self.city,
            'province': self.province,
            'postal_code': self.postal_code,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'sold_price': float(self.sold_price) if self.sold_price else None,
            'original_price': float(self.original_price) if self.original_price else None,
            'price_per_sqft': float(self.price_per_sqft) if self.price_per_sqft else None,
            'bedrooms': self.bedrooms,
            'bathrooms': float(self.bathrooms) if self.bathrooms else None,
            'kitchens_plus': self.kitchens_plus,
            'rooms': self.rooms,
            'sqft': self.sqft,
            'lot_size': float(self.lot_size) if self.lot_size else None,
            'year_built': self.year_built,
            'sold_date': self.sold_date.isoformat() if self.sold_date else None,
            'dom': self.dom,
            'taxes': float(self.taxes) if self.taxes else None,
            'maintenance_fee': float(self.maintenance_fee) if self.maintenance_fee else None,
            'features': self.features,
            'community_features': self.community_features,
            'remarks': self.remarks,
            'ai_valuation': float(self.ai_valuation) if self.ai_valuation else None,
            'investment_score': float(self.investment_score) if self.investment_score else None,
            'risk_assessment': self.risk_assessment,
            'market_trend': self.market_trend,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_top_deal(self):
        """Check if this property qualifies as a top deal (listed below AI prediction by 5%+)."""
        if not self.ai_valuation:
            return False
            
        # Use original_price as listing price, fallback to sold_price
        listing_price = self.original_price or self.sold_price
        if not listing_price:
            return False
            
        predicted_price = float(self.ai_valuation)
        listed_price = float(listing_price)
        
        # Calculate value difference percentage
        value_diff = predicted_price - listed_price
        value_diff_percent = (value_diff / predicted_price) * 100
        
        # Property qualifies as top deal if listed price is 5%+ below prediction
        return value_diff_percent >= 5
    
    def get_deal_quality(self):
        """Get the quality rating of the deal if it's a top deal."""
        if not self.is_top_deal():
            return None
            
        listing_price = self.original_price or self.sold_price
        predicted_price = float(self.ai_valuation)
        listed_price = float(listing_price)
        
        value_diff = predicted_price - listed_price
        value_diff_percent = (value_diff / predicted_price) * 100
        
        if value_diff_percent >= 25:
            return 'excellent'
        elif value_diff_percent >= 15:
            return 'great'
        elif value_diff_percent >= 5:
            return 'good'
        else:
            return None
    
    def get_investment_potential_percent(self):
        """Get the investment potential as a percentage."""
        if not self.is_top_deal():
            return 0
            
        listing_price = self.original_price or self.sold_price
        predicted_price = float(self.ai_valuation)
        listed_price = float(listing_price)
        
        value_diff = predicted_price - listed_price
        value_diff_percent = (value_diff / predicted_price) * 100
        
        return value_diff_percent
    
    @classmethod
    def get_filtered(cls, city=None, property_type=None, min_price=None, max_price=None, 
                    limit=20, offset=0):
        """Get filtered property listings."""
        query = cls.query
        
        if city:
            query = query.filter(cls.city.ilike(f'%{city}%'))
        if property_type:
            query = query.filter(cls.property_type.ilike(f'%{property_type}%'))
        if min_price:
            query = query.filter(cls.sold_price >= min_price)
        if max_price:
            query = query.filter(cls.sold_price <= max_price)
        
        return query.order_by(cls.sold_date.desc()).offset(offset).limit(limit).all()
    
    @classmethod
    def search_properties(cls, query_text, limit=20):
        """Full-text search on property features and descriptions."""
        # MySQL full-text search
        search_query = cls.query.filter(
            db.or_(
                cls.features.contains(query_text),
                cls.community_features.contains(query_text),
                cls.remarks.contains(query_text),
                cls.address.contains(query_text)
            )
        )
        
        return search_query.limit(limit).all()
    
    @classmethod
    def get_nearby_properties(cls, latitude, longitude, radius_km=5, limit=20):
        """Get properties within a certain radius using geospatial query."""
        # Haversine formula for distance calculation
        # Approximate: 1 degree = 111 km
        lat_range = radius_km / 111.0
        lng_range = radius_km / (111.0 * abs(float(latitude)) * 0.01745)  # Adjust for latitude
        
        query = cls.query.filter(
            cls.latitude.between(float(latitude) - lat_range, float(latitude) + lat_range),
            cls.longitude.between(float(longitude) - lng_range, float(longitude) + lng_range)
        )
        
        return query.limit(limit).all()


class PropertyPhoto(db.Model):
    """Property photos model."""
    
    __tablename__ = 'property_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.String(50), db.ForeignKey('properties.listing_id'), nullable=False)
    photo_url = db.Column(db.String(500), nullable=False)
    photo_type = db.Column(db.String(50))  # exterior, interior, kitchen, bathroom, etc.
    order_index = db.Column(db.Integer, default=0)
    caption = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def url(self):
        """Alias for photo_url to maintain template compatibility."""
        return self.photo_url
    
    @property
    def image_url(self):
        """Alias for photo_url to maintain template compatibility."""
        return self.photo_url
    
    def __repr__(self):
        return f'<PropertyPhoto {self.id}: {self.listing_id}>'


class PropertyRoom(db.Model):
    """Property room details model."""
    
    __tablename__ = 'property_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.String(50), db.ForeignKey('properties.listing_id'), nullable=False)
    room_type = db.Column(db.String(50))  # bedroom, bathroom, kitchen, living room, etc.
    level = db.Column(db.String(20))  # main, upper, lower, basement
    dimensions = db.Column(db.String(50))
    features = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PropertyRoom {self.id}: {self.room_type} in {self.listing_id}>'
