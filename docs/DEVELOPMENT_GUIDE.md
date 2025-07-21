# NextProperty AI - Development Guide (v2.8.0)

## Table of Contents
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [API Key System Development](#api-key-system-development)
- [Security Development](#security-development)
- [Code Standards](#code-standards)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing Guidelines](#testing-guidelines)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Review Process](#code-review-process)

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Virtual environment (venv, conda, or virtualenv)
- Node.js (for frontend dependencies)
- Docker (recommended for database)
- MySQL 8.0+ (primary database)
- Redis (for rate limiting - optional, falls back to in-memory)
- SQLite (for testing only)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd "Nextproperty Real Estate"

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
# Edit .env with your specific configuration

# Initialize database
flask db upgrade

# Generate initial API key for testing
flask api-keys generate --developer-id dev-test --name "Development Key" --tier free

# Run the application
flask run
```

## Development Environment

### Environment Variables (.env)
```bash
# Database Configuration (Docker MySQL recommended)
DATABASE_URL=mysql+pymysql://studentGroup:juifcdhoifdqw13f@184.107.4.32:8001/NextProperty

# Redis Configuration (optional - for distributed rate limiting)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security Configuration
SECRET_KEY=your-secret-key-here
EXPIRY_DATE=2025-08-20
WTF_CSRF_SECRET_KEY=your-csrf-secret-key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# API Configuration
API_KEYS_STORAGE_FILE=api_keys_storage.json
RATE_LIMIT_STORAGE_URI=redis://localhost:6379/1
```

## API Key System Development

### Working with API Keys

The API key system is central to v2.8.0. Here's how to work with it:

#### CLI Commands for Development
```bash
# Generate test API keys
flask api-keys generate --developer-id test-dev --name "Test API" --tier premium

# Test API key functionality
flask api-keys test --api-key npai_premium_... --endpoint /api/properties

# Check key information and usage
flask api-keys info --api-key npai_premium_... --format json

# View analytics
flask api-keys analytics --developer-id test-dev --days 7

# Manage key lifecycle
flask api-keys suspend --api-key npai_premium_...
flask api-keys reactivate --api-key npai_premium_...
flask api-keys revoke --api-key npai_premium_...
```

#### API Key Integration in Code
```python
from app.security.api_key_limiter import api_key_limiter

# Protect routes with API key rate limiting
@api.route('/properties')
@api_key_limiter.limit_by_key()
def get_properties():
    return jsonify(properties)

# Custom rate limiting
@api.route('/expensive-operation')
@api_key_limiter.limit_by_key(override_limits={'requests': '5/hour'})
def expensive_operation():
    return jsonify(result)
```

### API Key Tiers and Limits

| Tier | Requests/min | Requests/hour | Requests/day | Data Transfer | Compute Time |
|------|--------------|---------------|--------------|---------------|--------------|
| FREE | 10 | 100 | 1,000 | 10MB/day | 60s/day |
| BASIC | 60 | 1,000 | 10,000 | 100MB/day | 300s/day |
| PREMIUM | 300 | 5,000 | 50,000 | 1GB/day | 1,800s/day |
| ENTERPRISE | 1,500 | 25,000 | 250,000 | 10GB/day | 7,200s/day |
| UNLIMITED | 10,000 | 100,000 | 1,000,000 | 100GB/day | 86,400s/day |
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db upgrade

# Run the application
python app.py
```

## Development Environment

### Environment Variables
Create a `.env` file in the project root with the following variables:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1

# Database - MySQL is now the primary database
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/nextproperty_ai

# API Keys
BANK_OF_CANADA_API_KEY=your-boc-api-key
STATISTICS_CANADA_API_KEY=your-statcan-api-key
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# ML Configuration
MODEL_PATH=models/trained_models/
MODEL_VERSION=1.0
PREDICTION_CACHE_TTL=3600

# Security
JWT_SECRET_KEY=your-jwt-secret
SESSION_TIMEOUT=3600
BCRYPT_LOG_ROUNDS=12

# External APIs
EXTERNAL_API_TIMEOUT=30
API_RATE_LIMIT=100

# Caching
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300
```

### IDE Configuration

#### VS Code
Recommended extensions:
- Python
- Pylance
- Python Docstring Generator
- GitLens
- MySQL Workbench (for database management)
- Thunder Client (for API testing)

#### Settings
Add to your `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Code Standards

### Python Style Guide
We follow PEP 8 with some modifications:
- Line length: 88 characters (Black default)
- Use double quotes for strings
- Use type hints for function parameters and return values
- Docstrings for all public functions, classes, and modules

### Formatting Tools
```bash
# Black for code formatting
black .

# isort for import sorting
isort .

# flake8 for linting
flake8 .

# mypy for type checking
mypy .
```

### Code Organization

#### Imports
```python
# Standard library imports
import os
from datetime import datetime
from typing import Dict, List, Optional

# Third-party imports
import pandas as pd
from flask import Flask, request, jsonify
from sqlalchemy import func

# Local imports
from app.models import Property, User
from app.services.prediction import PredictionService
from app.utils.validation import validate_property_data
```

#### Naming Conventions
- **Files and directories**: `snake_case`
- **Classes**: `PascalCase`
- **Functions and variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

#### Docstring Format
```python
def predict_property_price(property_data: Dict) -> Dict:
    """
    Predict property price using ML model.
    
    Args:
        property_data (Dict): Property features including location,
                            size, bedrooms, etc.
    
    Returns:
        Dict: Prediction result with price, confidence, and metadata.
        
    Raises:
        ValidationError: If property data is invalid.
        ModelError: If ML model prediction fails.
        
    Example:
        >>> data = {"location": "Toronto", "bedrooms": 3, "bathrooms": 2}
        >>> result = predict_property_price(data)
        >>> print(result["predicted_price"])
        750000
    """
```

## Project Structure

```
Nextproperty Real Estate/
 app/                    # Main application package
    __init__.py        # App factory
    models/            # Database models
    routes/            # Route blueprints
    services/          # Business logic services
    utils/             # Utility functions
    cache/             # Caching implementation
    static/            # Static files (CSS, JS, images)
 config/                # Configuration files
 migrations/            # Database migrations
 models/                # ML models and artifacts
 tests/                 # Test suite
 docs/                  # Documentation
 scripts/               # Utility scripts
 requirements.txt       # Python dependencies
```

### Component Guidelines

#### Models (`app/models/`)
- One model per file
- Include relationships and constraints
- Add validation methods
- Include serialization methods

#### Routes (`app/routes/`)
- Group related endpoints in blueprints
- Use decorators for authentication and validation
- Keep route handlers thin - delegate to services
- Include proper error handling

#### Services (`app/services/`)
- Implement business logic
- Handle external API calls
- Manage ML model operations
- Include comprehensive error handling

#### Utils (`app/utils/`)
- Reusable helper functions
- Validation utilities
- Security functions
- Data transformation utilities

## Development Workflow

### Branch Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes

### Commit Messages
Follow conventional commits format:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add property search endpoint
fix(ml): resolve model loading issue
docs(readme): update installation instructions
```

### Development Process
1. Create feature branch from `develop`
2. Implement changes with tests
3. Run quality checks (linting, tests)
4. Submit pull request
5. Code review and approval
6. Merge to `develop`
7. Deploy to staging for testing
8. Merge to `main` for production

## Testing Guidelines

### Test Structure
```
tests/
 unit/              # Unit tests
 integration/       # Integration tests
 fixtures/          # Test data
 conftest.py       # Test configuration
 test_*.py         # Test files
```

### Writing Tests
```python
def test_property_price_prediction():
    """Test property price prediction with valid data."""
    # Arrange
    property_data = {
        "location": "Toronto",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500
    }
    
    # Act
    result = predict_property_price(property_data)
    
    # Assert
    assert "predicted_price" in result
    assert result["predicted_price"] > 0
    assert "confidence" in result
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py

# Run tests matching pattern
pytest -k "test_prediction"

# Run tests with verbose output
pytest -v
```

## Contributing Guidelines

### Before Contributing
1. Check existing issues and pull requests
2. Create an issue for major changes
3. Fork the repository
4. Create a feature branch

### Pull Request Process
1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

### Code Quality Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Backward compatibility maintained

## Code Review Process

### For Authors
- Write clear commit messages and PR descriptions
- Include screenshots for UI changes
- Reference related issues
- Respond to feedback promptly
- Update based on review comments

### For Reviewers
- Review for correctness, security, and performance
- Check test coverage
- Verify documentation updates
- Provide constructive feedback
- Approve when requirements are met

### Review Criteria
- **Functionality**: Does the code work as intended?
- **Security**: Are there any security implications?
- **Performance**: Will this impact system performance?
- **Maintainability**: Is the code readable and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is documentation updated?

## Best Practices

### Error Handling
```python
from app.error_handling import handle_api_error

@api.route('/properties/<int:property_id>')
def get_property(property_id):
    try:
        property_data = PropertyService.get_by_id(property_id)
        return jsonify(property_data), 200
    except PropertyNotFoundError as e:
        return handle_api_error(e, 404)
    except Exception as e:
        return handle_api_error(e, 500)
```

### Logging
```python
import logging
from app.logging_config import get_logger

logger = get_logger(__name__)

def process_property_data(data):
    logger.info(f"Processing property data for {data.get('id')}")
    try:
        result = perform_processing(data)
        logger.info(f"Successfully processed property {data.get('id')}")
        return result
    except Exception as e:
        logger.error(f"Failed to process property {data.get('id')}: {str(e)}")
        raise
```

### Security
- Always validate input data
- Use parameterized queries
- Implement proper authentication and authorization
- Sanitize user inputs
- Use HTTPS in production
- Keep dependencies updated

### Performance
- Use database indexes appropriately
- Implement caching for expensive operations
- Optimize ML model inference
- Monitor memory usage
- Profile critical code paths

## Tools and Resources

### Development Tools
- **Flask**: Web framework
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **Pytest**: Testing framework
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking

### External Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

## Getting Help

### Contacts
- Lead Developer: [Contact Information]
- DevOps Team: [Contact Information]
- ML Team: [Contact Information]

### Resources
- Project Wiki: [Link]
- Slack Channel: #nextproperty-dev
- Issue Tracker: GitHub Issues
- Documentation: `/docs` directory

## Troubleshooting

### Common Issues
1. **Database connection errors**: Check DATABASE_URL in .env
2. **ML model loading fails**: Verify model files exist in models/ directory
3. **API key errors**: Ensure all required API keys are configured
4. **Import errors**: Check virtual environment activation

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=1
python app.py
```

### Logging Levels
```python
# Adjust logging level for debugging
import logging
logging.getLogger('app').setLevel(logging.DEBUG)
```
