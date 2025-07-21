# NextProperty AI - File Structure (v2.8.0)

## Project Organization

```
nextproperty-ai/
├── app/
│   ├── __init__.py                    # Flask application factory with API key limiter
│   ├── extensions.py                  # Flask extensions (Flask-Limiter, CSRF, etc.)
│   ├── error_handling.py              # Global error handlers
│   ├── logging_config.py              # Logging configuration
│   │
│   ├── models/                        # Database models
│   │   ├── __init__.py
│   │   ├── property.py                # Property model with performance optimizations
│   │   ├── agent.py                   # Real estate agent model
│   │   ├── economic_data.py           # Economic indicators model
│   │   ├── user.py                    # User authentication model
│   │   └── favourite.py               # User favorites model
│   │
│   ├── routes/                        # Application routes/blueprints
│   │   ├── __init__.py
│   │   ├── api.py                     # REST API endpoints with rate limiting
│   │   ├── main.py                    # Main web routes with CSRF protection
│   │   ├── admin.py                   # Admin routes with enhanced security
│   │   └── dashboard.py               # Dashboard routes
│   │
│   ├── services/                      # Business logic layer
│   │   ├── __init__.py
│   │   ├── ml_service.py              # Enhanced ML service (6+ models, 88.3% accuracy)
│   │   ├── data_service.py            # Data processing and analysis
│   │   ├── economic_service.py        # Economic data integration (BoC/StatCan)
│   │   ├── external_apis.py           # External API integrations
│   │   ├── geospatial_service.py      # Location-based services
│   │   ├── data_processors.py         # Data cleaning and processing
│   │   ├── database_optimizer.py      # Database performance optimization
│   │   ├── etl_service.py             # ETL operations service
│   │   └── export_service.py          # Enhanced export capabilities
│   │
│   ├── security/                      # 🔒 COMPREHENSIVE SECURITY MODULE
│   │   ├── __init__.py                # Security module initialization
│   │   ├── middleware.py              # Security middleware and decorators
│   │   ├── config.py                  # Security configuration
│   │   ├── rate_limiter.py            # Advanced rate limiting engine
│   │   ├── rate_limit_config.py       # Rate limiting configuration
│   │   ├── api_key_limiter.py         # 🆕 API key rate limiting system (600+ lines)
│   │   ├── advanced_xss.py            # Advanced XSS protection with ML
│   │   ├── behavioral_analysis.py     # Behavioral security analysis
│   │   ├── enhanced_csp.py            # Enhanced CSP management
│   │   ├── advanced_validation.py     # ML-based input validation
│   │   ├── enhanced_integration.py    # Unified security framework
│   │   └── enhanced_config.py         # Enhanced security configuration
│   │
│   ├── forms/                         # 🔒 SECURE FORMS MODULE
│   │   ├── __init__.py
│   │   └── secure_forms.py            # XSS-protected form fields
│   │
│   ├── cli/                           # 🔧 COMMAND LINE INTERFACE
│   │   ├── __init__.py                # CLI registration
│   │   ├── etl_commands.py            # ETL and model management CLI
│   │   ├── rate_limit_commands.py     # Rate limiting management CLI
│   │   └── api_key_commands.py        # 🆕 API key management CLI (400+ lines)
│   │
│   ├── cache/                         # 📊 CACHING SYSTEM
│   │   ├── __init__.py
│   │   └── api_cache.py               # API response caching
│   │
│   ├── static/                        # 🎨 STATIC ASSETS
│   │   ├── css/                       # Stylesheets with security headers
│   │   ├── js/                        # JavaScript with CSRF protection
│   │   ├── images/                    # Image assets
│   │   └── uploads/                   # User uploaded files
│   │
│   ├── templates/                     # 🌐 JINJA2 TEMPLATES
│   │   ├── base.html                  # Base template with security headers
│   │   ├── index.html                 # Homepage with optimized loading
│   │   ├── errors/
│   │   │   └── 429.html               # Rate limit exceeded page
│   │   ├── macros/
│   │   │   └── secure_forms.html      # 🔒 Secure form macros
│   │   ├── pages/                     # Static pages
│   │   ├── properties/                # Property-related templates
│   │   ├── dashboard/                 # Dashboard templates
│   │   └── admin/                     # Admin templates
│   │
│   └── utils/                         # 🛠️ UTILITY MODULES
│       ├── __init__.py
│       ├── validators.py              # Data validation utilities
│       ├── formatters.py              # Data formatting utilities
│       ├── helpers.py                 # General helper functions
│       └── constants.py               # Application constants
│
├── config/                            # ⚙️ CONFIGURATION
│   ├── __init__.py
│   ├── config.py                      # Application configuration with security settings
│   └── logging.conf                   # Logging configuration
│
├── data/                              # 📊 DATA STORAGE
│   ├── raw/                           # Raw data files
│   ├── processed/                     # Processed datasets
│   ├── models/                        # Trained ML models
│   └── exports/                       # Data exports
│
├── database_export/                   # 🗄️ DATABASE EXPORTS
│   └── nextproperty_backup.sql        # Database backup files
│
├── docs/                              # 📚 DOCUMENTATION
│   ├── README.md                      # Main documentation
│   ├── CHANGELOG.md                   # Version history and changes
│   ├── COMPREHENSIVE_MANAGEMENT_REPORT.md  # Executive management report
│   ├── DEVELOPMENT_GUIDE.md           # Development setup and guidelines
│   ├── DEPLOYMENT_GUIDE.md            # Production deployment guide
│   ├── API_DOCUMENTATION.md           # Complete API reference
│   ├── MACHINE_LEARNING_DOCUMENTATION.md  # ML models and implementation
│   ├── DATABASE_DOCUMENTATION.md      # Database schema and operations
│   ├── SECURITY_IMPLEMENTATION.md     # Security implementation guide
│   ├── RATE_LIMITING_COMPREHENSIVE_DOCUMENTATION.md  # Rate limiting guide
│   ├── ARCHITECTURE_DOCUMENTATION.md  # System architecture
│   ├── TESTING_DOCUMENTATION.md       # Testing procedures
│   ├── PERFORMANCE_OPTIMIZATION.md    # Performance tuning guide
│   ├── SECRET_KEY_MANAGEMENT.md       # Secret key management
│   ├── FILE_STRUCTURE.md              # This file
│   ├── USER_GUIDE.md                  # End-user documentation
│   └── CONTRIBUTORS.md                # Contributing guidelines
│
├── instance/                          # 🔧 INSTANCE CONFIGURATION
│   ├── config.py                      # Instance-specific configuration
│   └── logs/                          # Application logs
│
├── logs/                              # 📋 LOGGING
│   ├── application.log                # Application logs
│   ├── error.log                      # Error logs
│   └── security.log                   # Security event logs
│
├── migrations/                        # 🔄 DATABASE MIGRATIONS
│   ├── versions/                      # Migration versions
│   ├── alembic.ini                    # Alembic configuration
│   ├── env.py                         # Migration environment
│   └── script.py.mako                 # Migration script template
│
├── scripts/                           # 🔧 UTILITY SCRIPTS
│   ├── generate_secret_key.py         # Secret key generation
│   ├── generate_secret_key.sh         # Shell wrapper for automation
│   ├── setup_secret_key_cron.sh       # Cron job setup
│   ├── check_secret_key.py            # Secret key status checker
│   ├── secret-key                     # Unified CLI tool
│   ├── database_migration_script.py   # Database migration utilities
│   └── SECRET_KEY_MANAGEMENT.md       # Secret key documentation
│
├── tests/                             # 🧪 TEST SUITE
│   ├── __init__.py
│   ├── test_models.py                 # Model unit tests
│   ├── test_routes.py                 # Route integration tests
│   ├── test_services.py               # Service layer tests
│   ├── test_security.py               # Security feature tests
│   ├── test_api.py                    # API endpoint tests
│   ├── test_ml.py                     # ML model tests
│   └── conftest.py                    # Test configuration
│
├── .env                               # 🔐 ENVIRONMENT VARIABLES
├── .gitignore                         # Git ignore rules
├── requirements.txt                   # 📦 Python dependencies
├── pytest.ini                        # Testing configuration
├── docker-compose.yml                # 🐳 Docker composition
├── Dockerfile                        # Docker container definition
├── README.md                          # 📖 Project README
└── app.py                            # 🚀 Application entry point
```
       base.html               # Base template with navigation
       index.html              # Landing page
       economic_dashboard.html # Economic indicators dashboard
       favourites.html         # User favorites page
       mapview.html            # Map view interface
       market_insights.html    # Market insights page
       properties.html         # Properties listing page
       properties/             # Property-related templates
          price_prediction_form.html # Price prediction form
          upload_form.html    # Property upload form
          detail.html         # Property details
          search.html         # Advanced search
          analysis.html       # AI analysis results
       dashboard/              # Dashboard templates
          overview.html       # Main dashboard
          portfolio.html      # Investment portfolio
          market.html         # Market trends
          analytics.html      # Advanced analytics
       admin/                  # Admin templates
          dashboard.html      # Admin dashboard
          users.html          # User management
          properties.html     # Property management
       errors/                 # Error pages
          404.html            # Not found page
          429.html            #  Rate limit exceeded page (NEW)
          500.html            # Server error page
       pages/                  # Static pages
          contact.html        # Contact form
          about.html          # About page
       partials/               # Reusable template components
          navbar.html         # Navigation bar
          footer.html         # Footer
          property_card.html  # Property card component
       macros/                 #  SECURE TEMPLATE MACROS (NEW)
          secure_forms.html   # XSS-protected form macros
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
    config.py                   # Application configuration
    performance.py              # Performance optimization config
 migrations/                     # Database migrations (Alembic)
    alembic.ini                 # Alembic configuration
    env.py                      # Migration environment
    script.py.mako              # Migration template
    versions/                   # Migration versions
 tests/                          # Comprehensive test suite
    __init__.py
    conftest.py                 # Pytest configuration
    conftest_additional.py      # Additional test configuration
    test_api.py                 # API endpoint tests
    test_models.py              # Database model tests
    test_services.py            # Service layer tests
    test_utils.py               # Utility function tests
    test_performance.py         # Performance testing
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
    check_secret_key.py        # Secret key validation
    generate_secret_key.py     # Automated secret key generation
    load_data.py              # Load and validate initial data
    update_economic_data.py   # Update external economic data sources
    train_models.py           # Retrain ML models with validation
    backup_database.py        # Comprehensive database backup
    deploy.py                 # Automated deployment script
 instance/                      # Flask instance folder
    nextproperty_dev.db       # Development database (SQLite)
 logs/                         # Comprehensive application logging
    nextproperty-ai.log       # Main application log
    nextproperty-ai-errors.log # Error-specific logs
    nextproperty-ai-access.log # API access logs
    nextproperty-ai-performance.log # Performance monitoring
    nextproperty-ai-security.log    # Security event logs
 docs/                         #  COMPREHENSIVE DOCUMENTATION
    README.md                 # Main project documentation
    CHANGELOG.md              # Version changelog and release notes
    FILE_STRUCTURE.md         # Project structure documentation (this file)
    API_DOCUMENTATION.md      # Comprehensive API documentation
    ARCHITECTURE_DOCUMENTATION.md # System architecture guide
    DATABASE_DOCUMENTATION.md # Database schema and design
    DEPLOYMENT_GUIDE.md       # Production deployment guide
    DEVELOPMENT_GUIDE.md      # Developer setup and guidelines
    TESTING_DOCUMENTATION.md # Testing strategy and procedures
    USER_GUIDE.md            # End-user manual
    SETUP.md                 # Quick setup instructions
    CONFIGURATION_DOCUMENTATION.md # Configuration management
    MACHINE_LEARNING_DOCUMENTATION.md # ML models and algorithms
    PERFORMANCE_OPTIMIZATION.md # Performance tuning guide
    SECURITY_IMPLEMENTATION.md #  Security features guide (NEW)
    RATE_LIMITING_IMPLEMENTATION.md #  Rate limiting implementation guide (NEW)
    RATE_LIMITING_SUMMARY.md  #  Rate limiting executive summary (NEW)
    SECRET_KEY_MANAGEMENT.md  #  Secret key management (NEW)
    DOCUMENTATION_UPDATES_SUMMARY.md # Documentation change summary (NEW)
    ECONOMIC_INTEGRATION_COMPLETE.md # Economic integration guide
    PREDICTION_FIX_COMPLETE.md # Prediction system fixes
    MAPVIEW_FAVOURITES_IMPLEMENTATION.md # Map and favorites features
    CANADIAN_CITIES_ENHANCEMENT.md # Canadian cities integration
    COMPREHENSIVE_MANAGEMENT_REPORT.md # Project management report
    COMPREHENSIVE_PROGRESS_DOCUMENTATION.md # Progress tracking
    CONTRIBUTORS.md          # Team and contribution guidelines
    NextProperty_AI_Postman_Collection.json # API testing collection
    NextProperty_AI_Progress_Presentation.md # Progress presentation
 # Core Application Files
 enhanced_model_training.py    # Enhanced ML training pipeline (26 features)
 retrain_model_26_features.py  # Specialized retraining script
 simple_retrain.py            # Quick model retraining utility
 migrate_to_mysql.py          # Database migration script
 test_rate_limiting.py        #  Rate limiting testing suite (NEW)
 demo_rate_limiting.py        #  Interactive rate limiting demo (NEW)
 Week Four Next Property AI.ipynb # Development notebook
 app.py                       # Flask application entry point
 requirements.txt              # Python dependencies
 pytest.ini                  # Pytest configuration
 .env.example                 # Environment variables template
 .gitignore                   # Git ignore rules
 CHANGES_LOG.md.backup        # Backup of changes log
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
- **security/**:  **Enhanced enterprise security module** with comprehensive protection
  - **rate_limiter.py**: Advanced multi-layer rate limiting engine
  - **rate_limit_config.py**: Comprehensive rate limiting configuration
  - **middleware.py**: CSRF protection, XSS prevention, security headers
  - **advanced_xss.py**: ML-powered XSS detection and protection
  - **behavioral_analysis.py**: User behavior analysis and anomaly detection
  - **enhanced_csp.py**: Dynamic Content Security Policy management
- **forms/**:  **Secure form fields** with automatic sanitization
- **cli/**: Enhanced command line interface for operations and security management
  - **etl_commands.py**: ETL operations and model management
  - **rate_limit_commands.py**: Rate limiting monitoring and management tools
- **cache/**: Advanced caching system for API responses and ML predictions
- **templates/**: Responsive Jinja2 HTML templates with economic dashboards
- **static/**: Frontend assets with enhanced visualizations and charts
- **utils/**: Utility functions for database operations, validation, and ML helpers

###  Enhanced Security Architecture (v2.6.0)
- **security/rate_limiter.py**: Advanced multi-layer rate limiting engine
- **security/rate_limit_config.py**: Comprehensive rate limiting configuration system
- **security/middleware.py**: CSRF protection, XSS prevention, security headers
- **security/config.py**: Centralized security configuration and policies
- **security/advanced_xss.py**: ML-powered XSS detection and behavioral analysis
- **forms/secure_forms.py**: XSS-protected form fields with automatic validation
- **templates/macros/secure_forms.html**: Reusable secure form components
- **templates/errors/429.html**: User-friendly rate limit exceeded error page
- **CLI Security Tools**: Real-time monitoring and management capabilities
- **Enhanced Input Validation**: Server-side sanitization and client-side protection
- **Security Headers**: CSP, X-XSS-Protection, X-Frame-Options, and more
- **Rate Limiting Protection**: DDoS prevention, API abuse protection, brute force prevention

### Enhanced ML & Analytics
- **ml_service.py**: Production ML service with ensemble stacking (6+ models)
- **economic_service.py**: Real-time economic data integration (BoC, StatCan)
- **etl_service.py**: Comprehensive ETL operations for large datasets
- **export_service.py**: Advanced export capabilities (Excel, JSON, XML, Parquet)

### Configuration & Infrastructure
- **config/**: Application configuration with ML model settings and performance tuning
- **migrations/**: Database migration scripts with Alembic for schema management
- **instance/**: Flask instance folder with development database
- **scripts/**: Enhanced automation scripts for model training, data management, and security

### Development & Testing
- **tests/**: Comprehensive test suite with ML model validation and security testing
- **docs/**: Enhanced project documentation including ML, economic integration, and security
- **pytest.ini**: Pytest configuration for comprehensive testing strategies

### Enhanced Data & Models
- **data/**: Hierarchical data storage with economic indicators and feature engineering
- **models/**: Production ML model artifacts with 6+ trained models and ensemble
- **logs/**: Comprehensive application logging with security and performance monitoring
- **Dataset/**: Source datasets for development and training

### New Features & Capabilities (v2.5.0)
- ** Enterprise Security**: Comprehensive XSS and CSRF protection with security middleware
- ** Secure Forms**: Automatic input sanitization and validation
- ** Secret Key Management**: Automated rotation and security compliance
- **26-Feature Engineering**: Advanced feature extraction including economic indicators
- **Economic Integration**: Real-time Bank of Canada and Statistics Canada data
- **Ensemble ML Models**: Stacking regressor with 88.3% accuracy
- **CLI Management**: Complete command-line interface for model and data operations
- **Advanced Caching**: Multi-layer caching for performance optimization
- **Investment Analytics**: Risk assessment and portfolio analysis tools
- **Security Monitoring**: Comprehensive logging and security event tracking

This structure follows Flask best practices and supports:
- ** Enterprise Security Architecture**: XSS/CSRF protection with security middleware
- ** Secure Development**: Input validation, sanitization, and secure coding practices
- ** Compliance Standards**: OWASP, SOC 2, ISO 27001, PIPEDA/GDPR ready
- **Scalable ML Architecture**: Production-ready ensemble models with 88.3% accuracy
- **Economic Data Integration**: Real-time Bank of Canada and Statistics Canada APIs
- **Advanced Feature Engineering**: 26-feature analysis with economic indicators
- **Comprehensive CLI Tools**: Complete model management and ETL operations
- **Enhanced Caching System**: Multi-layer caching for optimal performance
- **Investment Analytics**: Risk assessment and portfolio management tools
- **Clean Separation of Concerns**: Modular architecture with clear responsibilities
- **Production-Ready Deployment**: Flask application with comprehensive logging
- **Comprehensive Testing Strategy**: Unit, integration, and security validation
- **Maintainable Codebase Organization**: Clear file structure and documentation
- **Security & Monitoring**: Comprehensive logging and security event tracking
- **Data Quality Assurance**: Validation, cleaning, and quality control processes
