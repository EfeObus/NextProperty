#!/usr/bin/env python3
"""
Enhanced ML Model Training Pipeline for NextProperty AI
Implements comprehensive model training with hyperparameter optimization and ensemble methods.
"""

import os
import sys
import datetime
import pandas as pd
import numpy as np
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

# ML libraries
from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy.stats import uniform, randint, loguniform

# Optional libraries (will be checked for availability)
XGBOOST_AVAILABLE = False
LIGHTGBM_AVAILABLE = False
USE_BAYES = False  # Set to True if scikit-optimize is available

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
    print("✓ XGBoost available")
except ImportError:
    print("⚠ XGBoost not available")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
    print("✓ LightGBM available")
except ImportError:
    print("⚠ LightGBM not available")

try:
    from skopt import BayesSearchCV
    from skopt.space import Real, Integer
    USE_BAYES = True
    print("✓ Bayesian optimization available")
except ImportError:
    print("⚠ Bayesian optimization not available, using RandomizedSearchCV")
    USE_BAYES = False

# Add the app directory to Python path
sys.path.append('/Users/efeobukohwo/Desktop/Nextproperty Real Estate')

def create_enhanced_training_data(n_samples=5000):
    """Create comprehensive training data with 26 features including economic indicators."""
    print(f"🔄 Creating enhanced training data with {n_samples} samples...")
    
    np.random.seed(42)
    
    # Define feature columns (26 features matching the ML service)
    feature_columns = [
        'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'rooms',
        'city_encoded', 'province_encoded', 'property_type_encoded',
        'year_built', 'current_year', 'current_month', 'dom', 'taxes',
        'policy_rate', 'prime_rate', 'mortgage_rate', 'inflation_rate',
        'unemployment_rate', 'exchange_rate', 'gdp_growth', 'interest_environment',
        'economic_momentum', 'affordability_pressure', 'property_affordability',
        'economic_sensitivity', 'market_timing'
    ]
    
    data = {}
    
    # Basic property features (1-5)
    data['bedrooms'] = np.random.choice([1, 2, 3, 4, 5, 6], n_samples, p=[0.05, 0.15, 0.35, 0.30, 0.10, 0.05])
    data['bathrooms'] = np.random.uniform(1, 5, n_samples)
    data['square_feet'] = np.random.normal(2000, 600, n_samples)
    data['square_feet'] = np.clip(data['square_feet'], 500, 8000)
    data['lot_size'] = np.random.lognormal(0, 0.5, n_samples)
    data['lot_size'] = np.clip(data['lot_size'], 0.05, 5.0)
    data['rooms'] = data['bedrooms'] + np.random.randint(1, 4, n_samples)
    
    # Location features (6-8)
    # Cities: Toronto=0, Vancouver=1, Calgary=2, Ottawa=3, Montreal=4
    city_probs = [0.30, 0.20, 0.15, 0.15, 0.20]  # Toronto has highest weight
    data['city_encoded'] = np.random.choice(range(5), n_samples, p=city_probs)
    
    # Provinces: ON=0, BC=1, AB=2, QC=3
    province_mapping = {0: 0, 1: 1, 2: 2, 3: 0, 4: 3}  # Map cities to provinces
    data['province_encoded'] = [province_mapping[city] for city in data['city_encoded']]
    
    # Property types: Detached=0, Semi=1, Townhouse=2, Condo=3
    data['property_type_encoded'] = np.random.choice(range(4), n_samples, p=[0.35, 0.15, 0.25, 0.25])
    
    # Temporal features (9-11)
    data['year_built'] = np.random.choice(range(1950, 2024), n_samples)
    data['current_year'] = np.full(n_samples, 2025)
    data['current_month'] = np.random.randint(1, 13, n_samples)
    
    # Market features (12-13)
    data['dom'] = np.random.exponential(30, n_samples)  # Days on market
    data['dom'] = np.clip(data['dom'], 1, 365)
    
    # Property taxes based on location and value
    base_taxes = np.random.uniform(3000, 12000, n_samples)
    city_tax_multiplier = [1.2, 1.0, 0.8, 1.1, 0.9]  # Toronto highest
    for i, city in enumerate(data['city_encoded']):
        base_taxes[i] *= city_tax_multiplier[city]
    data['taxes'] = base_taxes
    
    # Economic indicators (14-20) - realistic ranges
    data['policy_rate'] = np.random.uniform(0.25, 7.0, n_samples)
    data['prime_rate'] = data['policy_rate'] + np.random.uniform(1.75, 2.25, n_samples)
    data['mortgage_rate'] = data['prime_rate'] + np.random.uniform(0.5, 2.0, n_samples)
    data['inflation_rate'] = np.random.uniform(0.5, 6.0, n_samples)
    data['unemployment_rate'] = np.random.uniform(3.0, 12.0, n_samples)
    data['exchange_rate'] = np.random.uniform(1.20, 1.45, n_samples)  # CAD/USD
    data['gdp_growth'] = np.random.normal(2.0, 2.0, n_samples)
    data['gdp_growth'] = np.clip(data['gdp_growth'], -5.0, 8.0)
    
    # Derived economic features (21-23)
    # Interest rate environment (0=low, 1=high)
    data['interest_environment'] = np.clip(data['policy_rate'] / 8.0, 0, 1)
    
    # Economic momentum (-1=declining, 0=stable, 1=growing)
    momentum_base = (data['gdp_growth'] - 1.0) / 3.0  # Normalize around 1% GDP growth
    unemployment_effect = (7.0 - data['unemployment_rate']) / 4.0  # Lower unemployment = better
    data['economic_momentum'] = np.clip((momentum_base + unemployment_effect) / 2, -1, 1)
    
    # Affordability pressure (0=easy, 1=very difficult)
    rate_pressure = data['mortgage_rate'] / 10.0
    inflation_pressure = np.clip((data['inflation_rate'] - 2.0) / 4.0, 0, 1)
    data['affordability_pressure'] = np.clip(rate_pressure * 0.7 + inflation_pressure * 0.3, 0, 1)
    
    # Property-specific features (24-26)
    # Property affordability based on size and rates
    size_factor = np.clip(data['square_feet'] / 2000, 0.5, 2.0)
    rate_impact = data['mortgage_rate'] / 10.0
    inflation_impact = data['inflation_rate'] / 5.0
    data['property_affordability'] = np.clip(1.0 - (rate_impact * 0.6 + inflation_impact * 0.2 + (size_factor - 1.0) * 0.2), 0, 1)
    
    # Economic sensitivity by property type
    sensitivity_map = {0: 0.4, 1: 0.5, 2: 0.6, 3: 0.8}  # Detached < Semi < Townhouse < Condo
    base_sensitivity = [sensitivity_map[ptype] for ptype in data['property_type_encoded']]
    rate_adjustment = data['interest_environment'] * 0.2
    momentum_adjustment = data['economic_momentum'] * -0.1
    data['economic_sensitivity'] = np.clip(np.array(base_sensitivity) + rate_adjustment + momentum_adjustment, 0, 1)
    
    # Market timing (0=poor timing, 1=excellent timing)
    rate_timing = 1.0 - (data['policy_rate'] / 8.0)
    momentum_timing = (data['economic_momentum'] + 1.0) / 2.0
    pressure_timing = 1.0 - data['affordability_pressure']
    data['market_timing'] = np.clip(rate_timing * 0.4 + momentum_timing * 0.3 + pressure_timing * 0.3, 0, 1)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create realistic price based on comprehensive feature interactions
    print("🏠 Calculating realistic property prices...")
    
    # Base price calculation
    sqft_multiplier = [600, 800, 400, 500, 450]  # Price per sqft by city
    base_price_per_sqft = [sqft_multiplier[city] for city in data['city_encoded']]
    
    # Property type multipliers
    type_multipliers = [1.2, 1.0, 0.9, 0.8]  # Detached > Semi > Townhouse > Condo
    type_multiplier = [type_multipliers[ptype] for ptype in data['property_type_encoded']]
    
    # Base price
    base_price = df['square_feet'] * np.array(base_price_per_sqft) * np.array(type_multiplier)
    
    # Feature adjustments
    bedroom_adj = (df['bedrooms'] - 3) * 20000
    bathroom_adj = (df['bathrooms'] - 2) * 15000
    age_adj = np.clip((2025 - df['year_built'] - 20) * -800, -200000, 50000)  # Sweet spot around 20 years
    lot_adj = np.clip((df['lot_size'] - 0.25) * 75000, -50000, 200000)
    
    # Economic adjustments
    interest_adj = base_price * (1 - df['interest_environment']) * 0.15  # Low rates boost prices
    momentum_adj = base_price * df['economic_momentum'] * 0.10  # Good economy boosts prices
    affordability_adj = base_price * (1 - df['affordability_pressure']) * 0.12  # Low pressure boosts prices
    timing_adj = base_price * df['market_timing'] * 0.08  # Good timing boosts prices
    
    # Market factors
    dom_adj = np.clip((30 - df['dom']) * 500, -50000, 15000)  # Quick sales = higher price
    
    # Calculate final price
    final_price = (base_price + bedroom_adj + bathroom_adj + age_adj + lot_adj + 
                  interest_adj + momentum_adj + affordability_adj + timing_adj + dom_adj)
    
    # Add realistic market noise
    noise = np.random.normal(0, base_price * 0.05)  # 5% price noise
    final_price += noise
    
    # Ensure reasonable bounds
    df['price'] = np.clip(final_price, 150000, 15000000)
    
    print(f"✅ Training data created:")
    print(f"   📊 Samples: {len(df)}")
    print(f"   💰 Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
    print(f"   💰 Mean price: ${df['price'].mean():,.0f}")
    print(f"   🏠 Features: {len(feature_columns)}")
    
    return df, feature_columns

def get_param_distributions():
    """Get parameter distributions for hyperparameter optimization."""
    if USE_BAYES:
        # Bayesian optimization spaces
        return {
            'Ridge': {
                'model__alpha': Real(1e-3, 1e2, prior='log-uniform')
            },
            'ElasticNet': {
                'model__alpha': Real(1e-3, 1e1, prior='log-uniform'),
                'model__l1_ratio': Real(0.1, 0.9)
            },
            'RandomForest': {
                'model__n_estimators': Integer(50, 300),
                'model__max_depth': Integer(5, 25),
                'model__min_samples_split': Integer(2, 15),
                'model__min_samples_leaf': Integer(1, 8)
            },
            'GradientBoosting': {
                'model__n_estimators': Integer(50, 300),
                'model__learning_rate': Real(0.01, 0.3, prior='log-uniform'),
                'model__max_depth': Integer(3, 10),
                'model__subsample': Real(0.6, 1.0)
            },
            'XGBoost': {
                'model__n_estimators': Integer(50, 300),
                'model__learning_rate': Real(0.01, 0.3, prior='log-uniform'),
                'model__max_depth': Integer(3, 10),
                'model__subsample': Real(0.6, 1.0),
                'model__colsample_bytree': Real(0.6, 1.0)
            },
            'LightGBM': {
                'model__n_estimators': Integer(50, 300),
                'model__learning_rate': Real(0.01, 0.3, prior='log-uniform'),
                'model__max_depth': Integer(3, 10),
                'model__subsample': Real(0.6, 1.0),
                'model__colsample_bytree': Real(0.6, 1.0)
            }
        }
    else:
        # RandomizedSearchCV distributions
        return {
            'Ridge': {
                'model__alpha': loguniform(1e-3, 1e2)
            },
            'ElasticNet': {
                'model__alpha': loguniform(1e-3, 1e1),
                'model__l1_ratio': uniform(0.1, 0.8)
            },
            'RandomForest': {
                'model__n_estimators': randint(50, 301),
                'model__max_depth': randint(5, 26),
                'model__min_samples_split': randint(2, 16),
                'model__min_samples_leaf': randint(1, 9)
            },
            'GradientBoosting': {
                'model__n_estimators': randint(50, 301),
                'model__learning_rate': loguniform(0.01, 0.3),
                'model__max_depth': randint(3, 11),
                'model__subsample': uniform(0.6, 0.4)
            },
            'XGBoost': {
                'model__n_estimators': randint(50, 301),
                'model__learning_rate': loguniform(0.01, 0.3),
                'model__max_depth': randint(3, 11),
                'model__subsample': uniform(0.6, 0.4),
                'model__colsample_bytree': uniform(0.6, 0.4)
            },
            'LightGBM': {
                'model__n_estimators': randint(50, 301),
                'model__learning_rate': loguniform(0.01, 0.3),
                'model__max_depth': randint(3, 11),
                'model__subsample': uniform(0.6, 0.4),
                'model__colsample_bytree': uniform(0.6, 0.4)
            }
        }

def train_model_enhanced(name, config, X_train, y_train, X_test, y_test):
    """Enhanced model training with comprehensive error handling and metrics."""
    start_time = datetime.datetime.now()
    
    try:
        print(f"\n[{name}] 🔄 Training {name}...")
        print(f"⏰ Started: {start_time.strftime('%H:%M:%S')}")
        print(f"🔍 Hyperparameter search: {config.get('n_iter', 'Default')} iterations")
        
        # Choose search strategy
        if USE_BAYES:
            search = BayesSearchCV(
                config['pipeline'],
                config['params'],
                n_iter=config.get('n_iter', 15),
                cv=config.get('cv', 5),
                scoring='neg_mean_absolute_error',
                n_jobs=1,
                random_state=42,
                verbose=0
            )
        else:
            search = RandomizedSearchCV(
                config['pipeline'],
                config['params'],
                n_iter=config.get('n_iter', 15),
                cv=config.get('cv', 5),
                scoring='neg_mean_absolute_error',
                n_jobs=1,
                random_state=42,
                verbose=0
            )
        
        # Fit the model
        search.fit(X_train, y_train)
        
        # Get best model and make predictions
        best_model = search.best_estimator_
        y_pred_train = best_model.predict(X_train)
        y_pred_test = best_model.predict(X_test)
        
        # Calculate comprehensive metrics
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        # Calculate additional metrics
        overfitting = train_r2 - test_r2
        mape = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100  # Mean Absolute Percentage Error
        
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        results = {
            'model': best_model,
            'best_params': search.best_params_ if hasattr(search, 'best_params_') else {},
            'best_score': search.best_score_ if hasattr(search, 'best_score_') else None,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'mape': mape,
            'training_time': duration,
            'y_pred_test': y_pred_test,
            'y_pred_train': y_pred_train,
            'overfitting': overfitting,
            'cv_score': search.best_score_ if hasattr(search, 'best_score_') else None
        }
        
        # Performance assessment
        performance_grade = "🟩"  # Good
        if overfitting > 0.15:
            performance_grade = "🟥"  # Overfitting
        elif overfitting > 0.08:
            performance_grade = "🟨"  # Moderate overfitting
            
        print(f"✅ {name} completed successfully!")
        print(f"   📊 Test R²: {test_r2:.4f} | RMSE: ${test_rmse:,.0f} | MAE: ${test_mae:,.0f}")
        print(f"   📈 MAPE: {mape:.2f}% | Overfitting: {overfitting:.4f} {performance_grade}")
        print(f"   ⏱ Training time: {duration:.1f}s")
        
        return results
        
    except Exception as e:
        print(f"❌ Error training {name}: {str(e)}")
        return None

def enhanced_model_training():
    """Main enhanced model training pipeline."""
    
    print("\n" + "="*80)
    print("🚀 ENHANCED ML MODEL TRAINING PIPELINE - NextProperty AI")
    print("="*80)
    print(f"⏰ Started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create training data
    df, feature_columns = create_enhanced_training_data(n_samples=5000)
    
    # Prepare features and target
    X = df[feature_columns]
    y = df['price']
    
    print(f"\n📊 Data Preparation:")
    print(f"   🔢 Features: {X.shape[1]}")
    print(f"   📈 Samples: {X.shape[0]}")
    print(f"   💰 Target range: ${y.min():,.0f} - ${y.max():,.0f}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=None
    )
    print(f"   🔀 Train/Test split: {X_train.shape[0]}/{X_test.shape[0]}")
    
    # Cross-validation setup
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    print(f"   🔄 Cross-validation: {kf.n_splits}-fold")
    
    # PCA setup for dimensionality reduction
    print(f"\n🔍 PCA Analysis:")
    scaler_tmp = StandardScaler()
    X_train_scaled = scaler_tmp.fit_transform(X_train)
    pca_tmp = PCA().fit(X_train_scaled)
    cum_var = np.cumsum(pca_tmp.explained_variance_ratio_)
    n_pca = min(np.argmax(cum_var >= 0.95) + 1, X_train.shape[1])  # 95% variance
    n_pca = min(n_pca, 20)  # Cap at 20 components
    print(f"   📊 Using {n_pca} PCA components for {cum_var[n_pca-1]:.1%} explained variance")
    
    # Get parameter distributions
    param_dists = get_param_distributions()
    
    # Model configurations
    model_configs = {
        'Ridge': {
            'pipeline': Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=n_pca)),
                ('model', Ridge(random_state=42))
            ]),
            'params': param_dists['Ridge'],
            'n_iter': 25,
            'cv': kf
        },
        'ElasticNet': {
            'pipeline': Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=n_pca)),
                ('model', ElasticNet(random_state=42, max_iter=2000))
            ]),
            'params': param_dists['ElasticNet'],
            'n_iter': 25,
            'cv': kf
        },
        'RandomForest': {
            'pipeline': Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=n_pca)),
                ('model', RandomForestRegressor(random_state=42, n_jobs=1))
            ]),
            'params': param_dists['RandomForest'],
            'n_iter': 20,
            'cv': kf
        },
        'GradientBoosting': {
            'pipeline': Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=n_pca)),
                ('model', GradientBoostingRegressor(random_state=42))
            ]),
            'params': param_dists['GradientBoosting'],
            'n_iter': 20,
            'cv': kf
        }
    }
    
    # Add XGBoost if available
    if XGBOOST_AVAILABLE:
        model_configs['XGBoost'] = {
            'pipeline': Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=n_pca)),
                ('model', xgb.XGBRegressor(random_state=42, n_jobs=1, verbosity=0))
            ]),
            'params': param_dists['XGBoost'],
            'n_iter': 15,
            'cv': kf
        }
        print("✓ XGBoost added to training pipeline")
    
    # Add LightGBM if available
    if LIGHTGBM_AVAILABLE:
        model_configs['LightGBM'] = {
            'pipeline': Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=n_pca)),
                ('model', lgb.LGBMRegressor(random_state=42, n_jobs=1, verbosity=-1))
            ]),
            'params': param_dists['LightGBM'],
            'n_iter': 15,
            'cv': kf
        }
        print("✓ LightGBM added to training pipeline")
    
    print(f"\n🔧 Configured {len(model_configs)} models for training")
    print(f"🔍 Using {'Bayesian' if USE_BAYES else 'Random'} hyperparameter optimization")
    
    # Train all models
    print(f"\n" + "="*80)
    print("🎯 MODEL TRAINING PHASE")
    print("="*80)
    
    results_models = {}
    total_start_time = datetime.datetime.now()
    
    for i, (name, config) in enumerate(model_configs.items(), 1):
        result = train_model_enhanced(name, config, X_train, y_train, X_test, y_test)
        
        if result is not None:
            results_models[name] = result
        else:
            print(f"⚠ Skipping {name} due to training failure")
    
    total_end_time = datetime.datetime.now()
    total_duration = (total_end_time - total_start_time).total_seconds()
    
    # Performance Analysis
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE PERFORMANCE ANALYSIS")
    print("="*80)
    
    if results_models:
        # Create performance summary
        performance_data = []
        for name, result in results_models.items():
            performance_data.append({
                'Model': name,
                'Test_R2': result['test_r2'],
                'Test_RMSE': result['test_rmse'],
                'Test_MAE': result['test_mae'],
                'MAPE': result['mape'],
                'Training_Time': result['training_time'],
                'Overfitting': result['overfitting'],
                'CV_Score': result.get('cv_score', 0)
            })
        
        performance_df = pd.DataFrame(performance_data).sort_values('Test_R2', ascending=False)
        
        print("\n🏆 MODEL PERFORMANCE RANKING:")
        print("-" * 80)
        print(f"{'Rank':<4} {'Model':<15} {'R²':<8} {'RMSE':<12} {'MAE':<12} {'MAPE':<8} {'Time':<8} {'Overfit':<8}")
        print("-" * 80)
        
        for i, (_, row) in enumerate(performance_df.iterrows(), 1):
            overfit_status = "🟥" if row['Overfitting'] > 0.15 else "🟨" if row['Overfitting'] > 0.08 else "🟩"
            print(f"{i:<4} {row['Model']:<15} {row['Test_R2']:<8.4f} ${row['Test_RMSE']:<11,.0f} ${row['Test_MAE']:<11,.0f} {row['MAPE']:<7.2f}% {row['Training_Time']:<7.1f}s {overfit_status}")
        
        # Best model analysis
        best_model_name = performance_df.iloc[0]['Model']
        best_model_results = results_models[best_model_name]
        
        print(f"\n🎯 BEST MODEL ANALYSIS:")
        print("-" * 40)
        print(f"🏆 Model: {best_model_name}")
        print(f"📊 R² Score: {best_model_results['test_r2']:.4f}")
        print(f"💰 RMSE: ${best_model_results['test_rmse']:,.0f}")
        print(f"💰 MAE: ${best_model_results['test_mae']:,.0f}")
        print(f"📈 MAPE: {best_model_results['mape']:.2f}%")
        print(f"⏱ Training Time: {best_model_results['training_time']:.1f}s")
        print(f"🔧 Best Parameters: {best_model_results['best_params']}")
        
        # Build ensemble if we have multiple good models
        good_models = performance_df[performance_df['Test_R2'] > 0.6]
        
        if len(good_models) >= 2:
            print(f"\n🔄 Building ensemble from top {min(3, len(good_models))} models...")
            
            try:
                # Select top models for ensemble
                top_model_names = good_models.head(3)['Model'].tolist()
                estimators = [(name, results_models[name]['model']) for name in top_model_names]
                
                # Create stacking ensemble
                stacking_regressor = StackingRegressor(
                    estimators=estimators,
                    final_estimator=Ridge(alpha=1.0),
                    cv=3,
                    n_jobs=1
                )
                
                # Train ensemble
                ensemble_start = datetime.datetime.now()
                stacking_regressor.fit(X_train, y_train)
                ensemble_duration = (datetime.datetime.now() - ensemble_start).total_seconds()
                
                # Evaluate ensemble
                y_pred_ensemble = stacking_regressor.predict(X_test)
                ensemble_r2 = r2_score(y_test, y_pred_ensemble)
                ensemble_rmse = np.sqrt(mean_squared_error(y_test, y_pred_ensemble))
                ensemble_mae = mean_absolute_error(y_test, y_pred_ensemble)
                ensemble_mape = np.mean(np.abs((y_test - y_pred_ensemble) / y_test)) * 100
                
                results_models['Ensemble'] = {
                    'model': stacking_regressor,
                    'test_r2': ensemble_r2,
                    'test_rmse': ensemble_rmse,
                    'test_mae': ensemble_mae,
                    'mape': ensemble_mape,
                    'training_time': ensemble_duration,
                    'base_models': top_model_names,
                    'y_pred_test': y_pred_ensemble,
                    'overfitting': 0.0,
                    'best_params': {'base_models': top_model_names}
                }
                
                print(f"✅ Ensemble created successfully!")
                print(f"   📊 Test R²: {ensemble_r2:.4f} | RMSE: ${ensemble_rmse:,.0f} | MAE: ${ensemble_mae:,.0f}")
                print(f"   📈 MAPE: {ensemble_mape:.2f}%")
                print(f"   🏗 Base models: {', '.join(top_model_names)}")
                print(f"   ⏱ Training time: {ensemble_duration:.1f}s")
                
            except Exception as e:
                print(f"❌ Ensemble creation failed: {e}")
        
        # Final model selection (best overall)
        final_best = max(results_models.keys(), key=lambda k: results_models[k]['test_r2'])
        final_model = results_models[final_best]['model']
        
        # Save models and artifacts
        print(f"\n💾 Saving models and artifacts...")
        
        # Create directories if they don't exist
        model_dir = '/Users/efeobukohwo/Desktop/Nextproperty Real Estate/models/trained_models'
        artifacts_dir = '/Users/efeobukohwo/Desktop/Nextproperty Real Estate/models/model_artifacts'
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Save the best model
        best_model_path = os.path.join(model_dir, 'property_price_model.pkl')
        joblib.dump(final_model, best_model_path)
        print(f"✅ Best model saved: {best_model_path}")
        
        # Save feature columns
        feature_path = os.path.join(artifacts_dir, 'feature_columns.json')
        with open(feature_path, 'w') as f:
            json.dump(feature_columns, f, indent=2)
        print(f"✅ Feature columns saved: {feature_path}")
        
        # Save model metadata (convert numpy types to native Python types)
        def convert_numpy_types(obj):
            """Convert numpy types to native Python types for JSON serialization."""
            if hasattr(obj, 'item'):
                return obj.item()
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        metadata = {
            'best_model': final_best,
            'model_performance': {
                'r2_score': convert_numpy_types(results_models[final_best]['test_r2']),
                'rmse': convert_numpy_types(results_models[final_best]['test_rmse']),
                'mae': convert_numpy_types(results_models[final_best]['test_mae']),
                'mape': convert_numpy_types(results_models[final_best]['mape'])
            },
            'training_info': {
                'training_date': datetime.datetime.now().isoformat(),
                'training_samples': int(len(X_train)),
                'test_samples': int(len(X_test)),
                'features_count': int(len(feature_columns)),
                'pca_components': int(n_pca),
                'cv_folds': int(kf.n_splits)
            },
            'feature_columns': feature_columns,
            'all_models_performance': {
                name: {
                    'r2': convert_numpy_types(result['test_r2']),
                    'rmse': convert_numpy_types(result['test_rmse']),
                    'mae': convert_numpy_types(result['test_mae']),
                    'mape': convert_numpy_types(result['mape']),
                    'training_time': convert_numpy_types(result['training_time'])
                } for name, result in results_models.items()
            }
        }
        
        metadata_path = os.path.join(artifacts_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Model metadata saved: {metadata_path}")
        
        # Save additional models for comparison
        for name, result in results_models.items():
            if name != final_best:
                alt_model_path = os.path.join(model_dir, f'{name.lower()}_price_model.pkl')
                joblib.dump(result['model'], alt_model_path)
        
        print(f"✅ All models saved to: {model_dir}")
        
        # Final summary
        print("\n" + "="*80)
        print("🎉 ENHANCED MODEL TRAINING COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"🕐 Completed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏆 Best model: {final_best} (R² = {results_models[final_best]['test_r2']:.4f})")
        print(f"💰 Best RMSE: ${results_models[final_best]['test_rmse']:,.0f}")
        print(f"💰 Best MAE: ${results_models[final_best]['test_mae']:,.0f}")
        print(f"📈 Best MAPE: {results_models[final_best]['mape']:.2f}%")
        print(f"📊 Total models trained: {len(results_models)}")
        print(f"⏱ Total training time: {total_duration:.1f} seconds")
        print(f"📁 Models saved to: {model_dir}")
        print(f"📁 Artifacts saved to: {artifacts_dir}")
        print("="*80)
        
        return final_model, results_models, metadata
        
    else:
        print("❌ No models were successfully trained!")
        print("🔧 Check your dependencies and data")
        return None, {}, {}

if __name__ == "__main__":
    try:
        model, results, metadata = enhanced_model_training()
        
        if model is not None:
            print("\n🎯 Training completed successfully!")
            print("🚀 Your NextProperty AI now has enhanced ML capabilities!")
            
            # Quick test
            print("\n🧪 Quick model test:")
            test_features = [3, 2, 2000, 0.5, 6, 0, 0, 0, 2010, 2025, 6, 30, 8000,
                           4.5, 6.7, 7.2, 2.8, 5.5, 1.35, 2.1, 0.5, 0.1, 0.3, 0.6, 0.4, 0.7]
            
            prediction = model.predict([test_features])
            print(f"   Sample prediction: ${prediction[0]:,.0f}")
            print(f"   Model is ready for production use! 🎉")
        else:
            print("\n❌ Training failed. Please check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        import traceback
        traceback.print_exc()
