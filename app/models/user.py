from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import jwt
from flask import current_app

class User(UserMixin, db.Model):
    """User model for authentication and user management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    profile_picture = db.Column(db.String(500))
    
    # User preferences
    preferred_cities = db.Column(db.Text)  # JSON array
    preferred_property_types = db.Column(db.Text)  # JSON array
    price_range_min = db.Column(db.Numeric(12, 2))
    price_range_max = db.Column(db.Numeric(12, 2))
    
    # User role and permissions
    role = db.Column(db.String(20), default='user')  # user, agent, admin
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Account status
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    saved_properties = db.relationship('SavedProperty', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    search_history = db.relationship('SearchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'profile_picture': self.profile_picture,
            'preferred_cities': self.preferred_cities,
            'preferred_property_types': self.preferred_property_types,
            'price_range_min': float(self.price_range_min) if self.price_range_min else None,
            'price_range_max': float(self.price_range_max) if self.price_range_max else None,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def generate_token(self, expires_in=3600):
        """Generate JWT token for user."""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.utcnow().timestamp() + expires_in
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user."""
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            return User.query.get(user_id)
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def update_login_info(self):
        """Update login information."""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        db.session.commit()
    
    def has_permission(self, permission):
        """Check if user has specific permission."""
        permissions = {
            'user': ['view_properties', 'save_properties', 'search_properties'],
            'agent': ['view_properties', 'save_properties', 'search_properties', 'manage_listings'],
            'admin': ['view_properties', 'save_properties', 'search_properties', 'manage_listings', 'manage_users', 'view_analytics']
        }
        return permission in permissions.get(self.role, [])


class SavedProperty(db.Model):
    """Saved properties for users."""
    
    __tablename__ = 'saved_properties'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    listing_id = db.Column(db.String(50), db.ForeignKey('properties.listing_id'), nullable=False)
    notes = db.Column(db.Text)
    tags = db.Column(db.String(200))  # Comma-separated tags
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    property = db.relationship('Property', backref='saved_by_users')
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'listing_id', name='unique_user_property'),)
    
    def __repr__(self):
        return f'<SavedProperty {self.user_id}: {self.listing_id}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'listing_id': self.listing_id,
            'notes': self.notes,
            'tags': self.tags,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'property': self.property.to_dict() if self.property else None
        }


class SearchHistory(db.Model):
    """User search history for analytics and recommendations."""
    
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    search_query = db.Column(db.String(500))
    search_filters = db.Column(db.Text)  # JSON of search filters
    results_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchHistory {self.user_id}: {self.search_query}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'search_query': self.search_query,
            'search_filters': self.search_filters,
            'results_count': self.results_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
