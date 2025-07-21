#!/usr/bin/env python3
"""
Rate Limit Error Management CLI
NextProperty AI Platform

This script provides command-line tools for managing and monitoring
rate limiting errors across the application.
"""

import click
import json
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from tabulate import tabulate
from flask import Flask, current_app
from flask.cli import with_appcontext

# Add the app directory to the Python path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.security.rate_limit_error_handlers import rate_limit_error_handler


@click.group()
def rate_limit_errors():
    """Manage and monitor rate limiting errors."""
    pass


@rate_limit_errors.command()
@with_appcontext
def status():
    """Show current rate limit error status and metrics."""
    click.echo("🔍 Rate Limit Error Status")
    click.echo("=" * 50)
    
    try:
        metrics = rate_limit_error_handler.get_metrics()
        
        # Overall statistics
        click.echo(f"\n📊 Overall Statistics:")
        click.echo(f"  Total Blocks: {metrics['total_blocks']}")
        click.echo(f"  Recent Blocks: {metrics['recent_blocks_count']}")
        
        # Top blocked endpoints
        if metrics['top_blocked_endpoints']:
            click.echo(f"\n🎯 Top Blocked Endpoints:")
            headers = ['Endpoint', 'Blocks']
            table_data = metrics['top_blocked_endpoints']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        # Top blocked types
        if metrics['top_blocked_types']:
            click.echo(f"\n🚦 Top Block Types:")
            headers = ['Type', 'Blocks']
            table_data = metrics['top_blocked_types']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        click.echo(f"\n✅ Status check completed at {datetime.now()}")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}", err=True)
        sys.exit(1)


@rate_limit_errors.command()
@click.option('--limit', default=20, help='Number of recent incidents to show')
@with_appcontext
def recent(limit):
    """Show recent rate limit incidents."""
    click.echo("🕐 Recent Rate Limit Incidents")
    click.echo("=" * 50)
    
    try:
        metrics = rate_limit_error_handler.get_metrics()
        recent_blocks = getattr(rate_limit_error_handler.metrics, 'recent_blocks', [])
        
        if not recent_blocks:
            click.echo("No recent incidents found.")
            return
        
        # Show most recent incidents
        incidents = recent_blocks[-limit:]
        
        headers = ['Time', 'Type', 'Endpoint', 'IP', 'Retry After']
        table_data = []
        
        for incident in reversed(incidents):  # Show newest first
            time_str = incident['timestamp'][:19].replace('T', ' ')
            table_data.append([
                time_str,
                incident['limit_type'],
                incident['endpoint'][:30] + '...' if len(incident['endpoint']) > 30 else incident['endpoint'],
                incident['ip'],
                f"{incident['retry_after']}s"
            ])
        
        click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
        click.echo(f"\nShowing {len(table_data)} most recent incidents")
        
    except Exception as e:
        click.echo(f"❌ Error getting recent incidents: {e}", err=True)
        sys.exit(1)


@rate_limit_errors.command()
@click.option('--output', help='Output file for metrics (JSON format)')
@with_appcontext
def export(output):
    """Export rate limit metrics to file."""
    click.echo("📤 Exporting Rate Limit Metrics")
    click.echo("=" * 40)
    
    try:
        metrics = rate_limit_error_handler.get_metrics()
        
        # Add export metadata
        export_data = {
            'export_time': datetime.now().isoformat(),
            'metrics': metrics,
            'recent_blocks': getattr(rate_limit_error_handler.metrics, 'recent_blocks', [])
        }
        
        if output:
            with open(output, 'w') as f:
                json.dump(export_data, f, indent=2)
            click.echo(f"✅ Metrics exported to {output}")
        else:
            click.echo(json.dumps(export_data, indent=2))
        
    except Exception as e:
        click.echo(f"❌ Error exporting metrics: {e}", err=True)
        sys.exit(1)


@rate_limit_errors.command()
@with_appcontext
def clear():
    """Clear all rate limit metrics."""
    if click.confirm('Are you sure you want to clear all rate limit metrics?'):
        try:
            rate_limit_error_handler.clear_metrics()
            click.echo("✅ Rate limit metrics cleared successfully")
        except Exception as e:
            click.echo(f"❌ Error clearing metrics: {e}", err=True)
            sys.exit(1)
    else:
        click.echo("Operation cancelled")


@rate_limit_errors.command()
@click.option('--type', help='Filter by limit type')
@click.option('--endpoint', help='Filter by endpoint')
@click.option('--ip', help='Filter by IP address')
@click.option('--hours', default=24, help='Hours to look back (default: 24)')
@with_appcontext
def analyze(type, endpoint, ip, hours):
    """Analyze rate limit patterns and trends."""
    click.echo("📈 Rate Limit Pattern Analysis")
    click.echo("=" * 40)
    
    try:
        recent_blocks = getattr(rate_limit_error_handler.metrics, 'recent_blocks', [])
        
        if not recent_blocks:
            click.echo("No data available for analysis.")
            return
        
        # Filter by time
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_blocks = [
            block for block in recent_blocks
            if datetime.fromisoformat(block['timestamp']) > cutoff_time
        ]
        
        # Apply filters
        if type:
            filtered_blocks = [b for b in filtered_blocks if b['limit_type'] == type]
        if endpoint:
            filtered_blocks = [b for b in filtered_blocks if endpoint in b['endpoint']]
        if ip:
            filtered_blocks = [b for b in filtered_blocks if b['ip'] == ip]
        
        if not filtered_blocks:
            click.echo("No incidents match the specified criteria.")
            return
        
        click.echo(f"\n📊 Analysis for last {hours} hours:")
        click.echo(f"Total incidents: {len(filtered_blocks)}")
        
        # Analyze by type
        type_counts = {}
        for block in filtered_blocks:
            limit_type = block['limit_type']
            type_counts[limit_type] = type_counts.get(limit_type, 0) + 1
        
        if type_counts:
            click.echo("\n🏷️ By Type:")
            for limit_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(filtered_blocks)) * 100
                click.echo(f"  {limit_type}: {count} ({percentage:.1f}%)")
        
        # Analyze by IP
        ip_counts = {}
        for block in filtered_blocks:
            ip = block['ip']
            ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        # Show top IPs
        top_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_ips:
            click.echo("\n🌐 Top IPs:")
            for ip, count in top_ips:
                click.echo(f"  {ip}: {count} incidents")
        
        # Analyze by endpoint
        endpoint_counts = {}
        for block in filtered_blocks:
            endpoint = block['endpoint']
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
        
        # Show top endpoints
        top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        if top_endpoints:
            click.echo("\n🎯 Top Endpoints:")
            for endpoint, count in top_endpoints:
                display_endpoint = endpoint[:50] + '...' if len(endpoint) > 50 else endpoint
                click.echo(f"  {display_endpoint}: {count} incidents")
        
        # Time distribution
        hourly_counts = {}
        for block in filtered_blocks:
            hour = datetime.fromisoformat(block['timestamp']).hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        if hourly_counts:
            click.echo("\n🕐 Hourly Distribution:")
            for hour in range(24):
                count = hourly_counts.get(hour, 0)
                if count > 0:
                    bar = '█' * min(count, 20)
                    click.echo(f"  {hour:02d}:00 [{count:3d}] {bar}")
        
    except Exception as e:
        click.echo(f"❌ Error during analysis: {e}", err=True)
        sys.exit(1)


@rate_limit_errors.command()
@click.option('--interval', default=5, help='Update interval in seconds')
@with_appcontext
def monitor(interval):
    """Monitor rate limit incidents in real-time."""
    click.echo("👁️ Real-time Rate Limit Monitor")
    click.echo("Press Ctrl+C to stop")
    click.echo("=" * 40)
    
    last_count = 0
    
    try:
        while True:
            current_count = rate_limit_error_handler.metrics['total_blocks']
            
            if current_count > last_count:
                new_incidents = current_count - last_count
                timestamp = datetime.now().strftime('%H:%M:%S')
                click.echo(f"[{timestamp}] 🚨 {new_incidents} new rate limit incident(s)")
                
                # Show recent details
                recent_blocks = getattr(rate_limit_error_handler.metrics, 'recent_blocks', [])
                if recent_blocks:
                    latest = recent_blocks[-new_incidents:]
                    for incident in latest:
                        click.echo(f"  └─ {incident['limit_type']} at {incident['endpoint']} from {incident['ip']}")
                
                last_count = current_count
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        click.echo("\n👋 Monitoring stopped")
    except Exception as e:
        click.echo(f"❌ Error during monitoring: {e}", err=True)
        sys.exit(1)


@rate_limit_errors.command()
@click.argument('test_type', type=click.Choice(['global', 'ip', 'user', 'endpoint', 'burst', 'api']))
@click.option('--count', default=10, help='Number of test requests')
@click.option('--delay', default=0.1, help='Delay between requests in seconds')
@with_appcontext
def test(test_type, count, delay):
    """Test rate limiting error scenarios."""
    click.echo(f"🧪 Testing {test_type} rate limit scenarios")
    click.echo("=" * 40)
    
    try:
        import requests
        import time
        
        base_url = "http://localhost:5007"
        test_endpoints = {
            'global': '/health',
            'ip': '/api/properties',
            'user': '/api/properties',
            'endpoint': '/api/search',
            'burst': '/api/statistics',
            'api': '/api/market-data'
        }
        
        endpoint = test_endpoints.get(test_type, '/health')
        url = f"{base_url}{endpoint}"
        
        click.echo(f"Testing endpoint: {url}")
        click.echo(f"Making {count} requests with {delay}s delay...")
        
        success_count = 0
        error_count = 0
        rate_limited_count = 0
        
        for i in range(count):
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    success_count += 1
                    click.echo(f"  [{i+1:2d}] ✅ Success (200)")
                elif response.status_code == 429:
                    rate_limited_count += 1
                    retry_after = response.headers.get('Retry-After', 'unknown')
                    click.echo(f"  [{i+1:2d}] 🚦 Rate Limited (429) - Retry after: {retry_after}s")
                else:
                    error_count += 1
                    click.echo(f"  [{i+1:2d}] ❌ Error ({response.status_code})")
                
                time.sleep(delay)
                
            except requests.exceptions.RequestException as e:
                error_count += 1
                click.echo(f"  [{i+1:2d}] ❌ Connection Error: {e}")
        
        # Summary
        click.echo(f"\n📊 Test Summary:")
        click.echo(f"  Success: {success_count}/{count}")
        click.echo(f"  Rate Limited: {rate_limited_count}/{count}")
        click.echo(f"  Errors: {error_count}/{count}")
        
        if rate_limited_count > 0:
            click.echo(f"✅ Rate limiting is working for {test_type} scenario")
        else:
            click.echo(f"⚠️ No rate limiting triggered for {test_type} scenario")
        
    except Exception as e:
        click.echo(f"❌ Error during testing: {e}", err=True)
        sys.exit(1)


@rate_limit_errors.command()
@with_appcontext
def health():
    """Check health of rate limit error handling system."""
    click.echo("🏥 Rate Limit Error Handler Health Check")
    click.echo("=" * 45)
    
    try:
        # Initialize the error handler first
        rate_limit_error_handler.init_app(current_app)
        
        # Check if handler is initialized
        if rate_limit_error_handler.app:
            click.echo("✅ Error handler is initialized")
        else:
            click.echo("❌ Error handler is not initialized")
            return
        
        # Check metrics system
        metrics = rate_limit_error_handler.get_metrics()
        click.echo("✅ Metrics system is working")
        
        # Check template availability
        try:
            from flask import render_template_string
            test_template = "{{ message }}"
            render_template_string(test_template, message="test")
            click.echo("✅ Template system is working")
        except Exception:
            click.echo("⚠️ Template system may have issues")
        
        # Check logging
        try:
            rate_limit_error_handler.logger.info("Health check test log")
            click.echo("✅ Logging system is working")
        except Exception:
            click.echo("⚠️ Logging system may have issues")
        
        click.echo(f"\n🎯 System Status: Healthy")
        
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    # Create app context for CLI commands
    app = create_app()
    with app.app_context():
        rate_limit_errors()
