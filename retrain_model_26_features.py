#!/usr/bin/env python3
"""
Script to retrain the ML model with 26 features including economic indicators.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.append('/Users/efeobukohwo/Desktop/Nextproperty Real Estate')

from app import create_app
from app.models.property import Property
from app.extensions import db

def create_synthetic_training_data():
    """Create synthetic training data with 26 features."""
    print("Creating synthetic training data with 26 features...")
    
    # Generate 1000 synthetic property records
    n_samples = 1000
    np.random.seed(42)
    
    # Basic property features (13 original features)
    data = {
        'bedrooms': np.random.randint(1, 6, n_samples),
        'bathrooms': np.random.uniform(1, 4, n_samples),
        'square_feet': np.random.randint(800, 4000, n_samples),
        'lot_size': np.random.uniform(0.1, 2.0, n_samples),
        'rooms': np.random.randint(3, 10, n_samples),
        'year_built': np.random.randint(1950, 2023, n_samples),
        'current_year': [2025] * n_samples,
        'current_month': np.random.randint(1, 13, n_samples),
        'dom': np.random.randint(1, 180, n_samples),
        'taxes': np.random.uniform(2000, 15000, n_samples)
    }
    
    # Categorical features (will be encoded)
    cities = ['Toronto', 'Vancouver', 'Calgary', 'Ottawa', 'Montreal']
    provinces = ['ON', 'BC', 'AB', 'ON', 'QC']
    property_types = ['Detached', 'Semi-Detached', 'Townhouse', 'Condo']
    
    data['city'] = np.random.choice(cities, n_samples)
    data['province'] = np.random.choice(provinces, n_samples)
    data['property_type'] = np.random.choice(property_types, n_samples)
    
    # Economic indicators (13 new features)
    data['policy_rate'] = np.random.uniform(1.0, 6.0, n_samples)
    data['prime_rate'] = data['policy_rate'] + np.random.uniform(1.5, 2.5, n_samples)
    data['mortgage_rate'] = data['prime_rate'] + np.random.uniform(0.5, 2.0, n_samples)
    data['inflation_rate'] = np.random.uniform(1.0, 5.0, n_samples)
    data['unemployment_rate'] = np.random.uniform(3.0, 10.0, n_samples)
    data['exchange_rate'] = np.random.uniform(1.25, 1.40, n_samples)
    data['gdp_growth'] = np.random.uniform(-2.0, 4.0, n_samples)
    data['interest_environment'] = np.random.uniform(0, 1, n_samples)
    data['economic_momentum'] = np.random.uniform(-1, 1, n_samples)
    data['affordability_pressure'] = np.random.uniform(0, 1, n_samples)
    data['property_affordability'] = np.random.uniform(0, 1, n_samples)
    data['economic_sensitivity'] = np.random.uniform(0, 1, n_samples)
    data['market_timing'] = np.random.uniform(0, 1, n_samples)
    
    df = pd.DataFrame(data)
    
    # Create realistic price based on features
    base_price = (
        df['square_feet'] * 250 +
        df['bedrooms'] * 15000 +
        df['bathrooms'] * 10000 +
        df['lot_size'] * 50000 +
        (2025 - df['year_built']) * -500  # Newer houses cost more
    )
    
    # Add city multiplier
    city_multipliers = {'Toronto': 1.5, 'Vancouver': 1.4, 'Calgary': 0.8, 'Ottawa': 1.1, 'Montreal': 0.9}
    df['city_multiplier'] = df['city'].map(city_multipliers)
    base_price *= df['city_multiplier']
    
    # Add economic effects
    economic_effect = (
        (1 - df['interest_environment']) * 0.1 +  # Low interest = higher prices
        df['economic_momentum'] * 0.05 +  # Good economy = higher prices
        (1 - df['affordability_pressure']) * 0.1  # Low pressure = higher prices
    )
    
    df['price'] = base_price * (1 + economic_effect) + np.random.normal(0, 20000, n_samples)
    df['price'] = np.maximum(df['price'], 100000)  # Minimum price
    
    return df

def train_model_with_26_features():
    """Train a new model with 26 features."""
    print("Training model with 26 features...")
    
    # Create synthetic data
    df = create_synthetic_training_data()
    
    # Encode categorical variables
    le_city = LabelEncoder()
    le_province = LabelEncoder()
    le_property_type = LabelEncoder()
    
    df['city_encoded'] = le_city.fit_transform(df['city'])
    df['province_encoded'] = le_province.fit_transform(df['province'])
    df['property_type_encoded'] = le_property_type.fit_transform(df['property_type'])
    
    # Define feature columns (26 features matching feature_columns.json)
    feature_columns = [
        'bedrooms', 'bathrooms', 'square_feet', 'lot_size', 'rooms',
        'city_encoded', 'province_encoded', 'property_type_encoded',
        'year_built', 'current_year', 'current_month', 'dom', 'taxes',
        'policy_rate', 'prime_rate', 'mortgage_rate', 'inflation_rate',
        'unemployment_rate', 'exchange_rate', 'gdp_growth', 'interest_environment',
        'economic_momentum', 'affordability_pressure', 'property_affordability',
        'economic_sensitivity', 'market_timing'
    ]
    
    # Prepare features and target
    X = df[feature_columns]
    y = df['price']
    
    print(f"Training data shape: {X.shape}")
    print(f"Features: {feature_columns}")
    
    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X, y)
    
    # Save the model
    model_path = '/Users/efeobukohwo/Desktop/Nextproperty Real Estate/models/trained_models/property_price_model.pkl'
    joblib.dump(model, model_path)
    print(f"Model saved to: {model_path}")
    
    # Save feature columns
    feature_path = '/Users/efeobukohwo/Desktop/Nextproperty Real Estate/models/model_artifacts/feature_columns.json'
    with open(feature_path, 'w') as f:
        json.dump(feature_columns, f, indent=2)
    print(f"Feature columns saved to: {feature_path}")
    
    # Save encoders
    encoders = {
        'city_encoder': le_city,
        'province_encoder': le_province,
        'property_type_encoder': le_property_type
    }
    
    encoder_path = '/Users/efeobukohwo/Desktop/Nextproperty Real Estate/models/model_artifacts/encoders.pkl'
    joblib.dump(encoders, encoder_path)
    print(f"Encoders saved to: {encoder_path}")
    
    # Test the model
    print("Testing model...")
    sample_input = X.iloc[0:1]
    prediction = model.predict(sample_input)
    print(f"Sample prediction: ${prediction[0]:,.2f}")
    
    print("Model training completed successfully!")
    return model

if __name__ == "__main__":
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            model = train_model_with_26_features()
            print("✅ Model training completed successfully!")
            print("✅ All features now support economic integration!")
            
        except Exception as e:
            print(f"❌ Error training model: {str(e)}")
            import traceback
            traceback.print_exc()
