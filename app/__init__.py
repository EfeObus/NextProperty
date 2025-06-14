from flask import Flask, g, request, render_template
from flask_cors import CORS
import logging
import os
import uuid
from datetime import datetime
import pymysql

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Import extensions from the central location
from app.extensions import db, migrate, login_manager, cache

def create_app(config_name=None):
    """Application factory pattern."""
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from config.config import config
    app.config.from_object(config[config_name])
    
    # Set up logging first
    from app.logging_config import setup_logging, setup_error_handlers, log_request_start, log_request_end
    loggers = setup_logging(app)
    setup_error_handlers(app, loggers)
    
    # Set up error handling
    from app.error_handling import global_error_handler, global_error_metrics
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/static/*": {"origins": "*"}
    })
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Request hooks for logging and monitoring
    @app.before_request
    def before_request():
        g.request_start_time = datetime.utcnow()
        g.request_id = str(uuid.uuid4())
        log_request_start()
    
    @app.after_request
    def after_request(response):
        return log_request_end(response)
    
    @app.teardown_appcontext
    def teardown_db(error):
        if error:
            loggers['database'].error(f"Database teardown error: {error}")
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        from app.cache.cache_manager import cache_manager
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': 'healthy',
                'cache': 'healthy'
            }
        }
        
        try:
            # Check database
            db.session.execute('SELECT 1')
            db.session.commit()
        except Exception as e:
            health_status['services']['database'] = 'unhealthy'
            health_status['status'] = 'degraded'
            loggers['app'].error(f"Database health check failed: {e}")
        
        try:
            # Check cache
            cache_health = cache_manager.health_check()
            if cache_health.get('status') != 'healthy':
                health_status['services']['cache'] = 'unhealthy'
                health_status['status'] = 'degraded'
        except Exception as e:
            health_status['services']['cache'] = 'unhealthy'
            health_status['status'] = 'degraded'
            loggers['app'].error(f"Cache health check failed: {e}")
        
        return health_status, 200 if health_status['status'] == 'healthy' else 503
    
    # Register blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from app.routes.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('NextProperty AI startup')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Template filters
    @app.template_filter('currency')
    def currency_filter(value):
        """Format currency values."""
        if value is None:
            return "N/A"
        return "${:,.2f}".format(value)
    
    @app.template_filter('format_currency')
    def format_currency_filter(value):
        """Format currency values with CAD suffix."""
        if value is None:
            return "N/A"
        try:
            return "${:,.2f}".format(float(value))
        except (ValueError, TypeError):
            return "N/A"
    
    @app.template_filter('format_price')
    def format_price_filter(value):
        """Format price values."""
        if value is None:
            return "N/A"
        try:
            return "${:,.0f}".format(float(value))
        except (ValueError, TypeError):
            return "N/A"
    
    @app.template_filter('number')
    def number_filter(value):
        """Format large numbers with commas."""
        if value is None:
            return "N/A"
        return "{:,}".format(value)
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """Format percentage values."""
        if value is None:
            return "N/A"
        try:
            return "{:.1f}%".format(float(value))
        except (ValueError, TypeError):
            return "N/A"
    
    @app.template_filter('format_sqft')
    def format_sqft_filter(value):
        """Format square footage values."""
        if value is None:
            return "N/A"
        try:
            return "{:,}".format(int(value))
        except (ValueError, TypeError):
            return "N/A"
    
    @app.template_filter('nl2br')
    def nl2br_filter(value):
        """Convert newlines to HTML line breaks."""
        import markupsafe
        if value is None:
            return ""
        value = str(value)
        # Convert \n to <br> and return as safe HTML
        return markupsafe.Markup(value.replace('\n', '<br>\n'))
    
    # Import models so Flask-Migrate can detect them
    from app.models import user, property, agent, economic_data
    
    # Register CLI commands
    from app.cli import register_cli_commands
    register_cli_commands(app)
    
    return app
