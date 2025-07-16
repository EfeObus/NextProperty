#!/usr/bin/env python3
"""
NextProperty AI - Rate Limiting Feature Status Summary
=====================================================

This script provides a clean, actionable summary of the rate limiting feature status.
"""

import json
import os
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def load_test_results():
    """Load the latest test results"""
    results_file = "/Users/efeobukohwo/Desktop/Nextproperty Real Estate/feature_status_results.json"
    
    if not os.path.exists(results_file):
        print(f"{Colors.FAIL}❌ No test results found. Please run the feature status test first:{Colors.ENDC}")
        print(f"   python rate_limiting_feature_status_test.py --output feature_status_results.json")
        return None
    
    with open(results_file, 'r') as f:
        return json.load(f)

def print_feature_status_summary():
    """Print a clean summary of feature status"""
    results = load_test_results()
    if not results:
        return
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("🎯 NEXTPROPERTY AI - RATE LIMITING FEATURE STATUS SUMMARY")
    print("=" * 70)
    print(f"{Colors.ENDC}")
    
    # Summary Statistics
    total_implemented = len(results['feature_results']['fully_implemented'])
    total_demo = len(results['feature_results']['demo_mode'])
    total_not_implemented = len(results['feature_results']['not_implemented'])
    total_features = total_implemented + total_demo + total_not_implemented
    
    implementation_rate = (total_implemented / total_features) * 100 if total_features > 0 else 0
    
    print(f"{Colors.HEADER}📊 OVERALL STATUS:{Colors.ENDC}")
    print(f"   Implementation Rate: {implementation_rate:.1f}%")
    print(f"   Production Ready Features: {total_implemented}/{total_features}")
    print()
    
    # Feature Categories
    print(f"{Colors.OKGREEN}✅ FULLY IMPLEMENTED (Production Ready) - {total_implemented} features:{Colors.ENDC}")
    for feature in results['feature_results']['fully_implemented']:
        feature_details = results['feature_results']['detailed_results'].get(feature, {})
        endpoints = feature_details.get('endpoints_tested', [])
        print(f"   ✅ {feature.replace('_', ' ').title()}")
        if endpoints:
            working_endpoints = [ep for ep in endpoints if ep]  # Filter out empty
            print(f"      Rate limiting active on: {', '.join(working_endpoints[:3])}{'...' if len(working_endpoints) > 3 else ''}")
    print()
    
    print(f"{Colors.WARNING}🔄 DEMO MODE (Configured but not active) - {total_demo} features:{Colors.ENDC}")
    for feature in results['feature_results']['demo_mode']:
        print(f"   🔄 {feature.replace('_', ' ').title()}")
        if feature == 'authentication':
            print(f"      Login/Register pages exist but in demo mode")
    
    # Show inactive demo features
    demo_inactive = [k for k, v in results['demo_mode'].items() if not v]
    if demo_inactive:
        print(f"\n{Colors.WARNING}⚠️ DEMO MODE (Inactive) - {len(demo_inactive)} features:{Colors.ENDC}")
        for feature in demo_inactive:
            print(f"   ⚠️ {feature.replace('_', ' ').title()} - Ready for activation")
    print()
    
    print(f"{Colors.FAIL}❌ NOT IMPLEMENTED - {total_not_implemented} features:{Colors.ENDC}")
    for feature in results['feature_results']['not_implemented']:
        print(f"   ❌ {feature.replace('_', ' ').title()}")
    print()
    
    # Actionable Recommendations
    print(f"{Colors.HEADER}🚀 ACTIONABLE NEXT STEPS:{Colors.ENDC}")
    
    if implementation_rate >= 80:
        print(f"{Colors.OKGREEN}🎉 EXCELLENT STATUS - Ready for production!{Colors.ENDC}")
        print("   1. ✅ Core rate limiting is fully functional")
        print("   2. ✅ All critical endpoints are protected") 
        print("   3. 🔄 Consider activating authentication for user-based limits")
    elif implementation_rate >= 50:
        print(f"{Colors.WARNING}👍 GOOD STATUS - Core features working well{Colors.ENDC}")
        print("   1. ✅ Most critical features are implemented")
        print("   2. 🔄 Activate authentication system:")
        print("      - Enable user registration/login")
        print("      - Activate user-based rate limiting")
        print("   3. 📊 Monitor current usage patterns")
    else:
        print(f"{Colors.FAIL}🚨 NEEDS ATTENTION - Significant gaps{Colors.ENDC}")
        print("   1. ❌ Critical features missing")
        print("   2. 🔧 Complete core implementation first")
        print("   3. 🧪 Run comprehensive tests")
    
    print()
    print(f"{Colors.HEADER}📋 IMMEDIATE PRIORITIES:{Colors.ENDC}")
    
    # Specific recommendations based on current status
    if 'authentication' in results['feature_results']['demo_mode']:
        print(f"   1. 🔄 ACTIVATE AUTHENTICATION:")
        print(f"      - Set ENABLE_AUTHENTICATION = True in config")
        print(f"      - Enable user registration/login endpoints")
        print(f"      - This will unlock user-based rate limiting")
    
    print(f"   2. 🗄️ SETUP PRODUCTION REDIS:")
    print(f"      - Install Redis server")
    print(f"      - Configure REDIS_URL in environment")
    print(f"      - Enable distributed rate limiting")
    
    print(f"   3. 📊 MONITOR USAGE PATTERNS:")
    print(f"      - Track current rate limit usage")
    print(f"      - Adjust limits based on real traffic")
    print(f"      - Set up alerting for violations")
    
    if total_not_implemented > 0:
        print(f"   4. 📅 PLAN ADVANCED FEATURES:")
        print(f"      - Prioritize based on business needs")
        print(f"      - Consider: API keys, geographic limits, analytics")
    
    # Technical Status
    print()
    print(f"{Colors.HEADER}🔧 TECHNICAL STATUS:{Colors.ENDC}")
    cli_status = "✅ WORKING" if results.get('cli_working') else "❌ NOT WORKING"
    print(f"   CLI Commands: {cli_status}")
    
    if results.get('feature_results', {}).get('test_errors'):
        print(f"   Issues detected:")
        for error in results['feature_results']['test_errors']:
            print(f"   ⚠️ {error}")
    
    # Test Information
    test_time = results.get('timestamp', 'Unknown')
    duration = results.get('duration', 0)
    print()
    print(f"{Colors.HEADER}ℹ️ TEST INFORMATION:{Colors.ENDC}")
    print(f"   Last tested: {test_time}")
    print(f"   Test duration: {duration:.2f} seconds")
    print(f"   Results saved: feature_status_results.json")

def print_quick_status():
    """Print just the key numbers"""
    results = load_test_results()
    if not results:
        return
    
    total_implemented = len(results['feature_results']['fully_implemented'])
    total_demo = len(results['feature_results']['demo_mode'])
    total_not_implemented = len(results['feature_results']['not_implemented'])
    total_features = total_implemented + total_demo + total_not_implemented
    
    implementation_rate = (total_implemented / total_features) * 100 if total_features > 0 else 0
    
    print(f"{Colors.BOLD}NextProperty AI Rate Limiting Status:{Colors.ENDC}")
    print(f"✅ Implemented: {total_implemented} | 🔄 Demo: {total_demo} | ❌ Missing: {total_not_implemented}")
    print(f"📈 Implementation Rate: {implementation_rate:.1f}%")
    
    if implementation_rate >= 80:
        print(f"{Colors.OKGREEN}🎉 Status: EXCELLENT - Production Ready!{Colors.ENDC}")
    elif implementation_rate >= 50:
        print(f"{Colors.WARNING}👍 Status: GOOD - Most features working{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}🚨 Status: NEEDS ATTENTION{Colors.ENDC}")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        print_quick_status()
    else:
        print_feature_status_summary()

if __name__ == "__main__":
    main()
