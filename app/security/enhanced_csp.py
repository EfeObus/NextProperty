"""
Enhanced Content Security Policy (CSP) Manager for NextProperty AI.

This module provides advanced CSP management including nonce generation,
dynamic policy creation, and violation reporting.
"""

import secrets
import hashlib
import base64
import json
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from flask import request, g, current_app
import re


class CSPDirective(Enum):
    """CSP directive types."""
    DEFAULT_SRC = "default-src"
    SCRIPT_SRC = "script-src"
    STYLE_SRC = "style-src"
    IMG_SRC = "img-src"
    FONT_SRC = "font-src"
    CONNECT_SRC = "connect-src"
    FRAME_SRC = "frame-src"
    FRAME_ANCESTORS = "frame-ancestors"
    OBJECT_SRC = "object-src"
    MEDIA_SRC = "media-src"
    CHILD_SRC = "child-src"
    FORM_ACTION = "form-action"
    BASE_URI = "base-uri"
    MANIFEST_SRC = "manifest-src"
    WORKER_SRC = "worker-src"


class CSPMode(Enum):
    """CSP enforcement modes."""
    ENFORCE = "enforce"
    REPORT_ONLY = "report-only"


@dataclass
class CSPViolation:
    """CSP violation report."""
    timestamp: float
    directive: str
    blocked_uri: str
    document_uri: str
    referrer: str
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    sample: Optional[str] = None
    disposition: str = "enforce"
    effective_directive: Optional[str] = None


@dataclass
class CSPPolicy:
    """CSP policy configuration."""
    directives: Dict[CSPDirective, List[str]] = field(default_factory=dict)
    nonce: Optional[str] = None
    report_uri: Optional[str] = None
    report_to: Optional[str] = None
    mode: CSPMode = CSPMode.ENFORCE
    strict: bool = False


class EnhancedCSPManager:
    """Enhanced Content Security Policy manager with dynamic policies."""
    
    def __init__(self):
        """Initialize CSP manager."""
        self.violation_reports: List[CSPViolation] = []
        self.trusted_domains: Set[str] = set()
        self.script_hashes: Set[str] = set()
        self.style_hashes: Set[str] = set()
        self.nonce_cache: Dict[str, float] = {}
        
        # Default secure policy
        self.default_policy = CSPPolicy(
            directives={
                CSPDirective.DEFAULT_SRC: ["'self'"],
                CSPDirective.SCRIPT_SRC: ["'self'", "'strict-dynamic'"],
                CSPDirective.STYLE_SRC: ["'self'", "'unsafe-inline'"],
                CSPDirective.IMG_SRC: ["'self'", "data:", "https:"],
                CSPDirective.FONT_SRC: ["'self'", "https:"],
                CSPDirective.CONNECT_SRC: ["'self'"],
                CSPDirective.FRAME_SRC: ["'none'"],
                CSPDirective.FRAME_ANCESTORS: ["'none'"],
                CSPDirective.OBJECT_SRC: ["'none'"],
                CSPDirective.BASE_URI: ["'self'"],
                CSPDirective.FORM_ACTION: ["'self'"]
            },
            strict=True
        )
        
        # Context-specific policies
        self.context_policies = {
            'admin': self._create_admin_policy(),
            'api': self._create_api_policy(),
            'public': self._create_public_policy(),
            'upload': self._create_upload_policy()
        }

    def generate_nonce(self) -> str:
        """
        Generate a cryptographically secure nonce for CSP.
        
        Returns:
            str: Base64-encoded nonce
        """
        nonce_bytes = secrets.token_bytes(16)
        nonce = base64.b64encode(nonce_bytes).decode('ascii')
        
        # Cache nonce with timestamp for cleanup
        self.nonce_cache[nonce] = time.time()
        
        # Store in Flask g object for template access
        if not hasattr(g, 'csp_nonce'):
            g.csp_nonce = nonce
        
        return nonce

    def get_current_nonce(self) -> Optional[str]:
        """Get the current request's nonce."""
        return getattr(g, 'csp_nonce', None)

    def calculate_script_hash(self, script_content: str) -> str:
        """
        Calculate SHA256 hash for inline script content.
        
        Args:
            script_content: JavaScript content
            
        Returns:
            str: SHA256 hash in CSP format
        """
        script_bytes = script_content.encode('utf-8')
        hash_bytes = hashlib.sha256(script_bytes).digest()
        hash_b64 = base64.b64encode(hash_bytes).decode('ascii')
        return f"'sha256-{hash_b64}'"

    def calculate_style_hash(self, style_content: str) -> str:
        """
        Calculate SHA256 hash for inline style content.
        
        Args:
            style_content: CSS content
            
        Returns:
            str: SHA256 hash in CSP format
        """
        style_bytes = style_content.encode('utf-8')
        hash_bytes = hashlib.sha256(style_bytes).digest()
        hash_b64 = base64.b64encode(hash_bytes).decode('ascii')
        return f"'sha256-{hash_b64}'"

    def add_trusted_domain(self, domain: str):
        """Add a domain to the trusted domains list."""
        # Validate domain format
        if self._is_valid_domain(domain):
            self.trusted_domains.add(domain)

    def remove_trusted_domain(self, domain: str):
        """Remove a domain from the trusted domains list."""
        self.trusted_domains.discard(domain)

    def create_dynamic_policy(self, context: str = 'public', 
                            additional_sources: Optional[Dict[CSPDirective, List[str]]] = None,
                            nonce: Optional[str] = None) -> CSPPolicy:
        """
        Create a dynamic CSP policy based on context and requirements.
        
        Args:
            context: Policy context (admin, api, public, upload)
            additional_sources: Additional sources to include
            nonce: Specific nonce to use
            
        Returns:
            CSPPolicy: Generated policy
        """
        # Start with context-specific base policy
        base_policy = self.context_policies.get(context, self.default_policy)
        
        # Create new policy
        policy = CSPPolicy(
            directives=base_policy.directives.copy(),
            nonce=nonce or self.generate_nonce(),
            mode=base_policy.mode,
            strict=base_policy.strict
        )
        
        # Add nonce to script and style sources
        if policy.nonce:
            nonce_src = f"'nonce-{policy.nonce}'"
            
            if CSPDirective.SCRIPT_SRC in policy.directives:
                policy.directives[CSPDirective.SCRIPT_SRC].append(nonce_src)
            
            if CSPDirective.STYLE_SRC in policy.directives:
                policy.directives[CSPDirective.STYLE_SRC].append(nonce_src)
        
        # Add script hashes
        for script_hash in self.script_hashes:
            if CSPDirective.SCRIPT_SRC in policy.directives:
                policy.directives[CSPDirective.SCRIPT_SRC].append(script_hash)
        
        # Add style hashes
        for style_hash in self.style_hashes:
            if CSPDirective.STYLE_SRC in policy.directives:
                policy.directives[CSPDirective.STYLE_SRC].append(style_hash)
        
        # Add trusted domains
        for domain in self.trusted_domains:
            for directive in [CSPDirective.SCRIPT_SRC, CSPDirective.STYLE_SRC, 
                            CSPDirective.IMG_SRC, CSPDirective.FONT_SRC]:
                if directive in policy.directives:
                    policy.directives[directive].append(f"https://{domain}")
        
        # Merge additional sources
        if additional_sources:
            for directive, sources in additional_sources.items():
                if directive in policy.directives:
                    policy.directives[directive].extend(sources)
                else:
                    policy.directives[directive] = sources.copy()
        
        # Set report URI if configured
        if current_app and current_app.config.get('CSP_REPORT_URI'):
            policy.report_uri = current_app.config['CSP_REPORT_URI']
        
        return policy

    def policy_to_header(self, policy: CSPPolicy) -> str:
        """
        Convert CSP policy to header string.
        
        Args:
            policy: CSP policy object
            
        Returns:
            str: CSP header value
        """
        directives = []
        
        for directive, sources in policy.directives.items():
            if sources:
                directive_str = f"{directive.value} {' '.join(sources)}"
                directives.append(directive_str)
        
        # Add report URI if specified
        if policy.report_uri:
            directives.append(f"report-uri {policy.report_uri}")
        
        if policy.report_to:
            directives.append(f"report-to {policy.report_to}")
        
        return "; ".join(directives)

    def get_header_name(self, policy: CSPPolicy) -> str:
        """Get the appropriate CSP header name based on mode."""
        if policy.mode == CSPMode.REPORT_ONLY:
            return "Content-Security-Policy-Report-Only"
        else:
            return "Content-Security-Policy"

    def process_violation_report(self, report_data: Dict) -> CSPViolation:
        """
        Process a CSP violation report.
        
        Args:
            report_data: Violation report data
            
        Returns:
            CSPViolation: Processed violation
        """
        violation = CSPViolation(
            timestamp=time.time(),
            directive=report_data.get('violated-directive', ''),
            blocked_uri=report_data.get('blocked-uri', ''),
            document_uri=report_data.get('document-uri', ''),
            referrer=report_data.get('referrer', ''),
            source_file=report_data.get('source-file'),
            line_number=report_data.get('line-number'),
            column_number=report_data.get('column-number'),
            sample=report_data.get('script-sample'),
            disposition=report_data.get('disposition', 'enforce'),
            effective_directive=report_data.get('effective-directive')
        )
        
        # Store violation
        self.violation_reports.append(violation)
        
        # Log violation
        if current_app:
            current_app.logger.warning(f"CSP Violation: {violation.directive} blocked {violation.blocked_uri}")
        
        # Auto-adjust policy if needed
        self._analyze_violation(violation)
        
        return violation

    def get_violation_stats(self, time_window: int = 3600) -> Dict[str, int]:
        """
        Get violation statistics for a time window.
        
        Args:
            time_window: Time window in seconds
            
        Returns:
            Dict: Violation statistics
        """
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        recent_violations = [v for v in self.violation_reports if v.timestamp > cutoff_time]
        
        stats = {
            'total_violations': len(recent_violations),
            'by_directive': {},
            'by_domain': {},
            'blocked_uris': set()
        }
        
        for violation in recent_violations:
            # Count by directive
            directive = violation.directive
            stats['by_directive'][directive] = stats['by_directive'].get(directive, 0) + 1
            
            # Count by domain
            try:
                from urllib.parse import urlparse
                domain = urlparse(violation.blocked_uri).netloc
                if domain:
                    stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
            except:
                pass
            
            # Collect blocked URIs
            stats['blocked_uris'].add(violation.blocked_uri)
        
        # Convert set to list for JSON serialization
        stats['blocked_uris'] = list(stats['blocked_uris'])
        
        return stats

    def _create_admin_policy(self) -> CSPPolicy:
        """Create CSP policy for admin pages."""
        return CSPPolicy(
            directives={
                CSPDirective.DEFAULT_SRC: ["'self'"],
                CSPDirective.SCRIPT_SRC: ["'self'", "'strict-dynamic'"],
                CSPDirective.STYLE_SRC: ["'self'", "'unsafe-inline'"],
                CSPDirective.IMG_SRC: ["'self'", "data:"],
                CSPDirective.FONT_SRC: ["'self'"],
                CSPDirective.CONNECT_SRC: ["'self'"],
                CSPDirective.FRAME_SRC: ["'none'"],
                CSPDirective.FRAME_ANCESTORS: ["'none'"],
                CSPDirective.OBJECT_SRC: ["'none'"],
                CSPDirective.BASE_URI: ["'self'"],
                CSPDirective.FORM_ACTION: ["'self'"]
            },
            strict=True
        )

    def _create_api_policy(self) -> CSPPolicy:
        """Create CSP policy for API endpoints."""
        return CSPPolicy(
            directives={
                CSPDirective.DEFAULT_SRC: ["'none'"],
                CSPDirective.SCRIPT_SRC: ["'none'"],
                CSPDirective.STYLE_SRC: ["'none'"],
                CSPDirective.IMG_SRC: ["'none'"],
                CSPDirective.FONT_SRC: ["'none'"],
                CSPDirective.CONNECT_SRC: ["'self'"],
                CSPDirective.FRAME_SRC: ["'none'"],
                CSPDirective.FRAME_ANCESTORS: ["'none'"],
                CSPDirective.OBJECT_SRC: ["'none'"],
                CSPDirective.BASE_URI: ["'none'"],
                CSPDirective.FORM_ACTION: ["'none'"]
            },
            strict=True
        )

    def _create_public_policy(self) -> CSPPolicy:
        """Create CSP policy for public pages."""
        return CSPPolicy(
            directives={
                CSPDirective.DEFAULT_SRC: ["'self'"],
                CSPDirective.SCRIPT_SRC: [
                    "'self'",
                    "'strict-dynamic'",
                    "https://cdn.jsdelivr.net",
                    "https://cdnjs.cloudflare.com",
                    "https://unpkg.com"
                ],
                CSPDirective.STYLE_SRC: [
                    "'self'",
                    "'unsafe-inline'",
                    "https://cdn.jsdelivr.net",
                    "https://cdnjs.cloudflare.com",
                    "https://fonts.googleapis.com"
                ],
                CSPDirective.IMG_SRC: ["'self'", "data:", "https:"],
                CSPDirective.FONT_SRC: [
                    "'self'",
                    "https://fonts.gstatic.com",
                    "https://cdnjs.cloudflare.com"
                ],
                CSPDirective.CONNECT_SRC: ["'self'"],
                CSPDirective.FRAME_SRC: ["'self'"],
                CSPDirective.FRAME_ANCESTORS: ["'self'"],
                CSPDirective.OBJECT_SRC: ["'none'"],
                CSPDirective.BASE_URI: ["'self'"],
                CSPDirective.FORM_ACTION: ["'self'"]
            },
            strict=False
        )

    def _create_upload_policy(self) -> CSPPolicy:
        """Create CSP policy for file upload pages."""
        return CSPPolicy(
            directives={
                CSPDirective.DEFAULT_SRC: ["'self'"],
                CSPDirective.SCRIPT_SRC: ["'self'", "'strict-dynamic'"],
                CSPDirective.STYLE_SRC: ["'self'", "'unsafe-inline'"],
                CSPDirective.IMG_SRC: ["'self'", "data:", "blob:"],
                CSPDirective.FONT_SRC: ["'self'"],
                CSPDirective.CONNECT_SRC: ["'self'"],
                CSPDirective.FRAME_SRC: ["'none'"],
                CSPDirective.FRAME_ANCESTORS: ["'none'"],
                CSPDirective.OBJECT_SRC: ["'none'"],
                CSPDirective.BASE_URI: ["'self'"],
                CSPDirective.FORM_ACTION: ["'self'"]
            },
            strict=True
        )

    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format."""
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(domain_pattern.match(domain)) and len(domain) <= 253

    def _analyze_violation(self, violation: CSPViolation):
        """Analyze violation for potential policy adjustments."""
        # Check if this is a legitimate resource that should be allowed
        blocked_uri = violation.blocked_uri
        
        # Skip analysis for obvious attacks
        attack_indicators = ['javascript:', 'data:text/html', 'eval(', 'alert(']
        if any(indicator in blocked_uri.lower() for indicator in attack_indicators):
            return
        
        # Auto-whitelist common legitimate resources
        legitimate_domains = [
            'googleapis.com', 'gstatic.com', 'jsdelivr.net',
            'cdnjs.cloudflare.com', 'unpkg.com'
        ]
        
        try:
            from urllib.parse import urlparse
            parsed_uri = urlparse(blocked_uri)
            domain = parsed_uri.netloc
            
            if any(legit_domain in domain for legit_domain in legitimate_domains):
                # This might be a legitimate resource
                if current_app:
                    current_app.logger.info(f"Potential legitimate resource blocked: {blocked_uri}")
        except:
            pass

    def cleanup_old_data(self, max_age: int = 86400):
        """Clean up old violation reports and nonces."""
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        # Clean violation reports
        self.violation_reports = [
            v for v in self.violation_reports if v.timestamp > cutoff_time
        ]
        
        # Clean nonce cache
        self.nonce_cache = {
            nonce: timestamp for nonce, timestamp in self.nonce_cache.items()
            if timestamp > cutoff_time
        }

    def export_policy_config(self) -> Dict:
        """Export current policy configuration."""
        return {
            'default_policy': {
                'directives': {
                    directive.value: sources
                    for directive, sources in self.default_policy.directives.items()
                },
                'strict': self.default_policy.strict
            },
            'trusted_domains': list(self.trusted_domains),
            'script_hashes': list(self.script_hashes),
            'style_hashes': list(self.style_hashes),
            'context_policies': {
                context: {
                    'directives': {
                        directive.value: sources
                        for directive, sources in policy.directives.items()
                    },
                    'strict': policy.strict
                }
                for context, policy in self.context_policies.items()
            }
        }

    def import_policy_config(self, config: Dict):
        """Import policy configuration."""
        # Import trusted domains
        if 'trusted_domains' in config:
            self.trusted_domains = set(config['trusted_domains'])
        
        # Import hashes
        if 'script_hashes' in config:
            self.script_hashes = set(config['script_hashes'])
        
        if 'style_hashes' in config:
            self.style_hashes = set(config['style_hashes'])


# Global instance
csp_manager = EnhancedCSPManager()
