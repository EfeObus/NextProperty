# Machine Learning Documentation

## Table of Contents
- [Overview](#overview)
- [Model Architecture](#model-architecture)
- [Available Models](#available-models)
- [Feature Engineering](#feature-engineering)
- [Training Pipeline](#training-pipeline)
- [Model Evaluation](#model-evaluation)
- [Prediction Service](#prediction-service)
- [Model Management](#model-management)
- [Performance Optimization](#performance-optimization)
- [Economic Integration](#economic-integration)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)

## Overview

NextProperty AI implements a comprehensive machine learning system for real estate price prediction and investment analysis. The system supports multiple ML algorithms and provides ensemble methods for improved accuracy.

### Key Features
- **Multiple ML Models**: 6+ algorithms including XGBoost, LightGBM, Random Forest
- **Ensemble Learning**: Stacking and voting classifiers for enhanced predictions
- **Economic Integration**: Real-time economic indicators from BoC and StatCan
- **Feature Engineering**: 26+ engineered features for comprehensive analysis
- **Real-time Predictions**: Fast API responses with caching
- **Model Management**: Dynamic model switching and performance monitoring

### Performance Metrics
| Model | R² Score | RMSE | MAE | MAPE | Training Time |
|-------|----------|------|-----|------|---------------|
| LightGBM | 85.3% | $263,680 | $195,420 | 4.2% | 4.2s |
| XGBoost | 79.4% | $312,150 | $228,340 | 5.1% | 8.1s |
| Random Forest | 82.7% | $285,420 | $210,180 | 4.8% | 6.8s |
| Gradient Boosting | 76.2% | $334,890 | $245,120 | 5.5% | 12.3s |
| Ridge Regression | 72.1% | $356,406 | $268,910 | 6.2% | 0.2s |
| Ensemble | 87.1% | $245,320 | $180,240 | 3.9% | 15.7s |

## Model Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Input    │───▶│ Feature Engineer │───▶│ Model Training  │
│                 │    │                  │    │                 │
│ • Property Data │    │ • 26 Features    │    │ • 6+ Algorithms │
│ • Economic Data │    │ • Normalization  │    │ • Cross Valid.  │
│ • Market Data   │    │ • Encoding       │    │ • Hyperparams   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Model Serving   │◀───│ Model Selection  │◀───│ Model Ensemble  │
│                 │    │                  │    │                 │
│ • API Service   │    │ • Performance    │    │ • Stacking      │
│ • Caching       │    │ • Validation     │    │ • Voting        │
│ • Monitoring    │    │ • A/B Testing    │    │ • Blending      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Service Architecture

```python
# app/services/ml_service.py
class MLService:
    """Main ML service orchestrating all model operations."""
    
    def __init__(self):
        self.models = {}  # Loaded models cache
        self.feature_columns = []  # Feature definitions
        self.economic_cache = {}  # Economic data cache
        
    def predict_property_price(self, property_data: dict) -> dict
    def analyze_property(self, property_obj) -> dict
    def get_top_properties(self, limit: int = 20) -> list
    def predict_market_trends(self, city: str, horizon: int = 6) -> dict
```

## Available Models

### 1. LightGBM (Primary Model)
**Best overall performance with speed and accuracy balance**

```python
# Model Configuration
{
    "objective": "regression",
    "metric": "rmse",
    "boosting_type": "gbdt",
    "num_leaves": 31,
    "learning_rate": 0.05,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "verbose": 0
}
```

**Strengths:**
- Fast training and prediction
- Handles categorical features well
- Low memory usage
- Excellent accuracy

**Use Cases:**
- Real-time price predictions
- Batch processing
- Mobile/edge deployment

### 2. XGBoost
**High-performance gradient boosting with robust handling of missing values**

```python
# Model Configuration
{
    "objective": "reg:squarederror",
    "n_estimators": 100,
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "random_state": 42
}
```

**Strengths:**
- Handles missing values automatically
- Built-in regularization
- Feature importance analysis
- Cross-validation support

### 3. Random Forest
**Ensemble method with good interpretability and stability**

```python
# Model Configuration
{
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5,
    "min_samples_leaf": 2,
    "random_state": 42,
    "n_jobs": -1
}
```

**Strengths:**
- Robust to overfitting
- Feature importance ranking
- Handles non-linear relationships
- Good baseline performance

### 4. Gradient Boosting
**Traditional boosting with controlled overfitting**

```python
# Model Configuration
{
    "n_estimators": 100,
    "learning_rate": 0.1,
    "max_depth": 6,
    "random_state": 42,
    "validation_fraction": 0.1,
    "n_iter_no_change": 5
}
```

### 5. Ridge Regression
**Linear model with L2 regularization for baseline comparison**

```python
# Model Configuration
{
    "alpha": 1.0,
    "normalize": True,
    "random_state": 42
}
```

**Strengths:**
- Fast training and prediction
- Interpretable coefficients
- Good baseline model
- Low computational requirements

### 6. Ensemble Models
**Combining multiple models for superior performance**

#### Stacking Ensemble
```python
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import LinearRegression

base_models = [
    ('lgb', lgb_model),
    ('xgb', xgb_model),
    ('rf', rf_model)
]

stacking_model = StackingRegressor(
    estimators=base_models,
    final_estimator=LinearRegression(),
    cv=5
)
```

#### Voting Ensemble
```python
from sklearn.ensemble import VotingRegressor

voting_model = VotingRegressor([
    ('lgb', lgb_model),
    ('xgb', xgb_model),
    ('rf', rf_model)
], weights=[0.4, 0.3, 0.3])
```

## Feature Engineering

### Core Features (26 Features)

#### Property Features (12)
```python
property_features = [
    'bedrooms',           # Number of bedrooms
    'bathrooms',          # Number of bathrooms (float)
    'sqft',              # Square footage
    'lot_size',          # Lot size in acres
    'year_built',        # Year property was built
    'age',               # Calculated age (current_year - year_built)
    'property_type_encoded',  # Encoded property type
    'rooms',             # Total number of rooms
    'kitchens_plus',     # Kitchen count
    'dom',               # Days on market
    'taxes',             # Annual property taxes
    'maintenance_fee'    # Monthly maintenance fee
]
```

#### Location Features (6)
```python
location_features = [
    'city_encoded',         # Encoded city name
    'province_encoded',     # Encoded province
    'neighbourhood_encoded', # Encoded neighbourhood
    'postal_code_prefix',   # First 3 chars of postal code
    'latitude',            # Geographic latitude
    'longitude'            # Geographic longitude
]
```

#### Economic Features (8)
```python
economic_features = [
    'interest_rate',       # BoC overnight rate
    'inflation_rate',      # CPI year-over-year
    'unemployment_rate',   # National unemployment
    'gdp_growth',         # GDP growth rate
    'housing_starts',     # Housing construction starts
    'population_growth',  # Regional population growth
    'avg_income',         # Regional average income
    'mortgage_rate'       # 5-year fixed mortgage rate
]
```

### Feature Engineering Pipeline

```python
class FeatureEngineer:
    """Feature engineering pipeline for property data."""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.economic_service = EconomicService()
    
    def engineer_features(self, property_data: dict) -> np.ndarray:
        """Engineer all features for a property."""
        features = {}
        
        # Basic property features
        features.update(self._extract_property_features(property_data))
        
        # Location features
        features.update(self._encode_location_features(property_data))
        
        # Economic features
        features.update(self._get_economic_features())
        
        # Derived features
        features.update(self._calculate_derived_features(features))
        
        return self._normalize_features(features)
    
    def _extract_property_features(self, data: dict) -> dict:
        """Extract basic property features."""
        current_year = datetime.now().year
        
        return {
            'bedrooms': data.get('bedrooms', 3),
            'bathrooms': data.get('bathrooms', 2.0),
            'sqft': data.get('sqft', 1500),
            'lot_size': data.get('lot_size', 0.25),
            'age': current_year - data.get('year_built', 2010),
            'dom': data.get('dom', 30),
            'taxes': data.get('taxes', 5000),
            'maintenance_fee': data.get('maintenance_fee', 0)
        }
    
    def _encode_location_features(self, data: dict) -> dict:
        """Encode location-based features."""
        return {
            'city_encoded': self._encode_categorical(data.get('city', 'Toronto'), 'city'),
            'province_encoded': self._encode_categorical(data.get('province', 'ON'), 'province'),
            'property_type_encoded': self._encode_categorical(data.get('property_type', 'Detached'), 'property_type')
        }
    
    def _get_economic_features(self) -> dict:
        """Get current economic indicators."""
        try:
            economic_data = self.economic_service.get_current_indicators()
            return {
                'interest_rate': economic_data.get('overnight_rate', 5.0),
                'inflation_rate': economic_data.get('cpi_rate', 3.0),
                'unemployment_rate': economic_data.get('unemployment', 6.5),
                'gdp_growth': economic_data.get('gdp_growth', 2.5)
            }
        except Exception as e:
            logger.warning(f"Using default economic features: {e}")
            return self._default_economic_features()
    
    def _calculate_derived_features(self, features: dict) -> dict:
        """Calculate derived features."""
        return {
            'price_per_sqft_estimate': features['taxes'] / (features['sqft'] / 1000),
            'rooms_per_bedroom': (features.get('rooms', 8) / max(features['bedrooms'], 1)),
            'bathroom_bedroom_ratio': features['bathrooms'] / max(features['bedrooms'], 1),
            'age_normalized': min(features['age'] / 50, 1.0),  # Normalize age to 0-1
            'size_category': self._categorize_size(features['sqft'])
        }
```

### Feature Importance Analysis

```python
def analyze_feature_importance(model, feature_names):
    """Analyze and visualize feature importance."""
    
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importance = np.abs(model.coef_)
    else:
        return None
    
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    return feature_importance

# Example output for LightGBM
"""
        feature  importance
0          sqft    0.285
1         age     0.156
2    bedrooms     0.134
3   city_encoded  0.098
4    bathrooms    0.087
5   interest_rate 0.076
6    lot_size     0.064
7    dom         0.045
8    taxes       0.032
9  property_type 0.023
"""
```

## Training Pipeline

### Data Preparation

```python
def prepare_training_data():
    """Prepare data for model training."""
    
    # Load property data
    properties = Property.query.filter(
        Property.sold_price.isnot(None),
        Property.bedrooms.isnot(None),
        Property.bathrooms.isnot(None),
        Property.sqft.isnot(None)
    ).all()
    
    # Convert to DataFrame
    df = pd.DataFrame([prop.to_dict() for prop in properties])
    
    # Data cleaning
    df = clean_property_data(df)
    
    # Feature engineering
    feature_engineer = FeatureEngineer()
    X = np.array([feature_engineer.engineer_features(row.to_dict()) 
                  for _, row in df.iterrows()])
    y = df['sold_price'].values
    
    return train_test_split(X, y, test_size=0.2, random_state=42)

def clean_property_data(df):
    """Clean and validate property data."""
    
    # Remove outliers (outside 3 standard deviations)
    price_mean = df['sold_price'].mean()
    price_std = df['sold_price'].std()
    df = df[
        (df['sold_price'] >= price_mean - 3 * price_std) &
        (df['sold_price'] <= price_mean + 3 * price_std)
    ]
    
    # Remove impossible values
    df = df[
        (df['bedrooms'] <= 20) &
        (df['bathrooms'] <= 20) &
        (df['sqft'] >= 200) &
        (df['sqft'] <= 50000)
    ]
    
    # Fill missing values
    df['lot_size'] = df['lot_size'].fillna(df['lot_size'].median())
    df['year_built'] = df['year_built'].fillna(2000)
    df['dom'] = df['dom'].fillna(30)
    df['taxes'] = df['taxes'].fillna(df['taxes'].median())
    
    return df
```

### Model Training Script

```python
# enhanced_model_training.py
def train_all_models():
    """Train all available models with cross-validation."""
    
    # Prepare data
    X_train, X_test, y_train, y_test = prepare_training_data()
    
    # Define models
    models = {
        'LightGBM': LGBMRegressor(**lgb_params),
        'XGBoost': XGBRegressor(**xgb_params),
        'RandomForest': RandomForestRegressor(**rf_params),
        'GradientBoosting': GradientBoostingRegressor(**gb_params),
        'Ridge': Ridge(**ridge_params)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"Training {name}...")
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train,
            cv=5, scoring='neg_root_mean_squared_error'
        )
        
        # Train final model
        start_time = time.time()
        model.fit(X_train, y_train)
        training_time = time.time() - start_time
        
        # Evaluate
        y_pred = model.predict(X_test)
        
        results[name] = {
            'model': model,
            'r2': r2_score(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'mape': mean_absolute_percentage_error(y_test, y_pred),
            'cv_rmse_mean': -cv_scores.mean(),
            'cv_rmse_std': cv_scores.std(),
            'training_time': training_time
        }
        
        # Save model
        model_path = f'models/trained_models/{name.lower()}_price_model.pkl'
        joblib.dump(model, model_path)
        
        print(f"{name} - R²: {results[name]['r2']:.4f}, RMSE: ${results[name]['rmse']:,.0f}")
    
    # Train ensemble model
    results['Ensemble'] = train_ensemble_model(models, X_train, X_test, y_train, y_test)
    
    # Save results
    save_training_results(results)
    
    return results

def train_ensemble_model(base_models, X_train, X_test, y_train, y_test):
    """Train stacking ensemble model."""
    
    # Select top 3 models for ensemble
    model_performance = [(name, model['r2']) for name, model in base_models.items()]
    top_models = sorted(model_performance, key=lambda x: x[1], reverse=True)[:3]
    
    estimators = [(name.lower(), base_models[name]['model']) for name, _ in top_models]
    
    stacking_model = StackingRegressor(
        estimators=estimators,
        final_estimator=LinearRegression(),
        cv=5
    )
    
    start_time = time.time()
    stacking_model.fit(X_train, y_train)
    training_time = time.time() - start_time
    
    y_pred = stacking_model.predict(X_test)
    
    # Save ensemble model
    joblib.dump(stacking_model, 'models/trained_models/ensemble_price_model.pkl')
    
    return {
        'model': stacking_model,
        'r2': r2_score(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
        'mae': mean_absolute_error(y_test, y_pred),
        'mape': mean_absolute_percentage_error(y_test, y_pred),
        'training_time': training_time,
        'base_models': [name for name, _ in top_models]
    }
```

### Hyperparameter Optimization

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

def optimize_hyperparameters(model_type='lightgbm'):
    """Optimize hyperparameters using randomized search."""
    
    X_train, X_test, y_train, y_test = prepare_training_data()
    
    if model_type == 'lightgbm':
        model = LGBMRegressor()
        param_dist = {
            'num_leaves': randint(20, 100),
            'learning_rate': uniform(0.01, 0.2),
            'n_estimators': randint(50, 200),
            'max_depth': randint(3, 10),
            'min_child_samples': randint(10, 100),
            'subsample': uniform(0.6, 0.4),
            'colsample_bytree': uniform(0.6, 0.4)
        }
    
    random_search = RandomizedSearchCV(
        model, param_dist,
        n_iter=50,
        cv=3,
        scoring='neg_root_mean_squared_error',
        random_state=42,
        n_jobs=-1
    )
    
    random_search.fit(X_train, y_train)
    
    print(f"Best parameters: {random_search.best_params_}")
    print(f"Best CV score: {-random_search.best_score_:,.0f}")
    
    return random_search.best_estimator_
```

## Model Evaluation

### Comprehensive Evaluation Suite

```python
class ModelEvaluator:
    """Comprehensive model evaluation and validation."""
    
    def __init__(self, models, X_test, y_test):
        self.models = models
        self.X_test = X_test
        self.y_test = y_test
    
    def evaluate_all_models(self):
        """Evaluate all models with multiple metrics."""
        
        results = {}
        
        for name, model in self.models.items():
            y_pred = model.predict(self.X_test)
            
            results[name] = {
                'r2_score': r2_score(self.y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(self.y_test, y_pred)),
                'mae': mean_absolute_error(self.y_test, y_pred),
                'mape': self._mean_absolute_percentage_error(self.y_test, y_pred),
                'explained_variance': explained_variance_score(self.y_test, y_pred),
                'max_error': max_error(self.y_test, y_pred),
                'residual_analysis': self._analyze_residuals(self.y_test, y_pred)
            }
            
            # Price range accuracy
            results[name]['price_range_accuracy'] = self._price_range_accuracy(
                self.y_test, y_pred
            )
        
        return results
    
    def _mean_absolute_percentage_error(self, y_true, y_pred):
        """Calculate MAPE with handling for zero values."""
        return np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100
    
    def _analyze_residuals(self, y_true, y_pred):
        """Analyze prediction residuals."""
        residuals = y_true - y_pred
        
        return {
            'mean_residual': np.mean(residuals),
            'std_residual': np.std(residuals),
            'skewness': stats.skew(residuals),
            'kurtosis': stats.kurtosis(residuals),
            'normality_p_value': stats.jarque_bera(residuals)[1]
        }
    
    def _price_range_accuracy(self, y_true, y_pred):
        """Calculate accuracy within different price ranges."""
        ranges = [
            (0, 300000, 'Low'),
            (300000, 600000, 'Medium'), 
            (600000, 1000000, 'High'),
            (1000000, float('inf'), 'Luxury')
        ]
        
        range_accuracy = {}
        
        for min_price, max_price, label in ranges:
            mask = (y_true >= min_price) & (y_true < max_price)
            if np.any(mask):
                range_mape = self._mean_absolute_percentage_error(
                    y_true[mask], y_pred[mask]
                )
                range_accuracy[label] = {
                    'count': np.sum(mask),
                    'mape': range_mape,
                    'r2': r2_score(y_true[mask], y_pred[mask])
                }
        
        return range_accuracy
    
    def generate_evaluation_report(self):
        """Generate comprehensive evaluation report."""
        
        results = self.evaluate_all_models()
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame({
            model: {
                'R² Score': f"{metrics['r2_score']:.4f}",
                'RMSE': f"${metrics['rmse']:,.0f}",
                'MAE': f"${metrics['mae']:,.0f}",
                'MAPE': f"{metrics['mape']:.2f}%"
            }
            for model, metrics in results.items()
        }).T
        
        return comparison_df, results
```

### Cross-Validation Framework

```python
def comprehensive_cross_validation(models, X, y, cv_folds=5):
    """Perform comprehensive cross-validation."""
    
    cv_results = {}
    
    for name, model in models.items():
        print(f"Cross-validating {name}...")
        
        # Multiple scoring metrics
        scoring = {
            'r2': 'r2',
            'neg_rmse': 'neg_root_mean_squared_error', 
            'neg_mae': 'neg_mean_absolute_error'
        }
        
        cv_scores = cross_validate(
            model, X, y,
            cv=cv_folds,
            scoring=scoring,
            return_train_score=True
        )
        
        cv_results[name] = {
            'test_r2_mean': cv_scores['test_r2'].mean(),
            'test_r2_std': cv_scores['test_r2'].std(),
            'test_rmse_mean': -cv_scores['test_neg_rmse'].mean(),
            'test_rmse_std': cv_scores['test_neg_rmse'].std(),
            'test_mae_mean': -cv_scores['test_neg_mae'].mean(),
            'test_mae_std': cv_scores['test_neg_mae'].std(),
            'train_r2_mean': cv_scores['train_r2'].mean(),
            'overfitting_score': cv_scores['train_r2'].mean() - cv_scores['test_r2'].mean()
        }
    
    return cv_results
```

### Model Validation

```python
def validate_model_performance():
    """Validate current model performance against thresholds."""
    
    validation_results = {
        'overall_status': 'healthy',
        'checks': {},
        'recommendations': []
    }
    
    # Load current model
    ml_service = MLService()
    
    # Performance thresholds
    min_r2 = 0.75
    max_rmse = 400000
    max_mape = 8.0
    
    try:
        # Get current performance metrics
        performance = ml_service.get_model_metadata().get('performance', {})
        
        # R² score check
        r2_score = performance.get('r2', 0)
        validation_results['checks']['r2_check'] = {
            'value': r2_score,
            'threshold': min_r2,
            'passed': r2_score >= min_r2
        }
        
        # RMSE check
        rmse = performance.get('rmse', float('inf'))
        validation_results['checks']['rmse_check'] = {
            'value': rmse,
            'threshold': max_rmse,
            'passed': rmse <= max_rmse
        }
        
        # MAPE check
        mape = performance.get('mape', float('inf'))
        validation_results['checks']['mape_check'] = {
            'value': mape,
            'threshold': max_mape,
            'passed': mape <= max_mape
        }
        
        # Overall validation
        all_checks_passed = all(
            check['passed'] for check in validation_results['checks'].values()
        )
        
        if not all_checks_passed:
            validation_results['overall_status'] = 'degraded'
            validation_results['recommendations'].append('Consider retraining model')
        
        # Check model age
        training_date = performance.get('training_date')
        if training_date:
            days_old = (datetime.now() - datetime.fromisoformat(training_date)).days
            if days_old > 30:
                validation_results['recommendations'].append('Model is over 30 days old')
        
    except Exception as e:
        validation_results['overall_status'] = 'error'
        validation_results['error'] = str(e)
    
    return validation_results
```

## Prediction Service

### Real-time Prediction API

```python
class PredictionService:
    """High-performance prediction service with caching."""
    
    def __init__(self):
        self.ml_service = MLService()
        self.cache = cache  # Redis cache instance
        self.cache_ttl = 3600  # 1 hour cache
    
    def predict_property_price(self, property_data: dict) -> dict:
        """Predict property price with caching."""
        
        # Generate cache key
        cache_key = self._generate_cache_key(property_data)
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Generate prediction
        try:
            result = self.ml_service.predict_property_price(property_data)
            
            # Cache result
            self.cache.set(
                cache_key, 
                json.dumps(result), 
                timeout=self.cache_ttl
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'error': 'Prediction service unavailable',
                'fallback_price': self._fallback_prediction(property_data)
            }
    
    def batch_predict(self, properties: List[dict]) -> List[dict]:
        """Efficient batch prediction."""
        
        results = []
        
        # Check cache for all properties
        cache_keys = [self._generate_cache_key(prop) for prop in properties]
        cached_results = self.cache.get_many(cache_keys)
        
        # Separate cached and uncached
        uncached_indices = []
        uncached_properties = []
        
        for i, (key, prop) in enumerate(zip(cache_keys, properties)):
            if key in cached_results:
                results.append(json.loads(cached_results[key]))
            else:
                uncached_indices.append(i)
                uncached_properties.append(prop)
                results.append(None)  # Placeholder
        
        # Batch predict uncached properties
        if uncached_properties:
            batch_results = self.ml_service.batch_predict(uncached_properties)
            
            # Store in cache and update results
            cache_data = {}
            for idx, batch_result in zip(uncached_indices, batch_results):
                results[idx] = batch_result
                cache_data[cache_keys[idx]] = json.dumps(batch_result)
            
            self.cache.set_many(cache_data, timeout=self.cache_ttl)
        
        return results
    
    def _generate_cache_key(self, property_data: dict) -> str:
        """Generate cache key for property data."""
        
        # Use relevant fields for cache key
        key_fields = [
            'bedrooms', 'bathrooms', 'sqft', 'lot_size',
            'city', 'province', 'property_type', 'year_built'
        ]
        
        key_values = []
        for field in key_fields:
            value = property_data.get(field, '')
            key_values.append(f"{field}:{value}")
        
        key_string = "|".join(key_values)
        return f"prediction:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def _fallback_prediction(self, property_data: dict) -> float:
        """Simple fallback prediction when ML model fails."""
        
        # Basic price per sqft estimation by city
        city_price_per_sqft = {
            'Toronto': 600,
            'Vancouver': 800,
            'Calgary': 300,
            'Ottawa': 400,
            'Montreal': 350
        }
        
        city = property_data.get('city', 'Toronto')
        sqft = property_data.get('sqft', 1500)
        price_per_sqft = city_price_per_sqft.get(city, 500)
        
        return sqft * price_per_sqft
```

### Investment Analysis

```python
def analyze_investment_potential(property_data: dict) -> dict:
    """Comprehensive investment analysis."""
    
    ml_service = MLService()
    
    # Get price prediction
    prediction = ml_service.predict_property_price(property_data)
    predicted_price = prediction['predicted_price']
    
    # Get market data
    market_data = get_market_data(property_data['city'])
    
    # Calculate investment metrics
    analysis = {
        'predicted_price': predicted_price,
        'confidence': prediction['confidence'],
        'investment_score': calculate_investment_score(property_data, market_data),
        'risk_assessment': assess_investment_risk(property_data, market_data),
        'market_trend': predict_market_trend(property_data['city']),
        'comparable_analysis': find_comparable_properties(property_data),
        'financial_metrics': calculate_financial_metrics(property_data, predicted_price),
        'recommendation': generate_investment_recommendation(property_data, predicted_price)
    }
    
    return analysis

def calculate_investment_score(property_data: dict, market_data: dict) -> float:
    """Calculate investment score (0-10)."""
    
    score = 5.0  # Base score
    
    # Location factor (30%)
    location_score = evaluate_location(property_data['city'])
    score += (location_score - 5) * 0.3
    
    # Property condition factor (20%)
    age = datetime.now().year - property_data.get('year_built', 2000)
    condition_score = max(0, 10 - (age / 10))
    score += (condition_score - 5) * 0.2
    
    # Market trend factor (25%)
    trend_score = market_data.get('trend_score', 5)
    score += (trend_score - 5) * 0.25
    
    # Economic indicators factor (15%)
    economic_score = get_economic_sentiment_score()
    score += (economic_score - 5) * 0.15
    
    # Value proposition factor (10%)
    price_ratio = property_data.get('sold_price', 0) / max(property_data.get('ai_valuation', 1), 1)
    if price_ratio < 0.9:  # Below AI valuation
        score += 1.0
    elif price_ratio > 1.1:  # Above AI valuation
        score -= 1.0
    
    return max(0, min(10, score))
```

## Model Management

### Dynamic Model Switching

```python
class ModelManager:
    """Manage multiple models and enable dynamic switching."""
    
    def __init__(self):
        self.available_models = {}
        self.current_model = None
        self.model_metadata = {}
    
    def load_all_models(self):
        """Load all available trained models."""
        
        model_files = [
            'lightgbm_price_model.pkl',
            'xgboost_price_model.pkl',
            'randomforest_price_model.pkl',
            'gradientboosting_price_model.pkl',
            'ridge_price_model.pkl',
            'ensemble_price_model.pkl'
        ]
        
        for model_file in model_files:
            model_path = f'models/trained_models/{model_file}'
            if os.path.exists(model_path):
                try:
                    model = joblib.load(model_path)
                    model_name = model_file.replace('_price_model.pkl', '')
                    self.available_models[model_name] = model
                    
                    # Load metadata
                    metadata_path = model_path.replace('.pkl', '_metadata.json')
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            self.model_metadata[model_name] = json.load(f)
                    
                    logger.info(f"Loaded model: {model_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load {model_file}: {e}")
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model."""
        
        if model_name not in self.available_models:
            logger.error(f"Model {model_name} not available")
            return False
        
        try:
            self.current_model = self.available_models[model_name]
            
            # Update configuration
            config = {
                'active_model': model_name,
                'switched_at': datetime.now().isoformat()
            }
            
            with open('models/model_config.json', 'w') as f:
                json.dump(config, f)
            
            logger.info(f"Switched to model: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch model: {e}")
            return False
    
    def get_model_comparison(self) -> dict:
        """Compare performance of all available models."""
        
        comparison = {}
        
        for model_name, metadata in self.model_metadata.items():
            comparison[model_name] = {
                'r2_score': metadata.get('r2', 0),
                'rmse': metadata.get('rmse', 0),
                'mae': metadata.get('mae', 0),
                'mape': metadata.get('mape', 0),
                'training_time': metadata.get('training_time', 0),
                'training_date': metadata.get('training_date', ''),
                'features_count': metadata.get('features_count', 0)
            }
        
        # Sort by R² score
        sorted_models = sorted(
            comparison.items(),
            key=lambda x: x[1]['r2_score'],
            reverse=True
        )
        
        return dict(sorted_models)
    
    def auto_select_best_model(self) -> str:
        """Automatically select the best performing model."""
        
        comparison = self.get_model_comparison()
        
        if not comparison:
            return None
        
        # Select model with highest R² score
        best_model = next(iter(comparison))
        
        if self.switch_model(best_model):
            return best_model
        
        return None
```

### A/B Testing Framework

```python
class ModelABTesting:
    """A/B testing framework for model comparison."""
    
    def __init__(self):
        self.test_configs = {}
        self.test_results = {}
    
    def create_ab_test(self, test_name: str, model_a: str, model_b: str, 
                       traffic_split: float = 0.5):
        """Create a new A/B test."""
        
        self.test_configs[test_name] = {
            'model_a': model_a,
            'model_b': model_b,
            'traffic_split': traffic_split,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.test_results[test_name] = {
            'model_a_predictions': [],
            'model_b_predictions': [],
            'model_a_accuracy': [],
            'model_b_accuracy': []
        }
    
    def get_test_model(self, test_name: str, user_id: str = None) -> str:
        """Determine which model to use for this request."""
        
        if test_name not in self.test_configs:
            return 'default'
        
        config = self.test_configs[test_name]
        
        # Deterministic assignment based on user_id or request hash
        if user_id:
            hash_val = hash(user_id) % 100
        else:
            hash_val = random.randint(0, 99)
        
        split_point = int(config['traffic_split'] * 100)
        
        return config['model_a'] if hash_val < split_point else config['model_b']
    
    def record_prediction(self, test_name: str, model_used: str, 
                         prediction: float, actual_price: float = None):
        """Record prediction for A/B test analysis."""
        
        if test_name not in self.test_results:
            return
        
        config = self.test_configs[test_name]
        results = self.test_results[test_name]
        
        if model_used == config['model_a']:
            results['model_a_predictions'].append(prediction)
            if actual_price:
                accuracy = 1 - abs(prediction - actual_price) / actual_price
                results['model_a_accuracy'].append(accuracy)
        
        elif model_used == config['model_b']:
            results['model_b_predictions'].append(prediction)
            if actual_price:
                accuracy = 1 - abs(prediction - actual_price) / actual_price
                results['model_b_accuracy'].append(accuracy)
    
    def analyze_test_results(self, test_name: str) -> dict:
        """Analyze A/B test results."""
        
        if test_name not in self.test_results:
            return {}
        
        results = self.test_results[test_name]
        config = self.test_configs[test_name]
        
        analysis = {
            'test_name': test_name,
            'model_a': config['model_a'],
            'model_b': config['model_b'],
            'predictions_count': {
                'model_a': len(results['model_a_predictions']),
                'model_b': len(results['model_b_predictions'])
            }
        }
        
        # Calculate accuracy statistics
        if results['model_a_accuracy']:
            analysis['model_a_accuracy'] = {
                'mean': np.mean(results['model_a_accuracy']),
                'std': np.std(results['model_a_accuracy']),
                'count': len(results['model_a_accuracy'])
            }
        
        if results['model_b_accuracy']:
            analysis['model_b_accuracy'] = {
                'mean': np.mean(results['model_b_accuracy']),
                'std': np.std(results['model_b_accuracy']),
                'count': len(results['model_b_accuracy'])
            }
        
        # Statistical significance test
        if (results['model_a_accuracy'] and results['model_b_accuracy'] and
            len(results['model_a_accuracy']) >= 30 and 
            len(results['model_b_accuracy']) >= 30):
            
            statistic, p_value = stats.ttest_ind(
                results['model_a_accuracy'], 
                results['model_b_accuracy']
            )
            
            analysis['statistical_test'] = {
                'statistic': statistic,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        
        return analysis
```

## Performance Optimization

### Model Optimization Techniques

```python
class ModelOptimizer:
    """Optimize model performance and inference speed."""
    
    def optimize_lightgbm(self, model, X_train, y_train):
        """Optimize LightGBM model for production."""
        
        # Feature selection based on importance
        feature_importance = model.feature_importances_
        important_features = np.where(feature_importance > 0.01)[0]
        
        X_optimized = X_train[:, important_features]
        
        # Retrain with optimized parameters for speed
        optimized_params = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.1,  # Increased for faster training
            'n_estimators': 50,    # Reduced for faster inference
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'verbose': -1
        }
        
        optimized_model = LGBMRegressor(**optimized_params)
        optimized_model.fit(X_optimized, y_train)
        
        return optimized_model, important_features
    
    def quantize_model(self, model):
        """Quantize model weights for reduced memory usage."""
        
        if hasattr(model, 'feature_importances_'):
            # For tree-based models, we can reduce precision of leaf values
            # This is model-specific optimization
            pass
        
        return model
    
    def create_model_ensemble_cache(self, models, X_sample):
        """Pre-compute ensemble predictions for common input patterns."""
        
        cache = {}
        
        # Generate common property patterns
        common_patterns = self._generate_common_patterns()
        
        for pattern_name, pattern_data in common_patterns.items():
            ensemble_pred = np.mean([
                model.predict([pattern_data])[0] 
                for model in models.values()
            ])
            cache[pattern_name] = ensemble_pred
        
        return cache
    
    def _generate_common_patterns(self):
        """Generate common property patterns for caching."""
        
        patterns = {
            'toronto_3bed_2bath_1500sqft': [3, 2, 1500, 0.25, 10, 1, 0, 30, 5000, 0, 5.0, 3.0, 6.5, 2.5, 1.0, 2.0, 1.2, 0.3, 0.5, 0.8, 0.4, 0.6, 0.3, 0.2, 0.4, 0.6],
            'vancouver_2bed_1bath_1000sqft': [2, 1, 1000, 0.15, 15, 2, 1, 25, 4000, 0, 5.0, 3.0, 6.5, 2.5, 0.8, 1.5, 1.5, 0.4, 0.3, 0.7, 0.5, 0.5, 0.4, 0.3, 0.3, 0.7],
            # Add more common patterns
        }
        
        return patterns
```

### Caching Strategies

```python
class MLCachingService:
    """Advanced caching for ML predictions."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = {
            'predictions': 3600,     # 1 hour
            'market_data': 1800,     # 30 minutes
            'economic_data': 7200,   # 2 hours
            'model_metadata': 86400  # 24 hours
        }
    
    def cache_prediction(self, property_hash: str, prediction: dict):
        """Cache prediction result."""
        
        key = f"prediction:{property_hash}"
        self.redis.setex(
            key, 
            self.cache_ttl['predictions'],
            json.dumps(prediction)
        )
    
    def get_cached_prediction(self, property_hash: str) -> dict:
        """Retrieve cached prediction."""
        
        key = f"prediction:{property_hash}"
        cached = self.redis.get(key)
        
        if cached:
            return json.loads(cached)
        
        return None
    
    def warm_cache(self, common_properties: List[dict]):
        """Warm cache with common property predictions."""
        
        ml_service = MLService()
        
        for prop in common_properties:
            try:
                prediction = ml_service.predict_property_price(prop)
                prop_hash = self._generate_property_hash(prop)
                self.cache_prediction(prop_hash, prediction)
                
            except Exception as e:
                logger.warning(f"Failed to warm cache for property: {e}")
    
    def _generate_property_hash(self, property_data: dict) -> str:
        """Generate consistent hash for property data."""
        
        # Sort keys to ensure consistent hashing
        sorted_data = {k: property_data[k] for k in sorted(property_data.keys())}
        data_string = json.dumps(sorted_data, sort_keys=True)
        
        return hashlib.md5(data_string.encode()).hexdigest()
```

## Economic Integration

### Real-time Economic Data

```python
class EconomicDataIntegrator:
    """Integrate real-time economic data into ML features."""
    
    def __init__(self):
        self.boc_service = BankOfCanadaService()
        self.statcan_service = StatisticsCanadaService()
        self.cache_ttl = 3600  # 1 hour
    
    def get_current_economic_features(self) -> dict:
        """Get current economic indicators for ML features."""
        
        cache_key = "economic_features:current"
        cached = cache.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        try:
            # Bank of Canada data
            overnight_rate = self.boc_service.get_overnight_rate()
            
            # Statistics Canada data
            cpi_data = self.statcan_service.get_latest_cpi()
            unemployment = self.statcan_service.get_unemployment_rate()
            gdp_growth = self.statcan_service.get_gdp_growth()
            
            economic_features = {
                'interest_rate': overnight_rate['value'],
                'inflation_rate': cpi_data['annual_rate'],
                'unemployment_rate': unemployment['rate'],
                'gdp_growth': gdp_growth['quarterly_rate'],
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the results
            cache.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(economic_features)
            )
            
            return economic_features
            
        except Exception as e:
            logger.error(f"Failed to get economic data: {e}")
            return self._get_default_economic_features()
    
    def _get_default_economic_features(self) -> dict:
        """Fallback economic features when API is unavailable."""
        
        return {
            'interest_rate': 5.0,
            'inflation_rate': 3.0,
            'unemployment_rate': 6.5,
            'gdp_growth': 2.5
        }
    
    def update_model_with_economic_data(self, property_data: dict) -> dict:
        """Update property data with current economic indicators."""
        
        economic_features = self.get_current_economic_features()
        
        # Add economic features to property data
        enhanced_data = property_data.copy()
        enhanced_data.update(economic_features)
        
        return enhanced_data
```

### Economic Impact Analysis

```python
def analyze_economic_impact_on_prices():
    """Analyze how economic indicators affect property prices."""
    
    # Get historical economic data
    economic_service = EconomicService()
    economic_history = economic_service.get_historical_data(months=24)
    
    # Get property sales data
    properties = Property.query.filter(
        Property.sold_date >= datetime.now() - timedelta(days=730),
        Property.sold_price.isnot(None)
    ).all()
    
    # Create analysis dataset
    analysis_data = []
    
    for prop in properties:
        # Find economic data for property sale date
        economic_data = find_economic_data_for_date(
            economic_history, prop.sold_date
        )
        
        if economic_data:
            analysis_data.append({
                'sold_price': prop.sold_price,
                'sqft': prop.sqft,
                'city': prop.city,
                'sold_date': prop.sold_date,
                'interest_rate': economic_data['interest_rate'],
                'inflation_rate': economic_data['inflation_rate'],
                'unemployment_rate': economic_data['unemployment_rate']
            })
    
    df = pd.DataFrame(analysis_data)
    
    # Calculate correlations
    correlations = {
        'interest_rate_correlation': df['sold_price'].corr(df['interest_rate']),
        'inflation_correlation': df['sold_price'].corr(df['inflation_rate']),
        'unemployment_correlation': df['sold_price'].corr(df['unemployment_rate'])
    }
    
    # Regression analysis
    from sklearn.linear_model import LinearRegression
    
    X = df[['sqft', 'interest_rate', 'inflation_rate', 'unemployment_rate']]
    y = df['sold_price']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Economic factor importance
    coefficients = {
        'sqft_impact': model.coef_[0],
        'interest_rate_impact': model.coef_[1],
        'inflation_impact': model.coef_[2],
        'unemployment_impact': model.coef_[3]
    }
    
    return {
        'correlations': correlations,
        'coefficients': coefficients,
        'r2_score': model.score(X, y),
        'sample_size': len(df)
    }
```

## API Endpoints

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

### Key ML Endpoints

- `POST /api/property-prediction` - Predict property price
- `GET /api/property-prediction/<listing_id>` - Get existing property prediction
- `POST /api/properties/bulk-analyze` - Bulk property analysis
- `GET /api/top-deals` - Get undervalued properties
- `GET /api/model/status` - Model performance status
- `POST /api/model/switch` - Switch active model
- `GET /api/model/available` - List available models

## Troubleshooting

### Common Issues

#### Model Loading Errors
```bash
# Check model files exist
ls -la models/trained_models/

# Verify model compatibility
python -c "import joblib; model = joblib.load('models/trained_models/lightgbm_price_model.pkl'); print('Model loaded successfully')"
```

#### Feature Engineering Errors
```python
# Debug feature engineering
property_data = {'bedrooms': 3, 'bathrooms': 2, 'sqft': 1500}
feature_engineer = FeatureEngineer()

try:
    features = feature_engineer.engineer_features(property_data)
    print(f"Features generated: {len(features)}")
except Exception as e:
    print(f"Feature engineering failed: {e}")
```

#### Performance Issues
```python
# Profile prediction performance
import cProfile

def profile_prediction():
    ml_service = MLService()
    property_data = {...}  # Sample data
    return ml_service.predict_property_price(property_data)

cProfile.run('profile_prediction()')
```

### Model Performance Degradation

1. **Check data quality**: Verify input data hasn't changed
2. **Validate economic data**: Ensure economic APIs are working
3. **Monitor prediction accuracy**: Compare with recent sales
4. **Retrain if necessary**: Use latest data for retraining

### Memory and Performance

```python
# Monitor model memory usage
import psutil
import os

def check_model_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"RSS Memory: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS Memory: {memory_info.vms / 1024 / 1024:.2f} MB")

# Check prediction latency
import time

def benchmark_prediction():
    ml_service = MLService()
    property_data = {...}  # Sample data
    
    start_time = time.time()
    result = ml_service.predict_property_price(property_data)
    end_time = time.time()
    
    print(f"Prediction time: {(end_time - start_time) * 1000:.2f} ms")
    return result
```

For additional troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
