"""
Enhanced Security Integration Module for NextProperty AI.

This module integrates all advanced security features with the existing
security infrastructure, providing a unified security layer.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import json
from flask import request, g, current_app, session
from functools import wraps

# Import existing security modules
from app.security.middleware import XSSProtection, CSRFProtection, security_middleware
from app.security.config import XSS_SETTINGS, CSRF_SETTINGS, CSP_SETTINGS

# Import new enhanced modules
from .advanced_xss import advanced_xss, ThreatLevel, Context, ThreatAnalysis
from .behavioral_analysis import behavioral_analyzer, BehaviorAnalysis, BehaviorPattern
from .enhanced_csp import csp_manager, CSPPolicy, CSPMode, CSPDirective
from .advanced_validation import advanced_validator, ValidationResult, InputType, ValidationReport


class SecurityLevel(Enum):
    """Security enforcement levels."""
    MINIMAL = 1
    STANDARD = 2
    ENHANCED = 3
    MAXIMUM = 4


@dataclass
class SecurityConfig:
    """Security configuration for different contexts."""
    level: SecurityLevel
    enable_behavioral_analysis: bool = True
    enable_advanced_xss: bool = True
    enable_enhanced_csp: bool = True
    enable_advanced_validation: bool = True
    block_critical_threats: bool = True
    rate_limit_suspicious: bool = True
    log_all_attempts: bool = False


@dataclass
class ComprehensiveSecurityReport:
    """Comprehensive security analysis report."""
    timestamp: float
    request_id: str
    ip_address: str
    user_agent: str
    
    # Analysis results
    xss_analysis: Optional[ThreatAnalysis] = None
    behavior_analysis: Optional[BehaviorAnalysis] = None
    validation_reports: Dict[str, ValidationReport] = None
    csp_violations: List[str] = None
    
    # Overall assessment
    overall_threat_level: ThreatLevel = ThreatLevel.LOW
    recommendation: str = ""
    actions_taken: List[str] = None
    
    # Performance metrics
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.actions_taken is None:
            self.actions_taken = []
        if self.validation_reports is None:
            self.validation_reports = {}
        if self.csp_violations is None:
            self.csp_violations = []


class EnhancedSecurityManager:
    """Enhanced security manager integrating all security features."""
    
    def __init__(self):
        """Initialize enhanced security manager."""
        self.security_reports = []
        self.blocked_ips = set()
        self.rate_limited_ips = {}
        
        # Security configurations for different contexts
        self.context_configs = {
            'public': SecurityConfig(
                level=SecurityLevel.STANDARD,
                enable_behavioral_analysis=True,
                enable_advanced_xss=True,
                enable_enhanced_csp=True,
                log_all_attempts=False
            ),
            'admin': SecurityConfig(
                level=SecurityLevel.MAXIMUM,
                enable_behavioral_analysis=True,
                enable_advanced_xss=True,
                enable_enhanced_csp=True,
                log_all_attempts=True
            ),
            'api': SecurityConfig(
                level=SecurityLevel.ENHANCED,
                enable_behavioral_analysis=True,
                enable_advanced_xss=True,
                enable_enhanced_csp=False,  # APIs don't need CSP
                log_all_attempts=True
            ),
            'upload': SecurityConfig(
                level=SecurityLevel.MAXIMUM,
                enable_behavioral_analysis=True,
                enable_advanced_xss=True,
                enable_enhanced_csp=True,
                log_all_attempts=True
            )
        }

    def analyze_request(self, context: str = 'public') -> ComprehensiveSecurityReport:
        """
        Perform comprehensive security analysis on current request.
        
        Args:
            context: Security context (public, admin, api, upload)
            
        Returns:
            ComprehensiveSecurityReport: Detailed security analysis
        """
        start_time = time.time()
        
        # Get security configuration for context
        config = self.context_configs.get(context, self.context_configs['public'])
        
        # Generate unique request ID
        request_id = self._generate_request_id()
        
        # Extract request information
        ip_address = request.remote_addr if request else 'unknown'
        user_agent = request.headers.get('User-Agent', 'unknown') if request else 'unknown'
        
        # Initialize report
        report = ComprehensiveSecurityReport(
            timestamp=time.time(),
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Check if IP is already blocked
        if ip_address in self.blocked_ips:
            report.overall_threat_level = ThreatLevel.CRITICAL
            report.recommendation = "BLOCKED: IP address is on blocklist"
            report.actions_taken.append("request_blocked")
            return report
        
        # 1. Behavioral Analysis
        if config.enable_behavioral_analysis:
            try:
                report.behavior_analysis = behavioral_analyzer.analyze_request()
                
                # Handle behavioral threats
                if report.behavior_analysis.should_block:
                    self.blocked_ips.add(ip_address)
                    report.actions_taken.append("ip_blocked_behavioral")
                    
                elif report.behavior_analysis.should_rate_limit:
                    self._apply_rate_limit(ip_address)
                    report.actions_taken.append("rate_limited")
                    
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Behavioral analysis error: {e}")
        
        # 2. Advanced XSS Analysis
        if config.enable_advanced_xss and request:
            try:
                # Analyze form data
                if request.form:
                    for key, value in request.form.items():
                        analysis = advanced_xss.analyze_content(value, Context.HTML)
                        if analysis.threat_level.value >= ThreatLevel.HIGH.value:
                            report.xss_analysis = analysis
                            break
                
                # Analyze JSON data
                if request.is_json:
                    json_data = request.get_json(silent=True)
                    if json_data:
                        content = json.dumps(json_data)
                        analysis = advanced_xss.analyze_content(content, Context.JSON)
                        if analysis.threat_level.value >= ThreatLevel.HIGH.value:
                            report.xss_analysis = analysis
                
                # Handle XSS threats
                if report.xss_analysis and report.xss_analysis.blocked:
                    report.actions_taken.append("xss_blocked")
                    
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Advanced XSS analysis error: {e}")
        
        # 3. Advanced Input Validation
        if config.enable_advanced_validation and request:
            try:
                inputs_to_validate = {}
                
                # Collect all inputs
                if request.form:
                    inputs_to_validate.update(request.form.to_dict())
                if request.args:
                    inputs_to_validate.update(request.args.to_dict())
                if request.is_json:
                    json_data = request.get_json(silent=True)
                    if json_data:
                        inputs_to_validate.update(self._flatten_dict(json_data))
                
                # Validate inputs
                if inputs_to_validate:
                    report.validation_reports = advanced_validator.batch_validate(inputs_to_validate)
                    
                    # Check for critical validation failures
                    for field, validation in report.validation_reports.items():
                        if validation.result == ValidationResult.BLOCKED:
                            report.actions_taken.append(f"input_blocked_{field}")
                            
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Advanced validation error: {e}")
        
        # 4. Enhanced CSP Management
        if config.enable_enhanced_csp and request and request.endpoint:
            try:
                # Generate CSP policy for this request
                csp_policy = csp_manager.create_dynamic_policy(context)
                
                # Store CSP policy in g for response headers
                g.csp_policy = csp_policy
                
                # Check for recent CSP violations
                violation_stats = csp_manager.get_violation_stats(300)  # Last 5 minutes
                if violation_stats['total_violations'] > 10:
                    report.csp_violations.append("high_violation_rate")
                    
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Enhanced CSP error: {e}")
        
        # 5. Determine Overall Threat Level
        report.overall_threat_level = self._calculate_overall_threat_level(report)
        
        # 6. Generate Recommendation
        report.recommendation = self._generate_comprehensive_recommendation(report, config)
        
        # 7. Apply Security Actions
        self._apply_security_actions(report, config)
        
        # Calculate processing time
        report.processing_time = time.time() - start_time
        
        # Store report
        self.security_reports.append(report)
        
        # Log if required
        if config.log_all_attempts or report.overall_threat_level.value >= ThreatLevel.MEDIUM.value:
            self._log_security_event(report)
        
        return report

    def validate_file_upload(self, file_content: bytes, filename: str, 
                           context: str = 'upload') -> ComprehensiveSecurityReport:
        """
        Validate file upload for security threats.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            context: Upload context
            
        Returns:
            ComprehensiveSecurityReport: Security analysis results
        """
        start_time = time.time()
        
        # Initialize report
        report = ComprehensiveSecurityReport(
            timestamp=time.time(),
            request_id=self._generate_request_id(),
            ip_address=request.remote_addr if request else 'unknown',
            user_agent=request.headers.get('User-Agent', 'unknown') if request else 'unknown'
        )
        
        try:
            # Analyze file content with advanced XSS detection
            report.xss_analysis = advanced_xss.validate_file_content(file_content, filename)
            
            # Validate filename
            filename_report = advanced_validator.validate_input(filename, InputType.FILE_NAME)
            report.validation_reports['filename'] = filename_report
            
            # Additional file-specific checks
            if filename.lower().endswith(('.html', '.htm', '.js', '.css', '.svg')):
                # These file types need extra scrutiny
                try:
                    text_content = file_content.decode('utf-8', errors='ignore')
                    content_analysis = advanced_xss.analyze_content(text_content, Context.HTML)
                    
                    if content_analysis.threat_level.value > report.xss_analysis.threat_level.value:
                        report.xss_analysis = content_analysis
                        
                except Exception:
                    pass
            
            # Determine overall threat level
            report.overall_threat_level = self._calculate_overall_threat_level(report)
            
            # Generate recommendation
            config = self.context_configs.get(context, self.context_configs['upload'])
            report.recommendation = self._generate_comprehensive_recommendation(report, config)
            
            # Apply actions
            if report.overall_threat_level == ThreatLevel.CRITICAL:
                report.actions_taken.append("file_upload_blocked")
            elif report.overall_threat_level == ThreatLevel.HIGH:
                report.actions_taken.append("file_upload_quarantined")
            
        except Exception as e:
            if current_app:
                current_app.logger.error(f"File validation error: {e}")
            
            # Err on the side of caution
            report.overall_threat_level = ThreatLevel.HIGH
            report.recommendation = "REJECT: File validation failed"
            report.actions_taken.append("file_validation_error")
        
        report.processing_time = time.time() - start_time
        return report

    def create_security_decorator(self, context: str = 'public', 
                                block_on_threat: bool = True):
        """
        Create a decorator for route protection.
        
        Args:
            context: Security context
            block_on_threat: Whether to block on high threats
            
        Returns:
            Decorator function
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Perform security analysis
                report = self.analyze_request(context)
                
                # Store report in g for access in route
                g.security_report = report
                
                # Block if threat level is critical or high (depending on config)
                if block_on_threat:
                    if report.overall_threat_level == ThreatLevel.CRITICAL:
                        from flask import abort
                        abort(403)
                    elif (report.overall_threat_level == ThreatLevel.HIGH and 
                          context in ['admin', 'upload']):
                        from flask import abort
                        abort(403)
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())[:8]

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, str]:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, str(v)))
        return dict(items)

    def _apply_rate_limit(self, ip_address: str):
        """Apply rate limiting to IP address."""
        current_time = time.time()
        self.rate_limited_ips[ip_address] = current_time + 300  # 5 minutes

    def _calculate_overall_threat_level(self, report: ComprehensiveSecurityReport) -> ThreatLevel:
        """Calculate overall threat level from all analyses."""
        max_threat = ThreatLevel.LOW
        
        # Check XSS analysis
        if report.xss_analysis:
            max_threat = max(max_threat, report.xss_analysis.threat_level, key=lambda x: x.value)
        
        # Check behavioral analysis
        if report.behavior_analysis:
            if report.behavior_analysis.should_block:
                max_threat = max(max_threat, ThreatLevel.CRITICAL, key=lambda x: x.value)
            elif report.behavior_analysis.should_rate_limit:
                max_threat = max(max_threat, ThreatLevel.HIGH, key=lambda x: x.value)
            elif report.behavior_analysis.risk_score >= 3.0:
                max_threat = max(max_threat, ThreatLevel.MEDIUM, key=lambda x: x.value)
        
        # Check validation reports
        if report.validation_reports:
            for validation in report.validation_reports.values():
                if validation.result == ValidationResult.BLOCKED:
                    max_threat = max(max_threat, ThreatLevel.CRITICAL, key=lambda x: x.value)
                elif validation.result == ValidationResult.MALICIOUS:
                    max_threat = max(max_threat, ThreatLevel.HIGH, key=lambda x: x.value)
                elif validation.result == ValidationResult.SUSPICIOUS:
                    max_threat = max(max_threat, ThreatLevel.MEDIUM, key=lambda x: x.value)
        
        return max_threat

    def _generate_comprehensive_recommendation(self, report: ComprehensiveSecurityReport, 
                                             config: SecurityConfig) -> str:
        """Generate comprehensive security recommendation."""
        if report.overall_threat_level == ThreatLevel.CRITICAL:
            return "BLOCK: Critical security threat detected - immediate blocking required"
        elif report.overall_threat_level == ThreatLevel.HIGH:
            return "REJECT: High-risk request detected - should be rejected or quarantined"
        elif report.overall_threat_level == ThreatLevel.MEDIUM:
            return "SANITIZE: Medium-risk request - sanitize inputs and apply enhanced monitoring"
        else:
            return "ALLOW: Request appears safe - normal processing with standard monitoring"

    def _apply_security_actions(self, report: ComprehensiveSecurityReport, 
                               config: SecurityConfig):
        """Apply security actions based on analysis."""
        if config.block_critical_threats and report.overall_threat_level == ThreatLevel.CRITICAL:
            self.blocked_ips.add(report.ip_address)
            report.actions_taken.append("ip_blocked")
        
        if config.rate_limit_suspicious and report.overall_threat_level == ThreatLevel.HIGH:
            self._apply_rate_limit(report.ip_address)
            report.actions_taken.append("rate_limited")

    def _log_security_event(self, report: ComprehensiveSecurityReport):
        """Log security event."""
        log_data = {
            'timestamp': report.timestamp,
            'request_id': report.request_id,
            'ip_address': report.ip_address,
            'threat_level': report.overall_threat_level.name,
            'recommendation': report.recommendation,
            'actions_taken': report.actions_taken,
            'processing_time': report.processing_time
        }
        
        if current_app:
            if report.overall_threat_level.value >= ThreatLevel.HIGH.value:
                current_app.logger.error(f"High security threat: {log_data}")
            else:
                current_app.logger.warning(f"Security event: {log_data}")

    def get_security_metrics(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get security metrics for monitoring."""
        current_time = time.time()
        cutoff_time = current_time - time_window
        
        recent_reports = [r for r in self.security_reports if r.timestamp > cutoff_time]
        
        metrics = {
            'total_requests': len(recent_reports),
            'blocked_requests': len([r for r in recent_reports if ThreatLevel.CRITICAL in [r.overall_threat_level]]),
            'high_risk_requests': len([r for r in recent_reports if r.overall_threat_level == ThreatLevel.HIGH]),
            'medium_risk_requests': len([r for r in recent_reports if r.overall_threat_level == ThreatLevel.MEDIUM]),
            'safe_requests': len([r for r in recent_reports if r.overall_threat_level == ThreatLevel.LOW]),
            'blocked_ips': len(self.blocked_ips),
            'rate_limited_ips': len([ip for ip, expiry in self.rate_limited_ips.items() if expiry > current_time]),
            'avg_processing_time': sum(r.processing_time for r in recent_reports) / len(recent_reports) if recent_reports else 0.0,
            'threat_level_distribution': {
                level.name: len([r for r in recent_reports if r.overall_threat_level == level])
                for level in ThreatLevel
            }
        }
        
        return metrics

    def cleanup_old_data(self, max_age: int = 86400):
        """Clean up old security data."""
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        # Clean security reports
        self.security_reports = [r for r in self.security_reports if r.timestamp > cutoff_time]
        
        # Clean rate limit data
        self.rate_limited_ips = {
            ip: expiry for ip, expiry in self.rate_limited_ips.items()
            if expiry > current_time
        }
        
        # Clean other modules
        behavioral_analyzer.cleanup_old_data(max_age)
        csp_manager.cleanup_old_data(max_age)


# Global instance
enhanced_security = EnhancedSecurityManager()

# Decorators for easy use
def enhanced_security_protect(context: str = 'public', block_on_threat: bool = True):
    """Enhanced security protection decorator."""
    return enhanced_security.create_security_decorator(context, block_on_threat)

def admin_security_protect(f):
    """Admin-specific security protection."""
    return enhanced_security.create_security_decorator('admin', True)(f)

def api_security_protect(f):
    """API-specific security protection."""
    return enhanced_security.create_security_decorator('api', True)(f)

def upload_security_protect(f):
    """Upload-specific security protection."""
    return enhanced_security.create_security_decorator('upload', True)(f)
