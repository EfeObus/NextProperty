# Security Test Suite Documentation

This comprehensive security test suite provides thorough testing of NextProperty AI's security systems, including advanced input validation, XSS protection, SQL injection detection, behavioral analysis, and performance testing.

## 📁 Test Files Overview

### Core Test Files

1. **`test_security_comprehensive.py`** - Main security functionality tests
   - Advanced Input Validation tests
   - XSS Protection tests  
   - CSRF Protection tests
   - Security Middleware tests
   - Behavioral Analysis tests
   - Integration tests

2. **`test_security_performance.py`** - Performance and load testing
   - Single-threaded performance tests
   - Multi-threaded stress tests
   - Memory usage monitoring
   - Edge case performance testing
   - Resource exhaustion protection

3. **`test_security_attacks.py`** - Attack simulation and penetration testing
   - XSS attack vector simulation
   - SQL injection attack testing
   - Command injection detection
   - Real-world attack scenarios
   - Social engineering detection

### Support Files

4. **`security_test_config.py`** - Test configuration and fixtures
5. **`run_security_tests.py`** - Test runner with comprehensive reporting

## 🚀 Quick Start

### Prerequisites

```bash
# Install required dependencies
pip install pytest pytest-cov pytest-json-report coverage bleach markupsafe numpy

# Optional dependencies for enhanced features
pip install psutil  # For memory monitoring
```

### Running Tests

#### Run All Security Tests
```bash
# Basic run
python run_security_tests.py

# Verbose output
python run_security_tests.py --verbose

# Quick mode (less verbose)
python run_security_tests.py --quick
```

#### Run Specific Test Suites
```bash
# Run only comprehensive tests
python run_security_tests.py --suite tests/test_security_comprehensive.py

# Run only performance tests
python run_security_tests.py --suite tests/test_security_performance.py

# Run only attack simulation tests
python run_security_tests.py --suite tests/test_security_attacks.py
```

#### Generate Reports
```bash
# Generate JSON report
python run_security_tests.py --report security_report.json

# Generate HTML report
python run_security_tests.py --html

# Generate both reports
python run_security_tests.py --report security_report.json --html
```

#### Using pytest directly
```bash
# Run all security tests
pytest tests/test_security_*.py -v

# Run with coverage
pytest tests/test_security_*.py --cov=app.security --cov-report=html

# Run specific test categories
pytest -m xss tests/test_security_*.py  # XSS tests only
pytest -m performance tests/test_security_*.py  # Performance tests only
pytest -m attack_simulation tests/test_security_*.py  # Attack simulation only
```

## 📊 Test Categories

### 1. Input Validation Tests
- **Safe input validation** - Ensures legitimate inputs pass validation
- **XSS attack detection** - Tests detection of various XSS payloads
- **SQL injection detection** - Validates SQL injection pattern recognition
- **Command injection detection** - Tests command injection prevention
- **Encoding evasion detection** - Checks detection of encoding-based attacks
- **Input type validation** - Tests type-specific validation (email, URL, etc.)
- **Batch validation** - Tests multiple input validation
- **Length validation** - Tests input length limits
- **Sanitization** - Validates input sanitization effectiveness

### 2. XSS Protection Tests
- **Context-aware sanitization** - Tests sanitization based on content context
- **Advanced attack vectors** - Tests detection of sophisticated XSS attacks
- **Bypass attempt detection** - Tests detection of XSS filter bypass attempts
- **Mutation XSS detection** - Tests detection of mXSS attacks

### 3. Behavioral Analysis Tests
- **Rapid request detection** - Tests detection of automated attacks
- **Pattern probing detection** - Tests detection of vulnerability scanning
- **Session anomaly detection** - Tests detection of suspicious session activity
- **Encoding evasion patterns** - Tests behavioral pattern recognition
- **Parameter pollution detection** - Tests detection of parameter pollution attacks

### 4. Performance Tests
- **Single-threaded performance** - Measures validation performance
- **Multi-threaded stress testing** - Tests performance under concurrent load
- **Memory usage monitoring** - Monitors memory consumption under load
- **Edge case performance** - Tests performance with edge cases
- **Resource exhaustion protection** - Tests protection against DoS attacks

### 5. Attack Simulation Tests
- **Basic attack detection** - Tests detection of common attack patterns
- **Advanced attack vectors** - Tests sophisticated attack techniques
- **WAF bypass attempts** - Tests detection of firewall bypass techniques
- **Polyglot payload detection** - Tests multi-context attack payloads
- **Real-world scenarios** - Simulates actual attack scenarios

## 🎯 Expected Results

### Detection Rates (Minimum Expected)
- Basic XSS attacks: **≥90%** detection rate
- Advanced XSS attacks: **≥75%** detection rate
- WAF bypass attempts: **≥70%** detection rate
- Basic SQL injection: **≥80%** detection rate
- Advanced SQL injection: **≥70%** detection rate
- Command injection: **≥85%** detection rate

### Performance Benchmarks
- Average validation time: **<10ms**
- Maximum validation time: **<50ms**
- Throughput: **>50 validations/second**
- Memory increase under load: **<50MB**

### Test Success Criteria
- Overall test suite success rate: **≥95%**
- No critical security vulnerabilities undetected
- Performance benchmarks met
- No memory leaks detected

## 🔧 Test Configuration

### Environment Variables
```bash
# Optional configuration
export SECURITY_TEST_VERBOSE=1          # Enable verbose output
export SECURITY_TEST_QUICK=1            # Enable quick mode
export SECURITY_TEST_PERFORMANCE=1      # Include performance tests
export SECURITY_TEST_ATTACKS=1          # Include attack simulation
```

### Custom Test Configuration
Edit `tests/security_test_config.py` to customize:
- Performance thresholds
- Attack payload sets
- Detection rate requirements
- Test fixtures and data

## 📋 Test Markers

Use pytest markers to run specific test categories:

```bash
# Security-related tests
pytest -m security

# XSS protection tests
pytest -m xss

# SQL injection tests  
pytest -m sqli

# Performance tests
pytest -m performance

# Attack simulation tests
pytest -m attack_simulation
```

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure PYTHONPATH includes project root
export PYTHONPATH=/path/to/nextproperty:$PYTHONPATH

# Or run from project root
cd /path/to/nextproperty
python run_security_tests.py
```

**Missing Dependencies**
```bash
# Install all test dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-json-report
```

**Flask Not Available**
The test suite includes mocks for Flask components, so it can run even if Flask is not fully configured.

**Memory Issues in Performance Tests**
```bash
# Reduce test load for systems with limited memory
pytest tests/test_security_performance.py::TestSecurityPerformance::test_validator_performance_single_thread
```

### Test Debugging

**Enable Debug Output**
```bash
# Run with maximum verbosity
python run_security_tests.py --verbose

# Run specific failing test
pytest tests/test_security_comprehensive.py::TestAdvancedInputValidation::test_xss_attack_detection -v -s
```

**Performance Debugging**
```bash
# Run performance tests with profiling
pytest tests/test_security_performance.py --profile

# Monitor system resources
htop  # or similar system monitor
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Security Tests
on: [push, pull_request]
jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-json-report
      - name: Run security tests
        run: python run_security_tests.py --html
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: security-test-results
          path: security_test_report_*.html
```

## 🔒 Security Considerations

### Test Data Security
- Test payloads are contained within the test environment
- No real credentials or sensitive data used in tests
- Attack simulations are safe and do not perform actual attacks

### Production Testing
- **Never run attack simulation tests against production systems**
- Use staging/test environments for comprehensive security testing
- Monitor test runs for any unintended side effects

## 📊 Reporting

### Report Contents
- **Test Summary** - Overall pass/fail statistics
- **Performance Metrics** - Timing and throughput data
- **Security Analysis** - Detection rates and missed threats
- **Recommendations** - Actionable security improvements

### Report Formats
- **JSON** - Machine-readable detailed results
- **HTML** - Human-readable visual report
- **Console** - Real-time test progress and summary

## 🚨 Critical Security Alerts

The test suite will flag critical issues:

1. **Detection Rate Below Threshold** - Attack detection rates below expected minimums
2. **Performance Degradation** - Security checks taking too long
3. **Memory Leaks** - Excessive memory usage during testing
4. **Test Failures** - Any test failures indicate potential security gaps

## 📞 Support

For issues with the security test suite:

1. Check the troubleshooting section above
2. Review test logs for specific error messages
3. Ensure all dependencies are properly installed
4. Verify test environment configuration

## 🔄 Maintenance

### Regular Updates
- Update attack payloads based on latest threat intelligence
- Adjust detection thresholds based on false positive rates
- Add new test scenarios for emerging attack vectors
- Review and update performance benchmarks

### Version Compatibility
- Tests are designed to work with Python 3.7+
- Compatible with pytest 6.0+
- Supports both Flask 1.x and 2.x applications
