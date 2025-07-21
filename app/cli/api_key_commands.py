"""
API Key Management CLI Commands
Provides command-line interface for API key generation, management, and monitoring.
"""

import click
import json
import time
from datetime import datetime
from typing import Dict, Any
from flask.cli import with_appcontext
from flask import current_app

from app.security.api_key_limiter import (
    APIKeyTier, APIKeyStatus,
    generate_api_key, get_api_key_usage_analytics
)


def get_limiter():
    """Get the API key limiter from app context."""
    return getattr(current_app, 'api_key_limiter', None)


@click.group('api-keys')
def api_key_commands():
    """API key management commands."""
    pass


@api_key_commands.command('generate')
@click.option('--developer-id', required=True, help='Developer ID')
@click.option('--name', required=True, help='API key name')
@click.option('--tier', type=click.Choice(['free', 'basic', 'premium', 'enterprise', 'unlimited']), 
              default='free', help='API key tier')
@click.option('--description', default='', help='API key description')
@click.option('--expires-days', type=int, help='Days until expiration (optional)')
@click.option('--allowed-ips', help='Comma-separated list of allowed IP addresses')
@click.option('--allowed-domains', help='Comma-separated list of allowed domains')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@with_appcontext
def generate_key(developer_id: str, name: str, tier: str, description: str,
                expires_days: int, allowed_ips: str, allowed_domains: str, format: str):
    """Generate a new API key."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
        
        # Parse allowed IPs and domains
        ips = [ip.strip() for ip in allowed_ips.split(',')] if allowed_ips else []
        domains = [domain.strip() for domain in allowed_domains.split(',')] if allowed_domains else []
        
        # Generate the key
        raw_key, key_id = limiter.generate_api_key(
            developer_id=developer_id,
            name=name,
            tier=APIKeyTier(tier),
            description=description,
            expires_days=expires_days,
            allowed_ips=ips,
            allowed_domains=domains
        )
        
        # Get key info for display
        key_info = limiter.get_api_key_info(raw_key)
        
        if format == 'json':
            result = {
                'api_key': raw_key,
                'key_id': key_id,
                'key_info': key_info
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("🔑 API Key Generated Successfully")
            click.echo("=" * 50)
            click.echo(f"🆔 Key ID: {key_id}")
            click.echo(f"🔐 API Key: {raw_key}")
            click.echo(f"👤 Developer: {developer_id}")
            click.echo(f"📛 Name: {name}")
            click.echo(f"🎯 Tier: {tier.upper()}")
            if description:
                click.echo(f"📝 Description: {description}")
            if expires_days:
                click.echo(f"⏰ Expires: {expires_days} days")
            if ips:
                click.echo(f"🌐 Allowed IPs: {', '.join(ips)}")
            if domains:
                click.echo(f"🏠 Allowed Domains: {', '.join(domains)}")
            
            # Show limits
            if key_info and 'limits' in key_info:
                limits = key_info['limits']
                click.echo("\n📊 Rate Limits:")
                click.echo(f"  • {limits['requests_per_minute']}/minute")
                click.echo(f"  • {limits['requests_per_hour']}/hour")
                click.echo(f"  • {limits['requests_per_day']}/day")
                click.echo(f"  • {limits['data_transfer_mb_per_day']} MB/day")
                click.echo(f"  • {limits['concurrent_requests']} concurrent")
            
            click.echo("\n⚠️  IMPORTANT: Store this API key securely. It won't be shown again!")
            
    except Exception as e:
        click.echo(f"❌ Error generating API key: {e}", err=True)


@api_key_commands.command('info')
@click.option('--api-key', required=True, help='API key to get info for')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@with_appcontext
def key_info(api_key: str, format: str):
    """Get information about an API key."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
            
        info = limiter.get_api_key_info(api_key)
        
        if not info:
            click.echo("❌ API key not found", err=True)
            return
        
        if format == 'json':
            click.echo(json.dumps(info, indent=2))
        else:
            click.echo("🔑 API Key Information")
            click.echo("=" * 50)
            click.echo(f"🆔 Key ID: {info['key_id']}")
            click.echo(f"🔐 Key Prefix: {info['key_prefix']}")
            click.echo(f"📛 Name: {info['name']}")
            click.echo(f"📝 Description: {info['description']}")
            click.echo(f"🎯 Tier: {info['tier'].upper()}")
            click.echo(f"📊 Status: {info['status'].upper()}")
            click.echo(f"📅 Created: {info['created_at']}")
            if info['last_used']:
                click.echo(f"🕐 Last Used: {info['last_used']}")
            if info['expires_at']:
                click.echo(f"⏰ Expires: {info['expires_at']}")
            
            # Usage statistics
            click.echo(f"\n📈 Total Usage:")
            click.echo(f"  • Requests: {info['total_requests']:,}")
            click.echo(f"  • Data Transfer: {info['total_data_transfer_mb']} MB")
            click.echo(f"  • Compute Time: {info['total_compute_seconds']} seconds")
            
            # Current usage
            current = info['current_usage']
            click.echo(f"\n⏱️  Current Usage:")
            click.echo(f"  • Last minute: {current['minute_requests']}")
            click.echo(f"  • Last hour: {current['hour_requests']}")
            click.echo(f"  • Last day: {current['day_requests']}")
            click.echo(f"  • Data today: {current['day_data_mb']:.2f} MB")
            click.echo(f"  • Compute today: {current['day_compute_seconds']:.2f} seconds")
            
            # Limits
            limits = info['limits']
            click.echo(f"\n📊 Rate Limits:")
            click.echo(f"  • {limits['requests_per_minute']}/minute")
            click.echo(f"  • {limits['requests_per_hour']}/hour")  
            click.echo(f"  • {limits['requests_per_day']}/day")
            click.echo(f"  • {limits['data_transfer_mb_per_day']} MB/day")
            click.echo(f"  • {limits['concurrent_requests']} concurrent")
            
            # Restrictions
            if info['allowed_ips']:
                click.echo(f"\n🌐 Allowed IPs: {', '.join(info['allowed_ips'])}")
            if info['allowed_domains']:
                click.echo(f"🏠 Allowed Domains: {', '.join(info['allowed_domains'])}")
                
    except Exception as e:
        click.echo(f"❌ Error getting API key info: {e}", err=True)


@api_key_commands.command('test')
@click.option('--api-key', required=True, help='API key to test')
@click.option('--endpoint', default='/api/properties', help='Endpoint to test')
@click.option('--ip', default='127.0.0.1', help='IP address to test from')
@with_appcontext
def test_key(api_key: str, endpoint: str, ip: str):
    """Test an API key against rate limits."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
        
        click.echo(f"🧪 Testing API Key: {api_key[:12]}...")
        click.echo(f"📍 Endpoint: {endpoint}")
        click.echo(f"🌐 IP Address: {ip}")
        click.echo("=" * 50)
        
        # Test the rate limit
        allowed, result = limiter.check_rate_limit(api_key, endpoint, "GET", ip)
        
        if allowed:
            click.echo("✅ API Key Test PASSED")
            click.echo("\n📊 Remaining Limits:")
            remaining = result.get('remaining', {})
            limits = result.get('limits', {})
            
            for period in ['minute', 'hour', 'day']:
                if period in remaining and period in limits:
                    click.echo(f"  • {period.title()}: {remaining[period]}/{limits[period]}")
            
            if 'data_mb' in remaining:
                click.echo(f"  • Data: {remaining['data_mb']:.1f}/{limits['data_mb']} MB")
            if 'compute_seconds' in remaining:
                click.echo(f"  • Compute: {remaining['compute_seconds']:.1f}/{limits['compute_seconds']} seconds")
                
            click.echo(f"\n🎯 Tier: {result.get('tier', 'unknown').upper()}")
            
        else:
            click.echo("❌ API Key Test FAILED")
            error = result.get('error', 'Unknown error')
            click.echo(f"🚫 Reason: {error}")
            
            if 'retry_after' in result:
                retry_after = result['retry_after']
                if retry_after < 60:
                    click.echo(f"⏰ Retry after: {retry_after} seconds")
                elif retry_after < 3600:
                    click.echo(f"⏰ Retry after: {retry_after // 60} minutes")
                else:
                    click.echo(f"⏰ Retry after: {retry_after // 3600} hours")
            
            if 'current' in result and 'limit' in result:
                click.echo(f"📊 Current: {result['current']}/{result['limit']}")
                
    except Exception as e:
        click.echo(f"❌ Error testing API key: {e}", err=True)


@api_key_commands.command('revoke')
@click.option('--api-key', required=True, help='API key to revoke')
@click.confirmation_option(prompt='Are you sure you want to revoke this API key?')
@with_appcontext
def revoke_key(api_key: str):
    """Revoke an API key."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
        
        if limiter.revoke_api_key(api_key):
            click.echo(f"✅ API key {api_key[:12]}... has been revoked")
        else:
            click.echo("❌ API key not found", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error revoking API key: {e}", err=True)


@api_key_commands.command('suspend')
@click.option('--api-key', required=True, help='API key to suspend')
@with_appcontext
def suspend_key(api_key: str):
    """Suspend an API key."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
        
        if limiter.suspend_api_key(api_key):
            click.echo(f"⏸️  API key {api_key[:12]}... has been suspended")
        else:
            click.echo("❌ API key not found", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error suspending API key: {e}", err=True)


@api_key_commands.command('reactivate')
@click.option('--api-key', required=True, help='API key to reactivate')
@with_appcontext
def reactivate_key(api_key: str):
    """Reactivate a suspended API key."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
        
        if limiter.reactivate_api_key(api_key):
            click.echo(f"▶️  API key {api_key[:12]}... has been reactivated")
        else:
            click.echo("❌ API key not found or not suspended", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error reactivating API key: {e}", err=True)


@api_key_commands.command('analytics')
@click.option('--developer-id', help='Developer ID (optional, shows global if not specified)')
@click.option('--days', type=int, default=7, help='Number of days to analyze')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@with_appcontext
def analytics(developer_id: str, days: int, format: str):
    """Show API usage analytics."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
            
        data = get_api_key_usage_analytics(developer_id, days)
        
        if format == 'json':
            click.echo(json.dumps(data, indent=2))
        else:
            scope = f"Developer: {developer_id}" if developer_id else "Global Analytics"
            click.echo(f"📊 API Usage Analytics - {scope}")
            click.echo(f"📅 Period: {days} days")
            click.echo("=" * 60)
            
            # Summary stats
            click.echo(f"📈 Summary:")
            click.echo(f"  • Total Requests: {data['total_requests']:,}")
            click.echo(f"  • Data Transfer: {data['total_data_transfer_mb']} MB")
            click.echo(f"  • Compute Time: {data['total_compute_seconds']} seconds")
            click.echo(f"  • Unique Keys: {data['unique_keys']}")
            click.echo(f"  • Error Rate: {data['error_rate']:.2%}")
            
            # Tier distribution
            if data['tier_distribution']:
                click.echo(f"\n🎯 Tier Distribution:")
                for tier, count in data['tier_distribution'].items():
                    click.echo(f"  • {tier.title()}: {count} keys")
            
            # Top endpoints
            if data['top_endpoints']:
                click.echo(f"\n🔝 Top Endpoints:")
                for endpoint, count in list(data['top_endpoints'].items())[:5]:
                    click.echo(f"  • {endpoint}: {count:,} requests")
            
            # Daily breakdown
            if data['requests_by_day']:
                click.echo(f"\n📅 Daily Requests:")
                for day, count in sorted(data['requests_by_day'].items()):
                    click.echo(f"  • {day}: {count:,}")
                    
    except Exception as e:
        click.echo(f"❌ Error getting analytics: {e}", err=True)


@api_key_commands.command('quota')
@click.option('--developer-id', required=True, help='Developer ID')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@with_appcontext
def quota_info(developer_id: str, format: str):
    """Show developer quota information."""
    try:
        limiter = get_limiter()
        if not limiter:
            click.echo("❌ API key limiter not available", err=True)
            return
            
        info = limiter.get_developer_quota_info(developer_id)
        
        if not info:
            click.echo("❌ Developer quota not found", err=True)
            return
        
        if format == 'json':
            click.echo(json.dumps(info, indent=2))
        else:
            click.echo(f"👤 Developer Quota: {developer_id}")
            click.echo("=" * 50)
            
            # Monthly quotas
            quotas = info['monthly_quotas']
            usage = info['current_usage']
            
            click.echo(f"📊 Monthly Quotas:")
            click.echo(f"  • Requests: {usage['requests']:,}/{quotas['requests']:,} ({usage['requests']/quotas['requests']*100:.1f}%)")
            click.echo(f"  • Data: {usage['data_mb']:.1f}/{quotas['data_mb']} MB ({usage['data_mb']/quotas['data_mb']*100:.1f}%)")
            click.echo(f"  • Compute: {usage['compute_seconds']:.1f}/{quotas['compute_seconds']} seconds ({usage['compute_seconds']/quotas['compute_seconds']*100:.1f}%)")
            
            click.echo(f"\n📅 Quota Reset: {info['quota_reset_date']}")
            click.echo(f"🔄 Overage Allowed: {'Yes' if info['overage_allowed'] else 'No'}")
            if info['overage_allowed']:
                click.echo(f"💰 Overage Rate: {info['overage_rate_multiplier']:.1%} of normal rate")
                
    except Exception as e:
        click.echo(f"❌ Error getting quota info: {e}", err=True)


@api_key_commands.command('cleanup')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned up without doing it')
@with_appcontext
def cleanup(dry_run: bool):
    """Clean up expired API keys."""
    try:
        limiter = get_limiter()
        
        if dry_run:
            click.echo("🔍 Dry run - checking for expired keys...")
            # Would need to implement a dry run method
            click.echo("This would clean up expired API keys")
        else:
            cleaned = limiter.cleanup_expired_keys()
            click.echo(f"🧹 Cleaned up {cleaned} expired API keys")
            
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}", err=True)


@api_key_commands.command('list-tiers')
@with_appcontext
def list_tiers():
    """List available API key tiers and their limits."""
    limiter = get_limiter()
    
    click.echo("🎯 API Key Tiers and Limits")
    click.echo("=" * 80)
    
    for tier, limits in limiter.tier_limits.items():
        click.echo(f"\n🏷️  {tier.value.upper()}")
        click.echo(f"  • Requests: {limits.requests_per_minute}/min, {limits.requests_per_hour}/hr, {limits.requests_per_day}/day")
        click.echo(f"  • Data Transfer: {limits.data_transfer_mb_per_day} MB/day")
        click.echo(f"  • Compute Time: {limits.compute_seconds_per_day} seconds/day")
        click.echo(f"  • Concurrent: {limits.concurrent_requests} requests")
        click.echo(f"  • ML Predictions: {limits.ml_predictions_per_day}/day")
        click.echo(f"  • Property Searches: {limits.property_searches_per_hour}/hour")
        if limits.data_exports_per_day > 0:
            click.echo(f"  • Data Exports: {limits.data_exports_per_day}/day")
        if limits.admin_operations_per_day > 0:
            click.echo(f"  • Admin Operations: {limits.admin_operations_per_day}/day")
