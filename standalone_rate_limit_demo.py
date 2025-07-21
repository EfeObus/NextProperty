"""
Standalone Enhanced Rate Limit Error Handler
This version can work independently of the Flask app for testing and demonstration.
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


class StandaloneRateLimitErrorHandler:
    """Standalone version for testing and demonstration."""
    
    def __init__(self):
        # Abuse type mappings to user-friendly messages
        self.abuse_type_messages = {
            'resource_exhaustion': {
                'title': 'System Resources Overloaded',
                'message': 'Our servers are currently experiencing high load. Please wait and try again.',
                'icon': '⚡',
                'color': '#ff6b6b',
                'guidance': 'Reduce request frequency and wait for the specified time before retrying.'
            },
            'rapid_requests': {
                'title': 'Too Many Requests',
                'message': 'You are making requests too quickly. Please slow down.',
                'icon': '🚀',
                'color': '#ffa726',
                'guidance': 'Space out your requests and avoid rapid-fire API calls.'
            },
            'brute_force': {
                'title': 'Suspicious Login Activity',
                'message': 'Multiple failed authentication attempts detected.',
                'icon': '🔒',
                'color': '#e74c3c',
                'guidance': 'Verify your credentials and contact support if you need help.'
            },
            'scraping': {
                'title': 'Automated Activity Detected',
                'message': 'Automated data collection is not permitted.',
                'icon': '🤖',
                'color': '#9b59b6',
                'guidance': 'Use our official API for data access or contact us for legitimate business needs.'
            },
            'api_abuse': {
                'title': 'API Usage Limit Exceeded',
                'message': 'Your API usage has exceeded acceptable limits.',
                'icon': '📡',
                'color': '#3498db',
                'guidance': 'Review our API documentation for proper usage patterns.'
            },
            'suspicious_patterns': {
                'title': 'Unusual Activity Detected',
                'message': 'Unusual request patterns have been detected from your account.',
                'icon': '🔍',
                'color': '#f39c12',
                'guidance': 'If this is legitimate traffic, please contact our support team.'
            }
        }
        
        # Severity level configurations
        self.severity_configs = {
            1: {'retry_multiplier': 1.0, 'base_retry': 300, 'max_retry': 900},     # 5-15 minutes
            2: {'retry_multiplier': 1.5, 'base_retry': 600, 'max_retry': 1800},   # 10-30 minutes
            3: {'retry_multiplier': 2.0, 'base_retry': 900, 'max_retry': 3600},   # 15-60 minutes
            4: {'retry_multiplier': 3.0, 'base_retry': 1800, 'max_retry': 7200},  # 30-120 minutes
            5: {'retry_multiplier': 4.0, 'base_retry': 3600, 'max_retry': 14400}  # 60-240 minutes
        }
    
    def handle_abuse_detection_error(self, error_data):
        """
        Process abuse detection error data and return structured response.
        """
        
        # Parse error data
        if isinstance(error_data, dict):
            abuse_type = error_data.get('abuse_type', 'unknown')
            retry_after = error_data.get('retry_after', 300)
            level = error_data.get('level', 1)
            incident_id = error_data.get('incident_id')
        else:
            abuse_type = 'resource_exhaustion'
            retry_after = 300
            level = 1
            incident_id = int(time.time())
        
        # Get configuration for this abuse type
        abuse_config = self.abuse_type_messages.get(
            abuse_type, 
            self.abuse_type_messages['resource_exhaustion']
        )
        
        # Create response data
        response_data = {
            'status_code': 429,
            'error': True,
            'error_code': 'ABUSE_RATE_LIMIT',
            'type': 'abuse_rate_limit',
            'abuse_type': abuse_type,
            'level': level,
            'title': abuse_config['title'],
            'message': abuse_config['message'],
            'icon': abuse_config['icon'],
            'color': abuse_config['color'],
            'guidance': abuse_config['guidance'],
            'retry_after': retry_after,
            'retry_after_human': self._format_time_duration(retry_after),
            'incident_id': incident_id,
            'timestamp': datetime.utcnow().isoformat(),
            'severity_description': self._get_severity_description(level),
            'next_action': self._get_next_action(abuse_type, level),
            'headers': {
                'Retry-After': str(retry_after),
                'X-RateLimit-Type': 'abuse_detection',
                'X-RateLimit-Abuse-Type': abuse_type,
                'X-RateLimit-Level': str(level),
                'X-Incident-ID': str(incident_id) if incident_id else ''
            },
            'support': {
                'contact': 'support@nextproperty.ai',
                'documentation': 'https://docs.nextproperty.ai/rate-limits',
                'appeal_process': 'https://docs.nextproperty.ai/appeals'
            }
        }
        
        return response_data
    
    def _format_time_duration(self, seconds):
        """Format seconds into human-readable duration."""
        if seconds < 60:
            return f"{seconds} seconds"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds > 0:
                return f"{minutes} minutes and {remaining_seconds} seconds"
            return f"{minutes} minutes"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes > 0:
                return f"{hours} hours and {remaining_minutes} minutes"
            return f"{hours} hours"
    
    def _get_severity_description(self, level):
        """Get human-readable severity description."""
        descriptions = {
            1: 'Low severity - Minor rate limit violation',
            2: 'Medium severity - Moderate rate limit violation',
            3: 'High severity - Significant rate limit violation',
            4: 'Very High severity - Serious abuse detected',
            5: 'Critical severity - Severe abuse requiring immediate action'
        }
        return descriptions.get(level, 'Unknown severity level')
    
    def _get_next_action(self, abuse_type, level):
        """Get recommended next action based on abuse type and level."""
        if level >= 4:
            return "Contact our support team if you believe this is an error."
        elif abuse_type == 'brute_force':
            return "Verify your credentials and ensure you're using the correct login information."
        elif abuse_type in ['scraping', 'api_abuse']:
            return "Review our API documentation and ensure you're following rate limit guidelines."
        else:
            return "Wait for the specified time period and then retry your request."
    
    def generate_html_response(self, response_data):
        """Generate a simple HTML response."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{response_data['title']} - NextProperty AI</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }}
                .container {{
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .icon {{
                    font-size: 64px;
                    margin-bottom: 20px;
                }}
                .title {{
                    color: {response_data['color']};
                    margin-bottom: 15px;
                    font-size: 2em;
                }}
                .message {{
                    color: #666;
                    margin-bottom: 20px;
                    line-height: 1.5;
                }}
                .info-box {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid {response_data['color']};
                }}
                .countdown {{
                    font-size: 1.5em;
                    color: {response_data['color']};
                    font-weight: bold;
                    margin: 15px 0;
                }}
                .guidance {{
                    background: #e8f5e8;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #4caf50;
                    text-align: left;
                }}
                .details {{
                    background: #f1f3f4;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-size: 0.9em;
                    text-align: left;
                }}
                .support-links {{
                    margin-top: 25px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }}
                .support-links a {{
                    color: {response_data['color']};
                    text-decoration: none;
                    margin: 0 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">{response_data['icon']}</div>
                <h1 class="title">{response_data['title']}</h1>
                <p class="message">{response_data['message']}</p>
                
                <div class="info-box">
                    <strong>Wait Time:</strong> {response_data['retry_after_human']}<br>
                    <strong>Incident Type:</strong> {response_data['abuse_type'].replace('_', ' ').title()}<br>
                    <strong>Severity:</strong> {response_data['severity_description']}
                    {f"<br><strong>Incident ID:</strong> {response_data['incident_id']}" if response_data['incident_id'] else ""}
                </div>
                
                <div class="countdown">
                    Time Remaining: {response_data['retry_after_human']}
                </div>
                
                <div class="guidance">
                    <strong>💡 What You Can Do:</strong><br>
                    {response_data['guidance']}<br><br>
                    <strong>Next Action:</strong> {response_data['next_action']}
                </div>
                
                <div class="details">
                    <strong>Technical Details:</strong><br>
                    Timestamp: {response_data['timestamp']}<br>
                    Severity Level: {response_data['level']}/5<br>
                    Rate Limit Type: Abuse Detection<br>
                    Retry After: {response_data['retry_after']}s
                </div>
                
                <div class="support-links">
                    <a href="mailto:{response_data['support']['contact']}">📧 Contact Support</a>
                    <a href="{response_data['support']['documentation']}">📚 Documentation</a>
                    <a href="{response_data['support']['appeal_process']}">⚖️ Appeal Process</a>
                </div>
            </div>
            
            <script>
                console.log('NextProperty AI - Rate Limit Handler');
                console.log('Abuse Type: {response_data["abuse_type"]}');
                console.log('Severity Level: {response_data["level"]}/5');
                console.log('Retry After: {response_data["retry_after"]}s');
                console.log('Incident ID: {response_data["incident_id"]}');
            </script>
        </body>
        </html>
        """


# Global instance for standalone use
standalone_handler = StandaloneRateLimitErrorHandler()


def demonstrate_abuse_detection_handling():
    """Demonstrate the abuse detection error handling with the actual error you received."""
    
    print("🔧 NextProperty AI - Enhanced Rate Limit Error Handler Demo")
    print("=" * 60)
    
    # Your actual error data
    actual_error = {
        "abuse_type": "resource_exhaustion",
        "error": "Request blocked due to abuse detection",
        "incident_id": 1753105363.67304,
        "level": 4,
        "retry_after": 504,
        "type": "abuse_rate_limit"
    }
    
    print("📥 Processing your actual error:")
    print(json.dumps(actual_error, indent=2))
    print()
    
    # Process the error
    response = standalone_handler.handle_abuse_detection_error(actual_error)
    
    print("📤 Generated Response:")
    print(json.dumps(response, indent=2))
    print()
    
    # Generate HTML
    html_response = standalone_handler.generate_html_response(response)
    
    # Save HTML to file for viewing
    with open('abuse_detection_demo.html', 'w') as f:
        f.write(html_response)
    
    print("💾 HTML response saved to 'abuse_detection_demo.html'")
    print("🌐 Open this file in your browser to see the error page")
    print()
    
    # Test different abuse types
    print("🧪 Testing different abuse types:")
    
    abuse_types = ['rapid_requests', 'brute_force', 'scraping', 'api_abuse', 'suspicious_patterns']
    
    for abuse_type in abuse_types:
        test_error = {
            "abuse_type": abuse_type,
            "error": f"Request blocked due to {abuse_type}",
            "incident_id": int(time.time()),
            "level": 2,
            "retry_after": 180,
            "type": "abuse_rate_limit"
        }
        
        response = standalone_handler.handle_abuse_detection_error(test_error)
        print(f"  ✅ {abuse_type}: {response['title']}")
    
    print()
    print("🎉 Demo completed successfully!")
    print("📋 Summary of what this error handler provides:")
    print("   • User-friendly error messages")
    print("   • Specific guidance based on abuse type")
    print("   • Severity-based retry times")
    print("   • Professional HTML error pages")
    print("   • Proper HTTP headers")
    print("   • Support contact information")
    print("   • Incident tracking")


if __name__ == "__main__":
    demonstrate_abuse_detection_handling()
