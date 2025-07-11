"""
Flask extensions initialization.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
cache = Cache()
csrf = CSRFProtect()

# Initialize rate limiter with default key function
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10000 per hour", "500 per minute"]
)
