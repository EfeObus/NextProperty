#!/usr/bin/env python3
"""
Demo script to test the abuse detection system functionality.
"""

from flask import Flask, jsonify, request
import time
from app.security.abuse_detection import AbuseDetectionMiddleware

app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key'

# Initialize abuse detection
abuse_middleware = AbuseDetectionMiddleware(app)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

@app.route('/api/unlimited')
def unlimited():
    """Unlimited endpoint for testing."""
    return jsonify({
        'message': 'Unlimited endpoint',
        'timestamp': time.time(),
        'client': request.remote_addr
    })

@app.route('/api/limited')
def limited():
    """Limited endpoint for testing."""
    return jsonify({
        'message': 'Limited endpoint',
        'timestamp': time.time(),
        'client': request.remote_addr
    })

@app.route('/api/properties')
def properties():
    """Properties endpoint for testing scraping detection."""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    return jsonify({
        'message': 'Properties endpoint',
        'page': page,
        'limit': limit,
        'timestamp': time.time(),
        'client': request.remote_addr
    })

@app.route('/api/search')
def search():
    """Search endpoint for testing."""
    query = request.args.get('search', '')
    return jsonify({
        'message': 'Search endpoint',
        'query': query,
        'timestamp': time.time(),
        'client': request.remote_addr
    })

@app.route('/api/property/<int:property_id>')
def property_detail(property_id):
    """Property detail endpoint for testing."""
    return jsonify({
        'message': 'Property detail',
        'property_id': property_id,
        'timestamp': time.time(),
        'client': request.remote_addr
    })

@app.route('/api/agents')
def agents():
    """Agents endpoint for testing."""
    return jsonify({
        'message': 'Agents endpoint',
        'timestamp': time.time(),
        'client': request.remote_addr
    })

@app.route('/api/listings')
def listings():
    """Listings endpoint for testing."""
    return jsonify({
        'message': 'Listings endpoint',
        'timestamp': time.time(),
        'client': request.remote_addr
    })

@app.errorhandler(429)
def rate_limit_handler(e):
    """Handle rate limit errors."""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests',
        'timestamp': time.time()
    }), 429

if __name__ == '__main__':
    print("🚀 Starting Abuse Detection Demo Server")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET /health - Health check")
    print("  GET /api/unlimited - Unlimited endpoint")
    print("  GET /api/limited - Limited endpoint")
    print("  GET /api/properties - Properties listing")
    print("  GET /api/search - Search endpoint")
    print("  GET /api/property/<id> - Property details")
    print("  GET /api/agents - Agents listing")
    print("  GET /api/listings - Listings endpoint")
    print()
    print("Server running on http://localhost:5007")
    print("Use abuse_detection_test.py to test the system")
    print("=" * 50)
    
    app.run(host='localhost', port=5007, debug=True)
