"""
Rate Limiting Monitoring and Management Commands
Provides CLI commands for monitoring and managing rate limits.
"""

import click
from flask import current_app
from flask.cli import with_appcontext
from app.security.rate_limiter import rate_limiter
from datetime import datetime, timedelta
import json
import redis


@click.group(name='rate-limit')
def rate_limit_cli():
    """Rate limiting management commands."""
    pass


@rate_limit_cli.command()
@click.option('--client-type', default='all', help='Client type to monitor (ip, user, all)')
@click.option('--hours', default=1, help='Hours to look back')
@with_appcontext
def status(client_type, hours):
    """Show current rate limiting status."""
    click.echo("Rate Limiting Status")
    click.echo("=" * 50)
    
    try:
        if rate_limiter.redis_client:
            redis_client = rate_limiter.redis_client
            
            # Get all rate limiting keys
            keys = redis_client.keys("rl:*")
            
            if not keys:
                click.echo("No rate limiting data found.")
                return
            
            # Group by type
            stats = {'ip': {}, 'user': {}, 'endpoint': {}, 'global': {}}
            
            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                parts = key_str.split(':')
                
                if len(parts) >= 2:
                    key_type = parts[1]
                    if key_type in stats:
                        # Get request count for last hour
                        count = redis_client.zcard(key_str)
                        if count > 0:
                            stats[key_type][key_str] = count
            
            # Display stats
            for stat_type, data in stats.items():
                if data and (client_type == 'all' or client_type == stat_type):
                    click.echo(f"\n{stat_type.upper()} Rate Limits:")
                    click.echo("-" * 30)
                    
                    for key, count in sorted(data.items(), key=lambda x: x[1], reverse=True)[:10]:
                        click.echo(f"  {key}: {count} requests")
        
        else:
            click.echo("Rate limiter using in-memory backend - detailed stats not available")
            click.echo("Consider configuring Redis for better monitoring")
    
    except Exception as e:
        click.echo(f"Error retrieving rate limit status: {e}")


@rate_limit_cli.command()
@click.option('--threshold', default=0.8, help='Alert threshold (0.0-1.0)')
@with_appcontext
def alerts(threshold):
    """Check for rate limiting alerts."""
    click.echo(f"Rate Limiting Alerts (threshold: {threshold * 100}%)")
    click.echo("=" * 50)
    
    try:
        if not rate_limiter.redis_client:
            click.echo("Redis not available - cannot check alerts")
            return
        
        redis_client = rate_limiter.redis_client
        keys = redis_client.keys("rl:*")
        
        alerts_found = False
        
        for key in keys:
            key_str = key.decode() if isinstance(key, bytes) else key
            count = redis_client.zcard(key_str)
            
            # Get limit for this key type
            limit = 100  # Default limit
            if 'ip:' in key_str:
                limit = current_app.config.get('RATE_LIMIT_DEFAULTS', {}).get('ip', {}).get('requests', 100)
            elif 'user:' in key_str:
                limit = current_app.config.get('RATE_LIMIT_DEFAULTS', {}).get('user', {}).get('requests', 500)
            
            usage_percent = count / limit if limit > 0 else 0
            
            if usage_percent >= threshold:
                click.echo(f"⚠️  {key_str}: {count}/{limit} ({usage_percent:.1%})")
                alerts_found = True
        
        if not alerts_found:
            click.echo("✅ No rate limiting alerts")
    
    except Exception as e:
        click.echo(f"Error checking alerts: {e}")


@rate_limit_cli.command()
@click.argument('key')
@with_appcontext
def clear(key):
    """Clear rate limiting data for a specific key."""
    try:
        if not rate_limiter.redis_client:
            click.echo("Redis not available - cannot clear data")
            return
        
        redis_client = rate_limiter.redis_client
        
        if redis_client.exists(key):
            redis_client.delete(key)
            click.echo(f"✅ Cleared rate limiting data for: {key}")
        else:
            click.echo(f"❌ Key not found: {key}")
    
    except Exception as e:
        click.echo(f"Error clearing key: {e}")


@rate_limit_cli.command()
@click.option('--confirm', is_flag=True, help='Confirm the action')
@with_appcontext
def reset_all(confirm):
    """Reset all rate limiting data."""
    if not confirm:
        click.echo("This will clear ALL rate limiting data.")
        click.echo("Use --confirm to proceed.")
        return
    
    try:
        if not rate_limiter.redis_client:
            click.echo("Redis not available")
            return
        
        redis_client = rate_limiter.redis_client
        keys = redis_client.keys("rl:*")
        
        if keys:
            redis_client.delete(*keys)
            click.echo(f"✅ Cleared {len(keys)} rate limiting keys")
        else:
            click.echo("No rate limiting data to clear")
    
    except Exception as e:
        click.echo(f"Error resetting rate limits: {e}")


@rate_limit_cli.command()
@click.option('--client-id', required=True, help='Client identifier (e.g., ip:127.0.0.1)')
@with_appcontext
def details(client_id):
    """Show detailed rate limiting information for a client."""
    click.echo(f"Rate Limiting Details for: {client_id}")
    click.echo("=" * 50)
    
    try:
        if not rate_limiter.redis_client:
            click.echo("Redis not available - detailed info not available")
            return
        
        redis_client = rate_limiter.redis_client
        
        # Find all keys related to this client
        pattern = f"*{client_id}*"
        keys = redis_client.keys(pattern)
        
        if not keys:
            click.echo(f"No data found for client: {client_id}")
            return
        
        for key in keys:
            key_str = key.decode() if isinstance(key, bytes) else key
            
            # Get request count and timestamps
            count = redis_client.zcard(key_str)
            
            # Get oldest and newest requests
            oldest = redis_client.zrange(key_str, 0, 0, withscores=True)
            newest = redis_client.zrange(key_str, -1, -1, withscores=True)
            
            click.echo(f"\nKey: {key_str}")
            click.echo(f"  Request count: {count}")
            
            if oldest:
                oldest_time = datetime.fromtimestamp(oldest[0][1])
                click.echo(f"  Oldest request: {oldest_time}")
            
            if newest:
                newest_time = datetime.fromtimestamp(newest[0][1])
                click.echo(f"  Newest request: {newest_time}")
    
    except Exception as e:
        click.echo(f"Error getting details: {e}")


@rate_limit_cli.command()
@with_appcontext
def health():
    """Check rate limiter health."""
    click.echo("Rate Limiter Health Check")
    click.echo("=" * 30)
    
    try:
        # Check if rate limiter is initialized
        if rate_limiter.app is None:
            click.echo("❌ Rate limiter not initialized")
            return
        
        click.echo("✅ Rate limiter initialized")
        
        # Check storage backend
        if rate_limiter.redis_client:
            try:
                rate_limiter.redis_client.ping()
                click.echo("✅ Redis backend operational")
            except Exception as e:
                click.echo(f"❌ Redis backend error: {e}")
        else:
            click.echo("⚠️  Using in-memory backend")
        
        # Check configuration
        config_items = [
            'RATE_LIMIT_DEFAULTS',
            'RATE_LIMIT_SENSITIVE',
            'RATE_LIMIT_BURST'
        ]
        
        for item in config_items:
            if hasattr(current_app.config, item):
                click.echo(f"✅ {item} configured")
            else:
                click.echo(f"⚠️  {item} not configured")
    
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")


@rate_limit_cli.command()
@with_appcontext
def stats():
    """Show rate limiting statistics."""
    click.echo("Rate Limiting Statistics")
    click.echo("=" * 30)
    
    try:
        if rate_limiter.redis_client:
            redis_client = rate_limiter.redis_client
            
            # Get all rate limiting keys
            keys = redis_client.keys("rl:*")
            
            total_keys = len(keys)
            total_requests = 0
            
            for key in keys:
                count = redis_client.zcard(key)
                total_requests += count
            
            click.echo(f"Total active rate limit keys: {total_keys}")
            click.echo(f"Total requests tracked: {total_requests}")
            
            # Show top clients
            client_stats = {}
            for key in keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                count = redis_client.zcard(key_str)
                if count > 0:
                    client_stats[key_str] = count
            
            if client_stats:
                click.echo("\nTop 10 clients by request count:")
                click.echo("-" * 40)
                for key, count in sorted(client_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                    click.echo(f"  {key}: {count} requests")
        else:
            click.echo("Rate limiter using in-memory backend")
            click.echo("Detailed statistics not available")
            click.echo("✅ Rate limiter is operational")
    
    except Exception as e:
        click.echo(f"Error retrieving statistics: {e}")


def register_rate_limit_commands(app):
    """Register rate limiting CLI commands with the Flask app."""
    app.cli.add_command(rate_limit_cli)
