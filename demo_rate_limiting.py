"""
Rate Limiting Demonstration Script
Shows how rate limiting protects the application from abuse.
"""

from flask import Flask, jsonify, request
from app.security.rate_limiter import RateLimiter, rate_limit
from app.extensions import limiter
import time


# Create a simple demo app
demo_app = Flask(__name__)
demo_app.config['SECRET_KEY'] = 'demo-secret-key'

# Initialize rate limiter
rate_limiter = RateLimiter()
limiter.init_app(demo_app)
rate_limiter.init_app(demo_app)


@demo_app.route('/')
def index():
    """Simple index page."""
    return """
    <h1>Rate Limiting Demo</h1>
    <p>Try these endpoints to see rate limiting in action:</p>
    <ul>
        <li><a href="/api/unlimited">Unlimited endpoint</a></li>
        <li><a href="/api/limited">Limited endpoint (5 per minute)</a></li>
        <li><a href="/api/strict">Strict endpoint (2 per minute)</a></li>
        <li><a href="/api/burst">Burst protected endpoint</a></li>
    </ul>
    <p>Open browser dev tools to see rate limit headers.</p>
    """


@demo_app.route('/api/unlimited')
def unlimited_endpoint():
    """Endpoint without rate limiting."""
    return jsonify({
        'message': 'This endpoint has no rate limiting',
        'timestamp': time.time(),
        'tip': 'Check response headers for rate limit info'
    })


@demo_app.route('/api/limited')
@limiter.limit("5 per minute")
def limited_endpoint():
    """Endpoint with basic rate limiting."""
    return jsonify({
        'message': 'This endpoint is limited to 5 requests per minute',
        'timestamp': time.time(),
        'limit': '5 per minute'
    })


@demo_app.route('/api/strict')
@limiter.limit("2 per minute")
@rate_limit(requests=2, window=60, category='strict')
def strict_endpoint():
    """Endpoint with strict rate limiting."""
    return jsonify({
        'message': 'This endpoint is strictly limited to 2 requests per minute',
        'timestamp': time.time(),
        'limit': '2 per minute'
    })


@demo_app.route('/api/burst')
@limiter.limit("10 per hour", per_method=True)
@limiter.limit("3 per minute", per_method=True)
def burst_protected():
    """Endpoint with burst protection."""
    return jsonify({
        'message': 'This endpoint has burst protection (3/min, 10/hour)',
        'timestamp': time.time(),
        'limits': ['3 per minute', '10 per hour']
    })


@demo_app.route('/health')
def health():
    """Health check endpoint (not rate limited)."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'rate_limiter': 'active'
    })


@demo_app.errorhandler(429)
def rate_limit_handler(error):
    """Custom rate limit error handler."""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please slow down.',
        'retry_after': getattr(error, 'retry_after', 60),
        'tip': 'Check Retry-After header for when to try again'
    }), 429


if __name__ == '__main__':
    print("🚀 Starting Rate Limiting Demo")
    print("Visit http://localhost:5007 to test rate limiting")
    print("Try making multiple requests quickly to see rate limiting in action")
    print("Press Ctrl+C to stop")
    
    demo_app.run(debug=True, port=5007)
