import numpy as np
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from flask import current_app
from app.models.property import Property
from app.models.economic_data import EconomicData
from app.extensions import cache
import json
import logging
import warnings
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def suppress_sklearn_warnings():
    """Context manager to suppress sklearn feature name warnings."""
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='.*does not have valid feature names.*')
        warnings.filterwarnings('ignore', message='.*feature names.*')
        warnings.filterwarnings('ignore', message='.*X has feature names.*')
        warnings.filterwarnings('ignore', message='.*X does not have valid feature names.*')
        warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')
        warnings.filterwarnings('ignore', category=UserWarning)
        yield

class MLService:
    """Machine learning service for property analysis and predictions."""
    
    def __init__(self):
        self.model_path = None
        self.models = {}
        self.feature_columns = []
        self._models_loaded = False
        self._economic_cache = {}
        self._economic_cache_time = None
        self._economic_cache_ttl = 3600  # 1 hour cache
        self._use_economic_features = False  # Temporarily disabled until model retrained
    
    def _safe_float(self, value, default=0.0):
        """
        Safely convert any value (including Decimal) to float.
        This prevents the decimal/float division errors.
        """
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError, AttributeError):
            return default
    
    def _load_models(self):
        """Load trained ML models."""
        if self._models_loaded:
            return
            
        try:
            # Get absolute paths to avoid working directory issues
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Try to import current_app only when needed
            try:
                from flask import current_app
                model_path = current_app.config.get('MODEL_PATH', 'models/trained_models/')
                if not os.path.isabs(model_path):
                    model_path = os.path.join(base_dir, model_path)
            except RuntimeError:
                # Outside of app context, use default path
                model_path = os.path.join(base_dir, 'models/trained_models/')
            
            # Ensure model directory exists
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model directory not found: {model_path}")
            
            # Try loading models in order of preference
            model_files = [
                ('property_price_model.pkl', 'Property valuation'),
                ('xgboost_price_model.pkl', 'XGBoost valuation'),
                ('gradientboosting_price_model.pkl', 'GradientBoosting valuation'),
                ('randomforest_price_model.pkl', 'RandomForest valuation'),
                ('lightgbm_price_model.pkl', 'LightGBM valuation')
            ]
            
            model_loaded = False
            for model_file, model_name in model_files:
                model_file_path = os.path.join(model_path, model_file)
                if os.path.exists(model_file_path):
                    try:
                        # Test load the model with a dummy prediction to catch KeyError issues
                        test_model = joblib.load(model_file_path)
                        
                        # Create a test feature array with the expected 26 features
                        test_features = np.array([[3, 2, 1500, 0.25, 7, 50, 10, 3, 2010, 2025, 6, 30, 5000, 
                                                 5.0, 7.2, 6.5, 2.3, 5.2, 1.37, 1.8, 0.5, 0.0, 0.3, 0.5, 0.6, 0.4]])
                        
                        # Test prediction
                        _ = test_model.predict(test_features)
                        
                        # If we get here, the model works
                        self.models['valuation'] = test_model
                        logger.info(f"{model_name} model loaded and tested successfully")
                        model_loaded = True
                        break
                        
                    except Exception as model_error:
                        logger.warning(f"Failed to load {model_name} model: {type(model_error).__name__}: {model_error}")
                        continue
            
            if not model_loaded:
                logger.error("No working valuation models found - using fallback pricing")
                # Set a flag to use fallback pricing instead of raising an error
                self.models['valuation'] = None
            
            # Load feature columns
            feature_path = os.path.join(base_dir, 'models/model_artifacts/feature_columns.json')
            if os.path.exists(feature_path):
                with open(feature_path, 'r') as f:
                    self.feature_columns = json.load(f)
                logger.info("Feature columns loaded successfully")
            else:
                logger.warning(f"Feature columns file not found: {feature_path}")
                # Set default feature columns
                self.feature_columns = [
                    'size_sqft', 'bedrooms', 'bathrooms', 'lot_size', 'age',
                    'property_type_encoded', 'city_encoded', 'neighbourhood_encoded'
                ]
            
            self._models_loaded = True
            logger.info("ML models loaded successfully")
            
        except Exception as e:
            error_msg = f"Error loading ML models: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Current working directory: {os.getcwd()}")
            logger.error(f"Base directory: {base_dir if 'base_dir' in locals() else 'Not set'}")
            logger.error(f"Model path: {model_path if 'model_path' in locals() else 'Not set'}")
            print(error_msg)  # Keep for backward compatibility
    
    def _get_economic_indicators(self) -> Dict[str, float]:
        """Fetch current economic indicators with caching."""
        try:
            # Check cache first
            now = datetime.now()
            if (self._economic_cache_time and 
                self._economic_cache and
                (now - self._economic_cache_time).seconds < self._economic_cache_ttl):
                return self._economic_cache
            
            # Try to get from external APIs service first
            try:
                from app.services.external_apis import ExternalAPIsService
                economic_summary = ExternalAPIsService.get_latest_economic_summary()
                
                # Extract key indicators
                indicators = {}
                
                # Bank of Canada indicators
                if hasattr(economic_summary, 'bank_rate'):
                    indicators['policy_rate'] = float(economic_summary.bank_rate)
                if hasattr(economic_summary, 'prime_rate'):
                    indicators['prime_rate'] = float(economic_summary.prime_rate)
                if hasattr(economic_summary, 'inflation_rate'):
                    indicators['inflation_rate'] = float(economic_summary.inflation_rate)
                if hasattr(economic_summary, 'cad_usd_rate'):
                    indicators['exchange_rate'] = float(economic_summary.cad_usd_rate)
                
                # Get additional indicators from database
                try:
                    # Mortgage rate
                    mortgage_data = EconomicData.get_latest_value('V80691335')  # 5-year mortgage
                    if mortgage_data:
                        indicators['mortgage_5yr'] = float(mortgage_data.value)
                    
                    # Unemployment rate
                    unemployment_data = EconomicData.get_latest_value('3579270')  # Unemployment rate
                    if unemployment_data:
                        indicators['unemployment_rate'] = float(unemployment_data.value)
                    
                    # GDP growth
                    gdp_data = EconomicData.get_time_series('65201210', limit=8)  # GDP quarterly
                    if len(gdp_data) >= 4:
                        # Calculate year-over-year GDP growth
                        latest_gdp = float(gdp_data[0].value)
                        year_ago_gdp = float(gdp_data[3].value) if len(gdp_data) > 3 else latest_gdp
                        gdp_growth = ((latest_gdp - year_ago_gdp) / year_ago_gdp) * 100 if year_ago_gdp != 0 else 0
                        indicators['gdp_growth'] = gdp_growth
                        
                except Exception as db_error:
                    logger.warning(f"Could not fetch from database: {db_error}")
                
            except Exception as api_error:
                logger.warning(f"External API not available: {api_error}")
                indicators = {}
            
            # Fill in defaults for missing indicators
            default_indicators = {
                'policy_rate': 5.0,           # Bank of Canada overnight rate
                'prime_rate': 7.2,            # Prime rate
                'mortgage_5yr': 6.5,          # 5-year mortgage rate
                'inflation_rate': 2.3,        # Inflation rate
                'unemployment_rate': 5.2,     # Unemployment rate
                'exchange_rate': 1.37,        # CAD/USD
                'gdp_growth': 1.8,           # GDP growth %
            }
            
            # Use fetched values or defaults
            for key, default_value in default_indicators.items():
                if key not in indicators:
                    indicators[key] = default_value
            
            # Calculate derived economic features
            indicators['interest_rate_environment'] = self._calculate_interest_environment(indicators)
            indicators['economic_momentum'] = self._calculate_economic_momentum(indicators)
            indicators['affordability_pressure'] = self._calculate_affordability_pressure(indicators)
            
            # Cache the results
            self._economic_cache = indicators
            self._economic_cache_time = now
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error fetching economic indicators: {str(e)}")
            # Return defaults if everything fails
            return {
                'policy_rate': 5.0,
                'prime_rate': 7.2,
                'mortgage_5yr': 6.5,
                'inflation_rate': 2.3,
                'unemployment_rate': 5.2,
                'exchange_rate': 1.37,
                'gdp_growth': 1.8,
                'interest_rate_environment': 0.5,  # neutral
                'economic_momentum': 0.0,  # stable
                'affordability_pressure': 0.3,  # moderate
            }
    
    def _calculate_interest_environment(self, indicators: Dict[str, float]) -> float:
        """Calculate interest rate environment score (0=low, 1=high)."""
        policy_rate = indicators.get('policy_rate', 5.0)
        
        # Normalize based on historical ranges (0-8%)
        if policy_rate <= 1.0:
            return 0.0  # Very low
        elif policy_rate <= 3.0:
            return 0.25  # Low
        elif policy_rate <= 5.0:
            return 0.5  # Moderate
        elif policy_rate <= 7.0:
            return 0.75  # High
        else:
            return 1.0  # Very high
    
    def _calculate_economic_momentum(self, indicators: Dict[str, float]) -> float:
        """Calculate economic momentum (-1=declining, 0=stable, 1=growing)."""
        gdp_growth = indicators.get('gdp_growth', 2.0)
        unemployment = indicators.get('unemployment_rate', 5.0)
        
        # GDP component
        gdp_score = 0.0
        if gdp_growth > 3.0:
            gdp_score = 1.0
        elif gdp_growth > 1.0:
            gdp_score = 0.5
        elif gdp_growth < 0:
            gdp_score = -1.0
        
        # Employment component (lower unemployment = better)
        employment_score = 0.0
        if unemployment < 4.0:
            employment_score = 1.0
        elif unemployment < 6.0:
            employment_score = 0.5
        elif unemployment > 8.0:
            employment_score = -1.0
        
        # Combined momentum
        return (gdp_score + employment_score) / 2
    
    def _calculate_affordability_pressure(self, indicators: Dict[str, float]) -> float:
        """Calculate affordability pressure (0=easy, 1=very difficult)."""
        mortgage_rate = indicators.get('mortgage_5yr', 6.0)
        inflation_rate = indicators.get('inflation_rate', 2.0)
        
        # Mortgage rate pressure
        rate_pressure = min(mortgage_rate / 8.0, 1.0)  # Normalize to 8% max
        
        # Inflation pressure
        inflation_pressure = min(max(inflation_rate - 2.0, 0) / 5.0, 1.0)  # Above 2% target
        
        # Combined pressure
        return (rate_pressure * 0.7 + inflation_pressure * 0.3)
    
    def analyze_property(self, property):
        """Comprehensive AI analysis of a property."""
        # Load models if not already loaded
        self._load_models()
        
        try:
            analysis = {
                'listing_id': property.listing_id,
                'predicted_price': None,
                'investment_score': None,
                'risk_level': 'Medium',
                'market_trend': 'Stable',
                'comparables': [],
                'insights': []
            }
            
            # Get property features for ML model
            features = self._extract_features(property)
            
            # Predict property value
            if 'valuation' in self.models and self.models['valuation'] is not None and features is not None:
                try:
                    with suppress_sklearn_warnings():
                        predicted_price = self.models['valuation'].predict([features])[0]
                        analysis['predicted_price'] = float(predicted_price)
                except Exception as model_error:
                    logger.warning(f"Model prediction failed in analyze_property: {model_error}")
                    # Use statistical fallback
                    property_dict = {
                        'bedrooms': property.bedrooms,
                        'bathrooms': property.bathrooms,
                        'square_feet': property.sqft,
                        'city': property.city,
                        'property_type': property.property_type
                    }
                    analysis['predicted_price'] = self._statistical_price_prediction(property_dict)
            else:
                # Use statistical fallback when no model available
                property_dict = {
                    'bedrooms': property.bedrooms,
                    'bathrooms': property.bathrooms,
                    'square_feet': property.sqft,
                    'city': property.city,
                    'property_type': property.property_type
                }
                analysis['predicted_price'] = self._statistical_price_prediction(property_dict)
                
            # Compare with actual/listed price
            if property.sold_price and analysis['predicted_price']:
                predicted_price = analysis['predicted_price']
                price_diff = (predicted_price - self._safe_float(property.sold_price)) / self._safe_float(property.sold_price)
                if abs(price_diff) < 0.05:  # Within 5%
                    analysis['insights'].append("AI valuation closely matches sold price")
                elif price_diff > 0.1:  # AI values higher
                    analysis['insights'].append("Property may have been undervalued")
                elif price_diff < -0.1:  # AI values lower
                    analysis['insights'].append("Property may have been overvalued")
            
            # Calculate investment score
            analysis['investment_score'] = self._calculate_investment_score(property, features)
            
            # Assess risk level
            analysis['risk_level'] = self._assess_risk_level(property, features)
            
            # Determine market trend
            analysis['market_trend'] = self._get_market_trend(property.city, property.property_type)
            
            # Find comparable properties
            analysis['comparables'] = self._find_comparable_properties(property)
            
            # Generate insights
            analysis['insights'].extend(self._generate_insights(property, features))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in property analysis: {str(e)}")
            return {
                'listing_id': property.listing_id,
                'predicted_price': None,
                'confidence': 0.0,
                'insights': [f"Analysis error: {str(e)}"],
                'investment_score': 0.0,
                'risk_level': 'unknown'
            }
            
    @cache.memoize(timeout=1800)  # Cache for 30 minutes
    def get_top_properties(self, limit: int = 10, location: str = None, property_type: str = None, offset: int = 0) -> List[Dict]:
        """
        Get top properties where listed price is below AI prediction (undervalued opportunities).
        This method focuses on currently available properties for investment.
        
        Args:
            limit: Number of properties to return
            location: Filter by city/location
            property_type: Filter by property type
            offset: Number of properties to skip for pagination
            
        Returns:
            List of undervalued properties with analysis
        """
        self._load_models()
        
        try:
            from app import db
            
            # Build optimized query with indexes
            query = Property.query.filter(
                db.and_(
                    db.or_(
                        Property.original_price.isnot(None),
                        Property.sold_price.isnot(None)
                    ),
                    db.or_(
                        Property.original_price >= 100000,
                        Property.sold_price >= 100000
                    ),
                    db.or_(
                        Property.original_price <= 10000000,
                        Property.sold_price <= 10000000
                    ),
                    Property.ai_valuation.isnot(None)  # Only properties with AI predictions
                )
            )
            
            if location:
                query = query.filter(Property.city.ilike(f'%{location}%'))
            if property_type:
                query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
                
            # Limit initial query to reduce processing time
            properties = query.limit(200).all()  # Reduced from 500
            
            top_properties = []
            
            for property in properties:
                try:
                    # Get AI analysis
                    analysis = self.analyze_property(property)
                    
                    # Use listing price (original_price) if available, otherwise use sold_price
                    actual_price = None
                    if property.original_price and property.original_price > 0:
                        actual_price = self._safe_float(property.original_price)
                    elif property.sold_price and property.sold_price > 0:
                        actual_price = self._safe_float(property.sold_price)
                    
                    if not actual_price:
                        continue
                    
                    # If ML prediction failed, use statistical fallback
                    predicted_price = analysis.get('predicted_price')
                    if not predicted_price:
                        # Statistical fallback: use price per sqft and investment score
                        if property.sqft and property.sqft > 0:
                            # Average price per sqft for the area/type
                            avg_price_per_sqft = 250 if property.property_type in ['Condo', 'Apartment'] else 200
                            predicted_price = property.sqft * avg_price_per_sqft
                        else:
                            # Last resort: use a multiplier based on investment score
                            predicted_price = actual_price * 1.15  # Assume 15% potential
                    
                    # Ensure prediction is reasonable
                    if predicted_price < 50000 or predicted_price > 20000000:
                        continue
                    
                    # Additional validation: ensure the difference is reasonable
                    price_ratio = predicted_price / actual_price
                    if price_ratio > 5.0:  # Skip if prediction is more than 5x the actual price
                        continue
                    
                    # Calculate value difference (how much below prediction)
                    value_diff = predicted_price - actual_price
                    value_diff_percent = (value_diff / predicted_price) * 100
                    
                    # More lenient criteria: include properties with any positive potential (0-50%)
                    if 0 <= value_diff_percent <= 50:
                        investment_score = analysis.get('investment_score', 0.5)
                        
                        top_properties.append({
                            'property': property,
                            'analysis': analysis,
                            'actual_price': actual_price,
                            'predicted_price': predicted_price,
                            'value_difference': value_diff,
                            'value_difference_percent': value_diff_percent,
                            'investment_potential': self._calculate_investment_potential(
                                value_diff_percent, investment_score
                            )
                        })
                except Exception as e:
                    print(f"Error processing property {property.listing_id}: {e}")
                    continue
            
            # Sort by value difference percentage (highest undervaluation first)
            top_properties.sort(key=lambda x: x['value_difference_percent'], reverse=True)
            
            # Apply pagination
            start_index = offset
            end_index = offset + limit
            return top_properties[start_index:end_index]
            
        except Exception as e:
            print(f"Error getting top properties: {str(e)}")
            return []
    
    def get_top_properties_count(self, location: str = None, property_type: str = None) -> int:
        """
        Get total count of top properties (undervalued properties) for pagination.
        
        Args:
            location: Filter by city/location
            property_type: Filter by property type
            
        Returns:
            Total count of undervalued properties
        """
        self._load_models()
        
        try:
            from app import db
            
            # Build query for properties with realistic price filters
            query = Property.query.filter(
                db.or_(
                    Property.original_price.isnot(None),
                    Property.sold_price.isnot(None)
                )
            ).filter(
                db.or_(
                    Property.original_price >= 100000,
                    Property.sold_price >= 100000
                )
            ).filter(
                db.or_(
                    Property.original_price <= 10000000,
                    Property.sold_price <= 10000000
                )
            )
            
            if location:
                query = query.filter(Property.city.ilike(f'%{location}%'))
            if property_type:
                query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
                
            # Get properties for analysis
            properties = query.limit(500).all()  # Analyze up to 500 properties
            
            count = 0
            
            for property in properties:
                # Get AI analysis
                analysis = self.analyze_property(property)
                
                if analysis['predicted_price']:
                    # Use listing price (original_price) if available, otherwise use sold_price
                    actual_price = None
                    if property.original_price and property.original_price > 0:
                        actual_price = self._safe_float(property.original_price)
                    elif property.sold_price and property.sold_price > 0:
                        actual_price = self._safe_float(property.sold_price)
                    
                    if actual_price:
                        predicted_price = analysis['predicted_price']
                        
                        # Additional validation: ensure predictions and ratios are reasonable
                        if predicted_price < 50000 or predicted_price > 20000000:
                            continue
                        
                        price_ratio = predicted_price / actual_price
                        if price_ratio > 5.0:
                            continue
                        
                        # Calculate value difference (how much below prediction)
                        value_diff = predicted_price - actual_price
                        value_diff_percent = (value_diff / predicted_price) * 100
                        
                        # Only count properties that are undervalued by 5-50% (reasonable range)
                        if 5 <= value_diff_percent <= 50:
                            count += 1
            
            return count
            
        except Exception as e:
            print(f"Error getting top properties count: {str(e)}")
            return 0
    
    def _calculate_investment_potential(self, value_diff_percent: float, investment_score: float) -> float:
        """Calculate investment potential based on undervaluation and other factors."""
        if value_diff_percent >= 20 and investment_score >= 7:
            return 10.0  # Excellent
        elif value_diff_percent >= 15 and investment_score >= 6:
            return 8.0   # Very Good
        elif value_diff_percent >= 10 and investment_score >= 5:
            return 6.0   # Good
        elif value_diff_percent >= 5:
            return 4.0   # Fair
        else:
            return 2.0   # Poor
    
    def predict_property_price(self, property_features: Dict) -> Dict[str, Any]:
        """
        Predict property price using ML model or statistical approach.
        
        Args:
            property_features: Dictionary containing property features
            
        Returns:
            Prediction results with confidence interval
        """
        self._load_models()
        
        try:
            # Extract features for the model
            features = self._extract_features_from_dict(property_features)
            
            if features is None:
                return {
                    'predicted_price': None,
                    'confidence_interval': None,
                    'error': 'Could not extract features from input'
                }
            
            predicted_price = None
            
            # Try to use trained model first
            if 'valuation' in self.models:
                try:
                    # Use context manager to suppress sklearn warnings
                    with suppress_sklearn_warnings():
                        # Convert features to DataFrame with proper column names to avoid sklearn warnings
                        import pandas as pd
                        feature_columns = self._get_feature_columns()
                        
                        if len(features) == len(feature_columns):
                            # Create DataFrame with proper column names for sklearn compatibility
                            features_df = pd.DataFrame([features], columns=feature_columns)
                            
                            # Check if model has preprocessing pipeline (StandardScaler, etc.)
                            model = self.models['valuation']
                            
                            # Always use DataFrame to avoid feature name warnings
                            predicted_price = model.predict(features_df)[0]
                        else:
                            logger.warning(f"Feature mismatch: got {len(features)}, expected {len(feature_columns)}")
                            # Fallback to array prediction with warning suppression
                            predicted_price = self.models['valuation'].predict([features])[0]
                        
                except Exception as model_error:
                    logger.error(f"Model prediction failed: {str(model_error)}")
                    predicted_price = None
            
            # If model fails or doesn't exist, use statistical approach
            if predicted_price is None:
                predicted_price = self._statistical_price_prediction(property_features)
            
            # Ensure reasonable price range
            if predicted_price < 50000:
                predicted_price = 50000
            elif predicted_price > 20000000:
                predicted_price = 20000000
            
            # Calculate confidence interval
            confidence_range = predicted_price * 0.15  # ±15% confidence interval
            confidence_score = 0.75  # Default confidence
            
            # Adjust confidence based on data availability
            if 'valuation' in self.models:
                confidence_score = 0.85
            
            return {
                'predicted_price': float(predicted_price),
                'confidence': confidence_score,
                'confidence_interval': {
                    'lower': float(predicted_price - confidence_range),
                    'upper': float(predicted_price + confidence_range)
                },
                'model_version': '1.1',
                'features_used': len(features) if isinstance(features, list) else 'unknown',
                'prediction_method': 'ml_model' if 'valuation' in self.models else 'statistical'
            }
            
        except Exception as e:
            logger.error(f"Price prediction error: {str(e)}")
            return {
                'predicted_price': None,
                'confidence_interval': None,
                'error': f'Prediction failed: {str(e)}'
            }
    
    def _statistical_price_prediction(self, property_features: Dict) -> float:
        """
        Statistical approach to price prediction when ML model is not available.
        """
        try:
            from app import db
            
            # Base price calculation
            bedrooms = property_features.get('bedrooms', 3)
            bathrooms = property_features.get('bathrooms', 2)
            sqft = property_features.get('square_feet', 1500)
            city = property_features.get('city', 'Toronto').lower()
            property_type = property_features.get('property_type', 'Detached')
            
            # Base price per sqft by city (rough estimates)
            city_multipliers = {
                'toronto': 800,
                'vancouver': 900,
                'calgary': 400,
                'ottawa': 500,
                'montreal': 450,
                'edmonton': 350,
                'winnipeg': 300,
                'hamilton': 600,
                'kitchener': 550,
                'london': 400
            }
            
            base_price_per_sqft = city_multipliers.get(city, 500)
            
            # Property type multipliers
            type_multipliers = {
                'detached': 1.2,
                'semi-detached': 1.0,
                'townhouse': 0.9,
                'condo': 0.8,
                'apartment': 0.7
            }
            
            type_multiplier = type_multipliers.get(property_type.lower(), 1.0)
            
            # Calculate base price
            base_price = sqft * base_price_per_sqft * type_multiplier
            
            # Adjustments for bedrooms and bathrooms
            bedroom_adjustment = (bedrooms - 3) * 15000
            bathroom_adjustment = (bathrooms - 2) * 10000
            
            # Year built adjustment
            year_built = property_features.get('year_built')
            age_adjustment = 0
            if year_built:
                current_year = 2025
                age = current_year - year_built
                if age > 50:
                    age_adjustment = -50000
                elif age > 20:
                    age_adjustment = -20000
                elif age < 5:
                    age_adjustment = 30000
            
            # Lot size adjustment (for detached/semi-detached)
            lot_adjustment = 0
            lot_size = property_features.get('lot_size', 0)
            if lot_size and property_type.lower() in ['detached', 'semi-detached']:
                if lot_size > 6000:
                    lot_adjustment = 50000
                elif lot_size > 4000:
                    lot_adjustment = 25000
            
            # Calculate final price
            predicted_price = base_price + bedroom_adjustment + bathroom_adjustment + age_adjustment + lot_adjustment
            
            # Add some market variability
            import random
            market_variation = random.uniform(0.9, 1.1)
            predicted_price *= market_variation
            
            return max(predicted_price, 50000)  # Minimum price
            
        except Exception as e:
            logger.error(f"Statistical prediction error: {str(e)}")
            # Fallback calculation
            sqft = property_features.get('square_feet', 1500)
            return max(sqft * 500, 200000)  # Very basic fallback
    
    def get_market_predictions(self, city: str = None, property_type: str = None) -> Dict[str, Any]:
        """
        Get market trend predictions for a specific area/property type.
        
        Args:
            city: City to analyze
            property_type: Property type to analyze
            
        Returns:
            Market prediction analysis
        """
        try:
            from app import db
            from sqlalchemy import func
            
            # Build query for recent sales
            query = Property.query.filter(
                Property.sold_price.isnot(None),
                Property.sold_date >= (datetime.now() - timedelta(days=365))
            )
            
            if city:
                query = query.filter(Property.city.ilike(f'%{city}%'))
            if property_type:
                query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
            
            # Get price trends over time
            recent_properties = query.order_by(Property.sold_date.desc()).limit(100).all()
            
            if len(recent_properties) < 10:
                return {
                    'trend': 'Insufficient data',
                    'avg_price': None,
                    'price_change_6m': None,
                    'price_change_1y': None,
                    'sample_size': len(recent_properties)
                }
            
            # Calculate average prices for different periods
            now = datetime.now()
            six_months_ago = now - timedelta(days=180)
            one_year_ago = now - timedelta(days=365)
            
            # Convert datetime to date for comparison
            six_months_ago_date = six_months_ago.date()
            one_year_ago_date = one_year_ago.date()
            
            recent_avg = np.mean([self._safe_float(p.sold_price) for p in recent_properties[:30]])
            six_month_avg = np.mean([
                self._safe_float(p.sold_price) for p in recent_properties 
                if p.sold_date and p.sold_date >= six_months_ago_date
            ])
            one_year_avg = np.mean([self._safe_float(p.sold_price) for p in recent_properties])
            
            # Calculate trends
            price_change_6m = ((recent_avg - six_month_avg) / six_month_avg * 100) if six_month_avg > 0 else 0
            price_change_1y = ((recent_avg - one_year_avg) / one_year_avg * 100) if one_year_avg > 0 else 0
            
            # Determine trend
            if price_change_6m > 5:
                trend = 'Rising'
            elif price_change_6m < -5:
                trend = 'Declining'
            else:
                trend = 'Stable'
            
            return {
                'trend': trend,
                'avg_price': recent_avg,
                'price_change_6m': price_change_6m,
                'price_change_1y': price_change_1y,
                'sample_size': len(recent_properties),
                'analysis_date': now.isoformat()
            }
            
        except Exception as e:
            print(f"Error getting market predictions: {str(e)}")
            return {
                'trend': 'Error',
                'error': str(e)
            }

    def _get_feature_columns(self) -> List[str]:
        """Get the expected feature column names for the model."""
        if self.feature_columns:
            return self.feature_columns
        else:
            # Return default feature names if not loaded from file
            return [
                "bedrooms", "bathrooms", "square_feet", "lot_size", "rooms",
                "city_encoded", "province_encoded", "property_type_encoded",
                "year_built", "current_year", "current_month", "dom", "taxes",
                "policy_rate", "prime_rate", "mortgage_rate", "inflation_rate",
                "unemployment_rate", "exchange_rate", "gdp_growth",
                "interest_environment", "economic_momentum", "affordability_pressure",
                "property_affordability", "economic_sensitivity", "market_timing"
            ]
    
    def get_model_metadata(self) -> Dict[str, Any]:
        """Get metadata about the currently loaded model."""
        try:
            metadata_path = os.path.join(os.path.dirname(__file__), 
                                       '../../models/model_artifacts/model_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading model metadata: {str(e)}")
            return {}

    def validate_model_performance(self) -> Dict[str, Any]:
        """Validate the current model's performance metrics."""
        try:
            metadata = self.get_model_metadata()
            if not metadata:
                return {'status': 'no_metadata', 'message': 'No model metadata found'}
            
            performance = metadata.get('model_performance', {})
            training_info = metadata.get('training_info', {})
            
            # Performance thresholds
            min_r2 = 0.6
            max_rmse = 500000  # $500k
            max_mape = 20.0    # 20%
            
            validation_results = {
                'status': 'valid',
                'model_name': metadata.get('best_model', 'unknown'),
                'performance': performance,
                'training_date': training_info.get('training_date'),
                'checks': {}
            }
            
            # Validate R² score
            r2_score = performance.get('r2_score', 0)
            validation_results['checks']['r2_check'] = {
                'value': r2_score,
                'threshold': min_r2,
                'passed': r2_score >= min_r2
            }
            
            # Validate RMSE
            rmse = performance.get('rmse', float('inf'))
            validation_results['checks']['rmse_check'] = {
                'value': rmse,
                'threshold': max_rmse,
                'passed': rmse <= max_rmse
            }
            
            # Validate MAPE
            mape = performance.get('mape', float('inf'))
            validation_results['checks']['mape_check'] = {
                'value': mape,
                'threshold': max_mape,
                'passed': mape <= max_mape
            }
            
            # Overall validation
            all_checks_passed = all(check['passed'] for check in validation_results['checks'].values())
            if not all_checks_passed:
                validation_results['status'] = 'performance_issues'
                validation_results['message'] = 'Model performance below acceptable thresholds'
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating model performance: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def get_available_models(self) -> List[str]:
        """Get list of available trained models."""
        try:
            model_dir = os.path.join(os.path.dirname(__file__), '../../models/trained_models')
            if not os.path.exists(model_dir):
                return []
            
            models = []
            for file in os.listdir(model_dir):
                if file.endswith('.pkl'):
                    model_name = file.replace('.pkl', '').replace('_price_model', '')
                    models.append(model_name)
            
            return models
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return []

    def switch_model(self, model_name: str) -> bool:
        """Switch to a different trained model."""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 
                                    f'../../models/trained_models/{model_name.lower()}_price_model.pkl')
            
            if not os.path.exists(model_path):
                # Try alternative naming
                model_path = os.path.join(os.path.dirname(__file__), 
                                        f'../../models/trained_models/{model_name}_price_model.pkl')
                
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
            
            # Load the new model
            new_model = joblib.load(model_path)
            self.models['valuation'] = new_model
            logger.info(f"Successfully switched to model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching to model {model_name}: {str(e)}")
            return False

    def get_model_comparison(self) -> Dict[str, Any]:
        """Get performance comparison of all available models."""
        try:
            metadata = self.get_model_metadata()
            if not metadata:
                return {}
            
            all_models = metadata.get('all_models_performance', {})
            comparison = {
                'models': all_models,
                'best_model': metadata.get('best_model'),
                'ranking': sorted(all_models.items(), key=lambda x: x[1].get('r2', 0), reverse=True)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error getting model comparison: {str(e)}")
            return {}

    def retrain_recommended(self) -> bool:
        """Check if model retraining is recommended based on age and performance."""
        try:
            metadata = self.get_model_metadata()
            if not metadata:
                return True  # No metadata means old model
            
            training_info = metadata.get('training_info', {})
            training_date_str = training_info.get('training_date')
            
            if not training_date_str:
                return True
            
            from datetime import datetime, timedelta
            training_date = datetime.fromisoformat(training_date_str.replace('Z', '+00:00'))
            days_since_training = (datetime.now() - training_date).days
            
            # Recommend retraining if:
            # 1. Model is older than 30 days
            # 2. Performance is below thresholds
            validation = self.validate_model_performance()
            
            age_threshold = days_since_training > 30
            performance_issues = validation.get('status') == 'performance_issues'
            
            return age_threshold or performance_issues
            
        except Exception as e:
            logger.error(f"Error checking retrain recommendation: {str(e)}")
            return True

    def _calculate_investment_score(self, property, features=None) -> float:
        """Calculate investment score for a property (0-10 scale)."""
        try:
            score = 5.0  # Base score
            
            # Location score (based on city)
            location_scores = {
                'toronto': 8.5, 'vancouver': 8.0, 'ottawa': 7.5, 'calgary': 7.0,
                'montreal': 7.5, 'hamilton': 7.0, 'kitchener': 6.5, 'london': 6.0,
                'edmonton': 6.0, 'winnipeg': 5.5
            }
            city_score = location_scores.get(property.city.lower() if property.city else '', 6.0)
            score += (city_score - 6.0) * 0.3  # Weight location
            
            # Property type preference
            type_scores = {
                'detached': 0.5, 'semi-detached': 0.3, 'townhouse': 0.2,
                'condo': 0.0, 'apartment': -0.2
            }
            type_score = type_scores.get(property.property_type.lower() if property.property_type else '', 0.0)
            score += type_score
            
            # Size factor
            if property.sqft:
                if property.sqft > 2500:
                    score += 0.5
                elif property.sqft > 2000:
                    score += 0.3
                elif property.sqft < 1000:
                    score -= 0.3
            
            # Age factor
            if hasattr(property, 'year_built') and property.year_built:
                age = 2025 - property.year_built
                if age < 10:
                    score += 0.4
                elif age < 20:
                    score += 0.2
                elif age > 50:
                    score -= 0.3
            
            # Market conditions (economic indicators)
            economic_indicators = self._get_economic_indicators()
            interest_environment = economic_indicators.get('interest_rate_environment', 0.5)
            economic_momentum = economic_indicators.get('economic_momentum', 0.0)
            
            # Lower interest rates = better investment opportunity
            score += (1.0 - interest_environment) * 0.5
            # Positive economic momentum = better opportunity
            score += economic_momentum * 0.3
            
            # Days on market (if available)
            if hasattr(property, 'dom') and property.dom:
                if property.dom > 60:
                    score += 0.3  # May be undervalued
                elif property.dom < 7:
                    score -= 0.2  # May be overpriced
            
            # Ensure score is within bounds
            return max(0.0, min(10.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating investment score: {str(e)}")
            return 5.0  # Default neutral score

    def _assess_risk_level(self, property, features=None) -> str:
        """Assess risk level for property investment."""
        try:
            risk_score = 0  # Start neutral
            
            # Location risk
            high_risk_cities = ['winnipeg', 'edmonton']
            low_risk_cities = ['toronto', 'vancouver', 'ottawa']
            
            if property.city and property.city.lower() in high_risk_cities:
                risk_score += 1
            elif property.city and property.city.lower() in low_risk_cities:
                risk_score -= 1
            
            # Property type risk
            if property.property_type:
                if property.property_type.lower() in ['condo', 'apartment']:
                    risk_score += 1  # Higher risk due to fees/market volatility
                elif property.property_type.lower() == 'detached':
                    risk_score -= 1  # Lower risk, more stable
            
            # Economic conditions risk
            economic_indicators = self._get_economic_indicators()
            interest_environment = economic_indicators.get('interest_rate_environment', 0.5)
            affordability_pressure = economic_indicators.get('affordability_pressure', 0.5)
            
            if interest_environment > 0.7:  # High interest rates
                risk_score += 1
            if affordability_pressure > 0.6:  # High affordability pressure
                risk_score += 1
            
            # Age risk
            if hasattr(property, 'year_built') and property.year_built:
                age = 2025 - property.year_built
                if age > 40:
                    risk_score += 1  # Older properties may need more maintenance
            
            # Market timing risk
            if hasattr(property, 'dom') and property.dom:
                if property.dom > 90:
                    risk_score += 1  # Long time on market suggests issues
            
            # Classify risk level
            if risk_score <= -2:
                return 'Very Low'
            elif risk_score <= 0:
                return 'Low'
            elif risk_score <= 2:
                return 'Medium'
            elif risk_score <= 4:
                return 'High'
            else:
                return 'Very High'
                
        except Exception as e:
            logger.error(f"Error assessing risk level: {str(e)}")
            return 'Medium'  # Default

    def _get_market_trend(self, city: str, property_type: str) -> str:
        """Get market trend for specific city and property type."""
        try:
            from app import db
            
            # Get recent sales data
            query = Property.query.filter(
                Property.sold_price.isnot(None),
                Property.sold_date >= (datetime.now() - timedelta(days=180))
            )
            
            if city:
                query = query.filter(Property.city.ilike(f'%{city}%'))
            if property_type:
                query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
            
            recent_sales = query.order_by(Property.sold_date.desc()).limit(50).all()
            
            if len(recent_sales) < 10:
                return 'Insufficient Data'
            
            # Calculate price trend
            prices = [self._safe_float(p.sold_price) for p in recent_sales]
            recent_avg = np.mean(prices[:15])  # Last 15 sales
            older_avg = np.mean(prices[-15:])  # Older 15 sales
            
            price_change = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            
            if price_change > 5:
                return 'Rising'
            elif price_change < -5:
                return 'Declining'
            else:
                return 'Stable'
                
        except Exception as e:
            logger.error(f"Error getting market trend: {str(e)}")
            return 'Stable'

    def _find_comparable_properties(self, property) -> List[Dict]:
        """Find comparable properties for analysis."""
        try:
            from app import db
            
            # Build query for comparable properties
            query = Property.query.filter(
                Property.sold_price.isnot(None),
                Property.listing_id != property.listing_id
            )
            
            # Filter by location
            if property.city:
                query = query.filter(Property.city.ilike(f'%{property.city}%'))
            
            # Filter by property type
            if property.property_type:
                query = query.filter(Property.property_type.ilike(f'%{property.property_type}%'))
            
            # Filter by size (within 20% range)
            if property.sqft and property.sqft > 0:
                size_range = property.sqft * 0.2
                query = query.filter(
                    Property.sqft >= (property.sqft - size_range),
                    Property.sqft <= (property.sqft + size_range)
                )
            
            # Filter by bedrooms (within 1 bedroom)
            if property.bedrooms:
                query = query.filter(
                    Property.bedrooms >= (property.bedrooms - 1),
                    Property.bedrooms <= (property.bedrooms + 1)
                )
            
            # Get recent sales (last 6 months)
            recent_date = datetime.now() - timedelta(days=180)
            query = query.filter(Property.sold_date >= recent_date)
            
            # Get top 5 comparables
            comparables = query.order_by(Property.sold_date.desc()).limit(5).all()
            
            comparable_list = []
            for comp in comparables:
                comparable_list.append({
                    'listing_id': comp.listing_id,
                    'address': f"{comp.address}, {comp.city}" if comp.address and comp.city else 'Address not available',
                    'sold_price': self._safe_float(comp.sold_price),
                    'sqft': comp.sqft,
                    'bedrooms': comp.bedrooms,
                    'bathrooms': comp.bathrooms,
                    'sold_date': comp.sold_date.isoformat() if comp.sold_date else None,
                    'price_per_sqft': self._safe_float(comp.sold_price) / self._safe_float(comp.sqft) if comp.sqft and comp.sqft > 0 else None
                })
            
            return comparable_list
            
        except Exception as e:
            logger.error(f"Error finding comparable properties: {str(e)}")
            return []

    def _generate_insights(self, property, features=None) -> List[str]:
        """Generate AI insights about the property."""
        try:
            insights = []
            
            # Economic insights
            economic_indicators = self._get_economic_indicators()
            interest_environment = economic_indicators.get('interest_rate_environment', 0.5)
            economic_momentum = economic_indicators.get('economic_momentum', 0.0)
            affordability_pressure = economic_indicators.get('affordability_pressure', 0.5)
            
            # Interest rate insights
            if interest_environment > 0.7:
                insights.append("High interest rate environment may suppress demand")
            elif interest_environment < 0.3:
                insights.append("Low interest rate environment supports strong demand")
            
            # Economic momentum insights
            if economic_momentum > 0.5:
                insights.append("Strong economic growth supports real estate values")
            elif economic_momentum < -0.3:
                insights.append("Economic headwinds may impact property values")
            
            # Affordability insights
            if affordability_pressure > 0.7:
                insights.append("High affordability pressure may limit buyer pool")
            elif affordability_pressure < 0.3:
                insights.append("Good affordability conditions support market activity")
            
            # Property-specific insights
            if property.sqft:
                avg_sqft_for_type = {
                    'detached': 2200, 'semi-detached': 1800, 'townhouse': 1600,
                    'condo': 1200, 'apartment': 1000
                }
                avg_size = avg_sqft_for_type.get(property.property_type.lower() if property.property_type else '', 1500)
                
                if property.sqft > avg_size * 1.2:
                    insights.append(f"Above-average size for {property.property_type} in this market")
                elif property.sqft < avg_size * 0.8:
                    insights.append(f"Below-average size for {property.property_type} in this market")
            
            # Location insights
            if property.city:
                city = property.city.lower()
                if city in ['toronto', 'vancouver']:
                    insights.append("Prime location with strong long-term appreciation potential")
                elif city in ['ottawa', 'montreal']:
                    insights.append("Stable government/employment base supports real estate")
                elif city in ['calgary', 'edmonton']:
                    insights.append("Energy sector influence on local real estate market")
            
            # Market timing insights
            current_month = datetime.now().month
            if current_month in [5, 6, 7]:  # Spring/summer market
                insights.append("Listed during peak selling season")
            elif current_month in [11, 12, 1]:  # Winter market
                insights.append("Listed during slower winter market")
            
            # Days on market insights
            if hasattr(property, 'dom') and property.dom:
                if property.dom > 60:
                    insights.append("Extended time on market may indicate pricing or condition issues")
                elif property.dom < 7:
                    insights.append("Quick sale suggests strong demand or competitive pricing")
            
            # Age and condition insights
            if hasattr(property, 'year_built') and property.year_built:
                age = 2025 - property.year_built
                if age < 5:
                    insights.append("New construction with modern features and lower maintenance")
                elif age > 30:
                    insights.append("Mature property may require updates or renovations")
            
            return insights[:5]  # Limit to top 5 insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return ["Analysis completed with basic parameters"]

    def _extract_features_from_dict(self, property_features: Dict) -> List[float]:
        """
        Extract 26 features from property dictionary for ML model prediction.
        This method converts a property features dictionary to the expected 26 feature array.
        
        Args:
            property_features: Dictionary containing property features
            
        Returns:
            List of 26 features or None if extraction fails
        """
        try:
            features = []
            
            # Helper function to safely get float values
            def safe_float(value, default):
                if value is None or value == '':
                    return float(default)
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return float(default)
            
            # Get current economic indicators
            economic_indicators = self._get_economic_indicators()
            
            # 1-5: Basic property features
            features.extend([
                safe_float(property_features.get('bedrooms'), 3),
                safe_float(property_features.get('bathrooms'), 2.0),
                safe_float(property_features.get('square_feet'), 1500),
                safe_float(property_features.get('lot_size'), 0.25),
                safe_float(property_features.get('rooms'), 7)
            ])
            
            # 6: City encoding (simplified hash-based encoding)
            city = property_features.get('city', 'Toronto')
            city_encoded = hash(city) % 100 if city else 0
            features.append(float(city_encoded))
            
            # 7: Province encoding
            province_mapping = {
                'ON': 10, 'QC': 20, 'BC': 30, 'AB': 40, 'MB': 50, 
                'SK': 60, 'NS': 70, 'NB': 80, 'NL': 90, 'PE': 100
            }
            province = property_features.get('province', 'ON')
            province_encoded = province_mapping.get(province, 10)
            features.append(float(province_encoded))
            
            # 8: Property type encoding
            type_mapping = {
                'Condo': 1, 'Townhouse': 2, 'Detached': 3, 
                'Semi-Detached': 4, 'Apartment': 5
            }
            property_type = property_features.get('property_type', 'Detached')
            type_encoded = type_mapping.get(property_type, 3)
            features.append(float(type_encoded))
            
            # 9-11: Temporal features
            year_built = safe_float(property_features.get('year_built'), 2010)
            current_year = 2025
            current_month = 6
            features.extend([
                year_built,
                float(current_year),
                float(current_month)
            ])
            
            # 12-13: Market features
            dom = safe_float(property_features.get('dom'), 30)
            taxes = safe_float(property_features.get('taxes'), 5000)
            features.extend([
                dom,
                taxes
            ])
            
            # 14-20: Economic features (7 features)
            features.extend([
                safe_float(economic_indicators.get('policy_rate'), 5.0),           # 14: Bank of Canada rate
                safe_float(economic_indicators.get('prime_rate'), 7.2),            # 15: Prime rate
                safe_float(economic_indicators.get('mortgage_5yr'), 6.5),          # 16: 5-year mortgage rate
                safe_float(economic_indicators.get('inflation_rate'), 2.3),        # 17: Current inflation
                safe_float(economic_indicators.get('unemployment_rate'), 5.2),     # 18: Unemployment rate
                safe_float(economic_indicators.get('exchange_rate'), 1.37),         # 19: CAD/USD
                safe_float(economic_indicators.get('gdp_growth'), 1.8),           # 20: GDP growth
            ])
            
            # 21-23: Derived economic features (3 features)
            features.extend([
                safe_float(economic_indicators.get('interest_rate_environment'), 0.5),  # 21: Interest rate environment
                safe_float(economic_indicators.get('economic_momentum'), 0.0),     # 22: Economic momentum
                safe_float(economic_indicators.get('affordability_pressure'), 0.3), # 23: Affordability pressure
            ])
            
            # 24: Property affordability (1 feature)
            sqft = safe_float(property_features.get('square_feet'), 1500)
            mortgage_rate = safe_float(economic_indicators.get('mortgage_5yr'), 6.5)
            inflation_rate = safe_float(economic_indicators.get('inflation_rate'), 2.3)
            property_affordability = self._calculate_property_affordability(
                sqft, mortgage_rate, inflation_rate
            )
            features.append(property_affordability)
            
            # 25: Property economic sensitivity (1 feature)
            property_econ_sensitivity = self._calculate_property_economic_sensitivity(
                property_type, economic_indicators
            )
            features.append(property_econ_sensitivity)
            
            # 26: Market timing indicator (1 feature)
            market_timing = self._calculate_market_timing(economic_indicators)
            features.append(market_timing)
            
            # Validate we have exactly 26 features
            if len(features) != 26:
                logger.error(f"Feature extraction returned {len(features)} features, expected 26")
                return None
                
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from dict: {str(e)}")
            return None

    def _calculate_property_affordability(self, sqft: float, mortgage_rate: float, inflation_rate: float) -> float:
        """Calculate property-specific affordability based on size and economic conditions."""
        try:
            # Base affordability on property size and rates
            size_factor = min(sqft / 2000, 2.0)  # Normalize around 2000 sqft
            rate_impact = mortgage_rate / 10.0  # Normalize to 10%
            inflation_impact = inflation_rate / 5.0  # Normalize to 5%
            
            # Higher rates and inflation = lower affordability
            affordability = 1.0 - (rate_impact * 0.6 + inflation_impact * 0.2 + (size_factor - 1.0) * 0.2)
            return max(0.0, min(1.0, affordability))
        except Exception as e:
            logger.error(f"Error calculating property affordability: {str(e)}")
            return 0.5  # Default moderate affordability

    def _calculate_property_economic_sensitivity(self, property_type: str, economic_indicators: Dict) -> float:
        """Calculate how sensitive this property type is to economic conditions."""
        try:
            # Different property types have different economic sensitivities
            sensitivity_map = {
                'Condo': 0.8,        # High sensitivity to rates
                'Townhouse': 0.6,    # Medium sensitivity
                'Detached': 0.4,     # Lower sensitivity (more stable)
                'Semi-Detached': 0.5,
                'Apartment': 0.9     # Highest sensitivity
            }
            
            base_sensitivity = sensitivity_map.get(property_type, 0.6)
            
            # Adjust based on current economic conditions
            rate_environment = economic_indicators.get('interest_rate_environment', 0.5)
            economic_momentum = economic_indicators.get('economic_momentum', 0.0)
            
            # Higher rates increase sensitivity, positive momentum decreases it
            adjusted_sensitivity = base_sensitivity + (rate_environment * 0.2) - (economic_momentum * 0.1)
            
            return max(0.0, min(1.0, adjusted_sensitivity))
        except Exception as e:
            logger.error(f"Error calculating property economic sensitivity: {str(e)}")
            return 0.6  # Default medium sensitivity

    def _calculate_market_timing(self, economic_indicators: Dict) -> float:
        """Calculate market timing indicator (0=poor timing, 1=excellent timing)."""
        try:
            policy_rate = economic_indicators.get('policy_rate', 5.0)
            economic_momentum = economic_indicators.get('economic_momentum', 0.0)
            affordability_pressure = economic_indicators.get('affordability_pressure', 0.5)
            
            # Good timing = lower rates, positive momentum, low affordability pressure
            rate_timing = 1.0 - (policy_rate / 8.0)  # Lower rates = better timing
            momentum_timing = (economic_momentum + 1.0) / 2.0  # Positive momentum = better
            pressure_timing = 1.0 - affordability_pressure  # Lower pressure = better
            
            # Weighted combination
            timing = (rate_timing * 0.4 + momentum_timing * 0.3 + pressure_timing * 0.3)
            return max(0.0, min(1.0, timing))
        except Exception as e:
            logger.error(f"Error calculating market timing: {str(e)}")
            return 0.5  # Default neutral timing
    
    def _extract_features(self, property) -> List[float]:
        """
        Extract 26 features from property object for ML model prediction.
        This method converts a property object to the expected 26 feature array.
        
        Args:
            property: Property object from the database
            
        Returns:
            List of 26 features or None if extraction fails
        """
        try:
            # Convert property object to dictionary format
            property_dict = {
                'bedrooms': property.bedrooms if property.bedrooms else 3,
                'bathrooms': property.bathrooms if property.bathrooms else 2.0,
                'square_feet': property.sqft if property.sqft else 1500,
                'lot_size': property.lot_size if property.lot_size else 0.25,
                'rooms': property.rooms if property.rooms else 7,
                'city': property.city if property.city else 'Toronto',
                'province': property.province if property.province else 'ON',
                'property_type': property.property_type if property.property_type else 'Detached',
                'year_built': property.year_built if property.year_built else 2010,
                'dom': property.dom if property.dom else 30,
                'taxes': property.taxes if property.taxes else 5000
            }
            
            # Use the existing _extract_features_from_dict method
            return self._extract_features_from_dict(property_dict)
            
        except Exception as e:
            logger.error(f"Error extracting features from property object: {str(e)}")
            return None

    def get_top_deals(self, limit: int = 10, location: str = None, property_type: str = None, offset: int = 0) -> List[Dict]:
        """
        Get top deals where listed price is below AI prediction (undervalued opportunities).
        This method focuses on currently available properties for investment.
        
        Args:
            limit: Number of properties to return
            location: Filter by city/location
            property_type: Filter by property type
            offset: Number of properties to skip for pagination
            
        Returns:
            List of top deal properties with analysis
        """
        self._load_models()
        
        try:
            from app import db
            
            # Build query for properties that are currently listed (not sold)
            query = Property.query.filter(
                Property.sold_price.isnot(None),  # Has sold price (historical data)
                Property.sold_price > 0
            )
            
            if location:
                query = query.filter(Property.city.ilike(f'%{location}%'))
            if property_type:
                query = query.filter(Property.property_type.ilike(f'%{property_type}%'))
                
            # Get properties for analysis
            properties = query.limit(500).all()  # Analyze up to 500 properties
            
            top_deals = []
            
            for property in properties:
                # Get AI analysis
                analysis = self.analyze_property(property)
                
                if analysis['predicted_price'] and property.sold_price:
                    listed_price = self._safe_float(property.sold_price)
                    predicted_price = analysis['predicted_price']
                    
                    # TOP DEALS LOGIC: Listed price is BELOW predicted price (good deal)
                    # Calculate value difference (how much below prediction the listing is)
                    value_diff = predicted_price - listed_price
                    value_diff_percent = (value_diff / predicted_price) * 100
                    
                    # Only include properties where listing is below prediction by at least 5%
                    if value_diff_percent >= 5:  # Listed price is below AI prediction
                        top_deals.append({
                            'property': property,
                            'analysis': analysis,
                            'listed_price': listed_price,
                            'predicted_price': predicted_price,
                            'value_difference': value_diff,
                            'value_difference_percent': value_diff_percent,
                            'deal_quality': self._calculate_deal_quality(value_diff_percent, analysis.get('investment_score', 5.0)),
                            'is_top_deal': True
                        })
            
            # Sort by value difference percentage (best deals first)
            top_deals.sort(key=lambda x: x['value_difference_percent'], reverse=True)
            
            # Apply pagination
            start_index = offset
            end_index = offset + limit
            return top_deals[start_index:end_index]
            
        except Exception as e:
            print(f"Error getting top deals: {str(e)}")
            return []

    def _calculate_deal_quality(self, value_diff_percent: float, investment_score: float) -> str:
        """Calculate deal quality based on undervaluation and investment score."""
        if value_diff_percent >= 25 and investment_score >= 8:
            return "Exceptional Deal"
        elif value_diff_percent >= 20 and investment_score >= 7:
            return "Excellent Deal"
        elif value_diff_percent >= 15 and investment_score >= 6:
            return "Very Good Deal"
        elif value_diff_percent >= 10 and investment_score >= 5:
            return "Good Deal"
        elif value_diff_percent >= 5:
            return "Fair Deal"
        else:
            return "Below Average"
    
    def get_feature_importance_analysis(self) -> Dict[str, Any]:
        """
        Get feature importance analysis from the ML model.
        Returns feature importance scores and visualizations data for all 26 features.
        """
        try:
            self._load_models()
            
            if not self.models.get('valuation'):
                return {'error': 'No model loaded for feature analysis', 'success': False}
            
            model = self.models['valuation']
            
            # Get the 26 feature names used in training
            feature_names = [
                'Bedrooms', 'Bathrooms', 'Square Feet', 'Lot Size', 'Total Rooms',
                'City Code', 'Province Code', 'Property Type Code', 'Year Built', 'Current Year',
                'Current Month', 'Days on Market', 'Annual Taxes', 'Policy Rate', 'Prime Rate',
                'Mortgage 5yr Rate', 'Inflation Rate', 'Unemployment Rate', 'CAD/USD Exchange Rate',
                'GDP Growth %', 'Interest Rate Environment', 'Economic Momentum',
                'Affordability Pressure', 'Property Affordability Score', 'Economic Sensitivity',
                'Market Timing Score'
            ]
            
            # Categories for better visualization
            feature_categories = {
                'Property Physical': ['Bedrooms', 'Bathrooms', 'Square Feet', 'Lot Size', 'Total Rooms'],
                'Location & Type': ['City Code', 'Province Code', 'Property Type Code'],
                'Age & Timing': ['Year Built', 'Current Year', 'Current Month', 'Days on Market'],
                'Financial': ['Annual Taxes'],
                'Economic Indicators': ['Policy Rate', 'Prime Rate', 'Mortgage 5yr Rate', 'Inflation Rate', 
                                      'Unemployment Rate', 'CAD/USD Exchange Rate', 'GDP Growth %'],
                'Derived Economic': ['Interest Rate Environment', 'Economic Momentum', 'Affordability Pressure',
                                   'Property Affordability Score', 'Economic Sensitivity', 'Market Timing Score']
            }
            
            # Get feature importance (works for tree-based models and linear models)
            importance_scores = None
            model_name = type(model).__name__
            
            if hasattr(model, 'feature_importances_'):
                # Tree-based models (RandomForest, GradientBoosting, XGBoost, etc.)
                importance_scores = model.feature_importances_
                logger.info(f"Using feature_importances_ from {model_name}")
            elif hasattr(model, 'coef_'):
                # Linear models (LinearRegression, Ridge, Lasso, etc.)
                importance_scores = np.abs(model.coef_)
                if len(importance_scores.shape) > 1:
                    importance_scores = importance_scores[0]  # For multi-output models
                logger.info(f"Using coef_ from {model_name}")
            else:
                # Try to get from ensemble models or pipeline
                if hasattr(model, 'estimators_') and len(model.estimators_) > 0:
                    if hasattr(model.estimators_[0], 'feature_importances_'):
                        importance_scores = np.mean([estimator.feature_importances_ 
                                                   for estimator in model.estimators_], axis=0)
                        logger.info(f"Using averaged feature_importances_ from ensemble {model_name}")
                elif hasattr(model, 'named_steps') and 'regressor' in model.named_steps:
                    # For sklearn pipelines
                    regressor = model.named_steps['regressor']
                    if hasattr(regressor, 'feature_importances_'):
                        importance_scores = regressor.feature_importances_
                    elif hasattr(regressor, 'coef_'):
                        importance_scores = np.abs(regressor.coef_)
                        if len(importance_scores.shape) > 1:
                            importance_scores = importance_scores[0]
                    logger.info(f"Using feature importance from pipeline {model_name}")
            
            if importance_scores is not None and len(importance_scores) >= len(feature_names):
                # Normalize importance scores to sum to 1
                importance_scores = importance_scores[:len(feature_names)]  # Take only first 26
                total_importance = np.sum(importance_scores)
                if total_importance > 0:
                    normalized_scores = importance_scores / total_importance
                else:
                    normalized_scores = importance_scores
                
                # Create feature importance data
                feature_data = []
                for i, (name, score) in enumerate(zip(feature_names, normalized_scores)):
                    # Find category for this feature
                    category = 'Other'
                    for cat, features in feature_categories.items():
                        if name in features:
                            category = cat
                            break
                    
                    feature_data.append({
                        'feature': name,
                        'importance': float(score),
                        'importance_percent': float(score) * 100,
                        'category': category,
                        'rank': i + 1
                    })
                
                # Sort by importance
                feature_data.sort(key=lambda x: x['importance'], reverse=True)
                
                # Update ranks after sorting
                for i, feature in enumerate(feature_data):
                    feature['rank'] = i + 1
                
                # Get top features for different visualizations
                top_10_features = feature_data[:10]
                top_15_features = feature_data[:15]
                
                # Calculate category importance
                category_importance = {}
                for feature in feature_data:
                    cat = feature['category']
                    if cat not in category_importance:
                        category_importance[cat] = 0
                    category_importance[cat] += feature['importance']
                
                category_data = [
                    {'category': cat, 'importance': imp, 'importance_percent': imp * 100}
                    for cat, imp in category_importance.items()
                ]
                category_data.sort(key=lambda x: x['importance'], reverse=True)
                
                return {
                    'success': True,
                    'all_features': feature_data,
                    'top_10_features': top_10_features,
                    'top_15_features': top_15_features,
                    'category_importance': category_data,
                    'model_type': model_name,
                    'total_features': len(feature_data),
                    'feature_categories': feature_categories
                }
            else:
                return {'error': 'Unable to extract feature importance from this model type', 'success': False}
                
        except Exception as e:
            logger.error(f"Error getting feature importance analysis: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}', 'success': False}

    def get_price_analytics_by_location(self) -> Dict[str, Any]:
        """
        Get comprehensive price analytics by different location types.
        Returns average prices for cities, neighbourhoods, zones, and provinces.
        """
        try:
            from app import db
            from app.models.property import Property
            from sqlalchemy import func
            
            analytics_data = {
                'cities': [],
                'provinces': [],
                'property_types': [],
                'zones': []  # Will use postal code zones
            }
            
            # Get average prices by major cities
            city_query = db.session.query(
                Property.city,
                func.avg(func.coalesce(Property.sold_price, Property.original_price)).label('avg_price'),
                func.count(Property.listing_id).label('property_count'),
                func.min(func.coalesce(Property.sold_price, Property.original_price)).label('min_price'),
                func.max(func.coalesce(Property.sold_price, Property.original_price)).label('max_price')
            ).filter(
                db.or_(Property.sold_price.isnot(None), Property.original_price.isnot(None)),
                Property.city.isnot(None)
            ).group_by(Property.city).having(
                func.count(Property.listing_id) >= 5  # At least 5 properties
            ).order_by(func.avg(func.coalesce(Property.sold_price, Property.original_price)).desc()).limit(20)
            
            for city, avg_price, count, min_price, max_price in city_query:
                analytics_data['cities'].append({
                    'name': city,
                    'avg_price': float(avg_price) if avg_price else 0,
                    'property_count': int(count),
                    'min_price': float(min_price) if min_price else 0,
                    'max_price': float(max_price) if max_price else 0,
                    'price_range': float(max_price - min_price) if max_price and min_price else 0
                })
            
            # Get average prices by provinces
            province_query = db.session.query(
                Property.province,
                func.avg(func.coalesce(Property.sold_price, Property.original_price)).label('avg_price'),
                func.count(Property.listing_id).label('property_count'),
                func.min(func.coalesce(Property.sold_price, Property.original_price)).label('min_price'),
                func.max(func.coalesce(Property.sold_price, Property.original_price)).label('max_price')
            ).filter(
                db.or_(Property.sold_price.isnot(None), Property.original_price.isnot(None)),
                Property.province.isnot(None)
            ).group_by(Property.province).order_by(func.avg(func.coalesce(Property.sold_price, Property.original_price)).desc())
            
            for province, avg_price, count, min_price, max_price in province_query:
                analytics_data['provinces'].append({
                    'name': province,
                    'avg_price': float(avg_price) if avg_price else 0,
                    'property_count': int(count),
                    'min_price': float(min_price) if min_price else 0,
                    'max_price': float(max_price) if max_price else 0,
                    'price_range': float(max_price - min_price) if max_price and min_price else 0
                })
            
            # Get average prices by property types
            type_query = db.session.query(
                Property.property_type,
                func.avg(func.coalesce(Property.sold_price, Property.original_price)).label('avg_price'),
                func.count(Property.listing_id).label('property_count'),
                func.min(func.coalesce(Property.sold_price, Property.original_price)).label('min_price'),
                func.max(func.coalesce(Property.sold_price, Property.original_price)).label('max_price')
            ).filter(
                db.or_(Property.sold_price.isnot(None), Property.original_price.isnot(None)),
                Property.property_type.isnot(None)
            ).group_by(Property.property_type).order_by(func.avg(func.coalesce(Property.sold_price, Property.original_price)).desc())
            
            for prop_type, avg_price, count, min_price, max_price in type_query:
                analytics_data['property_types'].append({
                    'name': prop_type,
                    'avg_price': float(avg_price) if avg_price else 0,
                    'property_count': int(count),
                    'min_price': float(min_price) if min_price else 0,
                    'max_price': float(max_price) if max_price else 0,
                    'price_range': float(max_price - min_price) if max_price and min_price else 0
                })
            
            # Get price analytics by postal code zones (first 3 characters)
            zone_query = db.session.query(
                func.substr(Property.postal_code, 1, 3).label('zone'),
                func.avg(func.coalesce(Property.sold_price, Property.original_price)).label('avg_price'),
                func.count(Property.listing_id).label('property_count'),
                func.min(func.coalesce(Property.sold_price, Property.original_price)).label('min_price'),
                func.max(func.coalesce(Property.sold_price, Property.original_price)).label('max_price')
            ).filter(
                db.or_(Property.sold_price.isnot(None), Property.original_price.isnot(None)),
                Property.postal_code.isnot(None),
                func.length(Property.postal_code) >= 3
            ).group_by(func.substr(Property.postal_code, 1, 3)).having(
                func.count(Property.listing_id) >= 3  # At least 3 properties
            ).order_by(func.avg(func.coalesce(Property.sold_price, Property.original_price)).desc()).limit(15)
            
            for zone, avg_price, count, min_price, max_price in zone_query:
                analytics_data['zones'].append({
                    'name': zone,
                    'avg_price': float(avg_price) if avg_price else 0,
                    'property_count': int(count),
                    'min_price': float(min_price) if min_price else 0,
                    'max_price': float(max_price) if max_price else 0,
                    'price_range': float(max_price - min_price) if max_price and min_price else 0
                })
            
            # Calculate summary statistics
            summary = {
                'total_cities': len(analytics_data['cities']),
                'total_provinces': len(analytics_data['provinces']),
                'total_property_types': len(analytics_data['property_types']),
                'total_zones': len(analytics_data['zones']),
                'highest_avg_city': analytics_data['cities'][0] if analytics_data['cities'] else None,
                'lowest_avg_city': analytics_data['cities'][-1] if analytics_data['cities'] else None
            }
            
            return {
                'success': True,
                'data': analytics_data,
                'summary': summary,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting price analytics by location: {str(e)}")
            return {'error': f'Analytics failed: {str(e)}'}

    def get_neighbourhood_price_analysis(self, city: str = None) -> Dict[str, Any]:
        """
        Get detailed neighbourhood price analysis for a specific city or all cities.
        """
        try:
            from app import db
            from app.models.property import Property
            from sqlalchemy import func, and_
            
            # Base query
            query = db.session.query(
                Property.city,
                Property.address,
                func.avg(func.coalesce(Property.sold_price, Property.original_price)).label('avg_price'),
                func.count(Property.listing_id).label('property_count')
            ).filter(
                db.or_(Property.sold_price.isnot(None), Property.original_price.isnot(None)),
                Property.address.isnot(None)
            )
            
            if city:
                query = query.filter(Property.city.ilike(f'%{city}%'))
            
            # Group by city and street (extract street from address)
            neighbourhoods = []
            
            # Simplified approach - group by city only since neighbourhood parsing is complex
            results = query.group_by(
                Property.city, 
                Property.address  # Group by full address as proxy for neighbourhood
            ).having(
                func.count(Property.listing_id) >= 1  # At least 1 property per address
            ).order_by(
                Property.city, 
                func.avg(func.coalesce(Property.sold_price, Property.original_price)).desc()
            ).limit(50).all()
            
            for city_name, address_part, avg_price, count in results:
                # Extract neighbourhood name from address
                neighbourhood_name = address_part.split(',')[0] if address_part else 'Unknown'
                
                neighbourhoods.append({
                    'city': city_name,
                    'neighbourhood': neighbourhood_name,
                    'avg_price': float(avg_price) if avg_price else 0,
                    'property_count': int(count)
                })
            
            return {
                'success': True,
                'neighbourhoods': neighbourhoods,
                'filtered_city': city,
                'total_neighbourhoods': len(neighbourhoods)
            }
            
        except Exception as e:
            logger.error(f"Error getting neighbourhood analysis: {str(e)}")
            return {'error': f'Neighbourhood analysis failed: {str(e)}'}

    def get_general_investment_opportunities(self, limit: int = 10) -> List[Dict]:
        """
        Get general investment opportunities without user-specific data.
        Returns properties with high investment potential based on AI analysis.
        """
        try:
            from app import db
            from app.models.property import Property
            from sqlalchemy import and_, or_
            
            # Get properties with good investment characteristics
            query = Property.query.filter(
                Property.sold_price.isnot(None),
                Property.city.isnot(None),
                Property.property_type.isnot(None),
                Property.sqft.isnot(None),
                Property.sqft > 0
            )
            
            # Prefer recent data and reasonable price ranges
            properties = query.filter(
                and_(
                    Property.sold_price >= 100000,  # Minimum viable price
                    Property.sold_price <= 5000000,  # Maximum for general opportunities
                    or_(
                        Property.property_type.in_(['Detached', 'Semi-Detached', 'Townhouse', 'Condo']),
                        Property.property_type.ilike('%house%'),
                        Property.property_type.ilike('%condo%')
                    )
                )
            ).order_by(Property.sold_price.desc()).limit(limit * 2).all()  # Get extra to filter
            
            opportunities = []
            
            for property in properties[:limit]:
                try:
                    # Calculate investment metrics
                    investment_score = self._calculate_investment_score(property)
                    risk_level = self._assess_risk_level(property)
                    
                    # Get AI prediction if possible
                    predicted_price = property.sold_price  # Fallback to actual price
                    try:
                        prediction_result = self.predict_property_price({
                            'bedrooms': property.bedrooms or 3,
                            'bathrooms': property.bathrooms or 2,
                            'square_feet': property.sqft or 1500,
                            'city': property.city or 'Toronto',
                            'province': property.province or 'ON',
                            'property_type': property.property_type or 'Detached'
                        })
                        if prediction_result.get('success'):
                            predicted_price = prediction_result.get('predicted_price', property.sold_price)
                    except:
                        pass  # Use fallback
                    
                    # Generate AI insight
                    insights = self._generate_insights(property)
                    ai_insight = insights[0] if insights else "Property shows good investment potential based on location and market factors."
                    
                    opportunity = {
                        'listing_id': property.listing_id,
                        'address': property.address or f"Property in {property.city}",
                        'city': property.city,
                        'province': property.province,
                        'property_type': property.property_type,
                        'bedrooms': property.bedrooms,
                        'bathrooms': property.bathrooms,
                        'sqft': property.sqft,
                        'actual_price': self._safe_float(property.sold_price),
                        'predicted_price': float(predicted_price),
                        'investment_score': investment_score,
                        'risk_level': risk_level,
                        'ai_insight': ai_insight,
                        'price_per_sqft': self._safe_float(property.sold_price) / self._safe_float(property.sqft) if property.sqft and property.sqft > 0 else 0
                    }
                    
                    # Only include properties with decent investment scores
                    if investment_score >= 5.0:
                        opportunities.append(opportunity)
                        
                except Exception as e:
                    logger.warning(f"Error processing property {property.listing_id}: {str(e)}")
                    continue
            
            # Sort by investment score
            opportunities.sort(key=lambda x: x['investment_score'], reverse=True)
            
            return opportunities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting general investment opportunities: {str(e)}")
            # Return demo data as fallback
            return [
                {
                    'listing_id': 'DEMO_001',
                    'address': 'Sample Property, Toronto',
                    'city': 'Toronto',
                    'province': 'ON',
                    'property_type': 'Detached',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'sqft': 1800,
                    'actual_price': 850000,
                    'predicted_price': 875000,
                    'investment_score': 7.5,
                    'risk_level': 'Medium',
                    'ai_insight': 'Demo property showing strong fundamentals in growing Toronto market.',
                    'price_per_sqft': 472
                }
            ]
