"""
CLI commands for Geographic Rate Limiting System
Provides command-line interface for managing Canadian geographic rate limits.
"""

import click
import json
import time
from datetime import datetime
from typing import Dict, Any
from app.security.geographic_rate_limiter import (
    GeographicRateLimiter, check_geographic_rate_limit, get_geographic_status,
    CanadianProvince, CanadianTimeZone, GeographicRiskLevel
)


@click.group(name='geographic-limiting')
def geographic_limiting_commands():
    """Geographic rate limiting commands for Canadian locations."""
    pass


@geographic_limiting_commands.command('status')
@click.option('--client-id', help='Show status for specific client')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
def status(client_id, format):
    """Show geographic rate limiting system status."""
    click.echo("🌍 Geographic Rate Limiting System Status")
    click.echo("=" * 50)
    
    try:
        status_data = get_geographic_status(client_id)
        
        if format == 'json':
            click.echo(json.dumps(status_data, indent=2))
            return
        
        # Table format
        click.echo(f"📊 System Overview:")
        click.echo(f"  Total Clients: {status_data['total_clients']}")
        click.echo(f"  Blocked IP Ranges: {status_data['blocked_ip_ranges']}")
        
        # Province distribution
        if status_data['province_distribution']:
            click.echo(f"\n🏛️ Province Distribution:")
            for province, count in sorted(status_data['province_distribution'].items()):
                province_name = _get_province_name(province)
                click.echo(f"  {province} ({province_name}): {count} clients")
        
        # Major cities
        if status_data['city_distribution']:
            click.echo(f"\n🏙️ Top Cities:")
            sorted_cities = sorted(status_data['city_distribution'].items(), 
                                 key=lambda x: x[1], reverse=True)[:10]
            for city, count in sorted_cities:
                click.echo(f"  {city}: {count} clients")
        
        # Timezone distribution
        if status_data['timezone_distribution']:
            click.echo(f"\n🕐 Timezone Distribution:")
            for tz, count in sorted(status_data['timezone_distribution'].items()):
                tz_name = _get_timezone_name(tz)
                click.echo(f"  {tz_name}: {count} clients")
        
        # Regional quotas
        if status_data['regional_quotas']:
            click.echo(f"\n📈 Regional Quota Usage:")
            for quota_key, quota_info in status_data['regional_quotas'].items():
                percentage = quota_info['percentage_used']
                status_icon = "🟢" if percentage < 70 else "🟡" if percentage < 90 else "🔴"
                click.echo(f"  {status_icon} {quota_key}: {quota_info['current_usage']:,}/{quota_info['daily_quota']:,} ({percentage:.1f}%)")
        
        # Client-specific info
        if 'client_info' in status_data:
            click.echo(f"\n👤 Client Information:")
            client_info = status_data['client_info']
            click.echo(f"  Province: {client_info['province']} ({_get_province_name(client_info['province'])})")
            click.echo(f"  City: {client_info['city']}")
            click.echo(f"  Timezone: {client_info['timezone']}")
            click.echo(f"  IP Address: {client_info['ip_address']}")
            click.echo(f"  VPN/Proxy: {'Yes' if client_info['is_vpn'] or client_info['is_proxy'] else 'No'}")
            click.echo(f"  Last Updated: {client_info['last_updated']}")
        
    except Exception as e:
        click.echo(f"❌ Error getting geographic limiting status: {e}")


@geographic_limiting_commands.command('test-client')
@click.argument('client_id')
@click.argument('ip_address')
@click.option('--endpoint', default='general', help='Endpoint category to test')
def test_client(client_id, ip_address, endpoint):
    """Test geographic rate limiting for a specific client."""
    click.echo(f"🧪 Testing Geographic Rate Limiting")
    click.echo(f"Client ID: {client_id}")
    click.echo(f"IP Address: {ip_address}")
    click.echo(f"Endpoint: {endpoint}")
    click.echo("=" * 50)
    
    try:
        allowed, retry_after, metadata = check_geographic_rate_limit(
            client_id, ip_address, endpoint
        )
        
        if allowed:
            click.echo("✅ Request ALLOWED")
            click.echo(f"Location: {metadata.get('location', {})}")
            if 'applicable_limits' in metadata:
                click.echo(f"Applicable Limits: {', '.join(metadata['applicable_limits'])}")
        else:
            click.echo("❌ Request BLOCKED")
            click.echo(f"Reason: {metadata.get('reason', 'Unknown')}")
            click.echo(f"Message: {metadata.get('message', 'No message')}")
            click.echo(f"Retry After: {retry_after} seconds")
            
            if 'location' in metadata:
                click.echo(f"Location: {metadata['location']}")
            
            if metadata.get('reason') == 'rate_limited':
                click.echo(f"Current Requests: {metadata.get('current_requests', 'N/A')}")
                click.echo(f"Limit: {metadata.get('limit', 'N/A')}")
        
    except Exception as e:
        click.echo(f"❌ Error testing client: {e}")


@geographic_limiting_commands.command('province-limits')
@click.option('--province', type=click.Choice([p.value for p in CanadianProvince]), 
              help='Show limits for specific province')
def province_limits(province):
    """Show or configure province-based rate limits."""
    click.echo("🏛️ Provincial Rate Limits")
    click.echo("=" * 40)
    
    try:
        if not hasattr(check_geographic_rate_limit, '_limiter'):
            check_geographic_rate_limit._limiter = GeographicRateLimiter()
        
        limiter = check_geographic_rate_limit._limiter
        
        if province:
            # Show specific province
            limit_key = f'province_{province}'
            if limit_key in limiter.geographic_limits:
                limit_config = limiter.geographic_limits[limit_key]
                province_name = _get_province_name(province)
                
                click.echo(f"Province: {province} ({province_name})")
                click.echo(f"Base Limit: {limit_config.base_limit} requests")
                click.echo(f"Time Window: {limit_config.time_window} seconds")
                click.echo(f"Risk Level: {limit_config.risk_level.value}")
                click.echo(f"Business Hours Multiplier: {limit_config.business_hours_multiplier}")
                click.echo(f"Weekend Multiplier: {limit_config.weekend_multiplier}")
                
                # Show quota info
                quota_key = f'province_{province}'
                if quota_key in limiter.regional_quotas:
                    quota = limiter.regional_quotas[quota_key]
                    percentage = (quota.current_usage / quota.daily_quota * 100) if quota.daily_quota > 0 else 0
                    click.echo(f"\n📈 Quota Usage:")
                    click.echo(f"  Daily: {quota.current_usage:,}/{quota.daily_quota:,} ({percentage:.1f}%)")
                    click.echo(f"  Concurrent Users Limit: {quota.concurrent_users_limit}")
            else:
                click.echo(f"No limits configured for province: {province}")
        else:
            # Show all provinces
            click.echo("All Provincial Limits:")
            for province_enum in CanadianProvince:
                limit_key = f'province_{province_enum.value}'
                if limit_key in limiter.geographic_limits:
                    limit_config = limiter.geographic_limits[limit_key]
                    province_name = _get_province_name(province_enum.value)
                    click.echo(f"  {province_enum.value} ({province_name}): {limit_config.base_limit} req/{limit_config.time_window}s")
    
    except Exception as e:
        click.echo(f"❌ Error showing province limits: {e}")


@geographic_limiting_commands.command('city-limits')
@click.option('--city', help='Show limits for specific city')
@click.option('--top', type=int, default=10, help='Show top N cities by population')
def city_limits(city, top):
    """Show city-based rate limits."""
    click.echo("🏙️ City Rate Limits")
    click.echo("=" * 30)
    
    try:
        if not hasattr(check_geographic_rate_limit, '_limiter'):
            check_geographic_rate_limit._limiter = GeographicRateLimiter()
        
        limiter = check_geographic_rate_limit._limiter
        
        if city:
            # Show specific city
            clean_city = city.replace(" ", "_").replace(".", "").replace("'", "")
            city_key = f'city_{clean_city}'
            if city_key in limiter.geographic_limits:
                limit_config = limiter.geographic_limits[city_key]
                
                click.echo(f"City: {city}")
                click.echo(f"Province: {limit_config.province}")
                click.echo(f"Timezone: {limit_config.timezone}")
                click.echo(f"Base Limit: {limit_config.base_limit} requests")
                click.echo(f"Risk Level: {limit_config.risk_level.value}")
                click.echo(f"Active Hours: {limit_config.active_hours}")
                
                # Show quota info
                quota_key = f'city_{city}'
                if quota_key in limiter.regional_quotas:
                    quota = limiter.regional_quotas[quota_key]
                    percentage = (quota.current_usage / quota.daily_quota * 100) if quota.daily_quota > 0 else 0
                    click.echo(f"\n📈 Quota Usage:")
                    click.echo(f"  Daily: {quota.current_usage:,}/{quota.daily_quota:,} ({percentage:.1f}%)")
            else:
                click.echo(f"No limits configured for city: {city}")
        else:
            # Show major cities
            click.echo(f"Top {top} Major Cities:")
            major_cities_info = [
                ('Toronto', 'ON', 'High Risk', '500'),
                ('Montreal', 'QC', 'High Risk', '500'),
                ('Vancouver', 'BC', 'High Risk', '500'),
                ('Calgary', 'AB', 'Medium Risk', '300'),
                ('Edmonton', 'AB', 'Medium Risk', '300'),
                ('Ottawa', 'ON', 'Medium Risk', '300'),
                ('Mississauga', 'ON', 'Medium Risk', '300'),
                ('Winnipeg', 'MB', 'Medium Risk', '300'),
                ('Quebec City', 'QC', 'Low Risk', '200'),
                ('Hamilton', 'ON', 'Low Risk', '200')
            ]
            
            for i, (city_name, province, risk, limit) in enumerate(major_cities_info[:top]):
                click.echo(f"  {i+1:2}. {city_name:15} ({province}) - {risk:11} - {limit} req/hour")
    
    except Exception as e:
        click.echo(f"❌ Error showing city limits: {e}")


@geographic_limiting_commands.command('timezone-status')
@click.option('--timezone', type=click.Choice([tz.value for tz in CanadianTimeZone]),
              help='Show status for specific timezone')
def timezone_status(timezone):
    """Show timezone-based restrictions and current times."""
    click.echo("🕐 Canadian Timezone Status")
    click.echo("=" * 40)
    
    try:
        current_time = datetime.now()
        
        if timezone:
            # Show specific timezone
            import pytz
            tz = pytz.timezone(timezone)
            local_time = current_time.astimezone(tz)
            
            click.echo(f"Timezone: {timezone}")
            click.echo(f"Current Local Time: {local_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            click.echo(f"UTC Offset: {local_time.strftime('%z')}")
            
            # Check if in business hours
            business_hours = 6 <= local_time.hour <= 23
            status_icon = "🟢" if business_hours else "🔴"
            status_text = "ACTIVE" if business_hours else "RESTRICTED"
            click.echo(f"Service Status: {status_icon} {status_text}")
            
            if not business_hours:
                if local_time.hour < 6:
                    hours_until_open = 6 - local_time.hour
                else:
                    hours_until_open = 24 - local_time.hour + 6
                click.echo(f"Hours until service resumes: {hours_until_open}")
        else:
            # Show all Canadian timezones
            import pytz
            click.echo("All Canadian Timezones:")
            
            for tz_enum in CanadianTimeZone:
                try:
                    tz = pytz.timezone(tz_enum.value)
                    local_time = current_time.astimezone(tz)
                    business_hours = 6 <= local_time.hour <= 23
                    status_icon = "🟢" if business_hours else "🔴"
                    
                    tz_name = _get_timezone_name(tz_enum.value)
                    click.echo(f"  {status_icon} {tz_name:20} {local_time.strftime('%H:%M %Z')}")
                except Exception as e:
                    click.echo(f"  ❌ {tz_enum.value}: Error - {e}")
    
    except Exception as e:
        click.echo(f"❌ Error showing timezone status: {e}")


@geographic_limiting_commands.command('block-ip')
@click.argument('ip_range')
@click.option('--reason', help='Reason for blocking')
def block_ip(ip_range, reason):
    """Add an IP range to the block list."""
    click.echo(f"🚫 Blocking IP Range: {ip_range}")
    
    try:
        if not hasattr(check_geographic_rate_limit, '_limiter'):
            check_geographic_rate_limit._limiter = GeographicRateLimiter()
        
        limiter = check_geographic_rate_limit._limiter
        limiter.add_blocked_ip_range(ip_range)
        
        click.echo("✅ IP range blocked successfully")
        if reason:
            click.echo(f"Reason: {reason}")
    
    except Exception as e:
        click.echo(f"❌ Error blocking IP range: {e}")


@geographic_limiting_commands.command('unblock-ip')
@click.argument('ip_range')
def unblock_ip(ip_range):
    """Remove an IP range from the block list."""
    click.echo(f"✅ Unblocking IP Range: {ip_range}")
    
    try:
        if not hasattr(check_geographic_rate_limit, '_limiter'):
            check_geographic_rate_limit._limiter = GeographicRateLimiter()
        
        limiter = check_geographic_rate_limit._limiter
        limiter.remove_blocked_ip_range(ip_range)
        
        click.echo("✅ IP range unblocked successfully")
    
    except Exception as e:
        click.echo(f"❌ Error unblocking IP range: {e}")


@geographic_limiting_commands.command('quota-report')
@click.option('--region-type', type=click.Choice(['province', 'city', 'all']), 
              default='all', help='Type of regional report')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
def quota_report(region_type, format):
    """Generate regional quota usage report."""
    click.echo("📊 Regional Quota Usage Report")
    click.echo("=" * 45)
    
    try:
        status_data = get_geographic_status()
        regional_quotas = status_data.get('regional_quotas', {})
        
        if format == 'json':
            click.echo(json.dumps(regional_quotas, indent=2))
            return
        
        # Filter by region type
        if region_type != 'all':
            filtered_quotas = {k: v for k, v in regional_quotas.items() 
                             if k.startswith(f'{region_type}_')}
        else:
            filtered_quotas = regional_quotas
        
        if not filtered_quotas:
            click.echo(f"No quota data found for region type: {region_type}")
            return
        
        # Sort by usage percentage
        sorted_quotas = sorted(filtered_quotas.items(), 
                             key=lambda x: x[1]['percentage_used'], reverse=True)
        
        click.echo(f"{'Region':<25} {'Usage':<15} {'Percentage':<12} {'Status'}")
        click.echo("-" * 65)
        
        for quota_key, quota_info in sorted_quotas:
            region_name = quota_key.replace('province_', '').replace('city_', '')
            usage_str = f"{quota_info['current_usage']:,}/{quota_info['daily_quota']:,}"
            percentage = quota_info['percentage_used']
            
            if percentage < 50:
                status = "🟢 Normal"
            elif percentage < 75:
                status = "🟡 Moderate"
            elif percentage < 90:
                status = "🟠 High"
            else:
                status = "🔴 Critical"
            
            click.echo(f"{region_name:<25} {usage_str:<15} {percentage:>6.1f}%     {status}")
    
    except Exception as e:
        click.echo(f"❌ Error generating quota report: {e}")


@geographic_limiting_commands.command('cleanup')
@click.option('--max-age', type=int, default=24, help='Maximum age in hours for data cleanup')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without actually doing it')
def cleanup(max_age, dry_run):
    """Clean up old geographic data."""
    click.echo(f"🧹 Geographic Data Cleanup")
    click.echo(f"Max age: {max_age} hours")
    click.echo(f"Dry run: {'Yes' if dry_run else 'No'}")
    click.echo("=" * 40)
    
    try:
        if not hasattr(check_geographic_rate_limit, '_limiter'):
            check_geographic_rate_limit._limiter = GeographicRateLimiter()
        
        limiter = check_geographic_rate_limit._limiter
        
        if dry_run:
            # Count what would be cleaned
            current_time = time.time()
            cutoff_time = current_time - (max_age * 3600)
            
            old_locations = [
                client_id for client_id, location in limiter.client_locations.items()
                if location.last_updated < cutoff_time
            ]
            
            click.echo(f"Would clean up {len(old_locations)} old location records")
            if old_locations:
                click.echo("Clients to be cleaned:")
                for client_id in old_locations[:10]:  # Show first 10
                    location = limiter.client_locations[client_id]
                    age_hours = (current_time - location.last_updated) / 3600
                    click.echo(f"  {client_id}: {age_hours:.1f} hours old")
                if len(old_locations) > 10:
                    click.echo(f"  ... and {len(old_locations) - 10} more")
        else:
            # Actually perform cleanup
            limiter.cleanup_old_location_data(max_age)
            click.echo("✅ Cleanup completed")
    
    except Exception as e:
        click.echo(f"❌ Error during cleanup: {e}")


def _get_province_name(province_code: str) -> str:
    """Get full province name from code."""
    province_names = {
        'AB': 'Alberta',
        'BC': 'British Columbia',
        'MB': 'Manitoba',
        'NB': 'New Brunswick',
        'NL': 'Newfoundland and Labrador',
        'NT': 'Northwest Territories',
        'NS': 'Nova Scotia',
        'NU': 'Nunavut',
        'ON': 'Ontario',
        'PE': 'Prince Edward Island',
        'QC': 'Quebec',
        'SK': 'Saskatchewan',
        'YT': 'Yukon'
    }
    return province_names.get(province_code, province_code)


def _get_timezone_name(timezone: str) -> str:
    """Get friendly timezone name."""
    tz_names = {
        'America/Vancouver': 'Pacific Time',
        'America/Edmonton': 'Mountain Time',
        'America/Winnipeg': 'Central Time',
        'America/Toronto': 'Eastern Time',
        'America/Halifax': 'Atlantic Time',
        'America/St_Johns': 'Newfoundland Time',
        'America/Regina': 'Central Time (SK)',
        'America/Yellowknife': 'Mountain Time (NT)',
        'America/Whitehorse': 'Pacific Time (YT)',
        'America/Iqaluit': 'Eastern Time (NU)',
        'America/Moncton': 'Atlantic Time (NB)',
        'America/Thunder_Bay': 'Eastern Time (ON)',
        'America/Kamloops': 'Pacific Time (BC)'
    }
    return tz_names.get(timezone, timezone)


def register_geographic_limiting_commands(app):
    """Register geographic limiting CLI commands with Flask app."""
    app.cli.add_command(geographic_limiting_commands)
