"""
Geographic Rate Limiting System for Canada
Implements location-based rate limiting with Canadian provinces, cities, and time zones.
"""

import time
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import logging
from threading import Lock
import json
import ipaddress
import requests

# Try to import Redis for distributed caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CanadianProvince(Enum):
    """Canadian provinces and territories."""
    ALBERTA = "AB"
    BRITISH_COLUMBIA = "BC"
    MANITOBA = "MB"
    NEW_BRUNSWICK = "NB"
    NEWFOUNDLAND_AND_LABRADOR = "NL"
    NORTHWEST_TERRITORIES = "NT"
    NOVA_SCOTIA = "NS"
    NUNAVUT = "NU"
    ONTARIO = "ON"
    PRINCE_EDWARD_ISLAND = "PE"
    QUEBEC = "QC"
    SASKATCHEWAN = "SK"
    YUKON = "YT"


class CanadianTimeZone(Enum):
    """Canadian time zones."""
    PACIFIC = "America/Vancouver"      # BC, YT
    MOUNTAIN = "America/Edmonton"      # AB, NT, SK (some areas)
    CENTRAL = "America/Winnipeg"       # MB, SK, ON (northwest), NU (some)
    EASTERN = "America/Toronto"        # ON, QC, NU (some)
    ATLANTIC = "America/Halifax"       # NB, NS, PE
    NEWFOUNDLAND = "America/St_Johns"  # NL


class GeographicRiskLevel(Enum):
    """Risk levels for different geographic regions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GeographicLimit:
    """Configuration for geographic-based rate limiting."""
    province: Optional[str] = None
    timezone: Optional[str] = None
    city: Optional[str] = None
    base_limit: int = 100
    time_window: int = 3600  # seconds
    risk_level: GeographicRiskLevel = GeographicRiskLevel.LOW
    business_hours_multiplier: float = 1.0  # Adjust limits during business hours
    weekend_multiplier: float = 1.5  # Higher limits on weekends
    active_hours: Optional[Tuple[int, int]] = None  # (start_hour, end_hour)


@dataclass
class ClientLocation:
    """Client geographic location information."""
    ip_address: str
    country: str = "CA"  # Canada only
    province: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    isp: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False
    last_updated: float = field(default_factory=time.time)


@dataclass
class RegionalQuota:
    """Regional quota configuration."""
    region_type: str  # 'province', 'city', 'timezone'
    region_value: str
    daily_quota: int
    hourly_quota: int
    concurrent_users_limit: int
    current_usage: int = 0
    peak_usage: int = 0
    reset_time: float = field(default_factory=time.time)


class GeographicRateLimiter:
    """Rate limiter with Canadian geographic restrictions."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.client_locations: Dict[str, ClientLocation] = {}
        self.regional_quotas: Dict[str, RegionalQuota] = {}
        self.blocked_ranges: Set[str] = set()  # IP ranges to block
        self.lock = Lock()
        
        # Major Canadian cities with special limits
        self.major_cities = {
            'Toronto': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.HIGH},
            'Montreal': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.HIGH},
            'Vancouver': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.HIGH},
            'Calgary': {'province': 'AB', 'timezone': 'America/Edmonton', 'risk': GeographicRiskLevel.MEDIUM},
            'Edmonton': {'province': 'AB', 'timezone': 'America/Edmonton', 'risk': GeographicRiskLevel.MEDIUM},
            'Ottawa': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.MEDIUM},
            'Mississauga': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.MEDIUM},
            'Winnipeg': {'province': 'MB', 'timezone': 'America/Winnipeg', 'risk': GeographicRiskLevel.MEDIUM},
            'Quebec City': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Hamilton': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Brampton': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.MEDIUM},
            'Surrey': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.MEDIUM},
            'Laval': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Halifax': {'province': 'NS', 'timezone': 'America/Halifax', 'risk': GeographicRiskLevel.LOW},
            'London': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Markham': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.MEDIUM},
            'Vaughan': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.MEDIUM},
            'Gatineau': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Longueuil': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Burnaby': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.MEDIUM},
            'Saskatoon': {'province': 'SK', 'timezone': 'America/Regina', 'risk': GeographicRiskLevel.LOW},
            'Kitchener': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Windsor': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Regina': {'province': 'SK', 'timezone': 'America/Regina', 'risk': GeographicRiskLevel.LOW},
            'Richmond': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.MEDIUM},
            'Richmond Hill': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.MEDIUM},
            'Oakville': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Burlington': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Greater Sudbury': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Sherbrooke': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Oshawa': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Saguenay': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Lévis': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Barrie': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Abbotsford': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'St. Catharines': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Trois-Rivières': {'province': 'QC', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Guelph': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Cambridge': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Whitby': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Kelowna': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Kingston': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Ajax': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Langley': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Saanich': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Milton': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Coquitlam': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Newmarket': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Brantford': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Thunder Bay': {'province': 'ON', 'timezone': 'America/Thunder_Bay', 'risk': GeographicRiskLevel.LOW},
            'St. John\'s': {'province': 'NL', 'timezone': 'America/St_Johns', 'risk': GeographicRiskLevel.LOW},
            'Moncton': {'province': 'NB', 'timezone': 'America/Moncton', 'risk': GeographicRiskLevel.LOW},
            'Sudbury': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Peterborough': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Kawartha Lakes': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Kamloops': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Chilliwack': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Prince George': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Waterloo': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Niagara Falls': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Chatham-Kent': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Red Deer': {'province': 'AB', 'timezone': 'America/Edmonton', 'risk': GeographicRiskLevel.LOW},
            'North Bay': {'province': 'ON', 'timezone': 'America/Toronto', 'risk': GeographicRiskLevel.LOW},
            'Medicine Hat': {'province': 'AB', 'timezone': 'America/Edmonton', 'risk': GeographicRiskLevel.LOW},
            'Lethbridge': {'province': 'AB', 'timezone': 'America/Edmonton', 'risk': GeographicRiskLevel.LOW},
            'Kamloops': {'province': 'BC', 'timezone': 'America/Kamloops', 'risk': GeographicRiskLevel.LOW},
            'Nanaimo': {'province': 'BC', 'timezone': 'America/Vancouver', 'risk': GeographicRiskLevel.LOW},
            'Fredericton': {'province': 'NB', 'timezone': 'America/Moncton', 'risk': GeographicRiskLevel.LOW},
            'Saint John': {'province': 'NB', 'timezone': 'America/Moncton', 'risk': GeographicRiskLevel.LOW},
            'Charlottetown': {'province': 'PE', 'timezone': 'America/Halifax', 'risk': GeographicRiskLevel.LOW},
            'Yellowknife': {'province': 'NT', 'timezone': 'America/Yellowknife', 'risk': GeographicRiskLevel.LOW},
            'Whitehorse': {'province': 'YT', 'timezone': 'America/Whitehorse', 'risk': GeographicRiskLevel.LOW},
            'Iqaluit': {'province': 'NU', 'timezone': 'America/Iqaluit', 'risk': GeographicRiskLevel.LOW}
        }
        
        # Initialize Canadian geographic limits
        self.geographic_limits = self._initialize_canadian_limits()
        
        # Initialize regional quotas
        self._initialize_regional_quotas()
        
        # Canadian IP ranges (for validation)
        self.canadian_ip_ranges = [
            '24.0.0.0/8', '64.0.0.0/8', '65.0.0.0/8', '66.0.0.0/8',
            '67.0.0.0/8', '68.0.0.0/8', '69.0.0.0/8', '70.0.0.0/8',
            '72.0.0.0/8', '74.0.0.0/8', '75.0.0.0/8', '76.0.0.0/8',
            '96.0.0.0/8', '97.0.0.0/8', '98.0.0.0/8', '99.0.0.0/8',
            '142.0.0.0/8', '154.0.0.0/8', '184.0.0.0/8', '192.0.0.0/8',
            '198.0.0.0/8', '199.0.0.0/8', '206.0.0.0/8', '207.0.0.0/8',
            '208.0.0.0/8', '209.0.0.0/8', '216.0.0.0/8'
        ]
    
    def _initialize_canadian_limits(self) -> Dict[str, GeographicLimit]:
        """Initialize rate limits for Canadian provinces and major cities."""
        limits = {}
        
        # Province-based limits
        province_configs = {
            'ON': GeographicLimit(province='ON', base_limit=500, risk_level=GeographicRiskLevel.HIGH),
            'QC': GeographicLimit(province='QC', base_limit=400, risk_level=GeographicRiskLevel.HIGH),
            'BC': GeographicLimit(province='BC', base_limit=300, risk_level=GeographicRiskLevel.MEDIUM),
            'AB': GeographicLimit(province='AB', base_limit=250, risk_level=GeographicRiskLevel.MEDIUM),
            'MB': GeographicLimit(province='MB', base_limit=150, risk_level=GeographicRiskLevel.LOW),
            'SK': GeographicLimit(province='SK', base_limit=120, risk_level=GeographicRiskLevel.LOW),
            'NS': GeographicLimit(province='NS', base_limit=100, risk_level=GeographicRiskLevel.LOW),
            'NB': GeographicLimit(province='NB', base_limit=80, risk_level=GeographicRiskLevel.LOW),
            'NL': GeographicLimit(province='NL', base_limit=70, risk_level=GeographicRiskLevel.LOW),
            'PE': GeographicLimit(province='PE', base_limit=50, risk_level=GeographicRiskLevel.LOW),
            'NT': GeographicLimit(province='NT', base_limit=40, risk_level=GeographicRiskLevel.LOW),
            'YT': GeographicLimit(province='YT', base_limit=30, risk_level=GeographicRiskLevel.LOW),
            'NU': GeographicLimit(province='NU', base_limit=25, risk_level=GeographicRiskLevel.LOW),
        }
        
        for province, config in province_configs.items():
            limits[f'province_{province}'] = config
        
        # Timezone-based limits
        timezone_configs = {
            'America/Toronto': GeographicLimit(
                timezone='America/Toronto', base_limit=600, 
                active_hours=(8, 18), business_hours_multiplier=0.8
            ),
            'America/Vancouver': GeographicLimit(
                timezone='America/Vancouver', base_limit=400,
                active_hours=(8, 18), business_hours_multiplier=0.8
            ),
            'America/Edmonton': GeographicLimit(
                timezone='America/Edmonton', base_limit=300,
                active_hours=(8, 18), business_hours_multiplier=0.9
            ),
            'America/Winnipeg': GeographicLimit(
                timezone='America/Winnipeg', base_limit=200,
                active_hours=(8, 18), business_hours_multiplier=0.9
            ),
            'America/Halifax': GeographicLimit(
                timezone='America/Halifax', base_limit=150,
                active_hours=(8, 18), business_hours_multiplier=1.0
            ),
            'America/St_Johns': GeographicLimit(
                timezone='America/St_Johns', base_limit=100,
                active_hours=(8, 18), business_hours_multiplier=1.0
            )
        }
        
        for tz, config in timezone_configs.items():
            limits[f'timezone_{tz.replace("/", "_")}'] = config
        
        # City-based limits for major cities
        for city, info in self.major_cities.items():
            city_limit = GeographicLimit(
                city=city,
                province=info['province'],
                timezone=info['timezone'],
                base_limit=self._get_city_base_limit(info['risk']),
                risk_level=info['risk'],
                active_hours=(7, 19),
                business_hours_multiplier=0.7 if info['risk'] == GeographicRiskLevel.HIGH else 0.8
            )
            clean_city_name = city.replace(" ", "_").replace(".", "").replace("'", "")
            limits[f'city_{clean_city_name}'] = city_limit
        
        return limits
    
    def _get_city_base_limit(self, risk_level: GeographicRiskLevel) -> int:
        """Get base rate limit based on city risk level."""
        risk_limits = {
            GeographicRiskLevel.LOW: 200,
            GeographicRiskLevel.MEDIUM: 300,
            GeographicRiskLevel.HIGH: 500,
            GeographicRiskLevel.CRITICAL: 100
        }
        return risk_limits.get(risk_level, 150)
    
    def _initialize_regional_quotas(self):
        """Initialize regional quotas for Canadian regions."""
        # Province quotas
        province_quotas = {
            'ON': RegionalQuota('province', 'ON', daily_quota=50000, hourly_quota=5000, concurrent_users_limit=1000),
            'QC': RegionalQuota('province', 'QC', daily_quota=40000, hourly_quota=4000, concurrent_users_limit=800),
            'BC': RegionalQuota('province', 'BC', daily_quota=30000, hourly_quota=3000, concurrent_users_limit=600),
            'AB': RegionalQuota('province', 'AB', daily_quota=25000, hourly_quota=2500, concurrent_users_limit=500),
            'MB': RegionalQuota('province', 'MB', daily_quota=15000, hourly_quota=1500, concurrent_users_limit=300),
            'SK': RegionalQuota('province', 'SK', daily_quota=12000, hourly_quota=1200, concurrent_users_limit=250),
            'NS': RegionalQuota('province', 'NS', daily_quota=10000, hourly_quota=1000, concurrent_users_limit=200),
            'NB': RegionalQuota('province', 'NB', daily_quota=8000, hourly_quota=800, concurrent_users_limit=150),
            'NL': RegionalQuota('province', 'NL', daily_quota=7000, hourly_quota=700, concurrent_users_limit=120),
            'PE': RegionalQuota('province', 'PE', daily_quota=5000, hourly_quota=500, concurrent_users_limit=100),
            'NT': RegionalQuota('province', 'NT', daily_quota=4000, hourly_quota=400, concurrent_users_limit=80),
            'YT': RegionalQuota('province', 'YT', daily_quota=3000, hourly_quota=300, concurrent_users_limit=60),
            'NU': RegionalQuota('province', 'NU', daily_quota=2500, hourly_quota=250, concurrent_users_limit=50),
        }
        
        for province, quota in province_quotas.items():
            self.regional_quotas[f'province_{province}'] = quota
        
        # Major city quotas
        major_city_quotas = {
            'Toronto': RegionalQuota('city', 'Toronto', daily_quota=20000, hourly_quota=2000, concurrent_users_limit=400),
            'Montreal': RegionalQuota('city', 'Montreal', daily_quota=15000, hourly_quota=1500, concurrent_users_limit=300),
            'Vancouver': RegionalQuota('city', 'Vancouver', daily_quota=12000, hourly_quota=1200, concurrent_users_limit=250),
            'Calgary': RegionalQuota('city', 'Calgary', daily_quota=8000, hourly_quota=800, concurrent_users_limit=160),
            'Edmonton': RegionalQuota('city', 'Edmonton', daily_quota=7000, hourly_quota=700, concurrent_users_limit=140),
            'Ottawa': RegionalQuota('city', 'Ottawa', daily_quota=6000, hourly_quota=600, concurrent_users_limit=120),
        }
        
        for city, quota in major_city_quotas.items():
            self.regional_quotas[f'city_{city}'] = quota
    
    def get_client_location(self, client_id: str, ip_address: str) -> ClientLocation:
        """Get or resolve client location information."""
        if client_id in self.client_locations:
            location = self.client_locations[client_id]
            # Update if IP changed or data is stale
            if location.ip_address != ip_address or time.time() - location.last_updated > 3600:
                location = self._resolve_location(ip_address)
                self.client_locations[client_id] = location
        else:
            location = self._resolve_location(ip_address)
            self.client_locations[client_id] = location
        
        return location
    
    def _resolve_location(self, ip_address: str) -> ClientLocation:
        """Resolve IP address to Canadian location."""
        location = ClientLocation(ip_address=ip_address)
        
        # Basic validation - check if IP is in Canadian ranges
        if not self._is_canadian_ip(ip_address):
            location.country = "UNKNOWN"
            location.is_proxy = True  # Treat non-Canadian IPs as potential proxies
            return location
        
        # Mock location resolution (in production, use a real geolocation service)
        # For demo purposes, we'll assign based on IP patterns
        location_info = self._mock_location_resolution(ip_address)
        
        location.country = "CA"
        location.province = location_info.get('province')
        location.city = location_info.get('city')
        location.timezone = location_info.get('timezone')
        location.postal_code = location_info.get('postal_code')
        location.latitude = location_info.get('latitude')
        location.longitude = location_info.get('longitude')
        location.isp = location_info.get('isp')
        location.last_updated = time.time()
        
        return location
    
    def _is_canadian_ip(self, ip_address: str) -> bool:
        """Check if IP address is in Canadian ranges."""
        try:
            ip = ipaddress.ip_address(ip_address)
            for range_str in self.canadian_ip_ranges:
                if ip in ipaddress.ip_network(range_str, strict=False):
                    return True
        except Exception:
            pass
        return False
    
    def _mock_location_resolution(self, ip_address: str) -> Dict[str, Any]:
        """Mock location resolution for Canadian IPs."""
        # This is a simplified mock - in production, use a real geolocation API
        ip_parts = ip_address.split('.')
        hash_val = sum(int(part) for part in ip_parts) % 100
        
        # Distribute based on population
        if hash_val < 40:  # 40% Ontario
            provinces = ['ON'] * 8 + ['QC'] * 5 + ['BC'] * 3 + ['AB'] * 2
            major_cities_on = ['Toronto', 'Ottawa', 'Mississauga', 'Hamilton', 'London', 'Kitchener']
            major_cities_qc = ['Montreal', 'Quebec City', 'Laval', 'Gatineau']
            major_cities_bc = ['Vancouver', 'Surrey', 'Burnaby', 'Richmond']
            major_cities_ab = ['Calgary', 'Edmonton']
            
            province = provinces[hash_val % len(provinces)]
            if province == 'ON':
                city = major_cities_on[hash_val % len(major_cities_on)]
                timezone = 'America/Toronto'
            elif province == 'QC':
                city = major_cities_qc[hash_val % len(major_cities_qc)]
                timezone = 'America/Toronto'
            elif province == 'BC':
                city = major_cities_bc[hash_val % len(major_cities_bc)]
                timezone = 'America/Vancouver'
            else:  # AB
                city = major_cities_ab[hash_val % len(major_cities_ab)]
                timezone = 'America/Edmonton'
        else:
            # Other provinces
            other_provinces = ['MB', 'SK', 'NS', 'NB', 'NL', 'PE', 'NT', 'YT', 'NU']
            province = other_provinces[hash_val % len(other_provinces)]
            
            province_cities = {
                'MB': ['Winnipeg', 'Brandon'],
                'SK': ['Saskatoon', 'Regina'],
                'NS': ['Halifax', 'Sydney'],
                'NB': ['Moncton', 'Saint John', 'Fredericton'],
                'NL': ['St. John\'s', 'Corner Brook'],
                'PE': ['Charlottetown', 'Summerside'],
                'NT': ['Yellowknife', 'Hay River'],
                'YT': ['Whitehorse', 'Dawson City'],
                'NU': ['Iqaluit', 'Rankin Inlet']
            }
            
            province_timezones = {
                'MB': 'America/Winnipeg',
                'SK': 'America/Regina',
                'NS': 'America/Halifax',
                'NB': 'America/Moncton',
                'NL': 'America/St_Johns',
                'PE': 'America/Halifax',
                'NT': 'America/Yellowknife',
                'YT': 'America/Whitehorse',
                'NU': 'America/Iqaluit'
            }
            
            city = province_cities[province][hash_val % len(province_cities[province])]
            timezone = province_timezones[province]
        
        return {
            'province': province,
            'city': city,
            'timezone': timezone,
            'postal_code': f'{province[0]}{hash_val % 10}{province[1]}{hash_val % 10}{province[0]}{hash_val % 10}',
            'latitude': 45.0 + (hash_val % 20),
            'longitude': -75.0 - (hash_val % 30),
            'isp': ['Rogers', 'Bell', 'Telus', 'Shaw', 'Videotron'][hash_val % 5]
        }
    
    def check_geographic_rate_limit(self, client_id: str, ip_address: str,
                                  endpoint_category: str) -> Tuple[bool, int, Dict[str, Any]]:
        """Check geographic rate limiting for a client."""
        current_time = time.time()
        location = self.get_client_location(client_id, ip_address)
        
        # Block non-Canadian IPs
        if location.country != "CA":
            return False, 3600, {
                'reason': 'geo_blocked',
                'message': 'Service only available in Canada',
                'location': location.country
            }
        
        # Check if IP is in blocked ranges
        if self._is_ip_blocked(ip_address):
            return False, 86400, {
                'reason': 'ip_blocked',
                'message': 'IP address is blocked',
                'ip': ip_address
            }
        
        # Check VPN/Proxy restrictions
        if location.is_vpn or location.is_proxy:
            return False, 1800, {
                'reason': 'proxy_blocked',
                'message': 'VPN/Proxy usage detected',
                'location': location.city or location.province
            }
        
        # Get applicable limits
        applicable_limits = self._get_applicable_limits(location)
        
        # Check each applicable limit
        for limit_type, limit_config in applicable_limits.items():
            allowed, retry_after, limit_info = self._check_single_limit(
                client_id, location, limit_config, current_time
            )
            
            if not allowed:
                return False, retry_after, {
                    'reason': 'rate_limited',
                    'limit_type': limit_type,
                    'location': {
                        'province': location.province,
                        'city': location.city,
                        'timezone': location.timezone
                    },
                    **limit_info
                }
        
        # Check regional quotas
        quota_check = self._check_regional_quotas(location)
        if not quota_check['allowed']:
            return False, quota_check['retry_after'], quota_check
        
        # Check timezone restrictions
        timezone_check = self._check_timezone_restrictions(location)
        if not timezone_check['allowed']:
            return False, timezone_check['retry_after'], timezone_check
        
        # All checks passed
        self._record_successful_request(client_id, location)
        
        return True, 0, {
            'reason': 'allowed',
            'location': {
                'province': location.province,
                'city': location.city,
                'timezone': location.timezone
            },
            'applicable_limits': list(applicable_limits.keys())
        }
    
    def _get_applicable_limits(self, location: ClientLocation) -> Dict[str, GeographicLimit]:
        """Get all applicable geographic limits for a location."""
        applicable = {}
        
        # Province-based limit
        if location.province:
            province_key = f'province_{location.province}'
            if province_key in self.geographic_limits:
                applicable[province_key] = self.geographic_limits[province_key]
        
        # City-based limit
        if location.city:
            clean_city_name = location.city.replace(" ", "_").replace(".", "").replace("'", "")
            city_key = f'city_{clean_city_name}'
            if city_key in self.geographic_limits:
                applicable[city_key] = self.geographic_limits[city_key]
        
        # Timezone-based limit
        if location.timezone:
            tz_key = f'timezone_{location.timezone.replace("/", "_")}'
            if tz_key in self.geographic_limits:
                applicable[tz_key] = self.geographic_limits[tz_key]
        
        return applicable
    
    def _check_single_limit(self, client_id: str, location: ClientLocation,
                           limit_config: GeographicLimit, current_time: float) -> Tuple[bool, int, Dict[str, Any]]:
        """Check a single geographic limit."""
        # Get request history for this client and location
        window_start = current_time - limit_config.time_window
        
        # Calculate dynamic limit based on time of day
        dynamic_limit = self._calculate_dynamic_limit(limit_config, location, current_time)
        
        # Count recent requests (mock - in production, use Redis or database)
        request_count = self._get_request_count(client_id, window_start, current_time)
        
        if request_count >= dynamic_limit:
            retry_after = limit_config.time_window - int(current_time % limit_config.time_window)
            return False, retry_after, {
                'current_requests': request_count,
                'limit': dynamic_limit,
                'window_seconds': limit_config.time_window
            }
        
        return True, 0, {
            'current_requests': request_count,
            'limit': dynamic_limit,
            'remaining': dynamic_limit - request_count
        }
    
    def _calculate_dynamic_limit(self, limit_config: GeographicLimit,
                               location: ClientLocation, current_time: float) -> int:
        """Calculate dynamic limit based on time and location factors."""
        base_limit = limit_config.base_limit
        
        # Get local time for the client's timezone
        if location.timezone:
            try:
                tz = pytz.timezone(location.timezone)
                local_time = datetime.fromtimestamp(current_time, tz)
                current_hour = local_time.hour
                is_weekend = local_time.weekday() >= 5
            except:
                current_hour = datetime.fromtimestamp(current_time).hour
                is_weekend = datetime.fromtimestamp(current_time).weekday() >= 5
        else:
            current_hour = datetime.fromtimestamp(current_time).hour
            is_weekend = datetime.fromtimestamp(current_time).weekday() >= 5
        
        # Apply time-based multipliers
        multiplier = 1.0
        
        # Business hours adjustment
        if limit_config.active_hours:
            start_hour, end_hour = limit_config.active_hours
            if start_hour <= current_hour <= end_hour:
                multiplier *= limit_config.business_hours_multiplier
        
        # Weekend adjustment
        if is_weekend:
            multiplier *= limit_config.weekend_multiplier
        
        # Risk level adjustment
        risk_multipliers = {
            GeographicRiskLevel.LOW: 1.2,
            GeographicRiskLevel.MEDIUM: 1.0,
            GeographicRiskLevel.HIGH: 0.8,
            GeographicRiskLevel.CRITICAL: 0.5
        }
        multiplier *= risk_multipliers.get(limit_config.risk_level, 1.0)
        
        return max(1, int(base_limit * multiplier))
    
    def _get_request_count(self, client_id: str, window_start: float, current_time: float) -> int:
        """Get request count for client in time window (mock implementation)."""
        # In production, this would query Redis or database
        # For demo, return a mock count based on client_id hash
        hash_val = hash(client_id) % 100
        time_factor = int((current_time - window_start) / 60)  # Minutes in window
        return min(hash_val, time_factor * 2)
    
    def _check_regional_quotas(self, location: ClientLocation) -> Dict[str, Any]:
        """Check regional quotas for the client's location."""
        current_time = time.time()
        
        # Check province quota
        if location.province:
            province_key = f'province_{location.province}'
            if province_key in self.regional_quotas:
                quota = self.regional_quotas[province_key]
                
                # Reset quota if needed
                if current_time - quota.reset_time > 86400:  # Daily reset
                    quota.current_usage = 0
                    quota.reset_time = current_time
                
                if quota.current_usage >= quota.daily_quota:
                    return {
                        'allowed': False,
                        'reason': 'regional_quota_exceeded',
                        'quota_type': 'daily_provincial',
                        'region': location.province,
                        'retry_after': int(86400 - (current_time - quota.reset_time))
                    }
        
        # Check city quota
        if location.city:
            city_key = f'city_{location.city}'
            if city_key in self.regional_quotas:
                quota = self.regional_quotas[city_key]
                
                if current_time - quota.reset_time > 86400:
                    quota.current_usage = 0
                    quota.reset_time = current_time
                
                if quota.current_usage >= quota.daily_quota:
                    return {
                        'allowed': False,
                        'reason': 'regional_quota_exceeded',
                        'quota_type': 'daily_city',
                        'region': location.city,
                        'retry_after': int(86400 - (current_time - quota.reset_time))
                    }
        
        return {'allowed': True}
    
    def _check_timezone_restrictions(self, location: ClientLocation) -> Dict[str, Any]:
        """Check timezone-based restrictions."""
        if not location.timezone:
            return {'allowed': True}
        
        try:
            tz = pytz.timezone(location.timezone)
            local_time = datetime.now(tz)
            current_hour = local_time.hour
            
            # Business hours: 6 AM to 11 PM local time
            if not (6 <= current_hour <= 23):
                return {
                    'allowed': False,
                    'reason': 'timezone_restricted',
                    'message': 'Service unavailable during overnight hours (11 PM - 6 AM local time)',
                    'local_time': local_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
                    'retry_after': self._calculate_retry_until_business_hours(local_time)
                }
        except Exception as e:
            logger.warning(f"Timezone check failed for {location.timezone}: {e}")
        
        return {'allowed': True}
    
    def _calculate_retry_until_business_hours(self, local_time: datetime) -> int:
        """Calculate seconds until business hours resume."""
        current_hour = local_time.hour
        
        if current_hour < 6:
            # Before business hours - wait until 6 AM
            next_open = local_time.replace(hour=6, minute=0, second=0, microsecond=0)
        else:
            # After business hours - wait until 6 AM next day
            next_open = local_time.replace(hour=6, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return int((next_open - local_time).total_seconds())
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is in blocked ranges."""
        try:
            ip = ipaddress.ip_address(ip_address)
            for blocked_range in self.blocked_ranges:
                if ip in ipaddress.ip_network(blocked_range, strict=False):
                    return True
        except Exception:
            pass
        return False
    
    def _record_successful_request(self, client_id: str, location: ClientLocation):
        """Record a successful request for quota tracking."""
        # Update regional quotas
        if location.province:
            province_key = f'province_{location.province}'
            if province_key in self.regional_quotas:
                self.regional_quotas[province_key].current_usage += 1
        
        if location.city:
            city_key = f'city_{location.city}'
            if city_key in self.regional_quotas:
                self.regional_quotas[city_key].current_usage += 1
    
    def add_blocked_ip_range(self, ip_range: str):
        """Add an IP range to the block list."""
        try:
            # Validate the range
            ipaddress.ip_network(ip_range, strict=False)
            self.blocked_ranges.add(ip_range)
            logger.info(f"Added IP range to block list: {ip_range}")
        except Exception as e:
            logger.error(f"Invalid IP range {ip_range}: {e}")
    
    def remove_blocked_ip_range(self, ip_range: str):
        """Remove an IP range from the block list."""
        if ip_range in self.blocked_ranges:
            self.blocked_ranges.remove(ip_range)
            logger.info(f"Removed IP range from block list: {ip_range}")
    
    def get_geographic_status(self, client_id: str = None) -> Dict[str, Any]:
        """Get geographic rate limiting status."""
        status = {
            'total_clients': len(self.client_locations),
            'blocked_ip_ranges': len(self.blocked_ranges),
            'regional_quotas': {},
            'province_distribution': defaultdict(int),
            'city_distribution': defaultdict(int),
            'timezone_distribution': defaultdict(int)
        }
        
        # Regional quota status
        for quota_key, quota in self.regional_quotas.items():
            status['regional_quotas'][quota_key] = {
                'daily_quota': quota.daily_quota,
                'current_usage': quota.current_usage,
                'percentage_used': (quota.current_usage / quota.daily_quota * 100) if quota.daily_quota > 0 else 0,
                'concurrent_limit': quota.concurrent_users_limit
            }
        
        # Client distribution
        for location in self.client_locations.values():
            if location.province:
                status['province_distribution'][location.province] += 1
            if location.city:
                status['city_distribution'][location.city] += 1
            if location.timezone:
                status['timezone_distribution'][location.timezone] += 1
        
        # Specific client info if requested
        if client_id and client_id in self.client_locations:
            location = self.client_locations[client_id]
            status['client_info'] = {
                'province': location.province,
                'city': location.city,
                'timezone': location.timezone,
                'ip_address': location.ip_address,
                'is_vpn': location.is_vpn,
                'is_proxy': location.is_proxy,
                'last_updated': datetime.fromtimestamp(location.last_updated).isoformat()
            }
        
        return status
    
    def cleanup_old_location_data(self, max_age_hours: int = 24):
        """Clean up old location data."""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        inactive_clients = [
            client_id for client_id, location in self.client_locations.items()
            if location.last_updated < cutoff_time
        ]
        
        for client_id in inactive_clients:
            del self.client_locations[client_id]
        
        logger.info(f"Cleaned up {len(inactive_clients)} old location records")


# Convenience function for easy integration
def check_geographic_rate_limit(client_id: str, ip_address: str,
                              endpoint_category: str = "general") -> Tuple[bool, int, Dict[str, Any]]:
    """Check geographic rate limit for a client."""
    if not hasattr(check_geographic_rate_limit, '_limiter'):
        check_geographic_rate_limit._limiter = GeographicRateLimiter()
    
    return check_geographic_rate_limit._limiter.check_geographic_rate_limit(
        client_id, ip_address, endpoint_category
    )


def get_geographic_status(client_id: str = None) -> Dict[str, Any]:
    """Get geographic rate limiting status."""
    if not hasattr(check_geographic_rate_limit, '_limiter'):
        check_geographic_rate_limit._limiter = GeographicRateLimiter()
    
    return check_geographic_rate_limit._limiter.get_geographic_status(client_id)
