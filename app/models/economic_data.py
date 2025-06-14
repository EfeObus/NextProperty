from app import db
from datetime import datetime
from sqlalchemy import Index

class EconomicData(db.Model):
    """Economic indicators from Bank of Canada and Statistics Canada."""
    
    __tablename__ = 'economic_data'
    
    id = db.Column(db.Integer, primary_key=True)
    indicator_name = db.Column(db.String(100), nullable=False, index=True)
    indicator_code = db.Column(db.String(50), nullable=False, index=True)
    source = db.Column(db.String(50), nullable=False)  # 'BOC' or 'STATCAN'
    
    # Data values
    date = db.Column(db.Date, nullable=False, index=True)
    value = db.Column(db.Numeric(15, 6))
    unit = db.Column(db.String(50))
    
    # Metadata
    description = db.Column(db.Text)
    frequency = db.Column(db.String(20))  # daily, weekly, monthly, quarterly, annual
    seasonal_adjustment = db.Column(db.String(50))
    
    # Data quality and status
    is_preliminary = db.Column(db.Boolean, default=False)
    is_revised = db.Column(db.Boolean, default=False)
    data_quality = db.Column(db.String(20))  # good, fair, poor
    
    # System metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('idx_indicator_date', 'indicator_code', 'date'),
        Index('idx_source_date', 'source', 'date'),
        Index('idx_name_date', 'indicator_name', 'date'),
    )
    
    def __repr__(self):
        return f'<EconomicData {self.indicator_code}: {self.date} = {self.value}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'indicator_name': self.indicator_name,
            'indicator_code': self.indicator_code,
            'source': self.source,
            'date': self.date.isoformat() if self.date else None,
            'value': float(self.value) if self.value else None,
            'unit': self.unit,
            'description': self.description,
            'frequency': self.frequency,
            'seasonal_adjustment': self.seasonal_adjustment,
            'is_preliminary': self.is_preliminary,
            'is_revised': self.is_revised,
            'data_quality': self.data_quality,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_latest_value(cls, indicator_code):
        """Get the latest value for an economic indicator."""
        return cls.query.filter_by(indicator_code=indicator_code)\
                      .order_by(cls.date.desc())\
                      .first()
    
    @classmethod
    def get_time_series(cls, indicator_code, start_date=None, end_date=None, limit=None):
        """Get time series data for an economic indicator."""
        query = cls.query.filter_by(indicator_code=indicator_code)
        
        if start_date:
            query = query.filter(cls.date >= start_date)
        if end_date:
            query = query.filter(cls.date <= end_date)
        
        query = query.order_by(cls.date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_indicators_by_source(cls, source, limit=None):
        """Get all indicators from a specific source."""
        query = cls.query.filter_by(source=source)\
                        .distinct(cls.indicator_code)\
                        .order_by(cls.indicator_name)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def bulk_upsert(cls, data_list):
        """Bulk insert or update economic data."""
        for data in data_list:
            existing = cls.query.filter_by(
                indicator_code=data['indicator_code'],
                date=data['date']
            ).first()
            
            if existing:
                # Update existing record
                for key, value in data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                new_record = cls(**data)
                db.session.add(new_record)
        
        db.session.commit()


class EconomicIndicator(db.Model):
    """Master list of economic indicators and their metadata."""
    
    __tablename__ = 'economic_indicators'
    
    id = db.Column(db.Integer, primary_key=True)
    indicator_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    indicator_name = db.Column(db.String(200), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100))  # Interest Rates, Inflation, Employment, etc.
    
    # Indicator properties
    description = db.Column(db.Text)
    frequency = db.Column(db.String(20))
    unit = db.Column(db.String(50))
    seasonal_adjustment = db.Column(db.String(50))
    
    # Data availability
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    last_updated = db.Column(db.DateTime)
    
    # Configuration
    is_active = db.Column(db.Boolean, default=True)
    update_frequency = db.Column(db.String(20))  # How often to fetch updates
    priority = db.Column(db.Integer, default=1)  # 1=high, 5=low
    
    # AI/ML relevance
    ml_relevance = db.Column(db.Numeric(3, 2))  # Relevance score for ML models
    property_impact = db.Column(db.String(20))  # high, medium, low
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EconomicIndicator {self.indicator_code}: {self.indicator_name}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'indicator_code': self.indicator_code,
            'indicator_name': self.indicator_name,
            'source': self.source,
            'category': self.category,
            'description': self.description,
            'frequency': self.frequency,
            'unit': self.unit,
            'seasonal_adjustment': self.seasonal_adjustment,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_active': self.is_active,
            'update_frequency': self.update_frequency,
            'priority': self.priority,
            'ml_relevance': float(self.ml_relevance) if self.ml_relevance else None,
            'property_impact': self.property_impact,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active_indicators(cls, source=None, category=None):
        """Get active economic indicators."""
        query = cls.query.filter_by(is_active=True)
        
        if source:
            query = query.filter_by(source=source)
        if category:
            query = query.filter_by(category=category)
        
        return query.order_by(cls.priority, cls.indicator_name).all()
    
    @classmethod
    def get_high_impact_indicators(cls):
        """Get indicators with high property impact."""
        return cls.query.filter_by(
            is_active=True,
            property_impact='high'
        ).order_by(cls.ml_relevance.desc()).all()


# Define standard economic indicator categories
ECONOMIC_CATEGORIES = {
    'INTEREST_RATES': [
        {'code': 'V80691311', 'name': 'Bank Rate', 'source': 'BOC'},
        {'code': 'V80691312', 'name': 'Prime Rate', 'source': 'BOC'},
        {'code': 'V122530', 'name': '5-Year Mortgage Rate', 'source': 'BOC'},
    ],
    'INFLATION': [
        {'code': 'V41690973', 'name': 'Consumer Price Index', 'source': 'STATCAN'},
        {'code': 'V41690914', 'name': 'Core CPI', 'source': 'STATCAN'},
    ],
    'EMPLOYMENT': [
        {'code': 'V2062815', 'name': 'Unemployment Rate', 'source': 'STATCAN'},
        {'code': 'V2057781', 'name': 'Employment Rate', 'source': 'STATCAN'},
    ],
    'HOUSING': [
        {'code': 'V735319', 'name': 'New Housing Price Index', 'source': 'STATCAN'},
        {'code': 'V53731173', 'name': 'Housing Starts', 'source': 'STATCAN'},
    ]
}
