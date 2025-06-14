"""
Data processing components for ETL pipeline.
Handles data validation, transformation, and mapping between CSV and database models.
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal, InvalidOperation
import logging
from dataclasses import dataclass

from app.models.property import Property
from app.models.agent import Agent
from app.models.economic_data import EconomicIndicator

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Dict[str, Any]


class DataValidator:
    """Validate and clean incoming data."""
    
    def __init__(self):
        self.validation_rules = {
            'minimal': self._minimal_validation,
            'standard': self._standard_validation,
            'strict': self._strict_validation
        }
    
    def validate_batch(
        self,
        batch_data: List[Dict],
        validation_level: str = 'standard'
    ) -> Dict[str, Any]:
        """Validate a batch of records."""
        
        validator = self.validation_rules.get(validation_level, self._standard_validation)
        
        valid_records = []
        errors = []
        
        for i, record in enumerate(batch_data):
            try:
                result = validator(record)
                if result.is_valid:
                    valid_records.append(result.cleaned_data)
                else:
                    errors.append({
                        'record_index': i,
                        'record_id': record.get('property_id', record.get('ListingID', f'row_{i}')),
                        'errors': result.errors,
                        'warnings': result.warnings
                    })
            except Exception as e:
                errors.append({
                    'record_index': i,
                    'record_id': record.get('property_id', f'row_{i}'),
                    'errors': [f"Validation exception: {str(e)}"],
                    'warnings': []
                })
        
        return {
            'valid_records': valid_records,
            'invalid_records': len(batch_data) - len(valid_records),
            'errors': errors
        }
    
    def _minimal_validation(self, record: Dict) -> ValidationResult:
        """Minimal validation - only check required fields."""
        errors = []
        warnings = []
        cleaned_data = record.copy()
        
        # Check for required fields
        required_fields = ['property_id', 'ListingID', 'PostID']
        if not any(field in record for field in required_fields):
            errors.append("Missing required identifier field")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data
        )
    
    def _standard_validation(self, record: Dict) -> ValidationResult:
        """Standard validation with data cleaning."""
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Validate and clean each field
        try:
            # Required identifier
            listing_id = None
            if 'property_id' in record and record['property_id'] is not None and not pd.isna(record['property_id']):
                listing_id = str(record['property_id']).strip()
            elif 'ListingID' in record and record['ListingID'] is not None and not pd.isna(record['ListingID']):
                listing_id = str(record['ListingID']).strip()
            elif 'PostID' in record and record['PostID'] is not None and not pd.isna(record['PostID']):
                listing_id = str(record['PostID']).strip()
            
            if not listing_id or listing_id == 'NULL':
                errors.append("Missing required identifier field")
            else:
                cleaned_data['listing_id'] = listing_id
            
            # Property type
            if 'PropertyType' in record and record['PropertyType'] is not None and not pd.isna(record['PropertyType']):
                cleaned_data['property_type'] = self._clean_property_type(record['PropertyType'])
            
            # Address components
            if 'StreetAddress' in record:
                cleaned_data['address'] = self._clean_address(record['StreetAddress'])
            
            if 'City' in record:
                cleaned_data['city'] = self._clean_text(record['City'])
            
            if 'Province' in record:
                cleaned_data['province'] = self._clean_text(record['Province'])
            
            if 'PostalCode' in record:
                cleaned_data['postal_code'] = self._clean_postal_code(record['PostalCode'])
            
            # Coordinates
            if 'Latitude' in record:
                lat = self._clean_decimal(record['Latitude'])
                if lat and -90 <= lat <= 90:
                    cleaned_data['latitude'] = lat
                elif lat:
                    warnings.append(f"Invalid latitude: {lat}")
            
            if 'Longitude' in record:
                lon = self._clean_decimal(record['Longitude'])
                if lon and -180 <= lon <= 180:
                    cleaned_data['longitude'] = lon
                elif lon:
                    warnings.append(f"Invalid longitude: {lon}")
            
            # Price information
            if 'Price' in record:
                price = self._clean_price(record['Price'])
                if price and price > 0:
                    cleaned_data['sold_price'] = price
                elif price is not None:
                    warnings.append(f"Invalid price: {record['Price']}")
            
            # Property features
            if 'BedroomsTotal' in record:
                bedrooms = self._clean_integer(record['BedroomsTotal'])
                if bedrooms is not None and 0 <= bedrooms <= 20:
                    cleaned_data['bedrooms'] = bedrooms
            
            if 'BathroomTotal' in record:
                bathrooms = self._clean_decimal(record['BathroomTotal'])
                if bathrooms is not None and 0 <= bathrooms <= 20:
                    cleaned_data['bathrooms'] = bathrooms
            
            # Size information
            if 'SizeInterior' in record:
                sqft = self._extract_square_feet(record['SizeInterior'])
                if sqft and sqft > 0:
                    cleaned_data['sqft'] = sqft
            
            # Lot size
            if 'SizeTotal' in record:
                lot_size = self._extract_lot_size(record['SizeTotal'])
                if lot_size and lot_size > 0:
                    cleaned_data['lot_size'] = lot_size
            
            # Text fields
            if 'PublicRemarks' in record:
                cleaned_data['remarks'] = self._clean_text(record['PublicRemarks'])
            
            if 'Features' in record:
                cleaned_data['features'] = self._clean_text(record['Features'])
            
            if 'CommunityFeatures' in record:
                cleaned_data['community_features'] = self._clean_text(record['CommunityFeatures'])
            
            # Maintenance fee
            if 'MaintenanceFee' in record:
                fee = self._clean_price(record['MaintenanceFee'])
                if fee and fee >= 0:
                    cleaned_data['maintenance_fee'] = fee
            
            # Add metadata
            cleaned_data['created_at'] = datetime.utcnow()
            cleaned_data['updated_at'] = datetime.utcnow()
            
        except Exception as e:
            errors.append(f"Data cleaning error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data
        )
    
    def _strict_validation(self, record: Dict) -> ValidationResult:
        """Strict validation with comprehensive checks."""
        result = self._standard_validation(record)
        
        # Additional strict checks
        if result.is_valid:
            # Require minimum essential fields
            required_fields = ['listing_id', 'property_type', 'city', 'province']
            missing_required = [field for field in required_fields if field not in result.cleaned_data]
            
            if missing_required:
                result.errors.extend([f"Missing required field: {field}" for field in missing_required])
                result.is_valid = False
            
            # Validate data consistency
            if 'sold_price' in result.cleaned_data and result.cleaned_data['sold_price'] < 10000:
                result.errors.append("Price too low (< $10,000)")
                result.is_valid = False
            
            if 'sqft' in result.cleaned_data and result.cleaned_data['sqft'] < 100:
                result.warnings.append("Very small square footage (< 100 sqft)")
        
        return result
    
    def _clean_property_type(self, value: str) -> str:
        """Clean and normalize property type."""
        if not value or pd.isna(value):
            return None
        
        # Convert to string if not already
        value = str(value).strip()
        if not value or value == 'NULL' or value == 'None':
            return None
        
        # Map common variations
        type_mapping = {
            'single family': 'House',
            'detached': 'House',
            'townhouse': 'Townhouse',
            'condo': 'Condo',
            'condominium': 'Condo',
            'apartment': 'Condo',
            'vacant land': 'Vacant Land',
            'commercial': 'Commercial',
            'industrial': 'Industrial'
        }
        
        cleaned = value.lower().strip()
        return type_mapping.get(cleaned, value.title())
    
    def _clean_address(self, value: str) -> str:
        """Clean address string."""
        if not value or pd.isna(value) or value == 'NULL':
            return None
        
        # Convert to string if not already
        value = str(value).strip()
        if not value:
            return None
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(value.split())
        
        # Remove common prefixes/suffixes that shouldn't be in address
        cleaned = re.sub(r'^(LOT\s+\d+\s+)', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned[:255]  # Limit length
    
    def _clean_text(self, value: str) -> str:
        """Clean general text fields."""
        if not value or pd.isna(value) or value == 'NULL':
            return None
        
        # Convert to string if not already
        value = str(value).strip()
        if not value:
            return None
        
        # Remove extra whitespace
        cleaned = ' '.join(value.split())
        
        # Remove control characters
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
        
        return cleaned if cleaned else None
    
    def _clean_postal_code(self, value: str) -> str:
        """Clean and validate postal code."""
        if not value or pd.isna(value):
            return None
        
        # Convert to string and remove spaces, convert to uppercase
        cleaned = re.sub(r'\s+', '', str(value).upper())
        if not cleaned or cleaned == 'NULL':
            return None
        
        # Canadian postal code pattern
        if re.match(r'^[A-Z]\d[A-Z]\d[A-Z]\d$', cleaned):
            return cleaned
        
        # US ZIP code pattern
        if re.match(r'^\d{5}(-\d{4})?$', cleaned):
            return cleaned
        
        return cleaned[:10]  # Return as-is but limit length
    
    def _clean_decimal(self, value: Union[str, int, float]) -> Optional[Decimal]:
        """Clean and convert to decimal."""
        if value is None or value == '' or value == 'NULL' or pd.isna(value):
            return None
        
        try:
            # Remove non-numeric characters except decimal point and minus
            if isinstance(value, str):
                cleaned = re.sub(r'[^\d.-]', '', value)
                if not cleaned or cleaned == '-':
                    return None
                value = cleaned
            
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
    
    def _clean_integer(self, value: Union[str, int, float]) -> Optional[int]:
        """Clean and convert to integer."""
        if value is None or value == '' or value == 'NULL' or pd.isna(value):
            return None
        
        try:
            if isinstance(value, str):
                # Extract first number from string
                match = re.search(r'\d+', value)
                if match:
                    return int(match.group())
                return None
            
            return int(float(value))  # Handle float strings
        except (ValueError, TypeError):
            return None
    
    def _clean_price(self, value: Union[str, int, float]) -> Optional[Decimal]:
        """Clean price values."""
        if value is None or value == '' or value == 'NULL' or value == '0.00' or pd.isna(value):
            return None
        
        try:
            # Remove currency symbols and commas
            if isinstance(value, str):
                cleaned = re.sub(r'[$,\s]', '', value)
                if not cleaned:
                    return None
                value = cleaned
            
            price = Decimal(str(value))
            return price if price > 0 else None
        except (InvalidOperation, ValueError):
            return None
    
    def _extract_square_feet(self, value: str) -> Optional[int]:
        """Extract square footage from size string."""
        if not value or pd.isna(value):
            return None
        
        # Convert to string if not already
        value = str(value).strip()
        if not value or value == 'NULL':
            return None
        
        # Look for patterns like "1500 sqft", "1,500", etc.
        patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft\.?|sqft|square\s+feet)',
            r'(\d{1,3}(?:,\d{3})*)\s*$',  # Just numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, value, re.IGNORECASE)
            if match:
                try:
                    sqft = int(match.group(1).replace(',', ''))
                    if 100 <= sqft <= 50000:  # Reasonable range
                        return sqft
                except ValueError:
                    continue
        
        return None
    
    def _extract_lot_size(self, value: str) -> Optional[Decimal]:
        """Extract lot size from size string."""
        if not value or pd.isna(value):
            return None
        
        # Convert to string if not already
        value = str(value).strip()
        if not value or value == 'NULL':
            return None
        
        # Look for acreage
        acre_match = re.search(r'([\d.]+)\s*ac', value, re.IGNORECASE)
        if acre_match:
            try:
                acres = Decimal(acre_match.group(1))
                if 0 < acres <= 1000:  # Reasonable range
                    return acres
            except InvalidOperation:
                pass
        
        # Look for square footage
        sqft_match = re.search(r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft\.?|sqft)', value, re.IGNORECASE)
        if sqft_match:
            try:
                sqft = int(sqft_match.group(1).replace(',', ''))
                if sqft > 0:
                    return Decimal(sqft) / Decimal('43560')  # Convert to acres
            except (ValueError, InvalidOperation):
                pass
        
        return None


class DataMapper:
    """Map data between different formats and schemas."""
    
    # CSV column to database field mappings
    PROPERTY_FIELD_MAPPING = {
        'property_id': 'listing_id',
        'PostID': 'listing_id',
        'ListingID': 'listing_id',
        'DdfListingID': 'mls',
        'PropertyType': 'property_type',
        'StreetAddress': 'address',
        'City': 'city',
        'Province': 'province',
        'PostalCode': 'postal_code',
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Price': 'sold_price',
        'BedroomsTotal': 'bedrooms',
        'BathroomTotal': 'bathrooms',
        'SizeInterior': 'sqft',
        'SizeTotal': 'lot_size',
        'PublicRemarks': 'remarks',
        'Features': 'features',
        'CommunityFeatures': 'community_features',
        'MaintenanceFee': 'maintenance_fee'
    }
    
    def map_csv_to_property(self, csv_record: Dict[str, Any]) -> Dict[str, Any]:
        """Map CSV record to Property model fields."""
        mapped_record = {}
        
        # Ensure we have a listing_id (required field)
        listing_id = None
        for id_field in ['property_id', 'PostID', 'ListingID']:
            if id_field in csv_record and csv_record[id_field]:
                listing_id = str(csv_record[id_field]).strip()
                break
        
        if not listing_id:
            raise ValueError("No valid listing_id found in record")
            
        mapped_record['listing_id'] = listing_id
        
        # Map other fields
        for csv_field, db_field in self.PROPERTY_FIELD_MAPPING.items():
            if csv_field in csv_record and csv_record[csv_field] is not None:
                value = csv_record[csv_field]
                
                # Clean and convert the value based on the target field
                try:
                    if db_field in ['latitude', 'longitude', 'sold_price', 'maintenance_fee']:
                        # Convert to decimal/numeric
                        if value and str(value).strip() not in ['', 'NULL', 'None', 'null']:
                            value = float(str(value).replace(',', '').strip())
                        else:
                            continue  # Skip NULL values for numeric fields
                    elif db_field in ['lot_size']:
                        # Special handling for lot size which may have text descriptions
                        value = self._extract_numeric_from_text(value)
                        if value is None:
                            continue
                    elif db_field in ['sqft']:
                        # Special handling for square footage which may have text descriptions
                        value = self._extract_numeric_from_text(value)
                        if value is None:
                            continue
                        value = int(value)  # Convert to integer
                    elif db_field in ['bedrooms']:
                        # Convert to integer
                        if value and str(value).strip() not in ['', 'NULL', 'None', 'null']:
                            value = int(float(str(value).replace(',', '').strip()))
                        else:
                            continue  # Skip NULL values for integer fields
                    elif db_field in ['bathrooms']:
                        # Convert to float for decimal places
                        if value and str(value).strip() not in ['', 'NULL', 'None', 'null']:
                            value = float(str(value).replace(',', '').strip())
                        else:
                            continue  # Skip NULL values for float fields
                    else:
                        # String fields - handle NULL values
                        if value and str(value).strip() not in ['', 'NULL', 'None', 'null']:
                            value = str(value).strip()
                        else:
                            continue  # Skip NULL values for string fields
                    
                    if value is not None and value != '':
                        mapped_record[db_field] = value
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert field {csv_field} value '{value}': {e}")
        
        # Add timestamps
        mapped_record['created_at'] = datetime.utcnow()
        mapped_record['updated_at'] = datetime.utcnow()
        
        return mapped_record

    def _extract_numeric_from_text(self, text: str) -> Optional[float]:
        """Extract numeric value from text like '0.63 ac|1/2 - 1 acre' or '300 sqft'."""
        if not text or str(text).strip() in ['', 'NULL', 'None', 'null']:
            return None
        
        import re
        # Look for decimal numbers at the start of the string
        match = re.search(r'^([\d.]+)', str(text).strip())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None


class PropertyDataProcessor:
    """Process property data for ETL operations."""
    
    model_class = Property
    
    def __init__(self):
        self.data_mapper = DataMapper()
        self.ai_valuation_service = None  # Will be initialized when needed
    
    def transform_batch(self, batch_data: List[Dict]) -> List[Dict]:
        """Transform batch of property records."""
        transformed_records = []
        
        for record in batch_data:
            try:
                # Map CSV fields to database fields
                mapped_record = self.data_mapper.map_csv_to_property(record)
                
                # Add AI-generated fields (placeholder for now)
                mapped_record.update(self._generate_ai_fields(mapped_record))
                
                transformed_records.append(mapped_record)
                
            except Exception as e:
                logger.warning(f"Failed to transform record {record.get('listing_id', 'unknown')}: {e}")
                continue
        
        return transformed_records
    
    def _generate_ai_fields(self, record: Dict) -> Dict:
        """Generate AI-enhanced fields for property."""
        # Placeholder for AI valuation and scoring
        # In production, this would call actual ML models
        
        ai_fields = {}
        
        # Simple price-based valuation (placeholder)
        if 'sold_price' in record and record['sold_price']:
            price = float(record['sold_price'])  # Convert to float first
            # Simple market adjustment (placeholder)
            ai_fields['ai_valuation'] = Decimal(str(price * 1.05))
            
            # Simple investment score based on price range
            if price < 300000:
                ai_fields['investment_score'] = Decimal('7.5')
            elif price < 600000:
                ai_fields['investment_score'] = Decimal('6.0')
            else:
                ai_fields['investment_score'] = Decimal('5.0')
        
        # Risk assessment based on property type and location
        property_type = record.get('property_type', '') or ''
        property_type_lower = property_type.lower()
        if 'condo' in property_type_lower:
            ai_fields['risk_assessment'] = 'Medium'
        elif 'house' in property_type_lower:
            ai_fields['risk_assessment'] = 'Low'
        else:
            ai_fields['risk_assessment'] = 'High'
        
        # Market trend (placeholder)
        ai_fields['market_trend'] = 'Stable'
        
        return ai_fields


class AgentDataProcessor:
    """Process agent data for ETL operations."""
    
    model_class = Agent
    
    def transform_batch(self, batch_data: List[Dict]) -> List[Dict]:
        """Transform batch of agent records."""
        # Placeholder for agent data processing
        return batch_data


class EconomicDataProcessor:
    """Process economic data for ETL operations."""
    
    model_class = EconomicIndicator
    
    def transform_batch(self, batch_data: List[Dict]) -> List[Dict]:
        """Transform batch of economic data records."""
        # Placeholder for economic data processing
        return batch_data
