"""
Behavioral Analysis Module for Advanced XSS Detection.

This module implements behavioral analysis techniques to detect sophisticated
XSS attacks that might evade traditional pattern-based detection.
"""

import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import re
from flask import request, session, g
import numpy as np


class BehaviorPattern(Enum):
    """Behavioral patterns that indicate potential threats."""
    RAPID_REQUESTS = "rapid_requests"
    PATTERN_PROBING = "pattern_probing"
    ENCODING_EVASION = "encoding_evasion"
    PARAMETER_POLLUTION = "parameter_pollution"
    SESSION_ANOMALY = "session_anomaly"
    SCRIPT_INJECTION_ATTEMPTS = "script_injection_attempts"
    DOM_MANIPULATION = "dom_manipulation"
    SOCIAL_ENGINEERING = "social_engineering"


@dataclass
class RequestSignature:
    """Signature of a request for behavioral analysis."""
    timestamp: float
    ip_address: str
    user_agent: str
    url: str
    method: str
    parameters: Dict[str, str]
    headers: Dict[str, str]
    content_hash: str
    suspicious_score: float = 0.0
    patterns_detected: List[str] = field(default_factory=list)


@dataclass
class BehaviorAnalysis:
    """Result of behavioral analysis."""
    risk_score: float
    patterns_detected: List[BehaviorPattern]
    anomalies: List[str]
    recommendation: str
    should_block: bool = False
    should_rate_limit: bool = False


class BehavioralAnalyzer:
    """Behavioral analysis system for XSS attack detection."""
    
    def __init__(self, window_size: int = 300, max_requests: int = 1000):
        """
        Initialize behavioral analyzer.
        
        Args:
            window_size: Time window in seconds for analysis
            max_requests: Maximum requests to keep in memory per IP
        """
        self.window_size = window_size
        self.max_requests = max_requests
        
        # Request tracking by IP
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_requests))
        
        # Pattern tracking
        self.pattern_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # Session tracking
        self.session_signatures: Dict[str, Set[str]] = defaultdict(set)
        
        # Known attack patterns
        self.attack_patterns = {
            'encoding_variants': [
                'script', '%73%63%72%69%70%74', '&#115;&#99;&#114;&#105;&#112;&#116;',
                '&lt;script&gt;', '%3Cscript%3E', '\\u0073\\u0063\\u0072\\u0069\\u0070\\u0074'
            ],
            'obfuscation_techniques': [
                'eval', 'setTimeout', 'setInterval', 'Function', 'execScript',
                'fromCharCode', 'unescape', 'decodeURI', 'decodeURIComponent'
            ],
            'dom_properties': [
                'innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write',
                'document.writeln', 'location.href', 'window.location'
            ]
        }
        
        # Baseline metrics for anomaly detection
        self.baselines = {
            'avg_request_interval': 5.0,  # seconds
            'avg_parameter_count': 5,
            'avg_parameter_length': 50,
            'common_user_agents': set(),
            'common_request_patterns': set()
        }

    def analyze_request(self, request_data: Optional[Dict] = None) -> BehaviorAnalysis:
        """
        Analyze current request for behavioral anomalies.
        
        Args:
            request_data: Optional request data, uses Flask request if None
            
        Returns:
            BehaviorAnalysis: Analysis results
        """
        if request_data is None:
            if not request:
                return BehaviorAnalysis(0.0, [], [], "No request context")
            request_data = self._extract_request_data()
        
        signature = self._create_request_signature(request_data)
        
        # Add to history
        self.request_history[signature.ip_address].append(signature)
        
        # Perform behavioral analysis
        risk_score = 0.0
        patterns_detected = []
        anomalies = []
        
        # 1. Rapid request analysis
        rapid_score, rapid_patterns = self._analyze_rapid_requests(signature.ip_address)
        risk_score += rapid_score
        patterns_detected.extend(rapid_patterns)
        
        # 2. Pattern probing analysis
        probing_score, probing_patterns = self._analyze_pattern_probing(signature)
        risk_score += probing_score
        patterns_detected.extend(probing_patterns)
        
        # 3. Encoding evasion analysis
        evasion_score, evasion_patterns = self._analyze_encoding_evasion(signature)
        risk_score += evasion_score
        patterns_detected.extend(evasion_patterns)
        
        # 4. Parameter pollution analysis
        pollution_score, pollution_patterns = self._analyze_parameter_pollution(signature)
        risk_score += pollution_score
        patterns_detected.extend(pollution_patterns)
        
        # 5. Session anomaly analysis
        session_score, session_anomalies = self._analyze_session_anomalies(signature)
        risk_score += session_score
        anomalies.extend(session_anomalies)
        
        # 6. Content analysis
        content_score, content_patterns = self._analyze_content_patterns(signature)
        risk_score += content_score
        patterns_detected.extend(content_patterns)
        
        # Determine recommendation
        recommendation = self._generate_recommendation(risk_score, patterns_detected)
        
        # Determine actions
        should_block = risk_score >= 8.0
        should_rate_limit = risk_score >= 5.0
        
        return BehaviorAnalysis(
            risk_score=risk_score,
            patterns_detected=[BehaviorPattern(p) for p in set(patterns_detected)],
            anomalies=anomalies,
            recommendation=recommendation,
            should_block=should_block,
            should_rate_limit=should_rate_limit
        )

    def _extract_request_data(self) -> Dict:
        """Extract data from Flask request object."""
        return {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'url': request.url,
            'method': request.method,
            'parameters': dict(request.args) if request.args else {},
            'form_data': dict(request.form) if request.form else {},
            'json_data': request.get_json() if request.is_json else {},
            'headers': dict(request.headers),
            'cookies': dict(request.cookies) if request.cookies else {}
        }

    def _create_request_signature(self, request_data: Dict) -> RequestSignature:
        """Create a signature for the request."""
        # Combine all parameters
        all_params = {}
        all_params.update(request_data.get('parameters', {}))
        all_params.update(request_data.get('form_data', {}))
        if request_data.get('json_data'):
            all_params.update(self._flatten_json(request_data['json_data']))
        
        # Create content hash
        content_str = json.dumps(all_params, sort_keys=True)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        
        return RequestSignature(
            timestamp=time.time(),
            ip_address=request_data.get('ip_address', 'unknown'),
            user_agent=request_data.get('user_agent', ''),
            url=request_data.get('url', ''),
            method=request_data.get('method', 'GET'),
            parameters=all_params,
            headers=request_data.get('headers', {}),
            content_hash=content_hash
        )

    def _flatten_json(self, data: Dict, prefix: str = '') -> Dict[str, str]:
        """Flatten nested JSON data."""
        result = {}
        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten_json(value, new_key))
            else:
                result[new_key] = str(value)
        return result

    def _analyze_rapid_requests(self, ip_address: str) -> Tuple[float, List[str]]:
        """Analyze for rapid request patterns."""
        history = self.request_history[ip_address]
        if len(history) < 2:
            return 0.0, []
        
        current_time = time.time()
        recent_requests = [r for r in history if current_time - r.timestamp <= 60]  # Last minute
        
        patterns = []
        score = 0.0
        
        # Check request frequency
        if len(recent_requests) > 50:  # More than 50 requests per minute
            score += 3.0
            patterns.append(BehaviorPattern.RAPID_REQUESTS.value)
        elif len(recent_requests) > 20:  # More than 20 requests per minute
            score += 1.5
            patterns.append(BehaviorPattern.RAPID_REQUESTS.value)
        
        # Check for burst patterns
        if len(recent_requests) >= 5:
            intervals = []
            for i in range(1, len(recent_requests)):
                interval = recent_requests[i].timestamp - recent_requests[i-1].timestamp
                intervals.append(interval)
            
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval < 0.5:  # Requests less than 0.5 seconds apart
                score += 2.0
                patterns.append(BehaviorPattern.RAPID_REQUESTS.value)
        
        return score, patterns

    def _analyze_pattern_probing(self, signature: RequestSignature) -> Tuple[float, List[str]]:
        """Analyze for systematic pattern probing."""
        ip_history = self.request_history[signature.ip_address]
        
        patterns = []
        score = 0.0
        
        # Check for systematic parameter testing
        tested_patterns = set()
        for req in ip_history:
            for param_value in req.parameters.values():
                if any(pattern in param_value.lower() for pattern_group in self.attack_patterns.values() 
                       for pattern in pattern_group):
                    tested_patterns.add(param_value.lower())
        
        # If multiple attack patterns tested, likely probing
        if len(tested_patterns) > 5:
            score += 2.5
            patterns.append(BehaviorPattern.PATTERN_PROBING.value)
        elif len(tested_patterns) > 2:
            score += 1.0
            patterns.append(BehaviorPattern.PATTERN_PROBING.value)
        
        # Check for URL fuzzing
        urls_tested = set(req.url for req in ip_history)
        if len(urls_tested) > 20:  # Testing many different URLs
            score += 1.5
            patterns.append(BehaviorPattern.PATTERN_PROBING.value)
        
        return score, patterns

    def _analyze_encoding_evasion(self, signature: RequestSignature) -> Tuple[float, List[str]]:
        """Analyze for encoding evasion techniques."""
        patterns = []
        score = 0.0
        
        # Check all parameter values for encoding evasion
        for param_value in signature.parameters.values():
            if not isinstance(param_value, str):
                continue
            
            # URL encoding evasion
            if re.search(r'%[0-9a-f]{2}', param_value, re.IGNORECASE):
                decoded = self._url_decode(param_value)
                if self._contains_attack_patterns(decoded):
                    score += 2.0
                    patterns.append(BehaviorPattern.ENCODING_EVASION.value)
            
            # HTML entity encoding evasion
            if re.search(r'&#\d+;|&#x[0-9a-f]+;', param_value, re.IGNORECASE):
                decoded = self._html_decode(param_value)
                if self._contains_attack_patterns(decoded):
                    score += 2.0
                    patterns.append(BehaviorPattern.ENCODING_EVASION.value)
            
            # Unicode evasion
            if re.search(r'\\u[0-9a-f]{4}', param_value, re.IGNORECASE):
                try:
                    decoded = param_value.encode().decode('unicode_escape')
                    if self._contains_attack_patterns(decoded):
                        score += 2.0
                        patterns.append(BehaviorPattern.ENCODING_EVASION.value)
                except:
                    pass
            
            # Base64 evasion
            if re.search(r'[A-Za-z0-9+/]{10,}={0,2}', param_value):
                try:
                    import base64
                    decoded = base64.b64decode(param_value).decode('utf-8', errors='ignore')
                    if self._contains_attack_patterns(decoded):
                        score += 2.5
                        patterns.append(BehaviorPattern.ENCODING_EVASION.value)
                except:
                    pass
        
        return score, patterns

    def _analyze_parameter_pollution(self, signature: RequestSignature) -> Tuple[float, List[str]]:
        """Analyze for parameter pollution attacks."""
        patterns = []
        score = 0.0
        
        # Check for excessive parameters
        if len(signature.parameters) > 50:
            score += 2.0
            patterns.append(BehaviorPattern.PARAMETER_POLLUTION.value)
        elif len(signature.parameters) > 20:
            score += 1.0
            patterns.append(BehaviorPattern.PARAMETER_POLLUTION.value)
        
        # Check for duplicate parameter names with different values
        param_names = list(signature.parameters.keys())
        unique_names = set(param_names)
        if len(param_names) != len(unique_names):
            score += 1.5
            patterns.append(BehaviorPattern.PARAMETER_POLLUTION.value)
        
        # Check for suspiciously long parameter values
        for param_value in signature.parameters.values():
            if isinstance(param_value, str) and len(param_value) > 5000:
                score += 1.0
                patterns.append(BehaviorPattern.PARAMETER_POLLUTION.value)
        
        return score, patterns

    def _analyze_session_anomalies(self, signature: RequestSignature) -> Tuple[float, List[str]]:
        """Analyze for session-based anomalies."""
        anomalies = []
        score = 0.0
        
        # Check for unusual User-Agent patterns
        user_agent = signature.user_agent.lower()
        suspicious_ua_patterns = [
            'curl', 'wget', 'python', 'bot', 'scanner', 'sqlmap', 'nikto'
        ]
        
        for pattern in suspicious_ua_patterns:
            if pattern in user_agent:
                score += 1.0
                anomalies.append(f"Suspicious User-Agent: {pattern}")
        
        # Check for missing common headers
        common_headers = ['accept', 'accept-language', 'accept-encoding']
        missing_headers = [h for h in common_headers if h not in [k.lower() for k in signature.headers.keys()]]
        
        if len(missing_headers) > 1:
            score += 0.5
            anomalies.append(f"Missing common headers: {missing_headers}")
        
        # Check session consistency
        session_id = session.get('session_id') if session else None
        if session_id:
            current_signature = f"{signature.ip_address}:{signature.user_agent}"
            stored_signatures = self.session_signatures[session_id]
            
            if stored_signatures and current_signature not in stored_signatures:
                score += 2.0
                anomalies.append("Session signature mismatch")
            
            stored_signatures.add(current_signature)
        
        return score, anomalies

    def _analyze_content_patterns(self, signature: RequestSignature) -> Tuple[float, List[str]]:
        """Analyze content for specific attack patterns."""
        patterns = []
        score = 0.0
        
        for param_value in signature.parameters.values():
            if not isinstance(param_value, str):
                continue
            
            param_lower = param_value.lower()
            
            # Script injection attempts
            script_patterns = ['<script', 'javascript:', 'onload=', 'onerror=', 'eval(']
            for pattern in script_patterns:
                if pattern in param_lower:
                    score += 1.5
                    patterns.append(BehaviorPattern.SCRIPT_INJECTION_ATTEMPTS.value)
            
            # DOM manipulation attempts
            dom_patterns = ['document.write', 'innerHTML', 'location.href', 'window.open']
            for pattern in dom_patterns:
                if pattern in param_lower:
                    score += 1.0
                    patterns.append(BehaviorPattern.DOM_MANIPULATION.value)
            
            # Social engineering indicators
            social_patterns = ['alert(', 'confirm(', 'prompt(', 'document.cookie']
            for pattern in social_patterns:
                if pattern in param_lower:
                    score += 0.5
                    patterns.append(BehaviorPattern.SOCIAL_ENGINEERING.value)
        
        return score, patterns

    def _contains_attack_patterns(self, content: str) -> bool:
        """Check if content contains known attack patterns."""
        content_lower = content.lower()
        for pattern_group in self.attack_patterns.values():
            for pattern in pattern_group:
                if pattern.lower() in content_lower:
                    return True
        return False

    def _url_decode(self, content: str) -> str:
        """URL decode content."""
        import urllib.parse
        try:
            return urllib.parse.unquote(content)
        except:
            return content

    def _html_decode(self, content: str) -> str:
        """HTML decode content."""
        import html
        try:
            return html.unescape(content)
        except:
            return content

    def _generate_recommendation(self, risk_score: float, patterns: List[str]) -> str:
        """Generate security recommendation based on analysis."""
        if risk_score >= 8.0:
            return "BLOCK: Critical threat detected - immediate blocking recommended"
        elif risk_score >= 5.0:
            return "LIMIT: High risk detected - rate limiting recommended"
        elif risk_score >= 2.0:
            return "MONITOR: Medium risk detected - enhanced monitoring recommended"
        else:
            return "ALLOW: Low risk - normal processing"

    def get_ip_reputation(self, ip_address: str) -> Dict[str, float]:
        """Get reputation metrics for an IP address."""
        history = self.request_history[ip_address]
        if not history:
            return {'trust_score': 1.0, 'threat_score': 0.0, 'request_count': 0}
        
        # Calculate metrics
        total_requests = len(history)
        recent_requests = [r for r in history if time.time() - r.timestamp <= 3600]  # Last hour
        
        # Calculate average suspicious score
        avg_suspicious_score = sum(r.suspicious_score for r in history) / total_requests if total_requests > 0 else 0.0
        
        # Calculate request frequency
        time_span = max(history, key=lambda x: x.timestamp).timestamp - min(history, key=lambda x: x.timestamp).timestamp
        request_frequency = total_requests / max(time_span / 3600, 1)  # Requests per hour
        
        # Calculate trust score (0-1, higher is better)
        trust_score = max(0.0, 1.0 - (avg_suspicious_score / 10.0) - (min(request_frequency / 100, 0.5)))
        
        # Calculate threat score (0-10, higher is worse)
        threat_score = min(10.0, avg_suspicious_score + (request_frequency / 50))
        
        return {
            'trust_score': trust_score,
            'threat_score': threat_score,
            'request_count': total_requests,
            'recent_requests': len(recent_requests),
            'avg_suspicious_score': avg_suspicious_score,
            'request_frequency': request_frequency
        }

    def cleanup_old_data(self, max_age: int = 86400):
        """Clean up old tracking data."""
        current_time = time.time()
        cutoff_time = current_time - max_age
        
        # Clean request history
        for ip_address in list(self.request_history.keys()):
            history = self.request_history[ip_address]
            # Keep only recent requests
            self.request_history[ip_address] = deque([
                req for req in history if req.timestamp > cutoff_time
            ], maxlen=self.max_requests)
            
            # Remove empty histories
            if not self.request_history[ip_address]:
                del self.request_history[ip_address]
        
        # Clean pattern counts
        for ip_address in list(self.pattern_counts.keys()):
            if ip_address not in self.request_history:
                del self.pattern_counts[ip_address]


# Global instance
behavioral_analyzer = BehavioralAnalyzer()
