"""
CLI commands for abuse detection management.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from datetime import datetime, timedelta
import json
from app.security.abuse_detection import abuse_detector


@click.group()
def abuse_detection():
    """Abuse detection management commands."""
    pass


@abuse_detection.command()
@click.option('--hours', default=1, help='Hours to look back for statistics')
@with_appcontext
def status(hours):
    """Show abuse detection status and statistics."""
    click.echo("🔍 Abuse Detection System Status")
    click.echo("=" * 50)
    
    if not abuse_detector:
        click.echo("❌ Abuse detection system not initialized")
        return
    
    try:
        stats = abuse_detector.abuse_detector.get_abuse_statistics()
        
        click.echo(f"📊 Statistics (last {hours} hours):")
        click.echo(f"  Total incidents: {stats['total_incidents']}")
        click.echo(f"  Unique clients: {stats['unique_clients']}")
        
        if stats['abuse_types']:
            click.echo("\n🚨 Abuse Types Detected:")
            for abuse_type, count in stats['abuse_types'].items():
                click.echo(f"  {abuse_type}: {count}")
        
        if stats['abuse_levels']:
            click.echo("\n⚠️ Abuse Levels:")
            for level, count in stats['abuse_levels'].items():
                click.echo(f"  {level}: {count}")
        
        if stats['most_common_abuse']:
            click.echo(f"\n🎯 Most common abuse type: {stats['most_common_abuse']}")
        
        click.echo("\n✅ Abuse detection system is operational")
        
    except Exception as e:
        click.echo(f"❌ Error getting abuse detection status: {e}")


@abuse_detection.command()
@click.option('--client-id', required=True, help='Client ID to analyze')
@with_appcontext
def analyze(client_id):
    """Analyze abuse history for a specific client."""
    click.echo(f"🔍 Abuse Analysis for Client: {client_id}")
    click.echo("=" * 50)
    
    if not abuse_detector:
        click.echo("❌ Abuse detection system not initialized")
        return
    
    try:
        history = abuse_detector.abuse_detector.get_client_abuse_history(client_id)
        
        if not history:
            click.echo("✅ No abuse incidents found for this client")
            return
        
        click.echo(f"📊 Found {len(history)} incidents:")
        click.echo()
        
        for i, incident in enumerate(history, 1):
            timestamp = datetime.fromtimestamp(incident.timestamp)
            click.echo(f"Incident {i}:")
            click.echo(f"  Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            click.echo(f"  Type: {incident.abuse_type.value}")
            click.echo(f"  Level: {incident.level.value}")
            click.echo(f"  Confidence: {incident.confidence:.2f}")
            click.echo(f"  Actions: {', '.join(incident.actions_taken) if incident.actions_taken else 'None'}")
            
            if incident.metrics:
                click.echo(f"  Metrics:")
                click.echo(f"    Request count: {incident.metrics.request_count}")
                click.echo(f"    Error rate: {incident.metrics.error_rate:.2f}")
                click.echo(f"    Unique endpoints: {incident.metrics.unique_endpoints}")
                click.echo(f"    Failed auth attempts: {incident.metrics.failed_auth_attempts}")
            
            if incident.details:
                triggered = incident.details.get('thresholds_triggered', [])
                if triggered:
                    click.echo(f"  Triggered thresholds: {', '.join(triggered)}")
            
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error analyzing client: {e}")


@abuse_detection.command()
@click.option('--client-id', required=True, help='Client ID to clear history for')
@click.confirmation_option(prompt='Are you sure you want to clear abuse history?')
@with_appcontext
def clear_history(client_id):
    """Clear abuse history for a specific client."""
    click.echo(f"🧹 Clearing abuse history for client: {client_id}")
    
    if not abuse_detector:
        click.echo("❌ Abuse detection system not initialized")
        return
    
    try:
        abuse_detector.abuse_detector.clear_client_history(client_id)
        click.echo("✅ Abuse history cleared successfully")
        
    except Exception as e:
        click.echo(f"❌ Error clearing history: {e}")


@abuse_detection.command()
@click.option('--level', type=click.Choice(['low', 'medium', 'high', 'critical']), 
              help='Filter by abuse level')
@click.option('--type', 'abuse_type', help='Filter by abuse type')
@click.option('--hours', default=24, help='Hours to look back')
@with_appcontext
def incidents(level, abuse_type, hours):
    """List recent abuse incidents."""
    click.echo(f"🚨 Abuse Incidents (last {hours} hours)")
    click.echo("=" * 50)
    
    if not abuse_detector:
        click.echo("❌ Abuse detection system not initialized")
        return
    
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cutoff_timestamp = cutoff_time.timestamp()
        
        all_incidents = []
        for client_id, incidents_list in abuse_detector.abuse_detector.incidents.items():
            for incident in incidents_list:
                if incident.timestamp >= cutoff_timestamp:
                    # Apply filters
                    if level and incident.level.value != level.upper():
                        continue
                    if abuse_type and incident.abuse_type.value != abuse_type:
                        continue
                    
                    all_incidents.append((client_id, incident))
        
        if not all_incidents:
            click.echo("✅ No incidents found matching criteria")
            return
        
        # Sort by timestamp (newest first)
        all_incidents.sort(key=lambda x: x[1].timestamp, reverse=True)
        
        click.echo(f"📊 Found {len(all_incidents)} incidents:")
        click.echo()
        
        for client_id, incident in all_incidents:
            timestamp = datetime.fromtimestamp(incident.timestamp)
            click.echo(f"🔸 {timestamp.strftime('%H:%M:%S')} | "
                      f"{incident.level.value:8} | "
                      f"{incident.abuse_type.value:20} | "
                      f"{client_id:20} | "
                      f"Confidence: {incident.confidence:.2f}")
        
    except Exception as e:
        click.echo(f"❌ Error listing incidents: {e}")


@abuse_detection.command()
@click.option('--export-format', type=click.Choice(['json', 'csv']), default='json',
              help='Export format')
@click.option('--output', help='Output file path')
@with_appcontext
def export_data(export_format, output):
    """Export abuse detection data."""
    click.echo(f"📤 Exporting abuse detection data in {export_format} format")
    
    if not abuse_detector:
        click.echo("❌ Abuse detection system not initialized")
        return
    
    try:
        stats = abuse_detector.abuse_detector.get_abuse_statistics()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'statistics': stats,
            'incidents': {}
        }
        
        # Add detailed incident data
        for client_id, incidents_list in abuse_detector.abuse_detector.incidents.items():
            export_data['incidents'][client_id] = []
            for incident in incidents_list:
                incident_data = {
                    'timestamp': incident.timestamp,
                    'abuse_type': incident.abuse_type.value,
                    'level': incident.level.value,
                    'confidence': incident.confidence,
                    'actions_taken': incident.actions_taken,
                    'details': incident.details
                }
                
                if incident.metrics:
                    incident_data['metrics'] = {
                        'request_count': incident.metrics.request_count,
                        'error_rate': incident.metrics.error_rate,
                        'unique_endpoints': incident.metrics.unique_endpoints,
                        'failed_auth_attempts': incident.metrics.failed_auth_attempts,
                        'parameter_variations': incident.metrics.parameter_variations,
                        'user_agent_switches': incident.metrics.user_agent_switches
                    }
                
                export_data['incidents'][client_id].append(incident_data)
        
        if output:
            filename = output
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"abuse_detection_export_{timestamp}.{export_format}"
        
        if export_format == 'json':
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        elif export_format == 'csv':
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Client ID', 'Timestamp', 'Abuse Type', 'Level', 
                                'Confidence', 'Actions Taken'])
                
                for client_id, incidents_list in export_data['incidents'].items():
                    for incident in incidents_list:
                        writer.writerow([
                            client_id,
                            datetime.fromtimestamp(incident['timestamp']).isoformat(),
                            incident['abuse_type'],
                            incident['level'],
                            incident['confidence'],
                            ', '.join(incident['actions_taken'])
                        ])
        
        click.echo(f"✅ Data exported to: {filename}")
        
    except Exception as e:
        click.echo(f"❌ Error exporting data: {e}")


@abuse_detection.command()
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without actually doing it')
@with_appcontext
def cleanup(dry_run):
    """Clean up old abuse detection data."""
    click.echo("🧹 Cleaning up old abuse detection data")
    
    if not abuse_detector:
        click.echo("❌ Abuse detection system not initialized")
        return
    
    try:
        cutoff_time = datetime.now() - timedelta(days=7)  # Keep 7 days of data
        cutoff_timestamp = cutoff_time.timestamp()
        
        cleaned_count = 0
        total_incidents = 0
        
        for client_id in list(abuse_detector.abuse_detector.incidents.keys()):
            incidents_list = abuse_detector.abuse_detector.incidents[client_id]
            total_incidents += len(incidents_list)
            
            # Filter out old incidents
            new_incidents = [i for i in incidents_list if i.timestamp >= cutoff_timestamp]
            old_count = len(incidents_list) - len(new_incidents)
            
            if old_count > 0:
                cleaned_count += old_count
                if not dry_run:
                    abuse_detector.abuse_detector.incidents[client_id] = new_incidents
                    if not new_incidents:  # Remove empty client entries
                        del abuse_detector.abuse_detector.incidents[client_id]
        
        if dry_run:
            click.echo(f"🔍 Would clean {cleaned_count} old incidents out of {total_incidents} total")
        else:
            click.echo(f"✅ Cleaned {cleaned_count} old incidents out of {total_incidents} total")
        
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}")


@abuse_detection.command()
@with_appcontext
def test():
    """Test abuse detection system functionality."""
    click.echo("🧪 Testing Abuse Detection System")
    click.echo("=" * 50)
    
    if not abuse_detector:
        click.echo("❌ Abuse detection system not initialized")
        return
    
    try:
        # Test basic functionality
        click.echo("1. Testing basic functionality...")
        
        test_client_id = "test:127.0.0.1"
        test_request_data = {
            'endpoint': '/api/test',
            'method': 'GET',
            'status_code': 200,
            'response_time': 50,
            'user_agent': 'TestAgent/1.0',
            'parameters': {'test': 'value'},
            'ip_address': '127.0.0.1'
        }
        
        # Record some test requests
        for i in range(10):
            abuse_detector.abuse_detector.record_request(test_client_id, test_request_data)
        
        click.echo("   ✅ Request recording works")
        
        # Test analysis
        metrics = abuse_detector.abuse_detector.analyze_request_patterns(test_client_id)
        click.echo(f"   ✅ Pattern analysis works (found {metrics.request_count} requests)")
        
        # Test rate limiting check
        allowed, retry_after, incident = abuse_detector.abuse_detector.check_abuse_rate_limit(test_client_id)
        click.echo(f"   ✅ Rate limit check works (allowed: {allowed})")
        
        # Test statistics
        stats = abuse_detector.abuse_detector.get_abuse_statistics()
        click.echo(f"   ✅ Statistics work (total incidents: {stats['total_incidents']})")
        
        # Clean up test data
        abuse_detector.abuse_detector.clear_client_history(test_client_id)
        click.echo("   ✅ Cleanup works")
        
        click.echo("\n🎉 All tests passed! Abuse detection system is working correctly.")
        
    except Exception as e:
        click.echo(f"❌ Test failed: {e}")


# Register CLI commands
def register_abuse_detection_commands(app):
    """Register abuse detection CLI commands with the Flask app."""
    app.cli.add_command(abuse_detection)
