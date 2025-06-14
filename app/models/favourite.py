from app import db
from datetime import datetime

class Favourite(db.Model):
    """User favourite properties - enhanced version."""
    
    __tablename__ = 'favourites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.String(50), db.ForeignKey('properties.listing_id'), nullable=False)
    
    # Enhanced fields
    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated tags
    priority = db.Column(db.Integer, default=0)  # 1=High, 2=Medium, 3=Low, 0=None
    
    # Tracking fields
    view_count = db.Column(db.Integer, default=0)
    last_viewed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='favourites')
    property = db.relationship('Property', backref='favourited_by')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'listing_id', name='unique_user_favourite'),
    )
    
    def __repr__(self):
        return f'<Favourite {self.user_id}: {self.listing_id}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'listing_id': self.listing_id,
            'notes': self.notes,
            'tags': self.tags.split(',') if self.tags else [],
            'priority': self.priority,
            'view_count': self.view_count,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'property': self.property.to_dict() if self.property else None
        }
    
    def add_view(self):
        """Increment view count and update last viewed timestamp."""
        self.view_count += 1
        self.last_viewed = datetime.utcnow()
        db.session.commit()