"""
CLI commands for pattern analysis rate limiting management.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from datetime import datetime, timedelta
import json
from app.security.pattern_analysis_rate_limiter import (
    pattern_analysis_limiter, PatternAnalysisType, AnalysisComplexity
)


@click.group()
def pattern_analysis():
    """Pattern analysis rate limiting management commands."""
    pass


@pattern_analysis.command()
@click.option('--client-id', help='Specific client to check')
@with_appcontext
def status(client_id):
    """Show pattern analysis rate limiting status."""
    click.echo("🔍 Pattern Analysis Rate Limiting Status")
    click.echo("=" * 60)
    
    if not pattern_analysis_limiter:
        click.echo("❌ Pattern analysis rate limiter not initialized")
        return
    
    try:
        if client_id:
            # Show status for specific client
            status_data = pattern_analysis_limiter.get_rate_limit_status(client_id)
            click.echo(f"📊 Status for client: {client_id}")
            click.echo(f"Timestamp: {datetime.fromtimestamp(status_data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo()
            
            click.echo("Rate Limit Status:")
            for limit_name, limit_data in status_data['limits'].items():
                utilization_pct = limit_data['utilization'] * 100
                status_icon = "🔴" if utilization_pct > 80 else "🟡" if utilization_pct > 60 else "🟢"
                
                click.echo(f"  {status_icon} {limit_name}:")
                click.echo(f"    Current: {limit_data['current']}/{limit_data['limit']}")
                click.echo(f"    Remaining: {limit_data['remaining']}")
                click.echo(f"    Utilization: {utilization_pct:.1f}%")
                click.echo()
        else:
            # Show overall metrics
            metrics = pattern_analysis_limiter.get_analysis_metrics()
            click.echo(f"📊 Overall Pattern Analysis Metrics")
            click.echo(f"Total clients: {metrics['total_clients']}")
            
            if metrics['total_clients'] > 0:
                agg_metrics = metrics['aggregate_metrics']
                click.echo()
                click.echo("Aggregate Metrics:")
                click.echo(f"  Total requests: {agg_metrics['total_requests']}")
                click.echo(f"  Successful requests: {agg_metrics['successful_requests']}")
                click.echo(f"  Failed requests: {agg_metrics['failed_requests']}")
                click.echo(f"  Average processing time: {agg_metrics['average_processing_time']:.3f}s")
                click.echo(f"  Cache hit rate: {agg_metrics['cache_hit_rate']:.1%}")
                
                if agg_metrics['complexity_distribution']:
                    click.echo()
                    click.echo("Complexity Distribution:")
                    for complexity, count in agg_metrics['complexity_distribution'].items():
                        click.echo(f"  {complexity}: {count}")
            
            click.echo("\n✅ Pattern analysis rate limiter is operational")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}")


@pattern_analysis.command()
@click.option('--client-id', help='Specific client to show metrics for')
@with_appcontext
def metrics(client_id):
    """Show detailed pattern analysis metrics."""
    click.echo("📈 Pattern Analysis Metrics")
    click.echo("=" * 50)
    
    if not pattern_analysis_limiter:
        click.echo("❌ Pattern analysis rate limiter not initialized")
        return
    
    try:
        metrics_data = pattern_analysis_limiter.get_analysis_metrics(client_id)
        
        if client_id:
            click.echo(f"Client: {client_id}")
            client_metrics = metrics_data['metrics']
            
            click.echo(f"Total requests: {client_metrics['total_requests']}")
            click.echo(f"Successful requests: {client_metrics['successful_requests']}")
            click.echo(f"Failed requests: {client_metrics['failed_requests']}")
            
            if client_metrics['total_requests'] > 0:
                success_rate = (client_metrics['successful_requests'] / 
                              client_metrics['total_requests']) * 100
                click.echo(f"Success rate: {success_rate:.1f}%")
            
            click.echo(f"Average processing time: {client_metrics['average_processing_time']:.3f}s")
            click.echo(f"Cache hit rate: {client_metrics['cache_hit_rate']:.1%}")
            
            if client_metrics['complexity_distribution']:
                click.echo("\nComplexity Distribution:")
                for complexity, count in client_metrics['complexity_distribution'].items():
                    click.echo(f"  {complexity}: {count}")
        else:
            # Show aggregate metrics for all clients
            click.echo(f"Total clients with analysis data: {metrics_data['total_clients']}")
            
            if metrics_data['total_clients'] > 0:
                agg_metrics = metrics_data['aggregate_metrics']
                click.echo(f"\nAggregate metrics:")
                click.echo(f"  Total requests: {agg_metrics['total_requests']}")
                click.echo(f"  Successful requests: {agg_metrics['successful_requests']}")
                click.echo(f"  Failed requests: {agg_metrics['failed_requests']}")
                
                if agg_metrics['total_requests'] > 0:
                    success_rate = (agg_metrics['successful_requests'] / 
                                  agg_metrics['total_requests']) * 100
                    click.echo(f"  Overall success rate: {success_rate:.1f}%")
                
                click.echo(f"  Average processing time: {agg_metrics['average_processing_time']:.3f}s")
                click.echo(f"  Cache hit rate: {agg_metrics['cache_hit_rate']:.1%}")
                
                if agg_metrics['complexity_distribution']:
                    click.echo("\n  Complexity Distribution:")
                    total_requests = sum(agg_metrics['complexity_distribution'].values())
                    for complexity, count in agg_metrics['complexity_distribution'].items():
                        percentage = (count / total_requests) * 100
                        click.echo(f"    {complexity}: {count} ({percentage:.1f}%)")
        
    except Exception as e:
        click.echo(f"❌ Error getting metrics: {e}")


@pattern_analysis.command()
@with_appcontext
def limits():
    """Show current rate limiting configuration."""
    click.echo("⚙️ Pattern Analysis Rate Limiting Configuration")
    click.echo("=" * 60)
    
    if not pattern_analysis_limiter:
        click.echo("❌ Pattern analysis rate limiter not initialized")
        return
    
    try:
        click.echo("Complexity-based Limits:")
        for complexity in AnalysisComplexity:
            if complexity in pattern_analysis_limiter.complexity_limits:
                config = pattern_analysis_limiter.complexity_limits[complexity]
                click.echo(f"  {complexity.name}:")
                click.echo(f"    Requests: {config['requests']} per {config['window']}s")
                click.echo(f"    Concurrent: {config['concurrent']}")
        
        click.echo("\nAnalysis Type Limits:")
        for analysis_type in PatternAnalysisType:
            if analysis_type in pattern_analysis_limiter.type_limits:
                config = pattern_analysis_limiter.type_limits[analysis_type]
                click.echo(f"  {analysis_type.value}:")
                click.echo(f"    Requests: {config['requests']} per {config['window']}s")
                click.echo(f"    Description: {config['description']}")
        
        click.echo("\nData Size Limits:")
        for category, config in pattern_analysis_limiter.data_size_limits.items():
            max_size = config['max_size']
            if max_size == float('inf'):
                size_str = "> 1MB"
            else:
                size_str = f"≤ {max_size} bytes"
            click.echo(f"  {category} ({size_str}): {config['requests']} requests/min")
        
        click.echo("\nClient Tier Limits:")
        for tier, config in pattern_analysis_limiter.client_limits.items():
            click.echo(f"  {tier}: {config['requests']} requests per {config['window']}s")
        
    except Exception as e:
        click.echo(f"❌ Error getting limits: {e}")


@pattern_analysis.command()
@click.option('--client-id', required=True, help='Client ID to clear data for')
@click.confirmation_option(prompt='Are you sure you want to clear pattern analysis data?')
@with_appcontext
def clear_client(client_id):
    """Clear pattern analysis data for a specific client."""
    click.echo(f"🧹 Clearing pattern analysis data for client: {client_id}")
    
    if not pattern_analysis_limiter:
        click.echo("❌ Pattern analysis rate limiter not initialized")
        return
    
    try:
        pattern_analysis_limiter.clear_client_data(client_id)
        click.echo("✅ Pattern analysis data cleared successfully")
        
    except Exception as e:
        click.echo(f"❌ Error clearing data: {e}")


@pattern_analysis.command()
@click.option('--analysis-type', type=click.Choice([t.value for t in PatternAnalysisType]),
              help='Type of analysis to test')
@click.option('--data-size', default=1024, help='Data size in bytes for testing')
@click.option('--client-id', default='test:127.0.0.1', help='Client ID for testing')
@with_appcontext
def test(analysis_type, data_size, client_id):
    """Test pattern analysis rate limiting functionality."""
    click.echo("🧪 Testing Pattern Analysis Rate Limiting")
    click.echo("=" * 50)
    
    if not pattern_analysis_limiter:
        click.echo("❌ Pattern analysis rate limiter not initialized")
        return
    
    try:
        # Import required modules
        from app.security.pattern_analysis_rate_limiter import (
            check_pattern_analysis_rate_limit, record_pattern_analysis
        )
        
        # Determine analysis type
        if analysis_type:
            test_type = PatternAnalysisType(analysis_type)
        else:
            test_type = PatternAnalysisType.BEHAVIORAL_ANALYSIS
        
        click.echo(f"Testing with:")
        click.echo(f"  Client ID: {client_id}")
        click.echo(f"  Analysis Type: {test_type.value}")
        click.echo(f"  Data Size: {data_size} bytes")
        
        # Test rate limiting
        click.echo("\n1. Testing rate limit check...")
        
        parameters = {'test': True, 'timestamp': time.time()}
        allowed, retry_after, reason = check_pattern_analysis_rate_limit(
            client_id, test_type, data_size, parameters
        )
        
        if allowed:
            click.echo("✅ Rate limit check passed")
            
            # Record a test analysis
            click.echo("2. Recording test analysis...")
            import time
            start_time = time.time()
            
            # Simulate some processing time
            time.sleep(0.1)
            
            processing_time = time.time() - start_time
            record_pattern_analysis(
                client_id, test_type, data_size, parameters, processing_time
            )
            
            click.echo(f"✅ Analysis recorded (processing time: {processing_time:.3f}s)")
            
        else:
            click.echo(f"🚫 Rate limit exceeded: {reason}")
            click.echo(f"   Retry after: {retry_after} seconds")
        
        # Show current status
        click.echo("\n3. Current rate limit status:")
        status_data = pattern_analysis_limiter.get_rate_limit_status(client_id)
        
        relevant_limits = [k for k in status_data['limits'].keys() 
                          if test_type.value in k or 'complexity' in k]
        
        for limit_name in relevant_limits[:3]:  # Show first 3 relevant limits
            limit_data = status_data['limits'][limit_name]
            utilization = limit_data['utilization'] * 100
            click.echo(f"  {limit_name}: {limit_data['current']}/{limit_data['limit']} ({utilization:.1f}%)")
        
        click.echo("\n🎉 Pattern analysis rate limiting test completed successfully!")
        
    except Exception as e:
        click.echo(f"❌ Test failed: {e}")


@pattern_analysis.command()
@click.option('--export-format', type=click.Choice(['json', 'csv']), default='json',
              help='Export format')
@click.option('--output', help='Output file path')
@with_appcontext
def export_metrics(export_format, output):
    """Export pattern analysis metrics."""
    click.echo(f"📤 Exporting pattern analysis metrics in {export_format} format")
    
    if not pattern_analysis_limiter:
        click.echo("❌ Pattern analysis rate limiter not initialized")
        return
    
    try:
        # Get all metrics
        metrics_data = pattern_analysis_limiter.get_analysis_metrics()
        
        # Add timestamp and configuration info
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'pattern_analysis_metrics': metrics_data,
            'configuration': {
                'complexity_limits': {
                    c.name: pattern_analysis_limiter.complexity_limits[c] 
                    for c in AnalysisComplexity 
                    if c in pattern_analysis_limiter.complexity_limits
                },
                'type_limits': {
                    t.value: pattern_analysis_limiter.type_limits[t] 
                    for t in PatternAnalysisType 
                    if t in pattern_analysis_limiter.type_limits
                },
                'data_size_limits': pattern_analysis_limiter.data_size_limits,
                'client_limits': pattern_analysis_limiter.client_limits
            }
        }
        
        if output:
            filename = output
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pattern_analysis_metrics_{timestamp}.{export_format}"
        
        if export_format == 'json':
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif export_format == 'csv':
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write summary data
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Export Timestamp', export_data['export_timestamp']])
                writer.writerow(['Total Clients', metrics_data['total_clients']])
                
                if metrics_data['total_clients'] > 0:
                    agg = metrics_data['aggregate_metrics']
                    writer.writerow(['Total Requests', agg['total_requests']])
                    writer.writerow(['Successful Requests', agg['successful_requests']])
                    writer.writerow(['Failed Requests', agg['failed_requests']])
                    writer.writerow(['Average Processing Time', f"{agg['average_processing_time']:.3f}s"])
                    writer.writerow(['Cache Hit Rate', f"{agg['cache_hit_rate']:.1%}"])
        
        click.echo(f"✅ Metrics exported to: {filename}")
        
    except Exception as e:
        click.echo(f"❌ Error exporting metrics: {e}")


# Register CLI commands
def register_pattern_analysis_commands(app):
    """Register pattern analysis CLI commands with the Flask app."""
    app.cli.add_command(pattern_analysis)
