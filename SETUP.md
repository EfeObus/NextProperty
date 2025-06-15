# 🏠 NextProperty AI - Setup Guide

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/EfeObus/NextProperty_AI.git
cd NextProperty_AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
# Add your API keys for Bank of Canada and Statistics Canada if available
```

### 4. Database Setup
```bash
# Initialize the database
flask db upgrade

# Load sample data (optional)
python scripts/load_data.py
```

### 5. Run the Application
```bash
python app.py
```

Visit `http://localhost:5007` to access the application.

## 📁 Missing Files (Due to GitHub Size Limits)

Some large files were excluded from the repository. Here's how to obtain them:

### Large Dataset Files
The following files are excluded but can be recreated:

- `Dataset/realEstate.csv` (113MB) - Main dataset
- `Dataset/large_sample_real_estate.csv` (2MB) - Extended sample

**Options:**
1. **Use the included sample**: `Dataset/sample_real_estate.csv` (170KB) works for testing
2. **Generate your own dataset**: Use the data generation scripts
3. **Contact the maintainer**: For access to the full dataset

### Large ML Model Files
The following trained models are excluded:

- `models/trained_models/randomforest_price_model.pkl` (83MB)
- `models/trained_models/property_price_model.pkl` (2.6MB)
- `models/trained_models/gradientboosting_price_model.pkl` (592KB)
- `models/trained_models/lightgbm_price_model.pkl` (323KB)
- `models/trained_models/xgboost_price_model.pkl` (413KB)

**Available models** (included):
- ✅ `elasticnet_price_model.pkl` (6.9KB)
- ✅ `ridge_price_model.pkl` (6.8KB)

**To recreate the missing models:**
```bash
# Run the model training script
python enhanced_model_training.py

# Or use the simpler retraining script
python retrain_model_26_features.py
```

## 🔧 Configuration

### API Keys (Optional)
Add these to your `.env` file for enhanced functionality:

```env
# Economic data APIs (optional for development)
BOC_API_KEY=your-bank-of-canada-api-key
STATCAN_API_KEY=your-statistics-canada-api-key

# Email configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Database Configuration
The application uses SQLite by default. To use PostgreSQL or MySQL:

```env
DATABASE_URL=postgresql://user:password@localhost/nextproperty
# or
DATABASE_URL=mysql://user:password@localhost/nextproperty
```

## 🚀 Features Available

Even without the large files, you can:

✅ **Property Price Prediction** - Using ElasticNet and Ridge models  
✅ **Economic Integration** - Real-time Bank of Canada data  
✅ **Property Search** - Interactive search and filtering  
✅ **Map Visualization** - Geospatial property display  
✅ **Admin Dashboard** - Property management interface  
✅ **API Endpoints** - RESTful API for all operations  
✅ **User Favorites** - Save and manage property lists  
✅ **Market Insights** - Economic indicators and trends  

## 📊 Sample Data

The repository includes `Dataset/sample_real_estate.csv` with sample properties from:
- Toronto, ON
- Vancouver, BC  
- Montreal, QC
- Calgary, AB
- Ottawa, ON

This is sufficient for testing all application features.

## 🧪 Testing

Run the test suite:
```bash
# All tests
pytest

# Specific test categories
pytest tests/test_api.py
pytest tests/test_models.py
pytest tests/test_services.py
```

## 📈 Model Training

To train new models with your own data:

1. **Prepare your dataset** in the same format as `sample_real_estate.csv`
2. **Place it in** `Dataset/` directory
3. **Run training**:
   ```bash
   python enhanced_model_training.py
   ```

## 🔧 Troubleshooting

### Missing Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Database Issues
```bash
# Reset database
rm instance/nextproperty_dev.db
flask db upgrade
```

### Model Errors
If prediction fails due to missing models:
```bash
# Retrain with available data
python simple_retrain.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📧 Support

For questions or issues:
- Open an issue on GitHub
- Check the documentation in `docs/`
- Review the test files for usage examples

---

**Note**: This is a complete, production-ready application. The excluded large files are optimizations - the core functionality works perfectly with the included files.
