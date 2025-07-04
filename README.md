# NextProperty AI - Real Estate Investment Platform

NextProperty AI revolutionizes property investment and management by leveraging advanced artificial intelligence solutions with comprehensive economic integration. The platform offers personalized, data-driven property analysis with real-time economic indicators to assist investors in making informed decisions.

## 🚀 Latest Updates (v2.0)

- **Enhanced ML Pipeline**: 6+ advanced models with ensemble stacking (88.3% accuracy)
- **Economic Integration**: Real-time Bank of Canada and Statistics Canada data
- **26-Feature Analysis**: Including 10 economic indicators + derived features
- **Model Management**: Complete CLI and API for model operations
- **Performance Excellence**: Best-in-class RMSE of $197K, MAPE of 9.87%

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Features](#features)
- [Enhanced ML Models](#enhanced-ml-models)
- [Economic Integration](#economic-integration)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [API Documentation](#api-documentation)
- [CLI Commands](#cli-commands)
- [REST API Endpoints](#rest-api-endpoints)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [ML Model Integration](#ml-model-integration)
- [Model Performance](#model-performance)
- [Data Sources](#data-sources)
- [Testing Strategy](#testing-strategy)
- [Deployment](#deployment)
- [Performance Optimization](#performance-optimization)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Architecture Overview

NextProperty AI features a modern, scalable architecture with enhanced ML capabilities:

```
Client ↔ API Gateway ↔ Backend Services ↔ MySQL Database
                                ↕
                    Enhanced ML Service (6+ Models)
                                ↕
                       Economic Data Integration
                                ↕
                  External APIs (BoC, StatCan, CMHC)
```

### Enhanced ML Pipeline Flow

1. **Property Analysis Request**: Client requests `/api/properties/{id}/analyze`
2. **Economic Data Fetch**: Real-time economic indicators from Bank of Canada
3. **Feature Engineering**: 26 features including economic indicators
4. **Model Ensemble**: Stacking regressor with 6+ trained models
5. **Analysis & Insights**: Comprehensive risk assessment and predictions
6. **Response Delivery**: Detailed analysis with confidence intervals

## Features

### 🏠 **Property Analysis**
- **AI-Powered Valuation**: Ensemble ML models with 88.3% accuracy
- **Investment Scoring**: 0-10 scale with economic factor integration
- **Risk Assessment**: Multi-factor risk analysis (Very Low to Very High)
- **Market Trends**: City and property-type specific trend analysis
- **Comparable Properties**: Intelligent matching within 20% size range

### 📊 **Market Intelligence**
- **Real-time Economic Integration**: Bank of Canada + Statistics Canada data
- **10 Economic Indicators**: Interest rates, inflation, unemployment, GDP growth
- **Derived Economic Features**: Market timing, affordability pressure, momentum
- **Market Predictions**: 6-month and 1-year trend forecasting
- **Economic Insights**: AI-generated insights based on economic conditions

### 🎯 **Investment Tools**
- **Top Deals Detection**: Identifies undervalued properties (≥5% below prediction)
- **Investment Potential Scoring**: Excellent, Very Good, Good, Fair ratings
- **Portfolio Analytics**: Track and analyze property investments
- **Economic Sensitivity Analysis**: Property-type specific economic impact

### 🔧 **Model Management**
- **6+ Trained Models**: Ridge, ElasticNet, RandomForest, GradientBoosting, XGBoost, LightGBM
- **Ensemble Stacking**: Combines best-performing models for superior accuracy
- **Model Switching**: Dynamic model selection via API/CLI
- **Performance Monitoring**: Automated validation and retraining recommendations
- **Hyperparameter Optimization**: RandomizedSearchCV + Bayesian optimization

## Enhanced ML Models

### 🏆 **Model Performance Rankings**

| Rank | Model | R² Score | RMSE | MAPE | Training Time |
|------|-------|----------|------|------|---------------|
| 🥇 | **Ensemble** | **0.883** | **$197K** | **9.87%** | 6.8s |
| 🥈 | XGBoost | 0.878 | $202K | 10.07% | 30.6s |
| 🥉 | LightGBM | 0.874 | $206K | 10.50% | 8.7s |
| 4 | GradientBoosting | 0.861 | $216K | 10.99% | 276.6s |
| 5 | RandomForest | 0.766 | $280K | 15.86% | 241.9s |
| 6 | Ridge | 0.714 | $310K | 17.45% | 0.6s |
| 7 | ElasticNet | 0.710 | $312K | 17.15% | 0.6s |

### 🧠 **26-Feature Engineering**

#### **Basic Property Features (5)**
- Bedrooms, Bathrooms, Square Feet, Lot Size, Total Rooms

#### **Location & Type Features (3)**
- City Encoding, Province Encoding, Property Type Encoding

#### **Temporal Features (3)**
- Year Built, Current Year, Current Month

#### **Market Features (2)**
- Days on Market (DOM), Property Taxes

#### **Economic Indicators (7)**
- Policy Rate, Prime Rate, 5-Year Mortgage Rate
- Inflation Rate, Unemployment Rate, CAD/USD Exchange Rate, GDP Growth

#### **Derived Economic Features (3)**
- Interest Rate Environment (0-1 scale)
- Economic Momentum (-1 to 1 scale)
- Affordability Pressure (0-1 scale)

#### **Property-Economic Interaction Features (3)**
- Property Affordability Index
- Economic Sensitivity Score
- Market Timing Indicator

## Economic Integration

### 📈 **Real-Time Data Sources**

#### **Bank of Canada API**
- Overnight Policy Rate
- Prime Business Rate  
- 5-Year Mortgage Rates
- Inflation Rate (CPI)
- CAD/USD Exchange Rate

#### **Statistics Canada API**
- Unemployment Rate
- GDP Growth (Quarterly)
- Employment Statistics
- Economic Indicators

#### **Derived Economic Metrics**
- **Interest Rate Environment**: Normalized 0-1 scale based on policy rate
- **Economic Momentum**: GDP + employment combined score (-1 to 1)
- **Affordability Pressure**: Mortgage rate + inflation pressure (0-1)

### 🔄 **Economic Data Pipeline**

1. **Caching Layer**: 1-hour TTL for economic indicators
2. **Fallback System**: Default values when APIs unavailable
3. **Real-time Integration**: Updates with each property analysis
4. **Historical Tracking**: Time-series storage for trend analysis

## Technology Stack

### **Backend & Core**
- **Framework**: Flask (Python 3.11+)
- **Database**: MySQL 8.0+ with optimized indexes
- **ORM**: SQLAlchemy with Flask-Migrate
- **Caching**: Redis for ML predictions and economic data

### **AI/ML Stack**
- **Models**: XGBoost, LightGBM, Scikit-learn (Ridge, ElasticNet, RandomForest, GradientBoosting)
- **Ensemble**: StackingRegressor for superior accuracy
- **Feature Engineering**: Pandas, NumPy for 26-feature extraction
- **Optimization**: RandomizedSearchCV, Bayesian optimization
- **Validation**: 5-fold cross-validation, performance monitoring

### **Economic Data Integration**
- **APIs**: Bank of Canada, Statistics Canada
- **Processing**: Real-time indicator calculation and caching
- **Storage**: Time-series economic data with trend analysis

### **Frontend & Visualization**
- **UI**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5
- **Charts**: Plotly.js, Chart.js for interactive visualizations
- **Maps**: Google Maps API for geospatial analysis

### **DevOps & Infrastructure**
- **Containerization**: Docker with multi-stage builds
- **Process Management**: Gunicorn WSGI server
- **Monitoring**: Logging with rotation, health checks
- **CLI Tools**: Flask-CLI for model management

### **External APIs**
- **Economic Data**: Bank of Canada, Statistics Canada
- **Geospatial**: Google Maps, Geocoding
- **Market Data**: MLS, CREA integration ready

## Project Structure

```
nextproperty-ai/
├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   ├── static/
│   ├── utils/
│   └── cache/
├── config/
├── migrations/
├── scripts/
├── tests/
├── data/
├── logs/
├── models/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app.py
├── wsgi.py
├── .env.example
└── README.md
```

## Installation & Setup

### Clone the Repo

```bash
git clone https://github.com/your-username/nextproperty-ai.git
cd nextproperty-ai
```

### Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Database Setup

```bash
mysql -u root -p < config/database.sql
cp .env.example .env
# edit .env with credentials & API keys
```

### Migrations & Seeding

```bash
flask db upgrade
python scripts/seed_data.py
```

### Run Application

```bash
flask run        # dev
gunicorn -w4 wsgi:app  # prod
```

## CLI Commands

NextProperty AI provides comprehensive CLI commands for data management, model operations, and system maintenance:

### Data Import/Export Commands

```bash
# Import property data with validation
flask etl import-data data/raw/realEstate.csv --data-type property --batch-size 1000 --validation-level standard

# Export properties with filters
flask etl export-properties --format csv --city Toronto --price-min 500000 --price-max 1000000

# Export with analytics (Excel format)
flask etl export-properties --format excel --include-analytics --compress

# Backup database
flask etl backup-database --format sql --compress --include-schema

# Restore from backup
flask etl restore-database backups/backup_20240615.sql.gz
```

### Model Management Commands

```bash
# Train new models with enhanced features
flask ml train-models --model-type ensemble --features 26 --cross-validation 5

# Evaluate model performance
flask ml evaluate-models --model-type all --metrics rmse,r2,mape

# Switch active model
flask ml switch-model --model-name xgboost_v2 --version 1.2

# Compare model performance
flask ml compare-models --models ensemble,xgboost,lightgbm

# Retrain with new data
flask ml retrain --incremental --batch-size 5000
```

### Economic Data Commands

```bash
# Update economic indicators
flask economic update-indicators --source all --cache-duration 3600

# Sync with Bank of Canada API
flask economic sync-boc --indicators policy_rate,prime_rate,inflation

# Update Statistics Canada data
flask economic sync-statcan --indicators unemployment,gdp_growth

# Clear economic data cache
flask economic clear-cache --confirm
```

### Data Validation & Quality

```bash
# Validate data quality
flask data validate --source properties --level comprehensive --fix-errors

# Clean duplicate properties
flask data clean-duplicates --threshold 0.95 --dry-run

# Update property geocoding
flask data update-geocoding --batch-size 100 --missing-only

# Refresh property features
flask data refresh-features --property-ids 1,2,3 --force
```

### System Maintenance

```bash
# Database optimization
flask maintenance optimize-db --analyze-tables --rebuild-indexes

# Clear application cache
flask maintenance clear-cache --type all

# Generate performance report
flask maintenance performance-report --format html --output reports/

# Health check
flask maintenance health-check --detailed
```

## API Documentation

We use OpenAPI (Swagger). To launch the interactive docs:

```bash
flask run
# Navigate to http://localhost:5000/docs
```

Examples for each endpoint, request/response schemas, status codes, pagination, and error formats are defined in `openapi.yaml`.

## REST API Endpoints

### Properties

- **GET** `/api/properties` - Get filtered property listings
  - Query params: `city`, `type`, `min_price`, `max_price`, `limit`, `offset`
- **GET** `/api/properties/{id}` - Get single property by ID
- **GET** `/api/properties/{id}/photos` - Get property images
- **GET** `/api/properties/{id}/rooms` - Get room details
- **POST** `/api/properties/{id}/analyze` - Get comprehensive AI analysis for property
- **GET** `/api/properties/{id}/comparables` - Find similar properties for comparison
- **GET** `/api/properties/{id}/investment-score` - Get investment potential score

### Enhanced ML & Analytics

- **POST** `/api/ml/predict` - Property price prediction with confidence intervals
- **GET** `/api/ml/models` - List available ML models and their performance
- **POST** `/api/ml/models/{model}/switch` - Switch active ML model
- **GET** `/api/ml/models/{model}/performance` - Get detailed model performance metrics
- **POST** `/api/ml/ensemble/predict` - Ensemble prediction using multiple models
- **GET** `/api/ml/feature-importance` - Get feature importance rankings

### Market Intelligence

- **GET** `/api/market/trends` - Get market trends with economic indicators
- **GET** `/api/market/economic-indicators` - Get real-time economic data
- **GET** `/api/market/predictions` - Get 6-month and 1-year market predictions
- **GET** `/api/market/city/{city}/analysis` - City-specific market analysis
- **GET** `/api/market/property-type/{type}/trends` - Property type specific trends

### Investment Analysis

- **GET** `/api/investment/top-deals` - Get undervalued properties (top deals)
- **POST** `/api/investment/portfolio/analyze` - Analyze investment portfolio
- **GET** `/api/investment/risk-assessment/{property_id}` - Detailed risk assessment
- **GET** `/api/investment/yield-calculator` - Calculate potential yields and ROI

### Economic Data

- **GET** `/api/economic/bank-of-canada` - Bank of Canada indicators
- **GET** `/api/economic/statistics-canada` - Statistics Canada data
- **GET** `/api/economic/derived-metrics` - Calculated economic features
- **POST** `/api/economic/refresh` - Force refresh of economic data cache

### Agents

- **GET** `/api/agents/{id}` - Get agent details
- **GET** `/api/agents/{id}/properties` - Get agent's listings
- **GET** `/api/agents/{id}/performance` - Get agent performance metrics

### Advanced Search

- **GET** `/api/search` - Advanced property search with filters
- **GET** `/api/search/geospatial` - Location-based search with radius
- **POST** `/api/search/intelligent` - AI-powered property matching
- **GET** `/api/search/suggestions` - Get search suggestions and autocomplete

## API Authentication Flows

### JWT Authentication:

1. **POST** `/api/auth/login` with credentials
2. Receive `access_token` + optional `refresh_token`
3. Use `Authorization: Bearer <token>` header until expiry
4. **Token Refresh**: **POST** `/api/auth/refresh`

### OAuth2: 
Configurable third-party providers via `/api/auth/oauth/{provider}`

## Model Performance

### 🎯 **Performance Metrics Overview**

Our ensemble ML model achieves industry-leading accuracy with comprehensive validation:

| Metric | Value | Industry Benchmark |
|--------|-------|-------------------|
| **R² Score** | **0.883** | 0.75-0.85 |
| **RMSE** | **$197,000** | $250K-350K |
| **MAPE** | **9.87%** | 12-18% |
| **Cross-Validation Score** | **0.879 ± 0.012** | 0.70-0.80 |

### 📊 **Model Comparison Matrix**

```
Performance by Property Type:
┌─────────────────┬─────────┬─────────┬─────────┬─────────┐
│ Property Type   │ R² Score│  RMSE   │  MAPE   │ Sample  │
├─────────────────┼─────────┼─────────┼─────────┼─────────┤
│ Detached        │  0.891  │ $185K   │  9.2%   │ 15,423  │
│ Semi-Detached   │  0.886  │ $198K   │  9.8%   │  8,756  │
│ Townhouse       │  0.878  │ $205K   │ 10.1%   │  6,834  │
│ Condo Apt       │  0.865  │ $225K   │ 11.3%   │ 12,998  │
│ Condo Townhouse│  0.872  │ $210K   │ 10.7%   │  3,445  │
└─────────────────┴─────────┴─────────┴─────────┴─────────┘
```

### 🏆 **Feature Importance Rankings**

1. **Square Footage** (18.2%) - Primary size indicator
2. **Location (City)** (16.8%) - Geographic market value
3. **Economic Momentum** (12.4%) - Economic conditions impact
4. **Bedrooms** (11.1%) - Functional space requirement
5. **Property Type** (9.7%) - Type-specific market dynamics
6. **Interest Rate Environment** (8.9%) - Economic sensitivity
7. **Bathrooms** (7.3%) - Functional amenity indicator
8. **Days on Market** (6.2%) - Market liquidity signal
9. **Year Built** (5.1%) - Age and condition proxy
10. **Affordability Pressure** (4.3%) - Economic constraint factor

### 🔄 **Model Validation Process**

- **5-Fold Cross-Validation** with stratified sampling
- **Temporal Validation** on 6-month holdout period
- **Geographic Validation** across all Canadian provinces
- **Economic Cycle Testing** across different market conditions
- **Outlier Robustness** with 99th percentile analysis

## CI/CD Pipeline

We use GitHub Actions to automate tests, linting, and deployments:

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with: python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
      - run: flake8
```

**Branching strategy**: `main` for production, `develop` for integration; feature branches off `develop`.

## Testing Strategy

- **Unit Tests**: `pytest tests/unit/`
- **Integration Tests**: `pytest tests/integration/`
- **API Tests**: `pytest tests/api/`
- **Load Tests**: configured via Locust (`locustfile.py`)
- **Coverage Reports**: `pytest --cov=app`

## Environment & Configuration

All variables in `.env` (see `.env.example`):

```bash
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=mysql://user:pass@localhost/db
SECRET_KEY=...
BANK_OF_CANADA_API_KEY=...
STATCAN_API_KEY=...
GOOGLE_MAPS_API_KEY=...
```

**Secrets Management**: Use AWS Secrets Manager or Vault in production.

## Data Migration & Seeding

- **Migrations**: Managed by Flask-Migrate (Alembic).`flask db migrate` → `flask db upgrade`
- **Seeding**: `python scripts/seed_data.py` loads initial property, agent, and economic data.

## Monitoring & Logging

- **Health Check**: **GET** `/health` returns status and version.
- **Metrics**: **GET** `/metrics` for Prometheus scraping.
- **Logging**: Configured in `config.py`, writes to `logs/app.log`.
- **APM**: Integrate with Prometheus + Grafana or ELK stack.

## Error Handling & Retries

Global error handler in `app/utils/error_handlers.py` formats:

```json
{
  "error": "ResourceNotFound",
  "message": "Property not found",
  "status": 404
}
```

Retry logic with exponential backoff for external API calls (via `tenacity`).

## Caching & Performance

- **Redis Cache** for frequent queries and ML predictions.
- **CDN** (e.g., CloudFront) for static assets.
- **Cache-Control** headers on assets.

## Security Policies

- **Rate Limiting**: Configured via Flask-Limiter (e.g. 100 requests/min).
- **CORS**: Only allow trusted domains.
- **Dependency Scanning**: dependabot and safety for vulnerability alerts.

## Configuration

### Environment Variables
Create a `.env` file with the following variables:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database Configuration
DATABASE_URL=mysql://username:password@localhost/nextproperty_db

# API Keys
BANK_OF_CANADA_API_KEY=your-boc-api-key
STATISTICS_CANADA_API_KEY=your-statcan-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-key

# ML Model Configuration
MODEL_PATH=models/trained_models/
MODEL_VERSION=1.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Database Schema

### Properties Table
```sql
CREATE TABLE properties (
    ListingID VARCHAR(50) PRIMARY KEY,
    MLS VARCHAR(20),
    PropertyType VARCHAR(50),
    Address VARCHAR(255),
    City VARCHAR(100),
    Province VARCHAR(50),
    PostalCode VARCHAR(10),
    Latitude DECIMAL(10, 8),
    Longitude DECIMAL(11, 8),
    SoldPrice DECIMAL(12, 2),
    OriginalPrice DECIMAL(12, 2),
    Bedrooms INT,
    Bathrooms DECIMAL(3, 1),
    KitchensPlus INT,
    Rooms INT,
    SoldDate DATE,
    DOM INT,
    Taxes DECIMAL(10, 2),
    MaintenanceFee DECIMAL(10, 2),
    Features TEXT,
    CommunityFeatures TEXT,
    Remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Indexes for Optimization
```sql
CREATE INDEX idx_listing_id ON properties(ListingID);
CREATE INDEX idx_location ON properties(Latitude, Longitude);
CREATE INDEX idx_property_type ON properties(PropertyType);
CREATE INDEX idx_city ON properties(City);
CREATE INDEX idx_price_range ON properties(SoldPrice);
CREATE INDEX idx_sold_date ON properties(SoldDate);
CREATE FULLTEXT INDEX idx_features ON properties(Features, CommunityFeatures, Remarks);
```

## ML Model Integration

The application integrates trained machine learning models for:

1. **Property Valuation**: XGBoost model for accurate price predictions
2. **Market Trend Analysis**: Time series forecasting
3. **Investment Risk Assessment**: Risk scoring based on economic indicators
4. **Neighborhood Analysis**: Clustering and similarity analysis
5. **Feature Importance**: Understanding key factors affecting property values

## Data Sources

### Bank of Canada (BoC)
- Interest rates and monetary policy
- Inflation data (CPI)
- Exchange rates
- Financial market indicators

### Statistics Canada (StatCan)
- Employment statistics
- GDP and economic growth
- Population demographics
- Housing statistics

### External APIs
- Google Maps (Geocoding, Places)
- Weather data
- Transit information

## CI/CD Pipeline

1. **Code Commit**: Developer commits code to the repository.
2. **Build**: CI server builds the application and runs unit tests.
3. **Docker Image**: Build and tag Docker image.
4. **Push to Registry**: Push Docker image to container registry.
5. **Deploy to Staging**: Deploy the latest image to the staging environment.
6. **Run Integration Tests**: Execute integration and end-to-end tests.
7. **Approval**: Manual approval for production deployment.
8. **Deploy to Production**: Deploy the approved image to the production environment.
9. **Monitor**: Monitor application health and performance.

## Testing Strategy

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/api/

# Run with coverage
python -m pytest --cov=app tests/
```

## Environment & Configuration

- **Development**: `.env.development`
- **Testing**: `.env.testing`
- **Staging**: `.env.staging`
- **Production**: `.env.production`

## Data Migration & Seeding

- **Migrations**: Managed by Flask-Migrate
- **Seeding**: `python scripts/load_data.py`

## Monitoring & Logging

- **Logging**: Configurable log levels and log file location
- **Monitoring**: Integration with monitoring tools (e.g., Prometheus, Grafana)

## Error Handling & Retries

- **Error Handling**: Centralized error handling in Flask
- **Retries**: Automatic retries for transient errors (e.g., database timeouts)

## Caching & Performance

- **Caching**: Redis for caching frequent queries and ML model predictions
- **Performance**: Optimized database queries and indexing

## Security Policies

- **Data Encryption**: At rest and in transit
- **API Security**: Authentication, authorization, and rate limiting
- **Network Security**: Firewall rules and VPC configuration

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t nextproperty-ai .

# Run container
docker run -p 8000:8000 --env-file .env nextproperty-ai
```

### Docker Compose
```bash
docker-compose up -d
```

### Production Considerations
- Use Gunicorn or uWSGI for WSGI server
- Configure Nginx as reverse proxy
- Set up SSL certificates
- Configure logging and monitoring
- Implement caching (Redis)
- Set up backup strategies

## Performance Optimization

1. **Database Indexing**: Optimized indexes for common queries
2. **Query Optimization**: Efficient SQL queries and database connections
3. **Caching**: Redis for frequently accessed data
4. **API Rate Limiting**: Prevent abuse and ensure fair usage
5. **Model Caching**: Cache ML model predictions
6. **CDN**: Static assets delivery optimization

## Security

- Input validation and sanitization
- SQL injection prevention
- CSRF protection
- Secure session management
- API authentication and authorization
- Data encryption at rest and in transit

## Roadmap & Changelog

### Roadmap

- **v1.1**: Add rental yield predictions
- **v1.2**: Mobile client SDK
- **v2.0**: Marketplace integration

### Changelog

See `CHANGELOG.md` for semantic version history.

## Contribution Guidelines & Code of Conduct

Please see `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md` for details on how to contribute and community standards.

## Contributing

We welcome contributions from the community! See our [CONTRIBUTORS.md](CONTRIBUTORS.md) for the full team and contribution guidelines.

### Quick Start
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Core Team
- [@EfeObus](https://github.com/EfeObus) - Project Lead
- [@RajyKetharaju9](https://github.com/RajyKetharaju9) - Developer
- [@KIRTIRAJ4327](https://github.com/KIRTIRAJ4327) - Developer
- [@Nisha-d7](https://github.com/Nisha-d7) - Developer
- [@AneettaJijo](https://github.com/AneettaJijo) - Developer

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@nextproperty.ai
- Documentation: https://docs.nextproperty.ai
- Issues: https://github.com/your-username/nextproperty-ai/issues
