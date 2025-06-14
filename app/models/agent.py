from app import db
from datetime import datetime

class Agent(db.Model):
    """Real estate agent model."""
    
    __tablename__ = 'agents'
    
    agent_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    license_number = db.Column(db.String(50))
    
    # Professional details
    brokerage = db.Column(db.String(100))
    specialties = db.Column(db.Text)  # JSON array of specialties
    years_experience = db.Column(db.Integer)
    languages = db.Column(db.String(200))
    
    # Contact and marketing info
    website = db.Column(db.String(200))
    bio = db.Column(db.Text)
    profile_photo = db.Column(db.String(500))
    
    # Performance metrics
    total_sales = db.Column(db.Integer, default=0)
    total_volume = db.Column(db.Numeric(15, 2), default=0)
    average_dom = db.Column(db.Numeric(5, 2))  # Average days on market
    client_satisfaction = db.Column(db.Numeric(3, 2))  # Rating out of 5
    
    # Location served
    service_areas = db.Column(db.Text)  # JSON array of cities/neighborhoods
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    properties = db.relationship('Property', backref='agent', lazy='dynamic')
    
    @property
    def avatar_url(self):
        """Alias for profile_photo to maintain template compatibility."""
        return self.profile_photo
    
    @property
    def title(self):
        """Get agent title/position."""
        return 'Real Estate Agent'  # Default title
    
    def __repr__(self):
        return f'<Agent {self.agent_id}: {self.name}>'
    
    def to_dict(self):
        """Convert agent to dictionary for JSON serialization."""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'license_number': self.license_number,
            'brokerage': self.brokerage,
            'specialties': self.specialties,
            'years_experience': self.years_experience,
            'languages': self.languages,
            'website': self.website,
            'bio': self.bio,
            'profile_photo': self.profile_photo,
            'total_sales': self.total_sales,
            'total_volume': float(self.total_volume) if self.total_volume else None,
            'average_dom': float(self.average_dom) if self.average_dom else None,
            'client_satisfaction': float(self.client_satisfaction) if self.client_satisfaction else None,
            'service_areas': self.service_areas,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_top_agents(cls, limit=10, order_by='total_volume'):
        """Get top performing agents."""
        if order_by == 'total_volume':
            return cls.query.filter(cls.is_active == True).order_by(cls.total_volume.desc()).limit(limit).all()
        elif order_by == 'total_sales':
            return cls.query.filter(cls.is_active == True).order_by(cls.total_sales.desc()).limit(limit).all()
        elif order_by == 'satisfaction':
            return cls.query.filter(cls.is_active == True).order_by(cls.client_satisfaction.desc()).limit(limit).all()
        else:
            return cls.query.filter(cls.is_active == True).limit(limit).all()
    
    def get_properties_count(self):
        """Get count of properties listed by this agent."""
        return self.properties.count()
    
    def get_recent_properties(self, limit=5):
        """Get recent properties listed by this agent."""
        return self.properties.order_by(Property.created_at.desc()).limit(limit).all()
    
    def calculate_performance_metrics(self):
        """Calculate and update agent performance metrics."""
        from sqlalchemy import func
        from app.models.property import Property
        
        # Calculate metrics from sold properties
        metrics = db.session.query(
            func.count(Property.listing_id).label('total_sales'),
            func.sum(Property.sold_price).label('total_volume'),
            func.avg(Property.dom).label('average_dom')
        ).filter(
            Property.agent_id == self.agent_id,
            Property.sold_price.isnot(None)
        ).first()
        
        if metrics and metrics.total_sales > 0:
            self.total_sales = metrics.total_sales
            self.total_volume = metrics.total_volume or 0
            self.average_dom = metrics.average_dom
            
            db.session.commit()
            
        return {
            'total_sales': self.total_sales,
            'total_volume': float(self.total_volume) if self.total_volume else 0,
            'average_dom': float(self.average_dom) if self.average_dom else 0
        }


class AgentReview(db.Model):
    """Agent reviews and ratings model."""
    
    __tablename__ = 'agent_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(50), db.ForeignKey('agents.agent_id'), nullable=False)
    reviewer_name = db.Column(db.String(100))
    rating = db.Column(db.Integer)  # 1-5 stars
    review_text = db.Column(db.Text)
    transaction_type = db.Column(db.String(20))  # buy, sell, rent
    property_type = db.Column(db.String(50))
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    agent = db.relationship('Agent', backref=db.backref('reviews', lazy='dynamic'))
    
    def __repr__(self):
        return f'<AgentReview {self.id}: {self.rating} stars for {self.agent_id}>'
    
    def to_dict(self):
        """Convert review to dictionary."""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'reviewer_name': self.reviewer_name,
            'rating': self.rating,
            'review_text': self.review_text,
            'transaction_type': self.transaction_type,
            'property_type': self.property_type,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
