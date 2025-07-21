"""
CLI commands for predictive rate limiting management.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from datetime import datetime, timedelta
import json
import statistics
from app.security.predictive_rate_limiter import (
    PredictiveRateLimiter, get_client_prediction_status, 
    get_global_prediction_metrics, PredictionModel, PredictiveStrategy
)


@click.group()
def predictive_limiting():
    """Predictive rate limiting management commands."""
    pass


@predictive_limiting.command()
@with_appcontext
def status():
    """Show predictive rate limiting system status."""
    click.echo("🔮 Predictive Rate Limiting System Status")
    click.echo("=" * 60)
    
    try:
        metrics = get_global_prediction_metrics()
        
        click.echo(f"📊 Global Metrics:")
        click.echo(f"  Total clients tracked: {metrics['total_clients']}")
        click.echo(f"  Average trust score: {metrics['average_trust_score']:.3f}")
        
        if metrics['behavior_distribution']:
            click.echo(f"\n🎭 Behavior Distribution:")
            for behavior, count in metrics['behavior_distribution'].items():
                percentage = (count / metrics['total_clients']) * 100 if metrics['total_clients'] > 0 else 0
                click.echo(f"  {behavior}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\n🧠 Model Performance:")
        for model, stats in metrics['model_performance'].items():
            click.echo(f"  {model}:")
            click.echo(f"    Accuracy: {stats['accuracy_score']:.3f}")
            click.echo(f"    Confidence: {stats['prediction_confidence']:.3f}")
            click.echo(f"    Last updated: {stats['last_updated']}")
        
        if metrics['global_patterns']:
            click.echo(f"\n📈 Global Patterns:")
            for category, count in metrics['global_patterns'].items():
                click.echo(f"  {category}: {count} requests tracked")
        
        click.echo("\n✅ Predictive rate limiting system is operational")
        
    except Exception as e:
        click.echo(f"❌ Error getting predictive limiting status: {e}")


@predictive_limiting.command()
@click.option('--client-id', required=True, help='Client ID to analyze')
@with_appcontext
def analyze_client(client_id):
    """Analyze predictive patterns for a specific client."""
    click.echo(f"🔍 Predictive Analysis for Client: {client_id}")
    click.echo("=" * 60)
    
    try:
        status = get_client_prediction_status(client_id)
        
        click.echo(f"📊 Client Profile:")
        click.echo(f"  Behavior Type: {status['behavior_type']}")
        click.echo(f"  Trust Score: {status['trust_score']:.3f}")
        click.echo(f"  Total Requests: {status['total_requests']}")
        click.echo(f"  Last Activity: {status['last_activity']}")
        
        metrics = status['prediction_metrics']
        click.echo(f"\n🎯 Prediction Metrics:")
        click.echo(f"  Accuracy: {metrics['accuracy']:.3f}")
        click.echo(f"  Confidence: {metrics['confidence']:.3f}")
        click.echo(f"  Variance: {metrics['variance']:.3f}")
        
        # Hourly patterns
        hourly = status['pattern_analysis']['hourly_patterns']
        if hourly:
            click.echo(f"\n⏰ Hourly Activity Patterns:")
            active_hours = {hour: avg for hour, avg in hourly.items() if avg > 0}
            
            if active_hours:
                sorted_hours = sorted(active_hours.items(), key=lambda x: x[1], reverse=True)
                click.echo("  Most active hours:")
                for hour, avg_requests in sorted_hours[:5]:
                    click.echo(f"    {hour:02d}:00 - {avg_requests:.1f} requests/hour")
            else:
                click.echo("  No significant hourly patterns detected")
        
        # Daily patterns
        daily = status['pattern_analysis']['daily_patterns']
        if daily:
            click.echo(f"\n📅 Daily Activity Patterns:")
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            active_days = {days[day]: avg for day, avg in daily.items() if avg > 0}
            
            if active_days:
                sorted_days = sorted(active_days.items(), key=lambda x: x[1], reverse=True)
                click.echo("  Most active days:")
                for day, avg_requests in sorted_days:
                    click.echo(f"    {day}: {avg_requests:.1f} requests/day")
            else:
                click.echo("  No significant daily patterns detected")
        
    except Exception as e:
        click.echo(f"❌ Error analyzing client: {e}")


@predictive_limiting.command()
@click.option('--model', type=click.Choice(['linear_regression', 'exponential_smoothing', 
              'moving_average', 'seasonal_decomposition', 'adaptive_threshold']),
              help='Filter by prediction model')
@click.option('--behavior', type=click.Choice(['normal', 'bursty', 'steady', 'irregular', 'suspicious']),
              help='Filter by behavior type')
@click.option('--min-trust', type=float, help='Minimum trust score filter')
@with_appcontext
def list_clients(model, behavior, min_trust):
    """List clients with their predictive metrics."""
    click.echo("👥 Predictive Rate Limiting Clients")
    click.echo("=" * 60)
    
    try:
        # Get global metrics to access client data
        metrics = get_global_prediction_metrics()
        
        if metrics['total_clients'] == 0:
            click.echo("📭 No clients tracked yet")
            return
        
        # Note: Since we don't have direct access to all client data through the convenience functions,
        # we'll create a temporary limiter instance to access the data
        limiter = PredictiveRateLimiter()
        
        filtered_clients = []
        
        for client_id, profile in limiter.client_profiles.items():
            # Apply filters
            if behavior and profile.behavior_type.value != behavior:
                continue
            if min_trust and profile.trust_score < min_trust:
                continue
            
            filtered_clients.append((client_id, profile))
        
        if not filtered_clients:
            click.echo("📭 No clients match the specified filters")
            return
        
        # Sort by trust score (descending)
        filtered_clients.sort(key=lambda x: x[1].trust_score, reverse=True)
        
        click.echo(f"📊 Found {len(filtered_clients)} clients:")
        click.echo()
        click.echo(f"{'Client ID':<30} {'Behavior':<12} {'Trust':<6} {'Requests':<8} {'Last Activity'}")
        click.echo("-" * 80)
        
        for client_id, profile in filtered_clients[:20]:  # Show top 20
            last_activity = datetime.fromtimestamp(profile.last_activity).strftime('%Y-%m-%d %H:%M')
            click.echo(f"{client_id:<30} {profile.behavior_type.value:<12} "
                      f"{profile.trust_score:<6.3f} {len(profile.request_history):<8} {last_activity}")
        
        if len(filtered_clients) > 20:
            click.echo(f"\n... and {len(filtered_clients) - 20} more clients")
        
    except Exception as e:
        click.echo(f"❌ Error listing clients: {e}")


@predictive_limiting.command()
@click.option('--endpoint-category', required=True, help='Endpoint category to test')
@click.option('--client-id', default='test:predictive', help='Test client ID')
@click.option('--num-requests', default=50, help='Number of test requests')
@with_appcontext
def test_predictions(endpoint_category, client_id, num_requests):
    """Test predictive rate limiting with simulated requests."""
    click.echo(f"🧪 Testing Predictive Rate Limiting")
    click.echo(f"Endpoint: {endpoint_category}, Client: {client_id}")
    click.echo("=" * 60)
    
    try:
        from app.security.predictive_rate_limiter import check_predictive_rate_limit
        import time
        import random
        
        allowed_count = 0
        blocked_count = 0
        predictions = []
        
        click.echo(f"Simulating {num_requests} requests...")
        
        for i in range(num_requests):
            # Simulate varying request intervals
            if i > 0:
                interval = random.uniform(0.1, 2.0)  # 0.1 to 2 seconds
                time.sleep(interval)
            
            # Test the predictive rate limit
            allowed, retry_after, metadata = check_predictive_rate_limit(
                client_id, endpoint_category, {'test_request': i}
            )
            
            if allowed:
                allowed_count += 1
            else:
                blocked_count += 1
            
            predictions.append(metadata.get('predicted_requests', 0))
            
            # Show progress every 10 requests
            if (i + 1) % 10 == 0:
                click.echo(f"  Processed {i + 1}/{num_requests} requests "
                          f"(Allowed: {allowed_count}, Blocked: {blocked_count})")
        
        click.echo(f"\n📊 Test Results:")
        click.echo(f"  Total requests: {num_requests}")
        click.echo(f"  Allowed: {allowed_count} ({(allowed_count/num_requests)*100:.1f}%)")
        click.echo(f"  Blocked: {blocked_count} ({(blocked_count/num_requests)*100:.1f}%)")
        
        if predictions:
            avg_prediction = statistics.mean(predictions)
            click.echo(f"  Average prediction: {avg_prediction:.1f} requests")
        
        # Get final client status
        final_status = get_client_prediction_status(client_id)
        click.echo(f"\n🎭 Final Client Profile:")
        click.echo(f"  Behavior Type: {final_status['behavior_type']}")
        click.echo(f"  Trust Score: {final_status['trust_score']:.3f}")
        
        click.echo(f"\n✅ Predictive rate limiting test completed")
        
    except Exception as e:
        click.echo(f"❌ Error running test: {e}")


@predictive_limiting.command()
@click.option('--limit-type', required=True, help='Limit type to configure')
@click.option('--base-limit', type=int, help='Base request limit')
@click.option('--prediction-window', type=int, help='Prediction window in seconds')
@click.option('--strategy', type=click.Choice(['conservative', 'balanced', 'aggressive', 'adaptive']),
              help='Prediction strategy')
@click.option('--model', type=click.Choice(['linear_regression', 'exponential_smoothing', 
              'moving_average', 'seasonal_decomposition', 'adaptive_threshold']),
              help='Prediction model')
@with_appcontext
def configure_limit(limit_type, base_limit, prediction_window, strategy, model):
    """Configure predictive rate limiting parameters."""
    click.echo(f"⚙️ Configuring Predictive Limit: {limit_type}")
    click.echo("=" * 60)
    
    try:
        # Create a temporary limiter to access configuration
        limiter = PredictiveRateLimiter()
        
        if limit_type not in limiter.predictive_limits:
            click.echo(f"❌ Unknown limit type: {limit_type}")
            click.echo(f"Available types: {', '.join(limiter.predictive_limits.keys())}")
            return
        
        current_config = limiter.predictive_limits[limit_type]
        
        click.echo(f"📋 Current Configuration:")
        click.echo(f"  Base Limit: {current_config.base_limit}")
        click.echo(f"  Prediction Window: {current_config.prediction_window}s")
        click.echo(f"  Strategy: {current_config.strategy.value}")
        click.echo(f"  Model: {current_config.model.value}")
        click.echo(f"  Adjustment Factor: {current_config.adjustment_factor}")
        
        # Apply updates
        changes_made = []
        
        if base_limit is not None:
            current_config.base_limit = base_limit
            changes_made.append(f"Base limit: {base_limit}")
        
        if prediction_window is not None:
            current_config.prediction_window = prediction_window
            changes_made.append(f"Prediction window: {prediction_window}s")
        
        if strategy is not None:
            from app.security.predictive_rate_limiter import PredictiveStrategy
            current_config.strategy = PredictiveStrategy(strategy)
            changes_made.append(f"Strategy: {strategy}")
        
        if model is not None:
            current_config.model = PredictionModel(model)
            changes_made.append(f"Model: {model}")
        
        if changes_made:
            click.echo(f"\n✅ Configuration Updated:")
            for change in changes_made:
                click.echo(f"  • {change}")
        else:
            click.echo(f"\n💡 No changes specified. Use options to modify configuration.")
        
    except Exception as e:
        click.echo(f"❌ Error configuring limit: {e}")


@predictive_limiting.command()
@click.option('--client-id', required=True, help='Client ID to clear data for')
@click.confirmation_option(prompt='Are you sure you want to clear predictive data?')
@with_appcontext
def clear_client(client_id):
    """Clear predictive data for a specific client."""
    click.echo(f"🧹 Clearing predictive data for client: {client_id}")
    
    try:
        limiter = PredictiveRateLimiter()
        limiter.clear_client_data(client_id)
        click.echo("✅ Client predictive data cleared successfully")
        
    except Exception as e:
        click.echo(f"❌ Error clearing client data: {e}")


@predictive_limiting.command()
@click.option('--max-age-hours', default=24, help='Maximum age of data to keep (hours)')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without doing it')
@with_appcontext
def cleanup(max_age_hours, dry_run):
    """Clean up old predictive rate limiting data."""
    click.echo(f"🧹 Cleaning up predictive data older than {max_age_hours} hours")
    
    try:
        limiter = PredictiveRateLimiter()
        
        # Count current data
        current_clients = len(limiter.client_profiles)
        current_patterns = sum(len(patterns) for patterns in limiter.global_patterns.values())
        
        click.echo(f"📊 Current data:")
        click.echo(f"  Client profiles: {current_clients}")
        click.echo(f"  Global pattern points: {current_patterns}")
        
        if dry_run:
            click.echo(f"\n🔍 DRY RUN - No data will be deleted")
            # Calculate what would be cleaned
            from datetime import datetime, timedelta
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cutoff_timestamp = cutoff_time.timestamp()
            
            inactive_clients = [
                client_id for client_id, profile in limiter.client_profiles.items()
                if profile.last_activity < cutoff_timestamp
            ]
            
            click.echo(f"  Would remove {len(inactive_clients)} inactive client profiles")
        else:
            limiter.cleanup_old_data(max_age_hours)
            
            # Count remaining data
            remaining_clients = len(limiter.client_profiles)
            remaining_patterns = sum(len(patterns) for patterns in limiter.global_patterns.values())
            
            cleaned_clients = current_clients - remaining_clients
            cleaned_patterns = current_patterns - remaining_patterns
            
            click.echo(f"\n✅ Cleanup completed:")
            click.echo(f"  Removed {cleaned_clients} client profiles")
            click.echo(f"  Removed {cleaned_patterns} pattern points")
            click.echo(f"  Remaining clients: {remaining_clients}")
        
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}")


@predictive_limiting.command()
@click.option('--format', 'export_format', type=click.Choice(['json', 'csv']), 
              default='json', help='Export format')
@click.option('--output', help='Output file path')
@click.option('--include-patterns', is_flag=True, help='Include detailed pattern data')
@with_appcontext
def export(export_format, output, include_patterns):
    """Export predictive rate limiting data."""
    click.echo(f"📤 Exporting predictive data in {export_format} format")
    
    try:
        # Get all data
        global_metrics = get_global_prediction_metrics()
        limiter = PredictiveRateLimiter()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'global_metrics': global_metrics,
            'client_profiles': {}
        }
        
        # Export client data
        for client_id, profile in limiter.client_profiles.items():
            client_data = {
                'behavior_type': profile.behavior_type.value,
                'trust_score': profile.trust_score,
                'total_requests': len(profile.request_history),
                'last_activity': datetime.fromtimestamp(profile.last_activity).isoformat(),
                'created_at': datetime.fromtimestamp(profile.created_at).isoformat()
            }
            
            if include_patterns:
                client_data['hourly_patterns'] = {
                    str(hour): data for hour, data in profile.hourly_patterns.items()
                }
                client_data['daily_patterns'] = {
                    str(day): data for day, data in profile.daily_patterns.items()
                }
            
            export_data['client_profiles'][client_id] = client_data
        
        # Generate filename
        if output:
            filename = output
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"predictive_rate_limiting_export_{timestamp}.{export_format}"
        
        # Write file
        if export_format == 'json':
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif export_format == 'csv':
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Client ID', 'Behavior Type', 'Trust Score', 
                                'Total Requests', 'Last Activity'])
                
                for client_id, data in export_data['client_profiles'].items():
                    writer.writerow([
                        client_id,
                        data['behavior_type'],
                        data['trust_score'],
                        data['total_requests'],
                        data['last_activity']
                    ])
        
        click.echo(f"✅ Data exported to: {filename}")
        click.echo(f"📊 Exported {len(export_data['client_profiles'])} client profiles")
        
    except Exception as e:
        click.echo(f"❌ Error exporting data: {e}")


# Register CLI commands
def register_predictive_limiting_commands(app):
    """Register predictive rate limiting CLI commands with the Flask app."""
    app.cli.add_command(predictive_limiting)
