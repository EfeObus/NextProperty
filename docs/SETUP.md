#  NextProperty AI - Complete Setup Guide

A comprehensive guide to set up and run the NextProperty AI Real Estate Investment Platform with advanced ML capabilities and economic integration.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [ML Models Setup](#ml-models-setup)
- [Running the Application](#running-the-application)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

## Quick Start

For impatient developers who want to get started immediately:

```bash
# 1. Clone and navigate
git clone https://github.com/EfeObus/NextProperty.git
cd NextProperty_AI

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env

# 5. Initialize database
flask db upgrade

# 6. Load sample data
python scripts/load_data.py

# 7. Run the application
python app.py
```

Visit `http://localhost:5007` to access the application.

## Prerequisites

Before setting up NextProperty AI, ensure your system meets the following requirements:

### System Requirements

- **Operating System**: macOS, Linux, or Windows 10+
- **Python**: 3.8 or higher (Python 3.9+ recommended)
- **Memory**: Minimum 4GB RAM (8GB+ recommended for ML training)
- **Storage**: At least 2GB free space
- **Internet**: Required for API integrations and package installation

### Required Software

1. **Python 3.8+**
   ```bash
   # Check Python version
   python --version
   
   # Install Python if needed (macOS with Homebrew)
   brew install python
   ```

2. **Git**
   ```bash
   # Check Git installation
   git --version
   
   # Install Git if needed (macOS)
   brew install git
   ```

3. **pip** (usually comes with Python)
   ```bash
   # Upgrade pip to latest version
   python -m pip install --upgrade pip
   ```

### Optional but Recommended

- **Redis** (for caching in production)
- **MySQL/PostgreSQL** (for production database)
- **Docker** (for containerized deployment)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EfeObus/NextProperty_AI.git
cd NextProperty_AI
```

### 2. Create Virtual Environment (Recommended)

Using a virtual environment isolates project dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation (should show venv in prompt)
which python
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### Development Dependencies (Optional)

For development work, install additional packages:

```bash
# Install development dependencies
pip install pytest pytest-flask pytest-cov black flake8 mypy

# Or install from dev requirements if available
pip install -r requirements-dev.txt
```

##  Missing Files (Due to GitHub Size Limits)

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
-  `elasticnet_price_model.pkl` (6.9KB)
-  `ridge_price_model.pkl` (6.8KB)

**To recreate the missing models:**
```bash
# Run the model training script
python enhanced_model_training.py

# Or use the simpler retraining script
python retrain_model_26_features.py
```

## Environment Configuration

### 1. Create Environment File

```bash
# Copy the example environment file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your specific configuration:

```bash
# Open in your preferred editor
nano .env
# or
code .env
```

### Essential Environment Variables

#### Flask Configuration
```env
FLASK_APP=app.py
FLASK_ENV=development  # Change to 'production' for production
SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=True  # Set to False in production
```

#### Database Configuration
```env
# Docker MySQL (production database - current)
DATABASE_URL=mysql+pymysql://studentGroup:password@184.107.4.32:8001/NextProperty

# Legacy configurations (deprecated)
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/nextproperty_ai
# DATABASE_URL=sqlite:///instance/nextproperty_dev.db
# DATABASE_URL=postgresql://username:password@localhost/nextproperty_db
```

#### API Keys (Optional but Recommended)
```env
# Bank of Canada API (for economic data)
BANK_OF_CANADA_API_KEY=your-boc-api-key

# Statistics Canada API (for economic indicators)
STATISTICS_CANADA_API_KEY=your-statcan-api-key

# Google Maps API (for geocoding and mapping)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
```

#### ML Model Configuration
```env
MODEL_PATH=models/trained_models/
MODEL_VERSION=2.0
PREDICTION_CACHE_TTL=3600
```

#### Security Settings
```env
JWT_SECRET_KEY=your-jwt-secret-key
SESSION_TIMEOUT=3600
BCRYPT_LOG_ROUNDS=12
```

### How to Obtain API Keys

#### Bank of Canada API Key
1. Visit [Bank of Canada Developer Portal](https://www.bankofcanada.ca/valet/)
2. Register for an account
3. Request API access
4. Add the key to your `.env` file

#### Statistics Canada API Key
1. Visit [Statistics Canada Web Data Service](https://www.statcan.gc.ca/en/developers)
2. Follow registration process
3. Request API access
4. Add the key to your `.env` file

#### Google Maps API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Maps JavaScript API and Geocoding API
4. Create credentials (API Key)
5. Restrict the key to your domain (recommended)

### Environment Configuration for Different Stages

#### Development Environment
```env
FLASK_ENV=development
DEBUG=True
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/nextproperty_ai
LOG_LEVEL=DEBUG
```

#### Testing Environment
```env
FLASK_ENV=testing
TESTING=True
DATABASE_URL=sqlite:///instance/test.db  # SQLite is fine for testing
LOG_LEVEL=INFO
```

#### Production Environment
```env
FLASK_ENV=production
DEBUG=False
DATABASE_URL=mysql://user:pass@prod-db-server/nextproperty
SECRET_KEY=very-strong-production-secret
LOG_LEVEL=WARNING
SSL_REQUIRED=True
```

## Database Setup

### 1. MySQL Setup (Primary Database)

NextProperty AI now uses MySQL as the primary database. Here's how to set it up:

#### Install MySQL
```bash
# macOS with Homebrew
brew install mysql
brew services start mysql

# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql

# Windows - Download from MySQL website
# https://dev.mysql.com/downloads/mysql/
```

#### Create Database and User
```bash
# Connect to MySQL as root
mysql -u root -p

# Create database
CREATE DATABASE nextproperty_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional, you can use root)
CREATE USER 'nextproperty'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON nextproperty_ai.* TO 'nextproperty'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Configure Environment
```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/nextproperty_ai
```

#### Run Migration
```bash
# Initialize database schema
flask db upgrade

# Load sample data
python migrate_to_mysql.py
```

### 2. SQLite Setup (Development/Testing Alternative)

If you prefer to use SQLite for development:

```bash
# Create instance directory if it doesn't exist
mkdir -p instance

# Configure SQLite in .env
DATABASE_URL=sqlite:///instance/nextproperty_dev.db

# Initialize database schema
flask db upgrade

# Verify database creation
ls -la instance/
```

### 3. PostgreSQL Setup (Alternative Production Option)

#### Install PostgreSQL
```bash
# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Create Database and User
```bash
# Switch to postgres user
sudo -u postgres psql

-- Create database and user
CREATE DATABASE nextproperty_db;
CREATE USER nextproperty_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE nextproperty_db TO nextproperty_user;
\q
```

#### Update Environment Configuration
```env
DATABASE_URL=postgresql://nextproperty_user:strong_password@localhost/nextproperty_db
```

#### Install PostgreSQL Python Driver
```bash
pip install psycopg2-binary
```

### 4. Initialize Database Schema

After configuring your database:

```bash
# Initialize Flask-Migrate
flask db init  # Only needed if migrations folder doesn't exist

# Create initial migration (if needed)
flask db migrate -m "Initial migration"

# Apply migrations to database
flask db upgrade

# Verify tables were created
flask shell
>>> from app import db
>>> db.engine.table_names()
>>> exit()
```

### 5. Load Sample Data

```bash
# Load sample real estate data
python scripts/load_data.py

# Alternative: Load specific datasets
python -c "from scripts.load_data import load_properties; load_properties()"
```

## ML Models Setup

The application includes multiple ML models for property price prediction. Some large model files are excluded from the repository due to size constraints.

### Available Models (Included)

 **ElasticNet Model** (`elasticnet_price_model.pkl`) - 6.9KB  
 **Ridge Regression Model** (`ridge_price_model.pkl`) - 6.8KB

### Missing Models (Need Training)

The following models need to be trained locally:

- **Random Forest Model** (~83MB when trained)
- **XGBoost Model** (~413KB when trained)
- **LightGBM Model** (~323KB when trained)
- **Gradient Boosting Model** (~592KB when trained)

### Model Training Options

#### Option 1: Quick Training (Recommended for Testing)
```bash
# Train basic models with sample data
python simple_retrain.py
```

#### Option 2: Full Model Training
```bash
# Train all models with comprehensive features
python enhanced_model_training.py
```

#### Option 3: 26-Feature Enhanced Training
```bash
# Train models with 26 features including economic indicators
python retrain_model_26_features.py
```

### Model Training Requirements

- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Time**: 5-30 minutes depending on dataset size and models
- **Data**: Training data in `Dataset/` directory

### Verifying Model Installation

```bash
# Check which models are available
python -c "
import os
model_dir = 'models/trained_models/'
if os.path.exists(model_dir):
    models = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
    print('Available models:', models)
else:
    print('Model directory not found')
"
```

## Running the Application

### Development Mode

```bash
# Standard method
python app.py

# Flask development server (alternative)
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=5007

# With debug mode
python app.py --debug
```

### Production Mode

```bash
# Update environment for production
export FLASK_ENV=production

# Run with Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5007 app:app

# Or with uWSGI
pip install uwsgi
uwsgi --http :5007 --wsgi-file app.py --callable app
```

### Accessing the Application

- **Local Development**: http://localhost:5007
- **Network Access**: http://your-ip-address:5007

### Key Application URLs

- **Homepage**: `/`
- **Property Search**: `/properties`
- **Price Prediction**: `/predict-price`
- **Map View**: `/mapview`
- **Economic Dashboard**: `/economic-dashboard`
- **API Documentation**: `/api/docs` (if available)
- **Admin Interface**: `/admin`

## Development Setup

### Code Quality Tools

```bash
# Install development tools
pip install black flake8 mypy pre-commit

# Format code with Black
black .

# Check code style
flake8 .

# Type checking
mypy app/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Testing Setup

```bash
# Install testing dependencies
pip install pytest pytest-flask pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test files
pytest tests/test_api.py
pytest tests/test_models.py
```

### Development Database

```bash
# Create separate development database
export FLASK_ENV=development
flask db upgrade

# Load development data
python scripts/load_data.py --env development
```

## Production Deployment

### Using Docker (Recommended)

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5007

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5007", "app:app"]
```

```bash
# Build and run with Docker
docker build -t nextproperty-ai .
docker run -p 5007:5007 --env-file .env nextproperty-ai
```

### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5007:5007"
    environment:
      - FLASK_ENV=production
    depends_on:
      - db
      - redis

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: nextproperty_db
      MYSQL_USER: nextproperty_user
      MYSQL_PASSWORD: userpassword

  redis:
    image: redis:alpine
```

### Environment-Specific Configurations

#### Production Environment Variables
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=super-secret-production-key
DATABASE_URL=mysql://user:pass@prod-db/nextproperty
CACHE_TYPE=redis
CACHE_REDIS_HOST=redis-server
SSL_REQUIRED=True
```

### Production Checklist

- [ ] Update `SECRET_KEY` to a strong, unique value
- [ ] Set `DEBUG=False`
- [ ] Configure production database (MySQL/PostgreSQL)
- [ ] Set up Redis for caching
- [ ] Configure logging for production
- [ ] Set up monitoring and health checks
- [ ] Configure SSL/HTTPS
- [ ] Set up backup procedures
- [ ] Configure rate limiting
- [ ] Review security settings
## Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors

**Problem**: ModuleNotFoundError when running the application
```
ModuleNotFoundError: No module named 'flask'
```

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Database Connection Errors

**Problem**: Database connection fails
```
sqlalchemy.exc.OperationalError: Connection failed
```

**Solution**:
```bash
# For MySQL - ensure MySQL is running
brew services start mysql  # macOS
sudo systemctl start mysql  # Linux

# Check connection
mysql -u root -p -e "SELECT 1;"

# Recreate database if needed
mysql -u root -p -e "DROP DATABASE IF EXISTS nextproperty_ai; CREATE DATABASE nextproperty_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
flask db upgrade

# Load data
python migrate_to_mysql.py
```

#### 3. Missing Model Files

**Problem**: Prediction fails due to missing ML models
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/trained_models/...'
```

**Solution**:
```bash
# Train missing models
python simple_retrain.py
# or for full training
python enhanced_model_training.py
```

#### 4. Permission Errors

**Problem**: Permission denied when creating files
```
PermissionError: [Errno 13] Permission denied: 'logs/app.log'
```

**Solution**:
```bash
# Create necessary directories
mkdir -p logs instance models/trained_models

# Fix permissions (Unix/macOS)
chmod 755 logs instance models
```

#### 5. Port Already in Use

**Problem**: Port 5007 is already occupied
```
OSError: [Errno 48] Address already in use
```

**Solution**:
```bash
# Find and kill process using port 5007
lsof -ti:5007 | xargs kill -9

# Or run on different port
python app.py --port 5007
```

#### 6. API Key Issues

**Problem**: External API calls fail
```
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**Solution**:
```bash
# Check API keys in .env file
cat .env | grep API_KEY

# Verify API keys are valid and have proper permissions
# Some APIs may need whitelisting of your IP address
```

#### 7. Memory Issues During Model Training

**Problem**: Out of memory during ML model training
```
MemoryError: Unable to allocate array
```

**Solution**:
```bash
# Use lighter training script
python simple_retrain.py

# Or reduce dataset size
head -1000 Dataset/realEstate.csv > Dataset/sample_small.csv
```

#### 8. Environment Variable Issues

**Problem**: Environment variables not loaded
```
KeyError: 'SECRET_KEY'
```

**Solution**:
```bash
# Verify .env file exists and has correct format
ls -la .env
cat .env

# Manually export critical variables
export SECRET_KEY=your-secret-key
export DATABASE_URL=sqlite:///instance/nextproperty_dev.db
```

### Performance Issues

#### Slow Application Startup

**Cause**: Large model files or extensive data loading

**Solutions**:
1. Use model lazy loading
2. Implement caching
3. Reduce dataset size for development

```bash
# Quick fix: Use minimal models only
mv models/trained_models/large_models models/backup/
python simple_retrain.py
```

#### Slow Prediction Responses

**Cause**: Complex ML models or lack of caching

**Solutions**:
1. Enable Redis caching
2. Use lighter models for development
3. Implement prediction result caching

```env
# Add to .env
CACHE_TYPE=redis
PREDICTION_CACHE_TTL=3600
```

### Development Issues

#### Code Quality Issues

```bash
# Fix code formatting
black .

# Fix import order
isort .

# Check for common issues
flake8 .
```

#### Test Failures

```bash
# Run tests with verbose output
pytest -v

# Run specific failing test
pytest tests/test_api.py::test_specific_function -v

# Run tests with debugging
pytest --pdb
```

### Logging and Debugging

#### Enable Debug Logging

```env
# In .env file
LOG_LEVEL=DEBUG
DEBUG=True
```

#### Check Application Logs

```bash
# View recent logs
tail -f logs/nextproperty-ai.log

# Search for errors
grep -i error logs/nextproperty-ai.log

# Check specific component logs
grep -i "ml_service" logs/nextproperty-ai.log
```

#### Database Debugging

```bash
# Connect to MySQL database
mysql -u root -p nextproperty_ai

# List tables
SHOW TABLES;

# Check table structure
DESCRIBE properties;

# View sample data
SELECT * FROM properties LIMIT 5;

# Check database size
SELECT 
    table_schema as 'Database', 
    table_name as 'Table', 
    round(((data_length + index_length) / 1024 / 1024), 2) 'Size in MB' 
FROM information_schema.tables 
WHERE table_schema='nextproperty_ai';
```

### Getting Help

#### Check Documentation
- Review `README.md` for feature documentation
- Check `docs/` directory for detailed guides
- Look at test files for usage examples

#### Community Support
- Open an issue on GitHub with:
  - Error message and full traceback
  - Steps to reproduce the problem
  - Your environment details (OS, Python version, etc.)
  - Relevant configuration (sanitized)

#### Debug Information Script

Create this debug script to gather system information:

```python
# debug_info.py
import sys
import os
import platform
import pkg_resources

print("=== System Information ===")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")

print("\n=== Environment Variables ===")
env_vars = ['FLASK_APP', 'FLASK_ENV', 'DATABASE_URL', 'SECRET_KEY']
for var in env_vars:
    value = os.environ.get(var, 'Not Set')
    if 'SECRET' in var or 'KEY' in var or 'PASSWORD' in var:
        value = '*' * len(str(value)) if value != 'Not Set' else 'Not Set'
    print(f"{var}: {value}")

print("\n=== Installed Packages ===")
installed_packages = [d.project_name for d in pkg_resources.working_set]
required_packages = ['flask', 'sqlalchemy', 'scikit-learn', 'pandas']
for package in required_packages:
    status = "" if package in installed_packages else ""
    print(f"{status} {package}")

print("\n=== File Structure ===")
important_files = [
    '.env', 'app.py', 'requirements.txt',
    'instance/nextproperty_dev.db',
    'models/trained_models/',
    'Dataset/sample_real_estate.csv'
]
for file_path in important_files:
    exists = "" if os.path.exists(file_path) else ""
    print(f"{exists} {file_path}")
```

Run with: `python debug_info.py`

---

## Additional Resources

### Useful Commands Reference

```bash
# Development
flask shell                    # Interactive Python shell
flask db migrate              # Create new migration
flask db upgrade              # Apply migrations
flask routes                  # List all routes

# Testing
pytest                        # Run all tests
pytest --cov=app             # Run with coverage
pytest -k "test_api"         # Run specific tests

# Code Quality
black .                       # Format code
flake8 .                     # Check style
mypy app/                    # Type checking

# Model Management
python simple_retrain.py     # Quick model training
python enhanced_model_training.py  # Full training

# Data Management
python scripts/load_data.py  # Load sample data
```

### Configuration Examples

#### Minimal .env for Development
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/nextproperty_ai
DEBUG=True
```

#### Production .env Template
```env
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=change-this-in-production
DATABASE_URL=mysql+pymysql://user:pass@db-server:3306/nextproperty_ai
DEBUG=False
CACHE_TYPE=redis
CACHE_REDIS_HOST=redis-server
SSL_REQUIRED=True
```

This setup guide should help you get NextProperty AI running smoothly in any environment. For additional support, please refer to the project documentation or open an issue on GitHub.
