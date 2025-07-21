# NextProperty AI - Comprehensive Security Test Suite

This comprehensive security test suite provides complete coverage of all security features implemented in the NextProperty AI platform. It tests multiple layers of security including rate limiting, XSS protection, CSRF protection, input validation, behavioral analysis, and more.

## 🔒 Features Tested

### 1. **Advanced Rate Limiting**
- Global rate limiting (system-wide)
- IP-based rate limiting 
- User-based rate limiting
- Endpoint-specific limits
- Category-based limits (auth, API, admin, upload)
- Burst protection
- Progressive penalties

### 2. **XSS Protection**
- Basic XSS attack vectors
- Advanced XSS payloads  
- Context-aware protection
- Input sanitization
- Output encoding
- DOM-based XSS protection

### 3. **CSRF Protection**
- Token validation
- Cross-origin request blocking
- State-changing operation protection
- Form-based CSRF
- AJAX CSRF protection

### 4. **Security Headers**
- X-XSS-Protection
- X-Content-Type-Options
- X-Frame-Options (Clickjacking protection)
- Content-Security-Policy
- Referrer-Policy
- Permissions-Policy
- Strict-Transport-Security

### 5. **Input Validation**
- SQL injection prevention
- Path traversal protection
- Command injection blocking
- Malformed input handling
- Length validation
- Character encoding validation

### 6. **API Security**
- Authentication validation
- Authorization checks
- API key management
- Rate limiting on API endpoints
- Input validation for API calls

### 7. **Behavioral Analysis**
- Rapid request detection
- Brute force attack prevention
- Directory scanning detection
- Anomaly detection
- Pattern recognition

### 8. **Geographic Rate Limiting**
- Country-based limiting
- Province/state-based controls
- City-specific restrictions
- IP geolocation validation

## 🚀 Quick Start

### Prerequisites

```bash
# Install required dependencies
pip install requests
```

### Basic Usage

```bash
# Run all security tests
python comprehensive_security_test.py

# Run with verbose output
python comprehensive_security_test.py --verbose

# Test specific security feature
python comprehensive_security_test.py --feature rate_limiting
python comprehensive_security_test.py --feature xss_protection
python comprehensive_security_test.py --feature csrf_protection

# Test against different URL
python comprehensive_security_test.py --url http://your-domain.com

# Save results to JSON file
python comprehensive_security_test.py --output security_results.json
```

### Advanced Usage

```bash
# Run with custom configuration
NEXTPROPERTY_URL=http://localhost:8080 python comprehensive_security_test.py

# Test in CI/CD environment
FLASK_ENV=testing python comprehensive_security_test.py

# Run specific test categories
python comprehensive_security_test.py --feature behavioral_analysis --verbose
```

## 📊 Test Results & Reporting

### Console Output
The test suite provides real-time colored console output showing:
- Test progress and status
- Pass/fail indicators
- Response times
- Detailed error messages
- Security recommendations

### JSON Output
Save detailed results to JSON for further analysis:
```bash
python comprehensive_security_test.py --output results.json
```

JSON output includes:
- Timestamp and test metadata
- Detailed test results per category
- Performance metrics
- Security compliance status
- Recommendations

### Sample Output
```
🔒 NextProperty AI - Comprehensive Security Test Suite
Target: http://localhost:5007
Timestamp: 2025-01-20 15:30:45

================================================================================
                           TESTING RATE LIMITING                              
================================================================================

[PASS] Testing global rate limiting
[PASS] Testing api rate limiting  
[PASS] Testing auth rate limiting
[WARN] Testing upload rate limiting - No rate limiting detected

================================================================================
                           TESTING XSS PROTECTION                             
================================================================================

[PASS] XSS Protection - /contact: XSS blocked - Code: 400
[PASS] XSS Protection - /properties: XSS blocked - Code: 403
[FAIL] XSS Protection - /api/save-property: XSS not blocked - Code: 200

SUMMARY:
  Total Tests: 45
  Passed: 38
  Failed: 7
  Success Rate: 84.4%
```

## ⚙️ Configuration

### Environment Variables
```bash
# Application settings
NEXTPROPERTY_URL=http://localhost:5007    # Target URL
REQUEST_TIMEOUT=30                        # Request timeout in seconds
MAX_RETRIES=3                            # Maximum retry attempts
REQUEST_DELAY=0.1                        # Delay between requests

# Environment settings  
FLASK_ENV=development                    # Environment mode
CI=true                                  # CI/CD mode
```

### Custom Configuration
Modify `security_test_config.py` to customize:
- Rate limiting test parameters
- XSS payload lists
- CSRF test endpoints
- Geographic test locations
- Behavioral analysis patterns

Example configuration modification:
```python
# In security_test_config.py
class RateLimitConfig:
    TESTS = {
        'api': {
            'limit': 50,           # Adjust API rate limit
            'test_requests': 60,   # Test with more requests
            'endpoint': '/api/v2/properties'  # Test different endpoint
        }
    }
```

## 🧪 Test Categories

### 1. Rate Limiting Tests (`--feature rate_limiting`)
Tests the multi-layered rate limiting system:
- Makes multiple requests to different endpoint categories
- Verifies rate limits are enforced
- Checks for proper HTTP 429 responses
- Tests burst protection

### 2. XSS Protection Tests (`--feature xss_protection`)
Tests XSS attack prevention:
- Injects various XSS payloads
- Tests different contexts (forms, URLs, JSON)
- Verifies input sanitization
- Checks output encoding

### 3. CSRF Protection Tests (`--feature csrf_protection`)
Tests CSRF attack prevention:
- Attempts requests without CSRF tokens
- Tests with invalid tokens
- Verifies token validation
- Tests cross-origin protection

### 4. Security Headers Tests (`--feature security_headers`)
Validates security headers:
- Checks for required security headers
- Validates header values
- Tests CSP implementation
- Verifies clickjacking protection

### 5. Input Validation Tests (`--feature input_validation`)
Tests input validation mechanisms:
- SQL injection attempts
- Path traversal attacks
- Command injection tests
- Malformed input handling

### 6. API Security Tests (`--feature api_security`)
Tests API-specific security:
- Authentication validation
- Authorization checks
- Rate limiting on APIs
- Input validation for API calls

### 7. Behavioral Analysis Tests (`--feature behavioral_analysis`)
Tests anomaly detection:
- Rapid request patterns
- Brute force simulations
- Directory scanning attempts
- Suspicious behavior detection

### 8. Geographic Limiting Tests (`--feature geographic_limiting`)
Tests location-based controls:
- Country-based restrictions
- Province/state limiting
- IP geolocation validation
- Regional quotas

## 🔍 Understanding Test Results

### Test Status Indicators
- ✅ **PASS**: Security feature working correctly
- ❌ **FAIL**: Security vulnerability detected
- ⚠️ **WARN**: Potential issue or feature not implemented
- ℹ️ **INFO**: Informational message

### Response Codes
- **200**: Request successful (may indicate missing protection)
- **400**: Bad request (often indicates input validation)
- **401**: Unauthorized (authentication required)
- **403**: Forbidden (authorization or CSRF failure)
- **429**: Too Many Requests (rate limiting active)
- **500**: Server error (unexpected issue)

### Security Recommendations
Based on test results, the suite provides specific recommendations:
- 🔴 **Critical**: Immediate action required
- 🟡 **Warning**: Should be addressed
- 🔵 **Info**: Best practice suggestions

## 🛡️ Security Best Practices

### For Developers
1. **Always run security tests** before deploying
2. **Address all critical failures** immediately
3. **Review warnings** and implement recommendations
4. **Test security features** during development
5. **Monitor test results** for trends

### For DevOps
1. **Integrate tests** into CI/CD pipeline
2. **Set up automated alerts** for security failures
3. **Archive test results** for compliance
4. **Monitor security metrics** over time
5. **Update test configurations** as needed

### For Security Teams
1. **Review test coverage** regularly
2. **Update attack vectors** and payloads
3. **Customize tests** for specific threats
4. **Correlate results** with security events
5. **Use results** for security audits

## 🔧 Troubleshooting

### Common Issues

#### Application Not Responding
```bash
# Check if application is running
curl http://localhost:5007/health

# Check firewall/network connectivity
telnet localhost 5007
```

#### Rate Limiting False Positives
```bash
# Increase delays between requests
REQUEST_DELAY=1.0 python comprehensive_security_test.py

# Test specific endpoints
python comprehensive_security_test.py --feature rate_limiting --verbose
```

#### CSRF Token Issues
```bash
# Check if CSRF is properly configured in app
# Verify meta tag is present in HTML
curl -s http://localhost:5007/ | grep csrf-token
```

#### Test Timeouts
```bash
# Increase timeout
REQUEST_TIMEOUT=60 python comprehensive_security_test.py

# Test specific features
python comprehensive_security_test.py --feature security_headers
```

### Debug Mode
Enable verbose output for detailed debugging:
```bash
python comprehensive_security_test.py --verbose --feature xss_protection
```

### Custom Debugging
Add debug prints to the test suite:
```python
# In comprehensive_security_test.py
def make_request(self, method: str, endpoint: str, **kwargs):
    print(f"DEBUG: Making {method} request to {endpoint}")
    # ... rest of method
```

## 📈 Integration

### CI/CD Integration
Add to your CI/CD pipeline:

#### GitHub Actions
```yaml
- name: Run Security Tests
  run: |
    python comprehensive_security_test.py --output security_results.json
    if [ $? -ne 0 ]; then
      echo "Security tests failed!"
      exit 1
    fi
```

#### Jenkins
```groovy
stage('Security Testing') {
    steps {
        sh 'python comprehensive_security_test.py --output security_results.json'
        archiveArtifacts artifacts: 'security_results.json'
    }
}
```

### Monitoring Integration
Integrate with monitoring systems:
```python
# Send results to monitoring system
import requests
import json

def send_to_monitoring(results):
    monitoring_endpoint = "https://your-monitoring.com/api/security"
    requests.post(monitoring_endpoint, json=results)
```

## 📋 Compliance

### OWASP Top 10 Coverage
- **A1 - Injection**: Input validation tests
- **A2 - Broken Authentication**: CSRF and rate limiting tests  
- **A3 - Sensitive Data Exposure**: Security headers tests
- **A7 - Cross-Site Scripting**: XSS protection tests
- **A10 - Insufficient Logging**: Behavioral analysis tests

### Security Standards
- **ISO 27001**: Access controls and security processes
- **SOC 2**: Security monitoring and incident response
- **PIPEDA/GDPR**: Data protection and privacy

## 🔄 Continuous Improvement

### Regular Updates
1. **Update attack vectors** based on latest threats
2. **Add new test cases** for emerging vulnerabilities
3. **Improve test coverage** based on code changes
4. **Optimize performance** of test suite
5. **Enhance reporting** capabilities

### Community Contributions
1. **Report issues** and false positives
2. **Suggest improvements** and new features
3. **Contribute test cases** for specific scenarios
4. **Share configurations** for different environments
5. **Provide feedback** on test effectiveness

## 📞 Support

For issues, questions, or contributions:
1. Check existing test results and logs
2. Review configuration settings
3. Test individual components
4. Create minimal reproduction cases
5. Report with detailed information

## 📜 License

This security test suite is part of the NextProperty AI platform and follows the same licensing terms.

---

**🛡️ Stay Secure! Regular security testing is essential for maintaining a robust application.**
