#!/usr/bin/env python3
"""
Simple Flask Test App for Rate Limit Error Handling Demo
This demonstrates the enhanced error handling without complex dependencies.
"""

from flask import Flask, request, jsonify, make_response
import json
import time
from standalone_rate_limit_demo import standalone_handler

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def index():
    """Home page with links to test the error handling."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NextProperty AI - Rate Limit Error Handler Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { background: #f8f9fa; padding: 30px; border-radius: 10px; }
            .test-link { display: block; margin: 10px 0; padding: 15px; background: #007bff; color: white; 
                        text-decoration: none; border-radius: 5px; text-align: center; }
            .test-link:hover { background: #0056b3; }
            .description { margin: 10px 0; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 NextProperty AI - Rate Limit Error Handler Demo</h1>
            <p>Test the enhanced rate limit error handling system:</p>
            
            <h2>🌐 Web Error Pages (HTML)</h2>
            <a href="/demo/your-error" class="test-link">Your Actual Error (Resource Exhaustion - Level 4)</a>
            <p class="description">See how your specific error would be displayed to web users</p>
            
            <a href="/demo/rapid-requests" class="test-link">Rapid Requests Error</a>
            <p class="description">Too many requests too quickly</p>
            
            <a href="/demo/brute-force" class="test-link">Brute Force Detection</a>
            <p class="description">Multiple failed login attempts</p>
            
            <a href="/demo/scraping" class="test-link">Scraping Detection</a>
            <p class="description">Automated data collection detected</p>
            
            <h2>📡 API Error Responses (JSON)</h2>
            <a href="/api/demo/your-error" class="test-link">Your Actual Error (API Response)</a>
            <p class="description">JSON response for your specific error</p>
            
            <a href="/api/demo/api-abuse" class="test-link">API Abuse Detection</a>
            <p class="description">API usage limit exceeded</p>
            
            <a href="/api/demo/suspicious-patterns" class="test-link">Suspicious Patterns</a>
            <p class="description">Unusual activity detected</p>
            
            <h2>📊 System Information</h2>
            <a href="/status" class="test-link">Error Handler Status</a>
            <p class="description">Check system status and configuration</p>
        </div>
    </body>
    </html>
    """

@app.route('/demo/your-error')
def demo_your_error():
    """Demo your actual error as a web page."""
    error_data = {
        "abuse_type": "resource_exhaustion",
        "error": "Request blocked due to abuse detection",
        "incident_id": 1753105363.67304,
        "level": 4,
        "retry_after": 504,
        "type": "abuse_rate_limit"
    }
    
    response_data = standalone_handler.handle_abuse_detection_error(error_data)
    html = standalone_handler.generate_html_response(response_data)
    
    response = make_response(html)
    response.status_code = 429
    response.headers.update(response_data['headers'])
    
    return response

@app.route('/demo/<abuse_type>')
def demo_abuse_type(abuse_type):
    """Demo different abuse types as web pages."""
    error_data = {
        "abuse_type": abuse_type,
        "error": f"Request blocked due to {abuse_type} detection",
        "incident_id": int(time.time()),
        "level": 3,
        "retry_after": 300,
        "type": "abuse_rate_limit"
    }
    
    response_data = standalone_handler.handle_abuse_detection_error(error_data)
    html = standalone_handler.generate_html_response(response_data)
    
    response = make_response(html)
    response.status_code = 429
    response.headers.update(response_data['headers'])
    
    return response

@app.route('/api/demo/your-error')
def api_demo_your_error():
    """Demo your actual error as API response."""
    error_data = {
        "abuse_type": "resource_exhaustion",
        "error": "Request blocked due to abuse detection",
        "incident_id": 1753105363.67304,
        "level": 4,
        "retry_after": 504,
        "type": "abuse_rate_limit"
    }
    
    response_data = standalone_handler.handle_abuse_detection_error(error_data)
    
    # Remove HTML-specific fields for API response
    api_response = {k: v for k, v in response_data.items() 
                   if k not in ['headers']}
    
    response = jsonify(api_response)
    response.status_code = 429
    
    for header, value in response_data['headers'].items():
        response.headers[header] = value
    
    return response

@app.route('/api/demo/<abuse_type>')
def api_demo_abuse_type(abuse_type):
    """Demo different abuse types as API responses."""
    error_data = {
        "abuse_type": abuse_type,
        "error": f"Request blocked due to {abuse_type} detection",
        "incident_id": int(time.time()),
        "level": 2,
        "retry_after": 180,
        "type": "abuse_rate_limit"
    }
    
    response_data = standalone_handler.handle_abuse_detection_error(error_data)
    
    # Remove HTML-specific fields for API response
    api_response = {k: v for k, v in response_data.items() 
                   if k not in ['headers']}
    
    response = jsonify(api_response)
    response.status_code = 429
    
    for header, value in response_data['headers'].items():
        response.headers[header] = value
    
    return response

@app.route('/status')
def status():
    """Show error handler status and configuration."""
    config_info = {
        'handler_initialized': True,
        'abuse_types_configured': len(standalone_handler.abuse_type_messages),
        'severity_levels': len(standalone_handler.severity_configs),
        'abuse_types': list(standalone_handler.abuse_type_messages.keys()),
        'demo_links': {
            'your_error_web': '/demo/your-error',
            'your_error_api': '/api/demo/your-error',
            'test_abuse_types': [f'/demo/{abuse_type}' for abuse_type in standalone_handler.abuse_type_messages.keys()]
        }
    }
    
    return jsonify(config_info)

@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler."""
    return """
    <h1>Page Not Found</h1>
    <p><a href="/">← Back to Demo Home</a></p>
    """, 404

if __name__ == '__main__':
    print("🚀 Starting NextProperty AI Rate Limit Error Handler Demo")
    print("=" * 60)
    print("📍 Demo URLs:")
    print("   Home: http://localhost:5000")
    print("   Your Error (Web): http://localhost:5000/demo/your-error")
    print("   Your Error (API): http://localhost:5000/api/demo/your-error")
    print("   Status: http://localhost:5000/status")
    print("=" * 60)
    print("🌐 Open http://localhost:5000 in your browser to test the error pages")
    print()
    
    app.run(debug=True, port=5000)
