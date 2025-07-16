#!/usr/bin/env python3
"""
NextProperty AI - Rate Limiting Test Scripts Overview
=====================================================

This script provides an overview of all available rate limiting test scripts
and their purposes, categorized by what they test.

Available Test Scripts:
1. rate_limiting_feature_status_test.py - NEW comprehensive feature status test
2. ultimate_rate_limit_functionality_test.py - Complete functionality testing
3. comprehensive_rate_limit_test.py - Comprehensive endpoint testing  
4. final_rate_limit_validation.py - Final validation and summary
5. Rate_limit_test.py - Basic rate limiting test

Author: NextProperty AI Team
Date: July 16, 2025
"""

import os
import subprocess
import sys
from datetime import datetime

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(message, level="INFO"):
    """Enhanced logging with colors"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "HEADER": Colors.HEADER,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "INFO": Colors.OKBLUE
    }
    color = colors.get(level, Colors.ENDC)
    print(f"{color}[{timestamp}] {message}{Colors.ENDC}")

def show_test_script_overview():
    """Show overview of all available test scripts"""
    log("🧪 NEXTPROPERTY AI - RATE LIMITING TEST SCRIPTS OVERVIEW", "HEADER")
    log("=" * 80, "INFO")
    
    test_scripts = {
        "rate_limiting_feature_status_test.py": {
            "description": "🆕 FEATURE STATUS TEST - Categorizes features by implementation status",
            "purpose": "Tests and categorizes rate limiting features as:",
            "categories": [
                "✅ FULLY IMPLEMENTED (Production Ready)",
                "🔄 PARTIALLY IMPLEMENTED (Demo Mode)", 
                "❌ NOT IMPLEMENTED YET"
            ],
            "usage": "python rate_limiting_feature_status_test.py [--url URL] [--output FILE]",
            "best_for": "Understanding current implementation status and what's working vs what needs development"
        },
        
        "ultimate_rate_limit_functionality_test.py": {
            "description": "🔬 ULTIMATE FUNCTIONALITY TEST - Comprehensive testing of all rate limiting features",
            "purpose": "Complete test suite covering:",
            "categories": [
                "Application Health & Status",
                "Web Route Rate Limiting", 
                "API Endpoint Rate Limiting",
                "ML Prediction Rate Limiting",
                "Search Functionality Rate Limiting",
                "Authentication Rate Limiting",
                "Concurrent Load Testing",
                "Sustained Load Testing",
                "CLI Command Testing",
                "Performance Metrics"
            ],
            "usage": "python ultimate_rate_limit_functionality_test.py",
            "best_for": "Comprehensive testing of all functionality and performance analysis"
        },
        
        "comprehensive_rate_limit_test.py": {
            "description": "📊 COMPREHENSIVE ENDPOINT TEST - Tests all endpoints with detailed metrics",
            "purpose": "Endpoint-focused testing including:",
            "categories": [
                "Complete endpoint coverage",
                "Performance analysis",
                "Concurrent load testing", 
                "Header validation",
                "Real-world scenario simulation"
            ],
            "usage": "python comprehensive_rate_limit_test.py",
            "best_for": "Detailed endpoint testing and performance metrics"
        },
        
        "final_rate_limit_validation.py": {
            "description": "✅ FINAL VALIDATION - Quick validation and summary",
            "purpose": "Final validation including:",
            "categories": [
                "File validation (check if all files exist)",
                "CLI command testing",
                "Basic integration testing",
                "Implementation status summary"
            ],
            "usage": "python final_rate_limit_validation.py",
            "best_for": "Quick validation and final status check"
        },
        
        "Rate_limit_test.py": {
            "description": "🔧 BASIC TEST - Simple rate limiting test",
            "purpose": "Basic rate limiting validation",
            "categories": [
                "Simple endpoint testing",
                "Basic rate limit validation"
            ],
            "usage": "python Rate_limit_test.py",
            "best_for": "Quick basic testing"
        }
    }
    
    current_dir = "/Users/efeobukohwo/Desktop/Nextproperty Real Estate"
    
    for script_name, info in test_scripts.items():
        script_path = os.path.join(current_dir, script_name)
        exists = os.path.exists(script_path)
        
        log(f"\n📄 {script_name}", "HEADER")
        log(f"Status: {'✅ EXISTS' if exists else '❌ MISSING'}", "SUCCESS" if exists else "ERROR")
        log(f"Description: {info['description']}", "INFO")
        log(f"Purpose: {info['purpose']}", "INFO")
        
        for category in info['categories']:
            log(f"  • {category}", "INFO")
            
        log(f"Usage: {info['usage']}", "WARNING")
        log(f"Best for: {info['best_for']}", "SUCCESS")

def run_feature_status_test():
    """Run the new feature status test"""
    log("\n🚀 Running Feature Status Test", "HEADER")
    log("This will test and categorize all rate limiting features by implementation status", "INFO")
    
    script_path = "/Users/efeobukohwo/Desktop/Nextproperty Real Estate/rate_limiting_feature_status_test.py"
    
    try:
        result = subprocess.run([
            sys.executable, script_path, 
            "--url", "http://localhost:5007",
            "--output", "feature_status_results.json"
        ], cwd="/Users/efeobukohwo/Desktop/Nextproperty Real Estate")
        
        if result.returncode == 0:
            log("✅ Feature status test completed successfully!", "SUCCESS")
        else:
            log("⚠️ Feature status test completed with issues", "WARNING")
            
    except Exception as e:
        log(f"❌ Error running feature status test: {str(e)}", "ERROR")

def run_status_summary():
    """Run the status summary"""
    log("\n📊 Running Status Summary", "HEADER")
    
    script_path = "/Users/efeobukohwo/Desktop/Nextproperty Real Estate/rate_limiting_status_summary.py"
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              cwd="/Users/efeobukohwo/Desktop/Nextproperty Real Estate")
        
        if result.returncode == 0:
            log("✅ Status summary completed successfully!", "SUCCESS")
        else:
            log("⚠️ Status summary completed with issues", "WARNING")
            
    except Exception as e:
        log(f"❌ Error running status summary: {str(e)}", "ERROR")

def show_menu():
    """Show interactive menu"""
    log("\n🎯 CHOOSE A TEST TO RUN:", "HEADER")
    log("=" * 50, "INFO")
    
    options = [
        ("1", "🆕 Feature Status Test", "Categorize features by implementation status", run_feature_status_test),
        ("2", "📊 Status Summary", "Show clean summary of current status", run_status_summary),
        ("3", "📊 Show Test Scripts Overview", "Show detailed overview again", show_test_script_overview),
        ("4", "❌ Exit", "Exit the test runner", lambda: exit(0))
    ]
    
    for option_num, title, description, _ in options:
        log(f"{option_num}. {title}", "SUCCESS")
        log(f"   {description}", "INFO")
    
    print()
    choice = input("Enter your choice (1-4): ").strip()
    
    for option_num, title, description, action in options:
        if choice == option_num:
            action()
            return
    
    log("❌ Invalid choice. Please try again.", "ERROR")
    show_menu()

def main():
    """Main execution"""
    log("🧪 NEXTPROPERTY AI - RATE LIMITING TEST RUNNER", "HEADER")
    log("=" * 60, "INFO")
    
    # Show overview first
    show_test_script_overview()
    
    # Check if the app is running
    log("\n🔍 Checking if NextProperty AI is running...", "INFO")
    try:
        import requests
        response = requests.get("http://localhost:5007/api/health", timeout=5)
        if response.status_code in [200, 404]:
            log("✅ Application is running at http://localhost:5007", "SUCCESS")
        else:
            log("⚠️ Application responded but may have issues", "WARNING")
    except:
        log("❌ Application not running at http://localhost:5007", "ERROR")
        log("💡 Please start the application first: python app.py", "INFO")
        
        start_choice = input("\nDo you want to continue anyway? (y/n): ").strip().lower()
        if start_choice != 'y':
            log("👋 Exiting. Please start the application and try again.", "INFO")
            return
    
    # Show interactive menu
    show_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️ Test runner interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Test runner failed: {str(e)}{Colors.ENDC}")
