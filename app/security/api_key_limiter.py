"""
API Key Rate Limiting System
Implements API key generation, key-based rate limiting, developer quotas, and usage tracking.
"""

import time
import uuid
import hashlib
import secrets
import json
import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum
import logging
from threading import Lock

# Try to import Redis for distributed caching
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class APIKeyTier(Enum):
    """API key tiers with different rate limits."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    UNLIMITED = "unlimited"


class APIKeyStatus(Enum):
    """API key status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


class UsageMetricType(Enum):
    """Types of usage metrics to track."""
    REQUESTS = "requests"
    DATA_TRANSFER = "data_transfer"
    COMPUTE_TIME = "compute_time"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"


@dataclass
@dataclass
class APIKeyLimits:
    """Rate limits for an API key tier."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    data_transfer_mb_per_day: int = 100
    compute_seconds_per_day: int = 300
    concurrent_requests: int = 5
    burst_allowance: int = 10
    
    # Special limits for different endpoints
    ml_predictions_per_day: int = 100
    property_searches_per_hour: int = 200
    data_exports_per_day: int = 5
    admin_operations_per_day: int = 0  # Admin access only for enterprise+


@dataclass
class UsageRecord:
    """Usage tracking record."""
    timestamp: float
    endpoint: str
    method: str
    response_size: int = 0
    compute_time: float = 0.0
    status_code: int = 200
    user_agent: str = ""
    ip_address: str = ""


@dataclass
class DeveloperQuota:
    """Developer quota configuration."""
    developer_id: str
    monthly_request_quota: int = 50000
    monthly_data_quota_mb: int = 1000
    monthly_compute_quota_seconds: int = 3600
    current_month_requests: int = 0
    current_month_data_mb: float = 0.0
    current_month_compute_seconds: float = 0.0
    quota_reset_date: float = field(default_factory=lambda: time.time() + 30 * 24 * 3600)
    overage_allowed: bool = False
    overage_rate_multiplier: float = 0.1  # 10% of normal rate when over quota


@dataclass
class APIKey:
    """API key configuration and metadata."""
    key_id: str
    key_hash: str  # Hashed version of the actual key
    key_prefix: str  # First few characters for identification
    developer_id: str
    name: str
    description: str = ""
    tier: APIKeyTier = APIKeyTier.FREE
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    limits: APIKeyLimits = field(default_factory=APIKeyLimits)
    created_at: float = field(default_factory=time.time)
    last_used: Optional[float] = None
    expires_at: Optional[float] = None
    usage_history: deque = field(default_factory=lambda: deque(maxlen=10000))
    allowed_ips: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    
    # Usage tracking
    total_requests: int = 0
    total_data_transfer_mb: float = 0.0
    total_compute_seconds: float = 0.0


class APIKeyRateLimiter:
    """Advanced API key-based rate limiting system."""
    
    def __init__(self, redis_client=None, storage_file="api_keys_storage.pkl"):
        self.redis_client = redis_client
        self.storage_file = storage_file
        self.api_keys: Dict[str, APIKey] = {}
        self.developer_quotas: Dict[str, DeveloperQuota] = {}
        self.usage_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = Lock()
        
        # Tier configurations
        self.tier_limits = {
            APIKeyTier.FREE: APIKeyLimits(
                requests_per_minute=10,
                requests_per_hour=100,
                requests_per_day=1000,
                data_transfer_mb_per_day=10,
                compute_seconds_per_day=60,
                concurrent_requests=2,
                ml_predictions_per_day=10,
                property_searches_per_hour=20
            ),
            APIKeyTier.BASIC: APIKeyLimits(
                requests_per_minute=60,
                requests_per_hour=1000,
                requests_per_day=10000,
                data_transfer_mb_per_day=100,
                compute_seconds_per_day=300,
                concurrent_requests=5,
                ml_predictions_per_day=100,
                property_searches_per_hour=200
            ),
            APIKeyTier.PREMIUM: APIKeyLimits(
                requests_per_minute=300,
                requests_per_hour=5000,
                requests_per_day=50000,
                data_transfer_mb_per_day=1000,
                compute_seconds_per_day=1800,
                concurrent_requests=20,
                ml_predictions_per_day=1000,
                property_searches_per_hour=1000,
                data_exports_per_day=25
            ),
            APIKeyTier.ENTERPRISE: APIKeyLimits(
                requests_per_minute=1000,
                requests_per_hour=20000,
                requests_per_day=200000,
                data_transfer_mb_per_day=10000,
                compute_seconds_per_day=7200,
                concurrent_requests=50,
                ml_predictions_per_day=10000,
                property_searches_per_hour=5000,
                data_exports_per_day=100,
                admin_operations_per_day=50
            ),
            APIKeyTier.UNLIMITED: APIKeyLimits(
                requests_per_minute=10000,
                requests_per_hour=100000,
                requests_per_day=1000000,
                data_transfer_mb_per_day=100000,
                compute_seconds_per_day=86400,
                concurrent_requests=100,
                ml_predictions_per_day=100000,
                property_searches_per_hour=50000,
                data_exports_per_day=1000,
                admin_operations_per_day=1000
            )
        }
        
        # Active request tracking for concurrent limits
        self.active_requests: Dict[str, set] = defaultdict(set)
        
        # Load persisted data if Redis is not available
        if not redis_client:
            self._load_from_file()
    
    def _save_to_file(self):
        """Save API keys and quotas to file for persistence."""
        if self.redis_client:
            return  # Use Redis instead of file storage
        
        try:
            storage_path = os.path.abspath(self.storage_file)
            
            # Simple serialization using JSON instead of pickle
            api_keys_data = {}
            for k, v in self.api_keys.items():
                try:
                    key_dict = {
                        'key_id': v.key_id,
                        'key_hash': v.key_hash,
                        'key_prefix': v.key_prefix,
                        'developer_id': v.developer_id,
                        'name': v.name,
                        'description': v.description,
                        'tier': v.tier.value if hasattr(v.tier, 'value') else str(v.tier),
                        'status': v.status.value if hasattr(v.status, 'value') else str(v.status),
                        'created_at': v.created_at.isoformat() if v.created_at and hasattr(v.created_at, 'isoformat') else None,
                        'last_used': v.last_used.isoformat() if v.last_used and hasattr(v.last_used, 'isoformat') else None,
                        'expires_at': v.expires_at.isoformat() if v.expires_at and hasattr(v.expires_at, 'isoformat') else None,
                        'allowed_ips': v.allowed_ips,
                        'allowed_domains': v.allowed_domains,
                        'total_requests': v.total_requests,
                        'total_data_transfer_mb': v.total_data_transfer_mb,
                        'total_compute_seconds': v.total_compute_seconds
                    }
                    api_keys_data[k] = key_dict
                except Exception as e:
                    # Skip this key but continue with others
                    continue
            
            data = {
                'api_keys': api_keys_data,
                'developer_quotas': {k: asdict(v) for k, v in self.developer_quotas.items()}
            }
            
            # Use JSON instead of pickle for better debugging
            storage_path_json = storage_path.replace('.pkl', '.json')
            with open(storage_path_json, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save API key data to file: {e}")
    
    def _load_from_file(self):
        """Load API keys and quotas from file."""
        storage_path = os.path.abspath(self.storage_file.replace('.pkl', '.json'))
        if not os.path.exists(storage_path):
            return
        
        try:
            with open(storage_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct API keys
            for key_hash, key_data in data.get('api_keys', {}).items():
                # Convert datetime strings back to datetime objects
                if 'created_at' in key_data and key_data['created_at']:
                    key_data['created_at'] = datetime.fromisoformat(key_data['created_at'])
                if 'last_used' in key_data and key_data['last_used']:
                    key_data['last_used'] = datetime.fromisoformat(key_data['last_used'])
                if 'expires_at' in key_data and key_data['expires_at']:
                    key_data['expires_at'] = datetime.fromisoformat(key_data['expires_at'])
                
                # Convert tier string to enum
                if 'tier' in key_data and isinstance(key_data['tier'], str):
                    key_data['tier'] = APIKeyTier(key_data['tier'])
                if 'status' in key_data and isinstance(key_data['status'], str):
                    key_data['status'] = APIKeyStatus(key_data['status'])
                
                # Get limits from tier
                limits = self.tier_limits.get(key_data['tier'], self.tier_limits[APIKeyTier.FREE])
                
                api_key = APIKey(
                    key_id=key_data['key_id'],
                    key_hash=key_data['key_hash'],
                    key_prefix=key_data['key_prefix'],
                    developer_id=key_data['developer_id'],
                    name=key_data['name'],
                    description=key_data['description'],
                    tier=key_data['tier'],
                    status=key_data['status'],
                    limits=limits,
                    created_at=key_data['created_at'],
                    last_used=key_data['last_used'],
                    expires_at=key_data['expires_at'],
                    allowed_ips=key_data.get('allowed_ips', []),
                    allowed_domains=key_data.get('allowed_domains', []),
                    total_requests=key_data.get('total_requests', 0),
                    total_data_transfer_mb=key_data.get('total_data_transfer_mb', 0.0),
                    total_compute_seconds=key_data.get('total_compute_seconds', 0.0)
                )
                
                self.api_keys[key_hash] = api_key
            
            # Reconstruct developer quotas
            for dev_id, quota_data in data.get('developer_quotas', {}).items():
                self.developer_quotas[dev_id] = DeveloperQuota(**quota_data)
                
        except Exception as e:
            logging.warning(f"Failed to load API key data from file: {e}")
        
    def generate_api_key(self, developer_id: str, name: str, tier: APIKeyTier = APIKeyTier.FREE,
                        description: str = "", expires_days: Optional[int] = None,
                        allowed_ips: List[str] = None, allowed_domains: List[str] = None) -> Tuple[str, str]:
        """Generate a new API key."""
        with self.lock:
            # Generate unique key
            key_id = str(uuid.uuid4())
            raw_key = f"npai_{tier.value}_{secrets.token_urlsafe(32)}"
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
            key_prefix = raw_key[:12] + "..."
            
            # Set expiration
            expires_at = None
            if expires_days:
                expires_at = time.time() + (expires_days * 24 * 3600)
            
            # Create API key
            api_key = APIKey(
                key_id=key_id,
                key_hash=key_hash,
                key_prefix=key_prefix,
                developer_id=developer_id,
                name=name,
                description=description,
                tier=tier,
                limits=self.tier_limits[tier],
                expires_at=expires_at,
                allowed_ips=allowed_ips or [],
                allowed_domains=allowed_domains or []
            )
            
            self.api_keys[key_hash] = api_key
            
            # Initialize developer quota if not exists
            if developer_id not in self.developer_quotas:
                self.developer_quotas[developer_id] = DeveloperQuota(developer_id=developer_id)
            
            # Save to file if not using Redis
            self._save_to_file()
            
            logger.info(f"Generated API key {key_prefix} for developer {developer_id}")
            return raw_key, key_id
    
    def _hash_key(self, raw_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(raw_key.encode()).hexdigest()
    
    def validate_api_key(self, raw_key: str, ip_address: str = "", 
                        domain: str = "") -> Tuple[bool, Optional[APIKey], str]:
        """Validate an API key and check permissions."""
        if not raw_key or not raw_key.startswith("npai_"):
            return False, None, "Invalid API key format"
        
        key_hash = self._hash_key(raw_key)
        
        if key_hash not in self.api_keys:
            return False, None, "API key not found"
        
        api_key = self.api_keys[key_hash]
        
        # Check status
        if api_key.status != APIKeyStatus.ACTIVE:
            return False, api_key, f"API key is {api_key.status.value}"
        
        # Check expiration
        if api_key.expires_at and time.time() > api_key.expires_at:
            api_key.status = APIKeyStatus.EXPIRED
            return False, api_key, "API key has expired"
        
        # Check IP restrictions
        if api_key.allowed_ips and ip_address:
            if ip_address not in api_key.allowed_ips:
                return False, api_key, f"IP address {ip_address} not allowed"
        
        # Check domain restrictions
        if api_key.allowed_domains and domain:
            allowed = any(domain.endswith(allowed_domain) for allowed_domain in api_key.allowed_domains)
            if not allowed:
                return False, api_key, f"Domain {domain} not allowed"
        
        return True, api_key, "Valid"
    
    def check_rate_limit(self, raw_key: str, endpoint: str, method: str = "GET",
                        ip_address: str = "", domain: str = "", 
                        expected_compute_time: float = 0.0,
                        expected_response_size: int = 0) -> Tuple[bool, Dict[str, Any]]:
        """Check rate limits for an API key."""
        current_time = time.time()
        
        # Validate key first
        valid, api_key, message = self.validate_api_key(raw_key, ip_address, domain)
        if not valid:
            return False, {"error": message, "retry_after": 3600}
        
        key_hash = self._hash_key(raw_key)
        limits = api_key.limits
        
        # Update last used timestamp
        api_key.last_used = current_time
        
        # Check concurrent requests
        active_count = len(self.active_requests[key_hash])
        if active_count >= limits.concurrent_requests:
            return False, {
                "error": "Concurrent request limit exceeded",
                "limit": limits.concurrent_requests,
                "current": active_count,
                "retry_after": 60
            }
        
        # Check developer quota
        quota = self.developer_quotas.get(api_key.developer_id)
        if quota:
            quota_valid, quota_message = self._check_developer_quota(
                quota, expected_compute_time, expected_response_size
            )
            if not quota_valid:
                return False, {"error": quota_message, "retry_after": 3600}
        
        # Get recent usage
        recent_usage = self._get_recent_usage(api_key, current_time)
        
        # Check minute limit
        minute_requests = recent_usage['minute_requests']
        if minute_requests >= limits.requests_per_minute:
            return False, {
                "error": "Requests per minute limit exceeded",
                "limit": limits.requests_per_minute,
                "current": minute_requests,
                "retry_after": 60 - int(current_time % 60)
            }
        
        # Check hour limit
        hour_requests = recent_usage['hour_requests']
        if hour_requests >= limits.requests_per_hour:
            return False, {
                "error": "Requests per hour limit exceeded",
                "limit": limits.requests_per_hour,
                "current": hour_requests,
                "retry_after": 3600 - int(current_time % 3600)
            }
        
        # Check day limit
        day_requests = recent_usage['day_requests']
        if day_requests >= limits.requests_per_day:
            return False, {
                "error": "Requests per day limit exceeded",
                "limit": limits.requests_per_day,
                "current": day_requests,
                "retry_after": 86400 - int(current_time % 86400)
            }
        
        # Check endpoint-specific limits
        endpoint_check = self._check_endpoint_limits(api_key, endpoint, recent_usage)
        if not endpoint_check[0]:
            return False, endpoint_check[1]
        
        # Check data transfer limits
        day_data_mb = recent_usage['day_data_mb']
        if day_data_mb + (expected_response_size / 1024 / 1024) > limits.data_transfer_mb_per_day:
            return False, {
                "error": "Daily data transfer limit exceeded",
                "limit_mb": limits.data_transfer_mb_per_day,
                "current_mb": day_data_mb,
                "retry_after": 86400 - int(current_time % 86400)
            }
        
        # Check compute time limits
        day_compute = recent_usage['day_compute_seconds']
        if day_compute + expected_compute_time > limits.compute_seconds_per_day:
            return False, {
                "error": "Daily compute time limit exceeded",
                "limit_seconds": limits.compute_seconds_per_day,
                "current_seconds": day_compute,
                "retry_after": 86400 - int(current_time % 86400)
            }
        
        # All checks passed
        return True, {
            "remaining": {
                "minute": limits.requests_per_minute - minute_requests - 1,
                "hour": limits.requests_per_hour - hour_requests - 1,
                "day": limits.requests_per_day - day_requests - 1,
                "data_mb": limits.data_transfer_mb_per_day - day_data_mb,
                "compute_seconds": limits.compute_seconds_per_day - day_compute
            },
            "limits": {
                "minute": limits.requests_per_minute,
                "hour": limits.requests_per_hour,
                "day": limits.requests_per_day,
                "data_mb": limits.data_transfer_mb_per_day,
                "compute_seconds": limits.compute_seconds_per_day
            },
            "tier": api_key.tier.value
        }
    
    def _check_developer_quota(self, quota: DeveloperQuota, expected_compute: float,
                             expected_data_mb: float) -> Tuple[bool, str]:
        """Check developer monthly quota."""
        current_time = time.time()
        
        # Reset quota if month has passed
        if current_time > quota.quota_reset_date:
            quota.current_month_requests = 0
            quota.current_month_data_mb = 0.0
            quota.current_month_compute_seconds = 0.0
            quota.quota_reset_date = current_time + 30 * 24 * 3600
        
        # Check monthly request quota
        if quota.current_month_requests >= quota.monthly_request_quota:
            if not quota.overage_allowed:
                return False, "Monthly request quota exceeded"
        
        # Check monthly data quota
        if quota.current_month_data_mb + expected_data_mb > quota.monthly_data_quota_mb:
            if not quota.overage_allowed:
                return False, "Monthly data transfer quota exceeded"
        
        # Check monthly compute quota
        if quota.current_month_compute_seconds + expected_compute > quota.monthly_compute_quota_seconds:
            if not quota.overage_allowed:
                return False, "Monthly compute quota exceeded"
        
        return True, "OK"
    
    def _get_recent_usage(self, api_key: APIKey, current_time: float) -> Dict[str, Any]:
        """Get recent usage statistics for rate limiting."""
        minute_start = current_time - 60
        hour_start = current_time - 3600
        day_start = current_time - 86400
        
        minute_requests = 0
        hour_requests = 0
        day_requests = 0
        day_data_mb = 0.0
        day_compute_seconds = 0.0
        
        # Count recent usage
        for usage in api_key.usage_history:
            if hasattr(usage, 'timestamp'):
                if usage.timestamp >= minute_start:
                    minute_requests += 1
                if usage.timestamp >= hour_start:
                    hour_requests += 1
                if usage.timestamp >= day_start:
                    day_requests += 1
                    day_data_mb += usage.response_size / 1024 / 1024
                    day_compute_seconds += usage.compute_time
        
        return {
            'minute_requests': minute_requests,
            'hour_requests': hour_requests,
            'day_requests': day_requests,
            'day_data_mb': day_data_mb,
            'day_compute_seconds': day_compute_seconds
        }
    
    def _check_endpoint_limits(self, api_key: APIKey, endpoint: str,
                             recent_usage: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Check endpoint-specific rate limits."""
        limits = api_key.limits
        current_time = time.time()
        
        # Count endpoint-specific usage
        hour_start = current_time - 3600
        day_start = current_time - 86400
        
        ml_predictions_today = 0
        property_searches_hour = 0
        data_exports_today = 0
        admin_operations_today = 0
        
        for usage in api_key.usage_history:
            if hasattr(usage, 'timestamp') and hasattr(usage, 'endpoint'):
                if usage.timestamp >= day_start:
                    if 'predict' in usage.endpoint or 'ml' in usage.endpoint:
                        ml_predictions_today += 1
                    elif 'export' in usage.endpoint:
                        data_exports_today += 1
                    elif 'admin' in usage.endpoint:
                        admin_operations_today += 1
                
                if usage.timestamp >= hour_start:
                    if 'search' in usage.endpoint or 'properties' in usage.endpoint:
                        property_searches_hour += 1
        
        # Check ML prediction limits
        if 'predict' in endpoint or 'ml' in endpoint:
            if ml_predictions_today >= limits.ml_predictions_per_day:
                return False, {
                    "error": "Daily ML prediction limit exceeded",
                    "limit": limits.ml_predictions_per_day,
                    "current": ml_predictions_today,
                    "retry_after": 86400 - int(current_time % 86400)
                }
        
        # Check property search limits
        if 'search' in endpoint or 'properties' in endpoint:
            if property_searches_hour >= limits.property_searches_per_hour:
                return False, {
                    "error": "Hourly property search limit exceeded",
                    "limit": limits.property_searches_per_hour,
                    "current": property_searches_hour,
                    "retry_after": 3600 - int(current_time % 3600)
                }
        
        # Check data export limits
        if 'export' in endpoint:
            if data_exports_today >= limits.data_exports_per_day:
                return False, {
                    "error": "Daily data export limit exceeded",
                    "limit": limits.data_exports_per_day,
                    "current": data_exports_today,
                    "retry_after": 86400 - int(current_time % 86400)
                }
        
        # Check admin operation limits
        if 'admin' in endpoint:
            if admin_operations_today >= limits.admin_operations_per_day:
                return False, {
                    "error": "Daily admin operation limit exceeded",
                    "limit": limits.admin_operations_per_day,
                    "current": admin_operations_today,
                    "retry_after": 86400 - int(current_time % 86400)
                }
        
        return True, {}
    
    def record_usage(self, raw_key: str, endpoint: str, method: str,
                    response_size: int = 0, compute_time: float = 0.0,
                    status_code: int = 200, user_agent: str = "",
                    ip_address: str = "") -> bool:
        """Record API usage for tracking and analytics."""
        try:
            key_hash = self._hash_key(raw_key)
            
            if key_hash not in self.api_keys:
                return False
            
            api_key = self.api_keys[key_hash]
            current_time = time.time()
            
            # Create usage record
            usage_record = UsageRecord(
                timestamp=current_time,
                endpoint=endpoint,
                method=method,
                response_size=response_size,
                compute_time=compute_time,
                status_code=status_code,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            # Add to usage history
            api_key.usage_history.append(usage_record)
            
            # Update totals
            api_key.total_requests += 1
            api_key.total_data_transfer_mb += response_size / 1024 / 1024
            api_key.total_compute_seconds += compute_time
            
            # Update developer quota
            quota = self.developer_quotas.get(api_key.developer_id)
            if quota:
                quota.current_month_requests += 1
                quota.current_month_data_mb += response_size / 1024 / 1024
                quota.current_month_compute_seconds += compute_time
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
            return False
    
    def start_request(self, raw_key: str) -> str:
        """Mark the start of a request for concurrent tracking."""
        key_hash = self._hash_key(raw_key)
        request_id = str(uuid.uuid4())
        self.active_requests[key_hash].add(request_id)
        return request_id
    
    def end_request(self, raw_key: str, request_id: str):
        """Mark the end of a request for concurrent tracking."""
        key_hash = self._hash_key(raw_key)
        self.active_requests[key_hash].discard(request_id)
    
    def get_api_key_info(self, raw_key: str) -> Optional[Dict[str, Any]]:
        """Get information about an API key."""
        key_hash = self._hash_key(raw_key)
        
        if key_hash not in self.api_keys:
            return None
        
        api_key = self.api_keys[key_hash]
        recent_usage = self._get_recent_usage(api_key, time.time())
        
        return {
            "key_id": api_key.key_id,
            "key_prefix": api_key.key_prefix,
            "name": api_key.name,
            "description": api_key.description,
            "tier": api_key.tier.value,
            "status": api_key.status.value,
            "created_at": api_key.created_at.isoformat() if api_key.created_at and hasattr(api_key.created_at, 'isoformat') 
                          else datetime.fromtimestamp(api_key.created_at).isoformat() if api_key.created_at 
                          else None,
            "last_used": api_key.last_used.isoformat() if api_key.last_used and hasattr(api_key.last_used, 'isoformat')
                        else datetime.fromtimestamp(api_key.last_used).isoformat() if api_key.last_used
                        else None,
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at and hasattr(api_key.expires_at, 'isoformat')
                         else datetime.fromtimestamp(api_key.expires_at).isoformat() if api_key.expires_at
                         else None,
            "total_requests": api_key.total_requests,
            "total_data_transfer_mb": round(api_key.total_data_transfer_mb, 2),
            "total_compute_seconds": round(api_key.total_compute_seconds, 2),
            "current_usage": recent_usage,
            "limits": {
                "requests_per_minute": api_key.limits.requests_per_minute,
                "requests_per_hour": api_key.limits.requests_per_hour,
                "requests_per_day": api_key.limits.requests_per_day,
                "data_transfer_mb_per_day": api_key.limits.data_transfer_mb_per_day,
                "compute_seconds_per_day": api_key.limits.compute_seconds_per_day,
                "concurrent_requests": api_key.limits.concurrent_requests
            },
            "allowed_ips": api_key.allowed_ips,
            "allowed_domains": api_key.allowed_domains
        }
    
    def get_developer_quota_info(self, developer_id: str) -> Optional[Dict[str, Any]]:
        """Get developer quota information."""
        if developer_id not in self.developer_quotas:
            return None
        
        quota = self.developer_quotas[developer_id]
        
        return {
            "developer_id": quota.developer_id,
            "monthly_quotas": {
                "requests": quota.monthly_request_quota,
                "data_mb": quota.monthly_data_quota_mb,
                "compute_seconds": quota.monthly_compute_quota_seconds
            },
            "current_usage": {
                "requests": quota.current_month_requests,
                "data_mb": round(quota.current_month_data_mb, 2),
                "compute_seconds": round(quota.current_month_compute_seconds, 2)
            },
            "quota_reset_date": datetime.fromtimestamp(quota.quota_reset_date).isoformat(),
            "overage_allowed": quota.overage_allowed,
            "overage_rate_multiplier": quota.overage_rate_multiplier
        }
    
    def revoke_api_key(self, raw_key: str) -> bool:
        """Revoke an API key."""
        key_hash = self._hash_key(raw_key)
        
        if key_hash not in self.api_keys:
            return False
        
        self.api_keys[key_hash].status = APIKeyStatus.REVOKED
        self._save_to_file()
        logger.info(f"Revoked API key {self.api_keys[key_hash].key_prefix}")
        return True
    
    def suspend_api_key(self, raw_key: str) -> bool:
        """Temporarily suspend an API key."""
        key_hash = self._hash_key(raw_key)
        
        if key_hash not in self.api_keys:
            return False
        
        self.api_keys[key_hash].status = APIKeyStatus.SUSPENDED
        self._save_to_file()
        logger.info(f"Suspended API key {self.api_keys[key_hash].key_prefix}")
        return True
    
    def reactivate_api_key(self, raw_key: str) -> bool:
        """Reactivate a suspended API key."""
        key_hash = self._hash_key(raw_key)
        
        if key_hash not in self.api_keys:
            return False
        
        api_key = self.api_keys[key_hash]
        if api_key.status == APIKeyStatus.SUSPENDED:
            api_key.status = APIKeyStatus.ACTIVE
            self._save_to_file()
            logger.info(f"Reactivated API key {api_key.key_prefix}")
            return True
        
        return False
    
    def get_usage_analytics(self, developer_id: str = None, 
                          days: int = 7) -> Dict[str, Any]:
        """Get usage analytics for a developer or globally."""
        current_time = time.time()
        start_time = current_time - (days * 24 * 3600)
        
        analytics = {
            "period_days": days,
            "total_requests": 0,
            "total_data_transfer_mb": 0.0,
            "total_compute_seconds": 0.0,
            "unique_keys": 0,
            "top_endpoints": defaultdict(int),
            "requests_by_day": defaultdict(int),
            "error_rate": 0.0,
            "tier_distribution": defaultdict(int)
        }
        
        total_responses = 0
        error_responses = 0
        
        for api_key in self.api_keys.values():
            if developer_id and api_key.developer_id != developer_id:
                continue
            
            analytics["unique_keys"] += 1
            analytics["tier_distribution"][api_key.tier.value] += 1
            
            for usage in api_key.usage_history:
                if hasattr(usage, 'timestamp') and usage.timestamp >= start_time:
                    analytics["total_requests"] += 1
                    analytics["total_data_transfer_mb"] += usage.response_size / 1024 / 1024
                    analytics["total_compute_seconds"] += usage.compute_time
                    
                    # Track endpoint usage
                    analytics["top_endpoints"][usage.endpoint] += 1
                    
                    # Track daily requests
                    day_key = datetime.fromtimestamp(usage.timestamp).strftime("%Y-%m-%d")
                    analytics["requests_by_day"][day_key] += 1
                    
                    # Track error rate
                    total_responses += 1
                    if usage.status_code >= 400:
                        error_responses += 1
        
        # Calculate error rate
        if total_responses > 0:
            analytics["error_rate"] = error_responses / total_responses
        
        # Convert defaultdicts to regular dicts and sort
        analytics["top_endpoints"] = dict(sorted(analytics["top_endpoints"].items(), 
                                                key=lambda x: x[1], reverse=True)[:10])
        analytics["requests_by_day"] = dict(analytics["requests_by_day"])
        analytics["tier_distribution"] = dict(analytics["tier_distribution"])
        
        # Round numeric values
        analytics["total_data_transfer_mb"] = round(analytics["total_data_transfer_mb"], 2)
        analytics["total_compute_seconds"] = round(analytics["total_compute_seconds"], 2)
        analytics["error_rate"] = round(analytics["error_rate"], 4)
        
        return analytics
    
    def cleanup_expired_keys(self):
        """Clean up expired API keys."""
        current_time = time.time()
        expired_keys = []
        
        for key_hash, api_key in self.api_keys.items():
            if api_key.expires_at and current_time > api_key.expires_at:
                api_key.status = APIKeyStatus.EXPIRED
                expired_keys.append(key_hash)
        
        logger.info(f"Marked {len(expired_keys)} API keys as expired")
        return len(expired_keys)


# Global instance for easy access
_api_key_limiter = None

def get_api_key_limiter() -> APIKeyRateLimiter:
    """Get the global API key rate limiter instance."""
    global _api_key_limiter
    if _api_key_limiter is None:
        _api_key_limiter = APIKeyRateLimiter()
    return _api_key_limiter


# Convenience functions
def generate_api_key(developer_id: str, name: str, tier: str = "free",
                    description: str = "", expires_days: int = None) -> Tuple[str, str]:
    """Generate a new API key."""
    limiter = get_api_key_limiter()
    tier_enum = APIKeyTier(tier.lower())
    return limiter.generate_api_key(developer_id, name, tier_enum, description, expires_days)


def check_api_key_rate_limit(api_key: str, endpoint: str, method: str = "GET",
                           ip_address: str = "", domain: str = "") -> Tuple[bool, Dict[str, Any]]:
    """Check rate limits for an API key."""
    limiter = get_api_key_limiter()
    return limiter.check_rate_limit(api_key, endpoint, method, ip_address, domain)


def record_api_usage(api_key: str, endpoint: str, method: str,
                    response_size: int = 0, compute_time: float = 0.0,
                    status_code: int = 200) -> bool:
    """Record API usage."""
    limiter = get_api_key_limiter()
    return limiter.record_usage(api_key, endpoint, method, response_size, compute_time, status_code)


def get_api_key_usage_analytics(developer_id: str = None, days: int = 7) -> Dict[str, Any]:
    """Get usage analytics."""
    limiter = get_api_key_limiter()
    return limiter.get_usage_analytics(developer_id, days)
