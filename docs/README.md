# NextProperty AI - Real Estate Investment Platform

[![Security Status](https://img.shields.io/badge/Security-Enterprise%20Ready-green.svg)](docs/ENHANCED_XSS_PROTECTION_IMPLEMENTATION.md)
[![OWASP Compliance](https://img.shields.io/badge/OWASP-Top%2010%20Protected-blue.svg)](docs/ENHANCED_XSS_PROTECTION_IMPLEMENTATION.md)
[![Advanced XSS Protection](https://img.shields.io/badge/XSS-Advanced%20ML%20Protection-brightgreen.svg)](docs/ENHANCED_XSS_PROTECTION_IMPLEMENTATION.md)
[![CSRF Protection](https://img.shields.io/badge/CSRF-Protected-brightgreen.svg)](docs/SECURITY_IMPLEMENTATION.md)
[![Rate Limiting](https://img.shields.io/badge/Rate%20Limiting-Multi%20Layer-red.svg)](docs/RATE_LIMITING_IMPLEMENTATION.md)
[![Behavioral Analysis](https://img.shields.io/badge/Behavioral-AI%20Monitoring-orange.svg)](docs/ENHANCED_XSS_PROTECTION_IMPLEMENTATION.md)
[![ML Validation](https://img.shields.io/badge/ML%20Validation-Neural%20Networks-purple.svg)](docs/ENHANCED_XSS_PROTECTION_IMPLEMENTATION.md)

NextProperty AI revolutionizes property investment and management by leveraging advanced artificial intelligence solutions with comprehensive economic integration. The platform offers personalized, data-driven property analysis with real-time economic indicators to assist investors in making informed decisions.

##  Latest Updates (v2.7.0)

###  **Docker Database Infrastructure Migration (v2.7.0)** 
- **Production Database**: Successfully migrated to Docker MySQL (184.107.4.32:8001)
- **Enhanced Reliability**: Centralized database infrastructure with improved uptime
- **Scalable Architecture**: Docker-based deployment for enterprise-ready scalability  
- **Network Optimization**: Resolved connectivity issues with optimized port configuration
- **Database Consolidation**: Unified database access across all environments
- **Zero Downtime Migration**: Seamless transition with comprehensive backup and validation

###  **Comprehensive Rate Limiting Security (v2.6.0)** 
- **Multi-Layer Rate Limiting**: Global, IP, user, endpoint, and category-based protection
- **DDoS Protection**: High-volume attack mitigation and traffic shaping
- **API Abuse Prevention**: Protection against automated scraping and excessive usage
- **Intelligent Detection**: Pattern recognition and progressive penalties for repeat offenders
- **Redis-Based Distribution**: Production-ready distributed rate limiting with in-memory fallback
- **CLI Management Tools**: Real-time monitoring, alerting, and management capabilities

###  **Enhanced Multi-Layer XSS Protection (v2.5.0)** 
- **Advanced XSS Detection**: ML-powered threat detection with 20+ attack patterns
- **Behavioral Analysis**: AI-driven anomaly detection and user behavior monitoring
- **Dynamic CSP Management**: Real-time Content Security Policy with nonce generation
- **ML-Based Validation**: Neural network input validation for multiple attack vectors
- **Unified Security Framework**: Centralized threat response and security analytics

###  **Enterprise Security Implementation (v2.5.0)**
- **XSS Protection**: Comprehensive Cross-Site Scripting prevention with HTML sanitization
- **CSRF Protection**: Cross-Site Request Forgery protection with automatic token management
- **Security Headers**: Content Security Policy, XSS Protection, and clickjacking prevention
- **Secure Forms**: XSS-protected form fields with real-time validation
- **Security Middleware**: Centralized security management with automatic protection

###  **Enhanced ML Pipeline (v2.0)**
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

###  **Property Analysis**
- **AI-Powered Valuation**: Ensemble ML models with 88.3% accuracy
- **Investment Scoring**: 0-10 scale with economic factor integration
- **Risk Assessment**: Multi-factor risk analysis (Very Low to Very High)
- **Market Trends**: City and property-type specific trend analysis
- **Comparable Properties**: Intelligent matching within 20% size range

###  **Market Intelligence**
- **Real-time Economic Integration**: Bank of Canada + Statistics Canada data
- **10 Economic Indicators**: Interest rates, inflation, unemployment, GDP growth
- **Derived Economic Features**: Market timing, affordability pressure, momentum
- **Market Predictions**: 6-month and 1-year trend forecasting
- **Economic Insights**: AI-generated insights based on economic conditions

###  **Investment Tools**
- **Top Deals Detection**: Identifies undervalued properties (≥5% below prediction)
- **Investment Potential Scoring**: Excellent, Very Good, Good, Fair ratings
- **Portfolio Analytics**: Track and analyze property investments
- **Economic Sensitivity Analysis**: Property-type specific economic impact

###  **Model Management**
- **6+ Trained Models**: Ridge, ElasticNet, RandomForest, GradientBoosting, XGBoost, LightGBM
- **Ensemble Stacking**: Combines best-performing models for superior accuracy
- **Model Switching**: Dynamic model selection via API/CLI
- **Performance Monitoring**: Automated validation and retraining recommendations
- **Hyperparameter Optimization**: RandomizedSearchCV + Bayesian optimization

## Enhanced ML Models

###  **Model Performance Rankings**

| Rank | Model | R² Score | RMSE | MAPE | Training Time |
|------|-------|----------|------|------|---------------|
|  | **Ensemble** | **0.883** | **$197K** | **9.87%** | 6.8s |
|  | XGBoost | 0.878 | $202K | 10.07% | 30.6s |
|  | LightGBM | 0.874 | $206K | 10.50% | 8.7s |
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

###  **Real-Time Data Sources**

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

###  **Economic Data Pipeline**

1. **Caching Layer**: 1-hour TTL for economic indicators
2. **Fallback System**: Default values when APIs unavailable
3. **Real-time Integration**: Updates with each property analysis
4. **Historical Tracking**: Time-series storage for trend analysis

## Technology Stack

### **Backend & Core**
- **Framework**: Flask (Python 3.11+)
- **Database**: Docker MySQL 8.0.42 (Production-Ready Infrastructure)
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

### **Security Stack**
- **CSRF Protection**: Flask-WTF for Cross-Site Request Forgery prevention
- **XSS Protection**: Bleach library for HTML sanitization and XSS prevention
- **Input Validation**: MarkupSafe for secure template rendering
- **Security Headers**: Content Security Policy and comprehensive security headers
- **Session Security**: Secure cookie configuration and session management

### **External APIs**
- **Economic Data**: Bank of Canada, Statistics Canada
- **Geospatial**: Google Maps, Geocoding
- **Market Data**: MLS, CREA integration ready

## Project Structure

```
nextproperty-ai/
 app/
    models/
    routes/
    services/
    templates/
      macros/
        secure_forms.html    # Security form macros
    static/
    utils/
    cache/
    security/               # Security module
      __init__.py
      middleware.py         # XSS/CSRF protection
      config.py            # Security configuration
    forms/                  # Secure forms
      __init__.py
      secure_forms.py      # XSS-protected forms
 config/
 migrations/
 scripts/
 tests/
 data/
 logs/
 models/
 docs/
    SECURITY_IMPLEMENTATION.md  # Security documentation
 Dockerfile
 docker-compose.yml
 requirements.txt
 app.py
 wsgi.py
 .env.example
 README.md
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

###  **Performance Metrics Overview**

Our ensemble ML model achieves industry-leading accuracy with comprehensive validation:

| Metric | Value | Industry Benchmark |
|--------|-------|-------------------|
| **R² Score** | **0.883** | 0.75-0.85 |
| **RMSE** | **$197,000** | $250K-350K |
| **MAPE** | **9.87%** | 12-18% |
| **Cross-Validation Score** | **0.879 ± 0.012** | 0.70-0.80 |

###  **Model Comparison Matrix**

```
Performance by Property Type:

 Property Type    R² Score  RMSE     MAPE    Sample  

 Detached          0.891   $185K     9.2%    15,423  
 Semi-Detached     0.886   $198K     9.8%     8,756  
 Townhouse         0.878   $205K    10.1%     6,834  
 Condo Apt         0.865   $225K    11.3%    12,998  
 Condo Townhouse  0.872   $210K    10.7%     3,445  

```

###  **Feature Importance Rankings**

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

###  **Model Validation Process**

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

# Database Configuration (Docker MySQL - Production Ready)
DATABASE_URL=mysql+pymysql://studentGroup:password@184.107.4.32:8001/NextProperty

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

NextProperty AI implements **state-of-the-art multi-layer security** with advanced machine learning-powered threat detection and comprehensive protection against modern web application threats.

###  **Comprehensive Rate Limiting Security (v2.6.0)**

#### **Multi-Layer Rate Limiting Protection**
- **Global Rate Limiting**: System-wide protection with 1,000 requests per hour across all users
- **IP-Based Limiting**: 100 requests per hour per IP address with burst protection (10/minute)
- **User-Based Limiting**: 500 requests per hour for authenticated users with role-based adjustments
- **Endpoint-Specific Limiting**: Custom limits for sensitive operations (5-50 requests per timeframe)
- **Category-Based Protection**: Specialized limits for authentication, ML predictions, admin operations

#### **Intelligent Attack Prevention**
- **DDoS Protection**: High-volume attack mitigation with traffic shaping and progressive penalties
- **Brute Force Prevention**: Login attempt limiting (5 attempts per 5 minutes) with exponential backoff
- **API Abuse Prevention**: Protection against automated scraping and excessive API usage
- **Resource Protection**: CPU and memory protection through intelligent request limiting
- **Progressive Penalties**: Increasing restrictions for repeat offenders with behavioral analysis

#### **Advanced Rate Limiting Features**
- **Redis-Based Distribution**: Production-ready distributed rate limiting with automatic failover
- **In-Memory Fallback**: Development-friendly local storage when Redis unavailable
- **Pattern Recognition**: Anomaly detection and suspicious behavior identification
- **Geographic Awareness**: Optional location-based rate limiting capabilities
- **Real-Time Monitoring**: Live usage tracking with comprehensive analytics

#### **Rate Limiting Management & Monitoring**
- **CLI Management Suite**: Comprehensive command-line tools for monitoring and management
  - `flask rate-limit status`: Real-time usage monitoring and statistics
  - `flask rate-limit alerts`: Violation detection and alert management
  - `flask rate-limit details`: Client-specific usage analysis and forensics
  - `flask rate-limit health`: System health monitoring and diagnostics
- **Custom 429 Error Pages**: User-friendly rate limit exceeded pages with countdown timers
- **Informative Headers**: Clear rate limit information in response headers
- **Performance Optimization**: <1ms latency overhead with optimized algorithms

###  **Enhanced Multi-Layer XSS Protection (v2.6.0)**

#### **Advanced XSS Detection System**
- **ML-Powered Pattern Recognition**: 20+ sophisticated attack pattern detectors with neural network validation
- **Context-Aware Sanitization**: Intelligent sanitization for HTML, URL, JavaScript, and CSS contexts
- **Threat Scoring System**: Risk-based classification with configurable threat thresholds
- **Real-Time Analysis**: Live payload inspection with sub-millisecond response times
- **Custom Sanitization Profiles**: Application-specific sanitization rules and policies

#### **Behavioral Analysis & Anomaly Detection**
- **AI-Driven User Monitoring**: Statistical analysis of user behavior patterns and interaction anomalies
- **IP Reputation Intelligence**: Real-time threat intelligence with geographic risk assessment
- **Session Correlation**: Multi-session behavioral pattern recognition and analysis
- **Adaptive Threshold System**: Self-adjusting anomaly detection with machine learning
- **Fraud Detection**: Advanced behavioral fingerprinting for suspicious activity identification

#### **Dynamic Content Security Policy (CSP) Management**
- **Nonce-Based Protection**: Cryptographically secure nonce generation for inline scripts
- **Real-Time CSP Generation**: Dynamic policy creation based on content requirements
- **Violation Monitoring**: Comprehensive CSP violation detection and incident response
- **Emergency Lockdown**: Rapid security policy enforcement during threat escalation
- **Compliance Reporting**: Automated CSP effectiveness metrics and audit trails

#### **Machine Learning Input Validation**
- **Neural Network Validation**: Deep learning models for multi-vector attack detection
- **Multi-Attack Recognition**: Simultaneous detection of XSS, SQL injection, command injection, and LDAP injection
- **Confidence Scoring**: ML model certainty levels for intelligent decision making
- **Continuous Learning**: Adaptive model improvement with emerging attack pattern recognition
- **Performance Optimization**: Efficient batch processing with 95%+ cache hit rates

###  **Enterprise Security Foundation (v2.5.0)**

#### **CSRF (Cross-Site Request Forgery) Protection**
- **Flask-WTF Integration**: Automatic CSRF token generation and validation
- **Form Protection**: Hidden CSRF tokens in all state-changing forms
- **AJAX Security**: Automatic CSRF token inclusion in JavaScript requests
- **API Protection**: CSRF validation for all POST/PUT/DELETE/PATCH endpoints
- **Multi-Source Validation**: Support for form data, headers, and JSON token sources

#### **Comprehensive Security Headers**
- **Content Security Policy (CSP)**: Advanced script source restrictions with nonce support
- **X-XSS-Protection**: Browser-level XSS filtering with blocking mode
- **X-Frame-Options**: Clickjacking protection (`SAMEORIGIN`)
- **X-Content-Type-Options**: MIME type sniffing prevention (`nosniff`)
- **Referrer-Policy**: Privacy protection (`strict-origin-when-cross-origin`)
- **Permissions-Policy**: Dangerous feature restrictions (camera, microphone, geolocation)

###  **Security Architecture & Infrastructure**

#### **Unified Security Framework**
- **Enhanced Security Middleware**: Centralized multi-layer protection with real-time threat response
- **Security Decorators**: Easy-to-use route-level security enhancements (`@enhanced_xss_protect`, `@behavioral_analyze`)
- **Advanced Template Filters**: Intelligent content rendering with `advanced_sanitize`, `context_escape`, `threat_check`
- **Automated Incident Response**: Configurable threat response actions and escalation procedures
- **Security Analytics Dashboard**: Real-time monitoring with comprehensive threat intelligence

#### **Performance-Optimized Security**
- **Intelligent Caching**: 95%+ hit rate for pattern matching with memory optimization
- **Asynchronous Analysis**: Non-blocking security operations for high-throughput scenarios
- **Batch Processing**: Efficient ML inference with minimal performance impact (<15ms overhead)
- **Resource Management**: Memory-efficient pattern storage and retrieval systems

###  **Additional Security Measures**

#### **Data Protection & Validation**
- **SQL Injection Prevention**: Parameterized queries and ORM protection
- **Input Validation**: Multi-layer data sanitization and validation
- **API Authentication**: Secure API access control and authorization
- **Data Encryption**: Encryption at rest and in transit
- **Session Security**: Enhanced session management with behavioral validation

#### **Monitoring & Incident Response**
- **Real-Time Threat Monitoring**: Live security dashboard with threat visualization
- **Automated Alerting**: Intelligent alert system with severity-based escalation
- **Forensic Logging**: Comprehensive audit trail for security investigations
- **SIEM Integration**: API endpoints for security orchestration and response platforms
- **Compliance Auditing**: Automated compliance checking and reporting

###  **Automated Secret Key Management**
- **30-Day Rotation**: Automated secret key rotation with cryptographically secure keys
- **Automated Expiry**: Real-time checking and regeneration of expired keys
- **Cron Integration**: Hands-free operation with scheduled key rotation
- **Audit Trail**: Complete logging of key generation and rotation activities

###  **Advanced Compliance & Standards**

#### **Security Frameworks**
- **OWASP Top 10 Protection**: Comprehensive coverage with advanced threat mitigation
- **NIST Cybersecurity Framework**: Implementation of identify, protect, detect, respond, recover
- **Zero Trust Architecture**: Behavioral analysis and continuous verification
- **SOC 2 Type II**: Enhanced controls for security monitoring and incident response
- **ISO 27001**: Advanced information security management with continuous monitoring

#### **Industry Compliance**
- **Financial Services**: Enhanced fraud detection and behavioral analysis
- **Healthcare (HIPAA)**: Advanced data protection with behavioral monitoring
- **PCI DSS**: Enhanced payment data protection with ML-based validation
- **GDPR/PIPEDA**: Privacy-preserving security analysis and data protection

###  **Security Documentation**
- **Enhanced XSS Protection**: `docs/ENHANCED_XSS_PROTECTION_IMPLEMENTATION.md`
- **Implementation Summary**: `ENHANCED_XSS_IMPLEMENTATION_SUMMARY.md`
- **Basic Security Guide**: `docs/SECURITY_IMPLEMENTATION.md`
- **Configuration Management**: `app/security/enhanced_config.py`
- **Secret Key Management**: `scripts/SECRET_KEY_MANAGEMENT.md`
- **Secure Forms Guide**: `app/templates/macros/secure_forms.html`

**Security Status**:  **Enterprise-Ready** |  **Production-Secure** |  **Compliance-Ready**

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
