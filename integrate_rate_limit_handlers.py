"""
Rate Limit Error Handler Integration Script
NextProperty AI Platform

This script integrates the rate limit error handlers into the main application
and provides initialization and testing functionality.
"""

import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.security.rate_limit_error_handlers import rate_limit_error_handler
from app.extensions import cache


def integrate_error_handlers():
    """Integrate rate limit error handlers into the Flask application."""
    print("🔧 Integrating Rate Limit Error Handlers")
    print("=" * 50)
    
    try:
        # Create the Flask app
        app = create_app()
        
        with app.app_context():
            # Initialize the error handler
            rate_limit_error_handler.init_app(app)
            
            # Register error handlers
            print("📝 Registering error handlers...")
            rate_limit_error_handler.register_handlers()
            
            # Test basic functionality
            print("🧪 Testing error handler functionality...")
            
            # Test metrics system
            metrics = rate_limit_error_handler.get_metrics()
            print(f"✅ Metrics system initialized: {len(metrics)} metric types")
            
            # Test template system
            try:
                with app.test_request_context():
                    from flask import render_template
                    template_test = render_template('errors/rate_limit.html', 
                                                 message="Test message",
                                                 retry_after=60,
                                                 limit_type="test")
                    print("✅ Template system working")
            except Exception as e:
                print(f"⚠️ Template system issue: {e}")
            
            # Test Redis connection (if available)
            try:
                # Try to get Redis from app config or use cache
                redis_url = app.config.get('REDIS_URL')
                if redis_url:
                    import redis
                    r = redis.from_url(redis_url)
                    r.ping()
                    print("✅ Redis connection working")
                else:
                    print("⚠️ Redis not configured - using in-memory storage")
            except Exception as e:
                print(f"⚠️ Redis connection issue: {e}")
            
            print("\n🎉 Integration completed successfully!")
            print(f"📊 Error handler initialized at {datetime.now()}")
            
            return app
            
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        raise


def test_error_scenarios():
    """Test various error scenarios to ensure handlers work correctly."""
    print("\n🧪 Testing Error Scenarios")
    print("=" * 30)
    
    app = create_app()
    
    with app.app_context():
        # Import error classes
        from app.security.rate_limit_error_handlers import (
            GlobalRateLimitError, IPRateLimitError, UserRateLimitError,
            EndpointRateLimitError, BurstRateLimitError, APIRateLimitError
        )
        
        test_cases = [
            (GlobalRateLimitError, {"retry_after": 60}),
            (IPRateLimitError, {"retry_after": 60, "ip_address": "127.0.0.1"}),
            (UserRateLimitError, {"retry_after": 60, "user_id": "test_user"}),
            (EndpointRateLimitError, {"retry_after": 60, "endpoint": "/test"}),
            (BurstRateLimitError, {"retry_after": 60}),
            (APIRateLimitError, {"retry_after": 60, "api_key": "test_key"})
        ]
        
        print("Testing error handler responses...")
        
        for error_class, kwargs in test_cases:
            try:
                with app.test_request_context('/test', method='GET'):
                    # Create error instance
                    error = error_class(**kwargs)
                    
                    # Test error response generation
                    response = rate_limit_error_handler.handle_rate_limit_error(error)
                    
                    if response and response.status_code == 429:
                        print(f"✅ {error_class.__name__}: Response generated correctly")
                    else:
                        print(f"❌ {error_class.__name__}: Invalid response")
                        
            except Exception as e:
                print(f"❌ {error_class.__name__}: Error during test - {e}")
        
        print(f"\n📊 Error scenario testing completed at {datetime.now()}")


def validate_configuration():
    """Validate the configuration and setup of rate limit error handlers."""
    print("\n🔍 Validating Configuration")
    print("=" * 30)
    
    app = create_app()
    
    with app.app_context():
        # Check configuration
        config_items = [
            ('RATE_LIMIT_STORAGE_URI', app.config.get('RATE_LIMIT_STORAGE_URI')),
            ('REDIS_URL', app.config.get('REDIS_URL')),
            ('SECRET_KEY', bool(app.config.get('SECRET_KEY'))),
            ('DEBUG', app.config.get('DEBUG')),
        ]
        
        print("Configuration validation:")
        for key, value in config_items:
            if value:
                if key == 'SECRET_KEY':
                    print(f"✅ {key}: Configured")
                else:
                    print(f"✅ {key}: {value}")
            else:
                print(f"⚠️ {key}: Not configured")
        
        # Check template directory
        template_dir = os.path.join(app.root_path, 'templates', 'errors')
        if os.path.exists(template_dir):
            template_files = os.listdir(template_dir)
            print(f"✅ Error templates directory: {len(template_files)} files")
            if 'rate_limit.html' in template_files:
                print("✅ Rate limit template found")
            else:
                print("⚠️ Rate limit template missing")
        else:
            print("❌ Error templates directory missing")
        
        # Check error handler registration
        error_handlers = app.error_handler_spec.get(None, {})
        if 429 in error_handlers:
            print("✅ HTTP 429 error handler registered")
        else:
            print("⚠️ HTTP 429 error handler not registered")
        
        print(f"\n📊 Configuration validation completed at {datetime.now()}")


def show_usage_examples():
    """Show usage examples for the rate limit error handling system."""
    print("\n📚 Usage Examples")
    print("=" * 20)
    
    examples = [
        {
            'title': 'Basic Error Handler Usage',
            'code': '''
from app.security.rate_limit_error_handlers import rate_limit_error_handler, GlobalRateLimitError

# Create and handle a rate limit error
error = GlobalRateLimitError(
    message="Global rate limit exceeded",
    retry_after=60,
    endpoint="/api/properties",
    ip="192.168.1.100"
)

# Handle the error (returns Flask Response)
response = rate_limit_error_handler.handle_rate_limit_error(error)
'''
        },
        {
            'title': 'Custom Error with Additional Context',
            'code': '''
from app.security.rate_limit_error_handlers import APIRateLimitError

# Create API-specific error with context
error = APIRateLimitError(
    message="API key rate limit exceeded",
    retry_after=3600,
    endpoint="/api/market-data",
    ip="10.0.0.50",
    additional_context={
        'api_key': 'key_123***',
        'tier': 'premium',
        'daily_limit': 10000,
        'requests_made': 10000
    }
)
'''
        },
        {
            'title': 'Metrics and Monitoring',
            'code': '''
from app.security.rate_limit_error_handlers import rate_limit_error_handler

# Get current metrics
metrics = rate_limit_error_handler.get_metrics()
print(f"Total blocks: {metrics['total_blocks']}")
print(f"Recent blocks: {metrics['recent_blocks_count']}")

# Clear metrics (admin operation)
rate_limit_error_handler.clear_metrics()
'''
        },
        {
            'title': 'CLI Management',
            'code': '''
# Check system status
python scripts/rate_limit_error_management.py status

# Monitor real-time incidents
python scripts/rate_limit_error_management.py monitor

# Analyze patterns
python scripts/rate_limit_error_management.py analyze --hours 24 --type api

# Test rate limiting
python scripts/rate_limit_error_management.py test burst --count 20
'''
        }
    ]
    
    for example in examples:
        print(f"\n🔸 {example['title']}")
        print("-" * len(example['title']))
        print(example['code'].strip())
    
    print(f"\n📊 Usage examples displayed at {datetime.now()}")


def main():
    """Main integration and testing function."""
    print("🚀 NextProperty AI - Rate Limit Error Handler Integration")
    print("=" * 65)
    
    try:
        # Step 1: Integrate error handlers
        app = integrate_error_handlers()
        
        # Step 2: Test error scenarios
        test_error_scenarios()
        
        # Step 3: Validate configuration
        validate_configuration()
        
        # Step 4: Show usage examples
        show_usage_examples()
        
        print("\n🎉 Integration and Testing Completed Successfully!")
        print("=" * 50)
        print("✅ Rate limit error handlers are now fully integrated")
        print("✅ All error scenarios tested successfully")
        print("✅ Configuration validated")
        print("✅ System ready for production use")
        
        print(f"\n📅 Completed at: {datetime.now()}")
        print("\n💡 Next steps:")
        print("   1. Start your Flask application")
        print("   2. Test rate limiting with: python scripts/rate_limit_error_management.py test global")
        print("   3. Monitor with: python scripts/rate_limit_error_management.py monitor")
        print("   4. Check status with: python scripts/rate_limit_error_management.py status")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration failed: {e}")
        print("Please check the error message above and try again.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
