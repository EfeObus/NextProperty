```
nextproperty-ai/
 app/
    __init__.py                 # Flask application factory
    extensions.py               # Flask extensions initialization
    error_handling.py           # Global error handlers
    logging_config.py           # Logging configuration
    models/                     # Database models
       __init__.py
       property.py             # Property model and database operations
       agent.py                # Real estate agent model
       economic_data.py        # Economic indicators model
       user.py                 # User authentication model
       favourite.py            # User favorites model
    routes/                     # Application routes/blueprints
       __init__.py
       api.py                  # Enhanced REST API endpoints
       main.py                 # Main web routes
       auth.py                 # Authentication routes
       dashboard.py            # Dashboard routes
    services/                   # Business logic layer
       __init__.py
       ml_service.py           # Enhanced ML service (6+ models)
       data_service.py         # Data processing and analysis
       economic_service.py     # Economic data integration
       external_apis.py        # BoC and StatCan API integration
       geospatial_service.py   # Location-based services
       data_processors.py      # Data cleaning and processing
       database_optimizer.py   # Database performance optimization
       etl_service.py          # ETL operations service
       export_service.py       # Enhanced export capabilities
    cli/                        # Command Line Interface
       __init__.py
       etl_commands.py         # ETL and model management CLI commands
    cache/                      # Caching system
       __init__.py
       api_cache.py            # API response caching
       cache_decorators.py     # Cache decorators
       cache_manager.py        # Cache management utilities
       cache_warming.py        # Cache warming strategies
       market_cache.py         # Market data caching
       property_cache.py       # Property data caching
    templates/                  # Jinja2 HTML templates
       base.html               # Base template with navigation
       index.html              # Landing page
       economic_dashboard.html # Economic indicators dashboard
       properties/             # Property-related templates
          list.html           # Property listings
          detail.html         # Property details
          search.html         # Advanced search
          analysis.html       # AI analysis results
       dashboard/              # Dashboard templates
          overview.html       # Main dashboard
          portfolio.html      # Investment portfolio
          market.html         # Market trends
          analytics.html      # Advanced analytics
       auth/                   # Authentication templates
          login.html
          register.html
          profile.html
       partials/               # Reusable template components
           navbar.html
           footer.html
           property_card.html
    static/                     # Static assets
       css/                    # Stylesheets
          style.css           # Main stylesheet
          dashboard.css       # Dashboard-specific styles
          components.css      # Reusable component styles
       js/                     # JavaScript files
          main.js             # Main application JavaScript
          dashboard.js        # Dashboard functionality
          maps.js             # Google Maps integration
          charts.js           # Chart.js/Plotly integration
          api.js              # API interaction helpers
       images/                 # Image assets
          logo.png
          icons/
          properties/         # Property images
       vendor/                 # Third-party libraries
           bootstrap/
           jquery/
           plotly/
    utils/                      # Utility modules
        __init__.py
        database.py             # Database connection and utilities
        helpers.py              # General helper functions
        validators.py           # Input validation
        decorators.py           # Custom decorators
        constants.py            # Application constants
 config/                         # Configuration files
    __init__.py
    config.py                   # Application configuration
    database.sql                # Database schema and indexes
    nginx.conf                  # Nginx configuration (production)
 migrations/                     # Database migrations
    __init__.py
    versions/                   # Migration versions
 tests/                          # Test suite
    __init__.py
    conftest.py                 # Test configuration
    unit/                       # Unit tests
       test_models.py
       test_services.py
       test_utils.py
    integration/                # Integration tests
       test_api.py
       test_database.py
       test_external_apis.py
    fixtures/                   # Test data fixtures
        sample_properties.json
        sample_economic_data.json
 models/                         # Enhanced ML model artifacts
    trained_models/             # Production-ready trained models
       ensemble_stacking_v2.pkl      # Best performing ensemble model
       xgboost_price_model_v2.pkl    # XGBoost regression model
       lightgbm_model_v2.pkl         # LightGBM model
       gradient_boosting_v2.pkl      # Gradient boosting model
       random_forest_v2.pkl          # Random forest model
       ridge_regression_v2.pkl       # Ridge regression model
       elastic_net_v2.pkl            # ElasticNet model
       trend_analysis_model.pkl      # Market trend analysis
       risk_assessment_model.pkl     # Investment risk model
    model_artifacts/            # Model metadata and configurations
       feature_columns_26.json       # 26-feature column definitions
       preprocessing_pipeline_v2.pkl # Enhanced preprocessing pipeline
       model_performance_v2.json     # Detailed performance metrics
       economic_features.json        # Economic feature definitions
       ensemble_weights.json         # Ensemble model weights
       hyperparameters/              # Optimized hyperparameters
           xgboost_params.json
           lightgbm_params.json
           ensemble_config.json
    notebooks/                  # Model development and analysis
        model_development_v2.ipynb    # Enhanced model development
        economic_integration.ipynb    # Economic data integration
        feature_engineering.ipynb    # 26-feature analysis
        model_comparison.ipynb       # Model performance comparison
 data/                          # Enhanced data storage
    raw/                       # Raw data files
       realEstate.csv         # Original real estate dataset
       large_sample_real_estate.csv  # Extended dataset
    processed/                 # Processed and cleaned data
       cleaned_properties_v2.csv     # Enhanced cleaned properties
       economic_indicators_v2.csv    # Economic data with derived features
       feature_engineered_data.csv   # 26-feature dataset
       model_training_data.csv       # Final training dataset
    external/                  # External API data cache
       boc_data/              # Bank of Canada data cache
          policy_rates.json
          inflation_data.json
          exchange_rates.json
       statcan_data/          # Statistics Canada data cache
           unemployment.json
           gdp_data.json
           employment_stats.json
    exports/                   # Enhanced data exports
        property_analytics.xlsx
        market_reports/
        performance_reports/
 Dataset/                       # Source datasets for development
    realEstate.csv             # Original dataset
    sample_real_estate.csv     # Sample dataset for testing
    large_sample_real_estate.csv # Extended dataset for training
 scripts/                       # Enhanced utility scripts
    load_data.py              # Load and validate initial data
    update_economic_data.py   # Update external economic data sources
    train_models.py           # Retrain ML models with validation
    backup_database.py        # Comprehensive database backup
    deploy.py                 # Automated deployment script
 enhanced_model_training.py    # Enhanced ML training pipeline (26 features)
 retrain_model_26_features.py  # Specialized retraining script
 simple_retrain.py            # Quick model retraining utility
 test_economic_integration.py  # Economic integration validation
 test_prediction_complete.py   # Comprehensive prediction testing
 test_prediction_fix.py        # Prediction system validation
 logs/                         # Comprehensive application logging
    nextproperty-ai.log       # Main application log
    nextproperty-ai-errors.log # Error-specific logs
    nextproperty-ai-access.log # API access logs
    nextproperty-ai-performance.log # Performance monitoring
    nextproperty-ai-security.log    # Security event logs
    ml_predictions.log        # ML prediction audit trail
 docs/                         # Enhanced documentation
    api.md                    # Comprehensive API documentation
    database_schema.md        # Database documentation
    deployment.md             # Deployment guide
    ml_models.md              # ML model documentation
    economic_integration.md   # Economic data integration guide
    feature_engineering.md   # 26-feature documentation
 ECONOMIC_INTEGRATION_COMPLETE.md   # Economic integration completion docs
 PREDICTION_FIX_COMPLETE.md         # Prediction system fix documentation
 MAPVIEW_FAVOURITES_IMPLEMENTATION.md # Map view and favorites feature docs
 Week Four Next Property AI.ipynb   # Development notebook
 docker/                       # Docker configuration
    Dockerfile                # Main application container
    docker-compose.yml        # Multi-container setup
    nginx/                    # Nginx container config
    mysql/                    # MySQL container config
 .github/                      # GitHub workflows
    workflows/
        ci.yml                # Continuous integration
        deploy.yml            # Deployment workflow
 requirements.txt              # Python dependencies
 requirements-dev.txt          # Development dependencies
 app.py                       # Flask application entry point
 wsgi.py                      # WSGI application for production
 .env.example                 # Environment variables template
 .gitignore                   # Git ignore rules
 .flaskenv                    # Flask environment variables
 Dockerfile                   # Production Docker configuration
 docker-compose.yml           # Docker Compose for development
 pytest.ini                  # Pytest configuration
 setup.cfg                   # Setup configuration
 CHANGELOG.md                 # Version changelog
 LICENSE                      # License file
 README.md                    # Project documentation
```

## File Descriptions

### Core Application Files
- **app.py**: Main Flask application entry point and configuration
- **wsgi.py**: WSGI application for production deployment with Gunicorn
- **requirements.txt**: Python package dependencies including ML libraries
- **enhanced_model_training.py**: Advanced ML training pipeline with 26 features
- **retrain_model_26_features.py**: Specialized retraining script for production

### Application Package (`app/`)
- **__init__.py**: Flask application factory pattern implementation
- **extensions.py**: Flask extensions initialization (SQLAlchemy, Redis, etc.)
- **error_handling.py**: Global error handlers and custom exceptions
- **logging_config.py**: Comprehensive logging configuration
- **models/**: Enhanced SQLAlchemy database models with economic data integration
- **routes/**: Flask blueprints with expanded API endpoints for ML and analytics
- **services/**: Enhanced business logic layer with 6+ ML models and economic integration
- **cli/**: Command line interface for ETL operations and model management
- **cache/**: Advanced caching system for API responses and ML predictions
- **templates/**: Responsive Jinja2 HTML templates with economic dashboards
- **static/**: Frontend assets with enhanced visualizations and charts
- **utils/**: Utility functions for database operations, validation, and ML helpers

### Enhanced ML & Analytics
- **ml_service.py**: Production ML service with ensemble stacking (6+ models)
- **economic_service.py**: Real-time economic data integration (BoC, StatCan)
- **etl_service.py**: Comprehensive ETL operations for large datasets
- **export_service.py**: Advanced export capabilities (Excel, JSON, XML, Parquet)

### Configuration & Infrastructure
- **config/**: Application configuration with ML model settings
- **migrations/**: Database migration scripts with economic data tables
- **docker/**: Docker containers for application, database, and web server
- **scripts/**: Enhanced automation scripts for model training and data management

### Development & Testing
- **tests/**: Comprehensive test suite with ML model validation
- **docs/**: Enhanced project documentation including ML and economic integration
- **.github/**: CI/CD workflows for automated testing and ML model validation

### Enhanced Data & Models
- **data/**: Hierarchical data storage with economic indicators and feature engineering
- **models/**: Production ML model artifacts with 6+ trained models and ensemble
- **logs/**: Comprehensive application logging with security and performance monitoring

### New Features & Capabilities
- **26-Feature Engineering**: Advanced feature extraction including economic indicators
- **Economic Integration**: Real-time Bank of Canada and Statistics Canada data
- **Ensemble ML Models**: Stacking regressor with 88.3% accuracy
- **CLI Management**: Complete command-line interface for model and data operations
- **Advanced Caching**: Multi-layer caching for performance optimization
- **Investment Analytics**: Risk assessment and portfolio analysis tools

This structure follows Flask best practices and supports:
- **Scalable ML Architecture**: Production-ready ensemble models with 88.3% accuracy
- **Economic Data Integration**: Real-time Bank of Canada and Statistics Canada APIs
- **Advanced Feature Engineering**: 26-feature analysis with economic indicators
- **Comprehensive CLI Tools**: Complete model management and ETL operations
- **Enhanced Caching System**: Multi-layer caching for optimal performance
- **Investment Analytics**: Risk assessment and portfolio management tools
- **Clean Separation of Concerns**: Modular architecture with clear responsibilities
- **Production-Ready Deployment**: Docker containerization and CI/CD pipelines
- **Comprehensive Testing Strategy**: Unit, integration, and ML model validation
- **Maintainable Codebase Organization**: Clear file structure and documentation
- **Security & Monitoring**: Comprehensive logging and security event tracking
- **Data Quality Assurance**: Validation, cleaning, and quality control processes
