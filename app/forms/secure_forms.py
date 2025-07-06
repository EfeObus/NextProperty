"""
Secure forms utilities for NextProperty AI.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, Regexp
from wtforms.widgets import TextArea, HiddenInput
from app.security.middleware import XSSProtection
import bleach


class SecureTextAreaWidget(TextArea):
    """Secure text area widget with XSS protection."""
    
    def __call__(self, field, **kwargs):
        if field.data:
            # Sanitize the data before rendering
            field.data = XSSProtection.sanitize_html(field.data)
        return super().__call__(field, **kwargs)


class SecureStringField(StringField):
    """String field with XSS protection."""
    
    def process_formdata(self, valuelist):
        if valuelist:
            # Sanitize input data
            self.data = XSSProtection.escape_html(valuelist[0]) if valuelist[0] else ''
        else:
            self.data = ''


class SecureTextAreaField(TextAreaField):
    """Text area field with XSS protection."""
    
    widget = SecureTextAreaWidget()
    
    def process_formdata(self, valuelist):
        if valuelist:
            # Sanitize HTML content but allow safe tags
            self.data = XSSProtection.sanitize_html(valuelist[0]) if valuelist[0] else ''
        else:
            self.data = ''


class PropertyUploadForm(FlaskForm):
    """Secure property upload form."""
    
    # Property details
    address = SecureStringField('Address', validators=[
        DataRequired(message="Address is required"),
        Length(min=5, max=255, message="Address must be between 5 and 255 characters")
    ])
    
    city = SecureStringField('City', validators=[
        DataRequired(message="City is required"),
        Length(min=2, max=100, message="City must be between 2 and 100 characters"),
        Regexp(r'^[a-zA-Z\s\-\'\.]+$', message="City contains invalid characters")
    ])
    
    province = SecureStringField('Province', validators=[
        DataRequired(message="Province is required"),
        Length(min=2, max=50, message="Province must be between 2 and 50 characters")
    ])
    
    postal_code = SecureStringField('Postal Code', validators=[
        DataRequired(message="Postal code is required"),
        Regexp(r'^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$', message="Invalid postal code format")
    ])
    
    property_type = SelectField('Property Type', validators=[
        DataRequired(message="Property type is required")
    ], choices=[
        ('', 'Select Property Type'),
        ('Single Family', 'Single Family'),
        ('Condo', 'Condo'),
        ('Townhouse', 'Townhouse'),
        ('Multi-Family', 'Multi-Family'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial'),
        ('Vacant Land', 'Vacant Land'),
        ('Other', 'Other')
    ])
    
    # Property specifications
    bedrooms = IntegerField('Bedrooms', validators=[
        DataRequired(message="Number of bedrooms is required"),
        NumberRange(min=0, max=20, message="Bedrooms must be between 0 and 20")
    ])
    
    bathrooms = FloatField('Bathrooms', validators=[
        DataRequired(message="Number of bathrooms is required"),
        NumberRange(min=0, max=20, message="Bathrooms must be between 0 and 20")
    ])
    
    square_feet = IntegerField('Square Feet', validators=[
        DataRequired(message="Square footage is required"),
        NumberRange(min=100, max=50000, message="Square feet must be between 100 and 50,000")
    ])
    
    lot_size = FloatField('Lot Size (sq ft)', validators=[
        Optional(),
        NumberRange(min=0, max=1000000, message="Lot size must be between 0 and 1,000,000 sq ft")
    ])
    
    year_built = IntegerField('Year Built', validators=[
        Optional(),
        NumberRange(min=1800, max=2030, message="Year built must be between 1800 and 2030")
    ])
    
    # Financial information
    listing_price = FloatField('Listing Price ($)', validators=[
        DataRequired(message="Listing price is required"),
        NumberRange(min=1000, max=100000000, message="Listing price must be between $1,000 and $100,000,000")
    ])
    
    property_taxes = FloatField('Annual Property Taxes ($)', validators=[
        Optional(),
        NumberRange(min=0, max=1000000, message="Property taxes must be between $0 and $1,000,000")
    ])
    
    # Description
    description = SecureTextAreaField('Property Description', validators=[
        Optional(),
        Length(max=5000, message="Description must be less than 5,000 characters")
    ])
    
    # Agent information
    agent_name = SecureStringField('Agent Name', validators=[
        Optional(),
        Length(max=100, message="Agent name must be less than 100 characters"),
        Regexp(r'^[a-zA-Z\s\-\'\.]+$', message="Agent name contains invalid characters")
    ])
    
    agent_email = StringField('Agent Email', validators=[
        Optional(),
        Email(message="Invalid email format"),
        Length(max=100, message="Email must be less than 100 characters")
    ])
    
    agent_phone = SecureStringField('Agent Phone', validators=[
        Optional(),
        Length(max=20, message="Phone number must be less than 20 characters"),
        Regexp(r'^[\d\s\-\(\)\.+]+$', message="Invalid phone number format")
    ])


class ContactForm(FlaskForm):
    """Secure contact form."""
    
    first_name = SecureStringField('First Name', validators=[
        DataRequired(message="First name is required"),
        Length(min=1, max=50, message="First name must be between 1 and 50 characters"),
        Regexp(r'^[a-zA-Z\s\-\']+$', message="First name contains invalid characters")
    ])
    
    last_name = SecureStringField('Last Name', validators=[
        DataRequired(message="Last name is required"),
        Length(min=1, max=50, message="Last name must be between 1 and 50 characters"),
        Regexp(r'^[a-zA-Z\s\-\']+$', message="Last name contains invalid characters")
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"),
        Email(message="Invalid email format"),
        Length(max=100, message="Email must be less than 100 characters")
    ])
    
    phone = SecureStringField('Phone', validators=[
        Optional(),
        Length(max=20, message="Phone number must be less than 20 characters"),
        Regexp(r'^[\d\s\-\(\)\.+]+$', message="Invalid phone number format")
    ])
    
    subject = SecureStringField('Subject', validators=[
        DataRequired(message="Subject is required"),
        Length(min=3, max=200, message="Subject must be between 3 and 200 characters")
    ])
    
    message = SecureTextAreaField('Message', validators=[
        DataRequired(message="Message is required"),
        Length(min=10, max=2000, message="Message must be between 10 and 2,000 characters")
    ])


class PricePredictionForm(FlaskForm):
    """Secure price prediction form."""
    
    bedrooms = IntegerField('Bedrooms', validators=[
        DataRequired(message="Number of bedrooms is required"),
        NumberRange(min=0, max=20, message="Bedrooms must be between 0 and 20")
    ])
    
    bathrooms = FloatField('Bathrooms', validators=[
        DataRequired(message="Number of bathrooms is required"),
        NumberRange(min=0, max=20, message="Bathrooms must be between 0 and 20")
    ])
    
    square_feet = IntegerField('Square Feet', validators=[
        DataRequired(message="Square footage is required"),
        NumberRange(min=100, max=50000, message="Square feet must be between 100 and 50,000")
    ])
    
    city = SecureStringField('City', validators=[
        DataRequired(message="City is required"),
        Length(min=2, max=100, message="City must be between 2 and 100 characters"),
        Regexp(r'^[a-zA-Z\s\-\'\.]+$', message="City contains invalid characters")
    ])
    
    property_type = SelectField('Property Type', validators=[
        DataRequired(message="Property type is required")
    ], choices=[
        ('', 'Select Property Type'),
        ('Single Family', 'Single Family'),
        ('Condo', 'Condo'),
        ('Townhouse', 'Townhouse'),
        ('Multi-Family', 'Multi-Family'),
        ('Commercial', 'Commercial'),
        ('Industrial', 'Industrial'),
        ('Vacant Land', 'Vacant Land'),
        ('Other', 'Other')
    ])
    
    year_built = IntegerField('Year Built', validators=[
        Optional(),
        NumberRange(min=1800, max=2030, message="Year built must be between 1800 and 2030")
    ])
    
    lot_size = FloatField('Lot Size (sq ft)', validators=[
        Optional(),
        NumberRange(min=0, max=1000000, message="Lot size must be between 0 and 1,000,000 sq ft")
    ])


def validate_form_data(form_data: dict, max_string_length: int = 1000) -> dict:
    """
    Validate and sanitize form data.
    
    Args:
        form_data: Dictionary of form data
        max_string_length: Maximum allowed string length
        
    Returns:
        dict: Sanitized form data
    """
    sanitized_data = {}
    
    for key, value in form_data.items():
        if isinstance(value, str):
            # Validate input
            if not XSSProtection.validate_input(value, max_string_length):
                raise ValueError(f"Invalid input detected in field: {key}")
            
            # Sanitize the value
            sanitized_data[key] = XSSProtection.escape_html(value)
        elif isinstance(value, (int, float, bool)):
            sanitized_data[key] = value
        elif value is None:
            sanitized_data[key] = None
        else:
            # Convert to string and sanitize
            sanitized_data[key] = XSSProtection.escape_html(str(value))
    
    return sanitized_data


def create_csrf_token_field():
    """
    Create a CSRF token hidden field.
    
    Returns:
        HiddenField: CSRF token field
    """
    return HiddenField('csrf_token', widget=HiddenInput())
