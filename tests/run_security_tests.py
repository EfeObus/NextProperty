#!/usr/bin/env python3
"""
Security Test Runner for NextProperty AI.

This script runs all security tests and generates comprehensive reports
on the security posture of the application.
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class SecurityTestRunner:
    """Security test runner with comprehensive reporting."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {},
            'recommendations': []
        }
        self.test_files = [
            'tests/test_security_comprehensive.py',
            'tests/test_security_performance.py', 
            'tests/test_security_attacks.py'
        ]
    
    def run_test_suite(self, test_file: str, verbose: bool = True) -> dict:
        """Run a specific test suite and capture results."""
        print(f"\n{'='*60}")
        print(f"Running: {test_file}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        # Build pytest command
        cmd = [
            'python', '-m', 'pytest',
            test_file,
            '-v' if verbose else '-q',
            '--tb=short'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse test output for basic statistics
            test_details = self._parse_pytest_output(result.stdout)
            
            suite_result = {
                'file': test_file,
                'duration': duration,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0,
                'details': test_details
            }
            
            # Print summary
            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED ({duration:.2f}s)")
            else:
                print(f"❌ {test_file} - FAILED ({duration:.2f}s)")
                print(f"Error output:\n{result.stderr}")
            
            return suite_result
            
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            return {
                'file': test_file,
                'duration': 0,
                'return_code': -1,
                'error': str(e),
                'success': False
            }
    
    def run_all_tests(self, verbose: bool = True) -> dict:
        """Run all security test suites."""
        print("🔒 NextProperty AI Security Test Suite")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        total_start_time = time.time()
        
        for test_file in self.test_files:
            suite_result = self.run_test_suite(test_file, verbose)
            self.results['test_suites'][Path(test_file).stem] = suite_result
        
        total_duration = time.time() - total_start_time
        
        # Generate summary
        self.generate_summary(total_duration)
        
        # Generate recommendations
        self.generate_recommendations()
        
        return self.results
    
    def generate_summary(self, total_duration: float):
        """Generate test summary."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        total_suites = len(self.test_files)
        passed_suites = 0
        
        for suite_name, suite_result in self.results['test_suites'].items():
            if suite_result['success']:
                passed_suites += 1
            
            # Extract test counts from details if available
            if 'details' in suite_result and 'summary' in suite_result['details']:
                summary = suite_result['details']['summary']
                total_tests += summary.get('total', 0)
                passed_tests += summary.get('passed', 0)
                failed_tests += summary.get('failed', 0)
        
        self.results['summary'] = {
            'total_duration': total_duration,
            'total_suites': total_suites,
            'passed_suites': passed_suites,
            'failed_suites': total_suites - passed_suites,
            'suite_success_rate': passed_suites / total_suites if total_suites > 0 else 0,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'test_success_rate': passed_tests / total_tests if total_tests > 0 else 0
        }
        
        # Print summary
        print(f"\n{'='*60}")
        print("🔒 SECURITY TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Test Suites: {passed_suites}/{total_suites} passed ({self.results['summary']['suite_success_rate']:.1%})")
        if total_tests > 0:
            print(f"Total Tests: {passed_tests}/{total_tests} passed ({self.results['summary']['test_success_rate']:.1%})")
        
        # Print individual suite results
        print(f"\n📊 Suite Breakdown:")
        for suite_name, suite_result in self.results['test_suites'].items():
            status = "✅ PASS" if suite_result['success'] else "❌ FAIL"
            duration = suite_result.get('duration', 0)
            print(f"  {suite_name:<30} {status} ({duration:.2f}s)")
    
    def generate_recommendations(self):
        """Generate security recommendations based on test results."""
        recommendations = []
        
        # Check overall test success rate
        summary = self.results['summary']
        
        if summary['suite_success_rate'] < 1.0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Test Failures',
                'issue': f"{summary['failed_suites']} test suite(s) failed",
                'recommendation': "Review and fix failing tests before deploying to production"
            })
        
        if summary.get('test_success_rate', 1.0) < 0.9:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Test Coverage',
                'issue': f"Test success rate is {summary.get('test_success_rate', 0):.1%}",
                'recommendation': "Investigate and fix failing individual tests"
            })
        
        # Check performance
        if summary['total_duration'] > 60:  # More than 1 minute
            recommendations.append({
                'priority': 'LOW',
                'category': 'Performance',
                'issue': f"Security tests took {summary['total_duration']:.1f}s to complete",
                'recommendation': "Consider optimizing security test performance"
            })
        
        # Analyze specific test failures
        for suite_name, suite_result in self.results['test_suites'].items():
            if not suite_result['success']:
                stderr = suite_result.get('stderr', '')
                
                if 'import' in stderr.lower() or 'modulenotfounderror' in stderr.lower():
                    recommendations.append({
                        'priority': 'HIGH',
                        'category': 'Dependencies',
                        'issue': f"Module import errors in {suite_name}",
                        'recommendation': "Check and install missing dependencies"
                    })
                
                if 'assertion' in stderr.lower():
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'category': 'Security Logic',
                        'issue': f"Security assertion failures in {suite_name}",
                        'recommendation': "Review security validation logic and thresholds"
                    })
        
        # Add general recommendations
        recommendations.extend([
            {
                'priority': 'MEDIUM',
                'category': 'Security Monitoring',
                'issue': 'Regular security testing',
                'recommendation': 'Run security tests in CI/CD pipeline and before each release'
            },
            {
                'priority': 'LOW',
                'category': 'Security Updates',
                'issue': 'Security pattern updates',
                'recommendation': 'Regularly update attack patterns and signatures based on latest threats'
            }
        ])
        
        self.results['recommendations'] = recommendations
        
        # Print recommendations
        if recommendations:
            print(f"\n🎯 SECURITY RECOMMENDATIONS")
            print(f"{'='*60}")
            
            for rec in recommendations:
                priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
                emoji = priority_emoji.get(rec['priority'], '⚪')
                
                print(f"{emoji} {rec['priority']} - {rec['category']}")
                print(f"   Issue: {rec['issue']}")
                print(f"   Action: {rec['recommendation']}")
                print()
    
    def save_report(self, output_file: str = None):
        """Save detailed test report to file."""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"security_test_report_{timestamp}.json"
        
        report_path = project_root / output_file
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {report_path}")
        return str(report_path)
    
    def generate_html_report(self, output_file: str = None):
        """Generate HTML report."""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"security_test_report_{timestamp}.html"
        
        report_path = project_root / output_file
        
        html_content = self._generate_html_content()
        
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        print(f"🌐 HTML report saved to: {report_path}")
        return str(report_path)
    
    def _generate_html_content(self) -> str:
        """Generate HTML content for the report."""
        summary = self.results['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NextProperty AI Security Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .success {{ color: #27ae60; }}
        .failure {{ color: #e74c3c; }}
        .suite {{ margin: 10px 0; padding: 10px; border-left: 4px solid #3498db; }}
        .recommendation {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .high {{ background: #ffebee; border-left: 4px solid #f44336; }}
        .medium {{ background: #fff3e0; border-left: 4px solid #ff9800; }}
        .low {{ background: #e8f5e8; border-left: 4px solid #4caf50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 NextProperty AI Security Test Report</h1>
        <p>Generated on: {self.results['timestamp']}</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Duration</td><td>{summary['total_duration']:.2f}s</td></tr>
            <tr><td>Test Suites</td><td class="{'success' if summary['suite_success_rate'] == 1.0 else 'failure'}">{summary['passed_suites']}/{summary['total_suites']} ({summary['suite_success_rate']:.1%})</td></tr>
            <tr><td>Total Tests</td><td class="{'success' if summary.get('test_success_rate', 0) > 0.9 else 'failure'}">{summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)} ({summary.get('test_success_rate', 0):.1%})</td></tr>
        </table>
    </div>
    
    <h2>🧪 Test Suite Results</h2>
"""
        
        for suite_name, suite_result in self.results['test_suites'].items():
            status_class = "success" if suite_result['success'] else "failure"
            status_text = "✅ PASSED" if suite_result['success'] else "❌ FAILED"
            
            html += f"""
    <div class="suite">
        <h3>{suite_name}</h3>
        <p><strong>Status:</strong> <span class="{status_class}">{status_text}</span></p>
        <p><strong>Duration:</strong> {suite_result.get('duration', 0):.2f}s</p>
"""
            
            if not suite_result['success'] and 'stderr' in suite_result:
                html += f"<p><strong>Error:</strong> <pre>{suite_result['stderr'][:500]}</pre></p>"
            
            html += "</div>"
        
        if self.results['recommendations']:
            html += "<h2>🎯 Recommendations</h2>"
            
            for rec in self.results['recommendations']:
                priority_class = rec['priority'].lower()
                html += f"""
    <div class="recommendation {priority_class}">
        <h4>{rec['priority']} - {rec['category']}</h4>
        <p><strong>Issue:</strong> {rec['issue']}</p>
        <p><strong>Recommendation:</strong> {rec['recommendation']}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def _parse_pytest_output(self, output: str) -> dict:
        """Parse pytest output to extract test statistics."""
        details = {
            'tests': {'passed': 0, 'failed': 0, 'skipped': 0, 'total': 0},
            'coverage': {},
            'errors': []
        }
        
        lines = output.split('\n')
        
        # Look for test summary line
        for line in lines:
            if 'failed' in line and 'passed' in line:
                # Example: "17 failed, 12 passed, 1 skipped, 1 warning in 0.91s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'failed' and i > 0:
                        details['tests']['failed'] = int(parts[i-1])
                    elif part == 'passed' and i > 0:
                        details['tests']['passed'] = int(parts[i-1])
                    elif part == 'skipped' and i > 0:
                        details['tests']['skipped'] = int(parts[i-1])
                break
            elif 'passed' in line and ('failed' not in line):
                # Example: "12 passed in 0.91s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        details['tests']['passed'] = int(parts[i-1])
                break
        
        details['tests']['total'] = (
            details['tests']['passed'] + 
            details['tests']['failed'] + 
            details['tests']['skipped']
        )
        
        return details
    
    # ...existing code...
def main():
    """Main function to run security tests."""
    parser = argparse.ArgumentParser(description='Run NextProperty AI security tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--quick', '-q', action='store_true', help='Quick mode (less verbose)')
    parser.add_argument('--report', '-r', help='Save report to specific file')
    parser.add_argument('--html', action='store_true', help='Generate HTML report')
    parser.add_argument('--suite', '-s', help='Run specific test suite only')
    
    args = parser.parse_args()
    
    runner = SecurityTestRunner()
    
    # Run specific suite or all suites
    if args.suite:
        if args.suite in runner.test_files:
            suite_result = runner.run_test_suite(args.suite, not args.quick)
            runner.results['test_suites'][Path(args.suite).stem] = suite_result
            runner.generate_summary(suite_result.get('duration', 0))
        else:
            print(f"❌ Test suite '{args.suite}' not found")
            print(f"Available suites: {', '.join(runner.test_files)}")
            return 1
    else:
        runner.run_all_tests(not args.quick)
    
    # Save reports
    if args.report or args.html:
        runner.save_report(args.report)
    
    if args.html:
        runner.generate_html_report()
    
    # Return appropriate exit code
    summary = runner.results['summary']
    if summary.get('suite_success_rate', 0) == 1.0:
        print("\n🎉 All security tests passed!")
        return 0
    else:
        print(f"\n⚠️  {summary.get('failed_suites', 0)} test suite(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
