"""
Advanced XSS Protection System for NextProperty AI.

This module provides enhanced XSS protection beyond basic bleach sanitization,
including behavioral analysis, content scoring, and context-aware sanitization.
"""

import re
import base64
import json
import urllib.parse
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import hashlib
import time
from collections import defaultdict
import bleach
from markupsafe import Markup
from flask import current_app, request, g
import html


class ThreatLevel(Enum):
    """Threat level enumeration."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Context(Enum):
    """Context enumeration for content sanitization."""
    HTML = "html"
    JAVASCRIPT = "javascript"
    CSS = "css"
    URL = "url"
    JSON = "json"
    ATTRIBUTE = "attribute"
    TEXT = "text"


@dataclass
class ThreatAnalysis:
    """Data class for threat analysis results."""
    threat_level: ThreatLevel
    score: float
    patterns_detected: List[str]
    context_violations: List[str]
    sanitized_content: str
    blocked: bool = False
    reason: Optional[str] = None


class AdvancedXSSProtection:
    """Advanced XSS protection with behavioral analysis and threat scoring."""
    
    def __init__(self):
        """Initialize the advanced XSS protection system."""
        self.threat_cache = {}
        self.pattern_cache = {}
        self.request_tracking = defaultdict(list)
        
        # Advanced XSS patterns with severity scores
        self.xss_patterns = {
            # High severity patterns (score 10)
            'script_injection': {
                'patterns': [
                    r'<script[^>]*>.*?</script>',
                    r'<script[^>]*/>',
                    r'javascript:',
                    r'vbscript:',
                    r'data:text/html',
                    r'eval\s*\(',
                    r'setTimeout\s*\(',
                    r'setInterval\s*\(',
                    r'Function\s*\(',
                    r'execScript\s*\(',
                ],
                'score': 10,
                'description': 'Direct script injection attempt'
            },
            
            # Medium-high severity patterns (score 8)
            'event_handlers': {
                'patterns': [
                    r'on\w+\s*=\s*["\'][^"\']*["\']',
                    r'on\w+\s*=\s*[^>\s]+',
                    r'onload\s*=',
                    r'onerror\s*=',
                    r'onclick\s*=',
                    r'onmouseover\s*=',
                    r'onfocus\s*=',
                    r'onblur\s*=',
                    r'onchange\s*=',
                    r'onsubmit\s*=',
                ],
                'score': 8,
                'description': 'Event handler injection'
            },
            
            # Medium severity patterns (score 6)
            'dom_manipulation': {
                'patterns': [
                    r'document\.write\s*\(',
                    r'document\.writeln\s*\(',
                    r'document\.cookie',
                    r'window\.location',
                    r'location\.href',
                    r'location\.replace',
                    r'location\.assign',
                    r'document\.location',
                    r'window\.open\s*\(',
                    r'history\.replaceState',
                    r'history\.pushState',
                ],
                'score': 6,
                'description': 'DOM manipulation attempt'
            },
            
            # Medium severity patterns (score 5)
            'html_injection': {
                'patterns': [
                    r'<iframe[^>]*>',
                    r'<object[^>]*>',
                    r'<embed[^>]*>',
                    r'<applet[^>]*>',
                    r'<form[^>]*>',
                    r'<input[^>]*>',
                    r'<textarea[^>]*>',
                    r'<select[^>]*>',
                    r'<button[^>]*>',
                    r'<link[^>]*>',
                    r'<meta[^>]*>',
                    r'<base[^>]*>',
                ],
                'score': 5,
                'description': 'HTML element injection'
            },
            
            # Low-medium severity patterns (score 3)
            'css_injection': {
                'patterns': [
                    r'expression\s*\(',
                    r'@import\s+url',
                    r'javascript\s*:',
                    r'vbscript\s*:',
                    r'mocha\s*:',
                    r'livescript\s*:',
                    r'behavior\s*:',
                    r'-moz-binding',
                    r'<style[^>]*>.*?</style>',
                ],
                'score': 3,
                'description': 'CSS injection attempt'
            },
            
            # Low severity patterns (score 2)
            'encoding_evasion': {
                'patterns': [
                    r'&#x[0-9a-f]+;',
                    r'&#[0-9]+;',
                    r'%[0-9a-f]{2}',
                    r'\\u[0-9a-f]{4}',
                    r'\\x[0-9a-f]{2}',
                    r'String\.fromCharCode',
                    r'unescape\s*\(',
                    r'decodeURI\s*\(',
                    r'decodeURIComponent\s*\(',
                ],
                'score': 2,
                'description': 'Encoding evasion attempt'
            }
        }
        
        # Suspicious keywords that increase threat score
        self.suspicious_keywords = {
            'alert', 'confirm', 'prompt', 'console.log', 'debugger',
            'innerHTML', 'outerHTML', 'insertAdjacentHTML',
            'createElement', 'appendChild', 'removeChild',
            'setAttribute', 'getAttribute', 'removeAttribute',
            'sessionStorage', 'localStorage', 'indexedDB',
            'XMLHttpRequest', 'fetch', 'WebSocket',
            'postMessage', 'addEventListener', 'removeEventListener'
        }
        
        # Context-specific encoders
        self.encoders = {
            Context.HTML: self._encode_html,
            Context.JAVASCRIPT: self._encode_javascript,
            Context.CSS: self._encode_css,
            Context.URL: self._encode_url,
            Context.JSON: self._encode_json,
            Context.ATTRIBUTE: self._encode_attribute,
            Context.TEXT: self._encode_text
        }

    def analyze_content(self, content: str, context: Context = Context.HTML) -> ThreatAnalysis:
        """
        Perform comprehensive threat analysis on content.
        
        Args:
            content: Content to analyze
            context: Context in which content will be used
            
        Returns:
            ThreatAnalysis: Detailed analysis results
        """
        if not content:
            return ThreatAnalysis(
                threat_level=ThreatLevel.LOW,
                score=0.0,
                patterns_detected=[],
                context_violations=[],
                sanitized_content=""
            )
        
        # Calculate threat score
        score, patterns_detected = self._calculate_threat_score(content)
        
        # Check for context violations
        context_violations = self._check_context_violations(content, context)
        
        # Determine threat level
        threat_level = self._determine_threat_level(score, context_violations)
        
        # Sanitize content based on threat level and context
        sanitized_content = self._sanitize_by_threat_level(
            content, threat_level, context
        )
        
        # Check if content should be blocked
        blocked = threat_level == ThreatLevel.CRITICAL
        reason = None
        if blocked:
            reason = f"Critical threat detected (score: {score})"
        
        return ThreatAnalysis(
            threat_level=threat_level,
            score=score,
            patterns_detected=patterns_detected,
            context_violations=context_violations,
            sanitized_content=sanitized_content,
            blocked=blocked,
            reason=reason
        )

    def _calculate_threat_score(self, content: str) -> Tuple[float, List[str]]:
        """Calculate threat score based on pattern matching."""
        total_score = 0.0
        patterns_detected = []
        
        content_lower = content.lower()
        
        # Check for XSS patterns
        for category, pattern_info in self.xss_patterns.items():
            for pattern in pattern_info['patterns']:
                matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                if matches:
                    total_score += pattern_info['score'] * len(matches)
                    patterns_detected.append(f"{category}: {pattern}")
        
        # Check for suspicious keywords
        for keyword in self.suspicious_keywords:
            if keyword.lower() in content_lower:
                total_score += 1.0
                patterns_detected.append(f"suspicious_keyword: {keyword}")
        
        # Check for base64 encoded content (potential evasion)
        base64_matches = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', content)
        for match in base64_matches:
            try:
                decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                if any(keyword in decoded.lower() for keyword in ['script', 'javascript', 'eval']):
                    total_score += 5.0
                    patterns_detected.append("base64_evasion: suspicious encoded content")
            except:
                pass
        
        # Check for URL schemes
        url_schemes = ['javascript:', 'data:', 'vbscript:', 'file:', 'about:']
        for scheme in url_schemes:
            if scheme in content_lower:
                total_score += 3.0
                patterns_detected.append(f"suspicious_url_scheme: {scheme}")
        
        return total_score, patterns_detected

    def _check_context_violations(self, content: str, context: Context) -> List[str]:
        """Check for context-specific violations."""
        violations = []
        
        if context == Context.JSON:
            # JSON should not contain HTML or JavaScript
            html_patterns = ['<script', '<iframe', '<object', '<embed']
            for pattern in html_patterns:
                if pattern in content.lower():
                    violations.append(f"HTML in JSON context: {pattern}")
        
        elif context == Context.URL:
            # URLs should be properly encoded and use safe schemes
            if not self._is_safe_url(content):
                violations.append("Unsafe URL detected")
        
        elif context == Context.CSS:
            # CSS should not contain JavaScript
            js_in_css = ['javascript:', 'expression(', '@import url(']
            for pattern in js_in_css:
                if pattern in content.lower():
                    violations.append(f"JavaScript in CSS: {pattern}")
        
        return violations

    def _determine_threat_level(self, score: float, context_violations: List[str]) -> ThreatLevel:
        """Determine threat level based on score and violations."""
        if score >= 20.0 or len(context_violations) >= 3:
            return ThreatLevel.CRITICAL
        elif score >= 10.0 or len(context_violations) >= 2:
            return ThreatLevel.HIGH
        elif score >= 5.0 or len(context_violations) >= 1:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def _sanitize_by_threat_level(self, content: str, threat_level: ThreatLevel, 
                                 context: Context) -> str:
        """Sanitize content based on threat level and context."""
        if threat_level == ThreatLevel.CRITICAL:
            # Block critical threats entirely
            return ""
        
        # Apply context-specific encoding
        if context in self.encoders:
            content = self.encoders[context](content)
        
        if threat_level == ThreatLevel.HIGH:
            # Aggressive sanitization for high threats
            content = self._aggressive_sanitize(content)
        elif threat_level == ThreatLevel.MEDIUM:
            # Standard sanitization with enhanced cleaning
            content = self._enhanced_sanitize(content)
        else:
            # Basic sanitization for low threats
            content = self._basic_sanitize(content)
        
        return content

    def _aggressive_sanitize(self, content: str) -> str:
        """Aggressive sanitization for high-threat content."""
        # Remove all script-related content
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        content = re.sub(r'<script[^>]*/?>', '', content, flags=re.IGNORECASE)
        
        # Remove all event handlers
        content = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\son\w+\s*=\s*[^>\s]+', '', content, flags=re.IGNORECASE)
        
        # Remove dangerous URLs
        content = re.sub(r'(javascript|vbscript|data):[^"\'\s>]*', '', content, flags=re.IGNORECASE)
        
        # Remove potentially dangerous elements
        dangerous_tags = ['iframe', 'object', 'embed', 'applet', 'form', 'input', 'textarea', 'select', 'button']
        for tag in dangerous_tags:
            content = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', content, flags=re.IGNORECASE | re.DOTALL)
            content = re.sub(f'<{tag}[^>]*/?>', '', content, flags=re.IGNORECASE)
        
        # Use bleach for final cleanup with very restrictive settings
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'b', 'i']
        allowed_attributes = {}
        
        return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    def _enhanced_sanitize(self, content: str) -> str:
        """Enhanced sanitization for medium-threat content."""
        # Use bleach with moderate restrictions
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'b', 'i',
            'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre', 'div', 'span'
        ]
        
        allowed_attributes = {
            '*': ['class'],
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'blockquote': ['cite'],
            'code': ['class']
        }
        
        # Clean with bleach
        content = bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)
        
        # Additional cleaning for specific patterns
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'vbscript:', '', content, flags=re.IGNORECASE)
        
        return content

    def _basic_sanitize(self, content: str) -> str:
        """Basic sanitization for low-threat content."""
        # Standard bleach sanitization
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'b', 'i',
            'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'blockquote', 'code', 'pre', 'div', 'span', 'a', 'img'
        ]
        
        allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title', 'target', 'rel'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'blockquote': ['cite'],
            'code': ['class'],
            'div': ['class', 'id'],
            'span': ['class', 'id']
        }
        
        return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes, strip=True)

    def _encode_html(self, content: str) -> str:
        """HTML context encoding."""
        return html.escape(content, quote=True)

    def _encode_javascript(self, content: str) -> str:
        """JavaScript context encoding."""
        content = str(content)
        # Escape JavaScript special characters
        content = content.replace('\\', '\\\\')
        content = content.replace('"', '\\"')
        content = content.replace("'", "\\'")
        content = content.replace('\n', '\\n')
        content = content.replace('\r', '\\r')
        content = content.replace('\t', '\\t')
        content = content.replace('<', '\\u003c')
        content = content.replace('>', '\\u003e')
        content = content.replace('&', '\\u0026')
        content = content.replace('/', '\\/')
        return content

    def _encode_css(self, content: str) -> str:
        """CSS context encoding."""
        content = str(content)
        # Escape CSS special characters
        content = re.sub(r'[^a-zA-Z0-9\-_]', lambda m: f'\\{ord(m.group(0)):06x}', content)
        return content

    def _encode_url(self, content: str) -> str:
        """URL context encoding."""
        return urllib.parse.quote(str(content), safe='')

    def _encode_json(self, content: str) -> str:
        """JSON context encoding."""
        return json.dumps(str(content))

    def _encode_attribute(self, content: str) -> str:
        """HTML attribute context encoding."""
        content = html.escape(str(content), quote=True)
        # Additional attribute-specific escaping
        content = content.replace('\n', '&#10;')
        content = content.replace('\r', '&#13;')
        content = content.replace('\t', '&#9;')
        return content

    def _encode_text(self, content: str) -> str:
        """Plain text context encoding."""
        return html.escape(str(content), quote=False)

    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe."""
        safe_schemes = ['http', 'https', 'ftp', 'ftps', 'mailto']
        
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.scheme.lower() in safe_schemes
        except:
            return False

    def validate_file_content(self, file_content: bytes, filename: str) -> ThreatAnalysis:
        """
        Validate file content for potential threats.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            ThreatAnalysis: Analysis results
        """
        try:
            # Try to decode as text
            text_content = file_content.decode('utf-8', errors='ignore')
            
            # Analyze text content
            analysis = self.analyze_content(text_content, Context.TEXT)
            
            # Additional file-specific checks
            if filename.lower().endswith(('.html', '.htm', '.js', '.css')):
                # These file types should be treated with higher suspicion
                analysis.score += 2.0
                analysis.patterns_detected.append("suspicious_file_type")
            
            # Check for embedded scripts in non-script files
            if not filename.lower().endswith('.js') and 'script' in text_content.lower():
                analysis.score += 3.0
                analysis.patterns_detected.append("embedded_script_in_non_js_file")
            
            return analysis
            
        except Exception as e:
            # If we can't analyze the file, treat it as low threat
            return ThreatAnalysis(
                threat_level=ThreatLevel.LOW,
                score=0.0,
                patterns_detected=[],
                context_violations=[],
                sanitized_content="",
                blocked=False
            )

    def get_content_hash(self, content: str) -> str:
        """Generate hash for content caching."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def log_threat(self, analysis: ThreatAnalysis, request_info: Dict[str, Any] = None):
        """Log threat detection for monitoring."""
        if analysis.threat_level.value >= ThreatLevel.MEDIUM.value:
            log_data = {
                'timestamp': time.time(),
                'threat_level': analysis.threat_level.name,
                'score': analysis.score,
                'patterns': analysis.patterns_detected,
                'blocked': analysis.blocked,
                'ip': request.remote_addr if request else 'unknown',
                'user_agent': request.headers.get('User-Agent', 'unknown') if request else 'unknown'
            }
            
            if current_app:
                current_app.logger.warning(f"XSS threat detected: {log_data}")

    def analyze_input(self, content: str, context: Context = Context.HTML) -> Dict[str, Any]:
        """
        Analyze user input for XSS threats (convenience method).
        
        Args:
            content: Input content to analyze
            context: Context in which content will be used
            
        Returns:
            Dict containing analysis results
        """
        analysis = self.analyze_content(content, context)
        
        return {
            'threat_detected': analysis.threat_level.value >= ThreatLevel.MEDIUM.value,
            'threat_level': analysis.threat_level.name,
            'score': analysis.score,
            'patterns_detected': analysis.patterns_detected,
            'context_violations': analysis.context_violations,
            'sanitized_content': analysis.sanitized_content,
            'blocked': analysis.blocked,
            'reason': analysis.reason
        }

    def sanitize_input(self, content: str, context: Context = Context.HTML) -> str:
        """
        Sanitize user input (convenience method).
        
        Args:
            content: Input content to sanitize
            context: Context in which content will be used
            
        Returns:
            Sanitized content string
        """
        analysis = self.analyze_content(content, context)
        return analysis.sanitized_content

    def is_safe_input(self, content: str, context: Context = Context.HTML) -> bool:
        """
        Check if input is safe (convenience method).
        
        Args:
            content: Input content to check
            context: Context in which content will be used
            
        Returns:
            True if input is safe (Low threat level), False otherwise
        """
        analysis = self.analyze_content(content, context)
        return analysis.threat_level == ThreatLevel.LOW


# Global instance
advanced_xss = AdvancedXSSProtection()
