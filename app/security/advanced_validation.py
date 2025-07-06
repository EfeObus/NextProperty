"""
Advanced Input Validation Module with ML-based Threat Detection.

This module provides sophisticated input validation using machine learning
techniques and advanced pattern recognition for XSS detection.
"""

import re
import json
import pickle
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from collections import Counter, defaultdict
import time
from flask import current_app


class ValidationResult(Enum):
    """Validation result types."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious" 
    MALICIOUS = "malicious"
    BLOCKED = "blocked"


class InputType(Enum):
    """Input data types."""
    TEXT = "text"
    HTML = "html"
    URL = "url"
    EMAIL = "email"
    PHONE = "phone"
    JSON = "json"
    XML = "xml"
    FILE_NAME = "filename"
    FILE_CONTENT = "file_content"


@dataclass
class ValidationReport:
    """Detailed validation report."""
    result: ValidationResult
    confidence: float
    threat_score: float
    patterns_detected: List[str]
    ml_prediction: Optional[float] = None
    sanitized_input: Optional[str] = None
    recommendation: Optional[str] = None
    processing_time: float = 0.0


class AdvancedInputValidator:
    """Advanced input validator with ML-based threat detection."""
    
    def __init__(self):
        """Initialize the advanced input validator."""
        self.feature_cache = {}
        self.pattern_weights = {}
        self.model_cache = {}
        
        # Enhanced XSS detection patterns with weights
        self.xss_patterns = {
            # Critical patterns (weight 10)
            'script_tags': {
                'patterns': [
                    r'<script[^>]*>.*?</script>',
                    r'<script[^>]*/>',
                    r'<script[^>]*>[^<]*</script>',
                ],
                'weight': 10,
                'description': 'Script tag injection'
            },
            
            # High severity patterns (weight 8)
            'javascript_protocol': {
                'patterns': [
                    r'javascript\s*:',
                    r'vbscript\s*:',
                    r'mocha\s*:',
                    r'livescript\s*:',
                ],
                'weight': 8,
                'description': 'JavaScript protocol injection'
            },
            
            # High severity patterns (weight 8)
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
                ],
                'weight': 8,
                'description': 'Event handler injection'
            },
            
            # Medium-high patterns (weight 6)
            'dangerous_functions': {
                'patterns': [
                    r'eval\s*\(',
                    r'setTimeout\s*\(',
                    r'setInterval\s*\(',
                    r'Function\s*\(',
                    r'execScript\s*\(',
                    r'document\.write\s*\(',
                    r'document\.writeln\s*\(',
                ],
                'weight': 6,
                'description': 'Dangerous function calls'
            },
            
            # Medium patterns (weight 5)
            'html_injection': {
                'patterns': [
                    r'<iframe[^>]*>',
                    r'<object[^>]*>',
                    r'<embed[^>]*>',
                    r'<applet[^>]*>',
                    r'<form[^>]*>',
                    r'<input[^>]*>',
                    r'<textarea[^>]*>',
                    r'<link[^>]*>',
                    r'<meta[^>]*>',
                ],
                'weight': 5,
                'description': 'HTML element injection'
            },
            
            # Medium patterns (weight 4)
            'css_injection': {
                'patterns': [
                    r'expression\s*\(',
                    r'@import\s+url',
                    r'behavior\s*:',
                    r'-moz-binding',
                    r'<style[^>]*>.*?</style>',
                ],
                'weight': 4,
                'description': 'CSS injection'
            },
            
            # Low-medium patterns (weight 3)
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
                ],
                'weight': 3,
                'description': 'Encoding evasion'
            },
            
            # Low patterns (weight 2)
            'suspicious_keywords': {
                'patterns': [
                    r'alert\s*\(',
                    r'confirm\s*\(',
                    r'prompt\s*\(',
                    r'console\.log',
                    r'debugger',
                    r'innerHTML',
                    r'outerHTML',
                    r'document\.cookie',
                    r'localStorage',
                    r'sessionStorage',
                ],
                'weight': 2,
                'description': 'Suspicious keywords'
            }
        }
        
        # SQL injection patterns
        self.sqli_patterns = {
            'union_attacks': {
                'patterns': [
                    r'\bunion\s+select\b',
                    r'\bunion\s+all\s+select\b',
                ],
                'weight': 9,
                'description': 'UNION-based SQL injection'
            },
            'boolean_attacks': {
                'patterns': [
                    r'\s+or\s+1\s*=\s*1',
                    r'\s+and\s+1\s*=\s*1',
                    r'\s+or\s+1\s*=\s*0',
                    r"'\s+or\s+'1'\s*=\s*'1'",
                ],
                'weight': 8,
                'description': 'Boolean-based SQL injection'
            },
            'time_based': {
                'patterns': [
                    r'sleep\s*\(',
                    r'waitfor\s+delay',
                    r'benchmark\s*\(',
                    r'pg_sleep\s*\(',
                ],
                'weight': 7,
                'description': 'Time-based SQL injection'
            }
        }
        
        # Command injection patterns
        self.command_injection_patterns = {
            'system_commands': {
                'patterns': [
                    r';\s*ls\s',
                    r';\s*cat\s',
                    r';\s*rm\s',
                    r';\s*nc\s',
                    r';\s*wget\s',
                    r';\s*curl\s',
                    r'\|\s*nc\s',
                    r'&\s*ping\s',
                ],
                'weight': 9,
                'description': 'System command injection'
            }
        }
        
        # Input type specific validators
        self.type_validators = {
            InputType.EMAIL: self._validate_email,
            InputType.URL: self._validate_url,
            InputType.PHONE: self._validate_phone,
            InputType.JSON: self._validate_json,
            InputType.XML: self._validate_xml,
            InputType.FILE_NAME: self._validate_filename,
        }

    def validate_input(self, data: Any, input_type: InputType = InputType.TEXT,
                      context: Optional[str] = None, 
                      max_length: Optional[int] = None) -> ValidationReport:
        """
        Validate input using multiple detection methods.
        
        Args:
            data: Input data to validate
            input_type: Type of input data
            context: Context where input will be used
            max_length: Maximum allowed length
            
        Returns:
            ValidationReport: Detailed validation results
        """
        start_time = time.time()
        
        # Convert to string if needed
        input_str = str(data) if data is not None else ""
        
        # Basic validation
        if max_length and len(input_str) > max_length:
            return ValidationReport(
                result=ValidationResult.BLOCKED,
                confidence=1.0,
                threat_score=10.0,
                patterns_detected=['input_too_long'],
                recommendation="Input exceeds maximum allowed length",
                processing_time=time.time() - start_time
            )
        
        # Empty input is safe
        if not input_str.strip():
            return ValidationReport(
                result=ValidationResult.SAFE,
                confidence=1.0,
                threat_score=0.0,
                patterns_detected=[],
                sanitized_input=input_str,
                processing_time=time.time() - start_time
            )
        
        # Pattern-based detection
        pattern_score, patterns = self._detect_patterns(input_str)
        
        # Feature extraction for ML
        features = self._extract_features(input_str, input_type)
        
        # ML-based prediction
        ml_score = self._ml_predict(features, input_type)
        
        # Context-specific validation
        context_score = self._validate_context(input_str, context)
        
        # Type-specific validation
        type_score = 0.0
        if input_type in self.type_validators:
            type_score = self._get_type_validation_score(input_str, input_type)
        
        # Combine scores
        total_score = pattern_score + (ml_score * 2) + context_score + type_score
        
        # Determine result
        result, confidence = self._determine_result(total_score, patterns)
        
        # Generate sanitized version if needed
        sanitized_input = None
        if result in [ValidationResult.SAFE, ValidationResult.SUSPICIOUS]:
            sanitized_input = self._sanitize_input(input_str, input_type, patterns)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(result, total_score, patterns)
        
        processing_time = time.time() - start_time
        
        return ValidationReport(
            result=result,
            confidence=confidence,
            threat_score=total_score,
            patterns_detected=patterns,
            ml_prediction=ml_score,
            sanitized_input=sanitized_input,
            recommendation=recommendation,
            processing_time=processing_time
        )

    def batch_validate(self, inputs: Dict[str, Any], 
                      input_types: Optional[Dict[str, InputType]] = None) -> Dict[str, ValidationReport]:
        """
        Validate multiple inputs in batch.
        
        Args:
            inputs: Dictionary of input names to values
            input_types: Dictionary of input names to types
            
        Returns:
            Dict: Validation reports for each input
        """
        results = {}
        
        for name, value in inputs.items():
            input_type = input_types.get(name, InputType.TEXT) if input_types else InputType.TEXT
            results[name] = self.validate_input(value, input_type, context=name)
        
        return results

    def _detect_patterns(self, input_str: str) -> Tuple[float, List[str]]:
        """Detect malicious patterns in input."""
        total_score = 0.0
        detected_patterns = []
        
        input_lower = input_str.lower()
        
        # Check XSS patterns
        for category, pattern_info in self.xss_patterns.items():
            for pattern in pattern_info['patterns']:
                matches = re.findall(pattern, input_str, re.IGNORECASE | re.DOTALL)
                if matches:
                    total_score += pattern_info['weight'] * len(matches)
                    detected_patterns.append(f"xss_{category}")
        
        # Check SQL injection patterns
        for category, pattern_info in self.sqli_patterns.items():
            for pattern in pattern_info['patterns']:
                matches = re.findall(pattern, input_str, re.IGNORECASE | re.DOTALL)
                if matches:
                    total_score += pattern_info['weight'] * len(matches)
                    detected_patterns.append(f"sqli_{category}")
        
        # Check command injection patterns
        for category, pattern_info in self.command_injection_patterns.items():
            for pattern in pattern_info['patterns']:
                matches = re.findall(pattern, input_str, re.IGNORECASE | re.DOTALL)
                if matches:
                    total_score += pattern_info['weight'] * len(matches)
                    detected_patterns.append(f"cmdi_{category}")
        
        return total_score, detected_patterns

    def _extract_features(self, input_str: str, input_type: InputType) -> np.ndarray:
        """Extract features for ML prediction."""
        features = []
        
        # Basic features
        features.extend([
            len(input_str),  # Length
            input_str.count('<'),  # HTML tag indicators
            input_str.count('>'),
            input_str.count('('),  # Function call indicators
            input_str.count(')'),
            input_str.count('"'),  # Quote indicators
            input_str.count("'"),
            input_str.count('='),  # Assignment indicators
            input_str.count(';'),  # Statement separators
            input_str.count('&'),  # Entity indicators
            input_str.count('%'),  # Encoding indicators
            input_str.count('\\'),  # Escape indicators
        ])
        
        # Character distribution features
        char_counts = Counter(input_str.lower())
        total_chars = len(input_str)
        
        if total_chars > 0:
            features.extend([
                char_counts.get('s', 0) / total_chars,  # 's' frequency (script)
                char_counts.get('c', 0) / total_chars,  # 'c' frequency
                char_counts.get('r', 0) / total_chars,  # 'r' frequency
                char_counts.get('i', 0) / total_chars,  # 'i' frequency
                char_counts.get('p', 0) / total_chars,  # 'p' frequency
                char_counts.get('t', 0) / total_chars,  # 't' frequency
            ])
        else:
            features.extend([0.0] * 6)
        
        # Keyword presence features
        keywords = [
            'script', 'javascript', 'eval', 'alert', 'document',
            'window', 'location', 'cookie', 'onload', 'onerror',
            'union', 'select', 'insert', 'delete', 'drop',
            'exec', 'system', 'cmd', 'shell'
        ]
        
        input_lower = input_str.lower()
        for keyword in keywords:
            features.append(1.0 if keyword in input_lower else 0.0)
        
        # N-gram features (trigrams of suspicious patterns)
        suspicious_trigrams = ['scr', 'ipt', 'eva', 'ale', 'ert', 'uni', 'ion', 'sel']
        for trigram in suspicious_trigrams:
            features.append(1.0 if trigram in input_lower else 0.0)
        
        # Encoding features
        features.extend([
            1.0 if re.search(r'%[0-9a-f]{2}', input_str, re.IGNORECASE) else 0.0,  # URL encoded
            1.0 if re.search(r'&#\d+;', input_str) else 0.0,  # HTML entities
            1.0 if re.search(r'\\u[0-9a-f]{4}', input_str, re.IGNORECASE) else 0.0,  # Unicode
            1.0 if re.search(r'\\x[0-9a-f]{2}', input_str, re.IGNORECASE) else 0.0,  # Hex
        ])
        
        # Structure features
        features.extend([
            input_str.count('http://') + input_str.count('https://'),  # URL count
            len(re.findall(r'<[^>]+>', input_str)),  # HTML tag count
            len(re.findall(r'\b\w+\s*\(', input_str)),  # Function call count
        ])
        
        return np.array(features, dtype=np.float32)

    def _ml_predict(self, features: np.ndarray, input_type: InputType) -> float:
        """Make ML-based prediction (simplified heuristic model)."""
        # Simple heuristic model (replace with trained ML model in production)
        
        # Normalize features
        normalized_features = features / (np.linalg.norm(features) + 1e-8)
        
        # Weight important features more heavily
        weights = np.array([
            2.0,  # Length (suspicious if very long)
            5.0,  # '<' count
            5.0,  # '>' count
            3.0,  # '(' count
            3.0,  # ')' count
            2.0,  # '"' count
            2.0,  # "'" count
            3.0,  # '=' count
            4.0,  # ';' count
            2.0,  # '&' count
            3.0,  # '%' count
            3.0,  # '\\' count
        ] + [1.0] * (len(normalized_features) - 12))  # Rest get weight 1.0
        
        # Ensure weights array matches features length
        if len(weights) != len(normalized_features):
            weights = np.ones(len(normalized_features))
        
        # Calculate weighted score
        score = np.dot(normalized_features[:len(weights)], weights[:len(normalized_features)])
        
        # Apply sigmoid to get probability between 0 and 1
        probability = 1 / (1 + np.exp(-score + 5))  # Bias towards lower scores
        
        return float(probability * 10)  # Scale to 0-10

    def _validate_context(self, input_str: str, context: Optional[str]) -> float:
        """Validate input based on context."""
        if not context:
            return 0.0
        
        score = 0.0
        context_lower = context.lower()
        input_lower = input_str.lower()
        
        # Context-specific validations
        if 'email' in context_lower:
            if not self._is_valid_email_format(input_str):
                score += 2.0
        
        elif 'url' in context_lower:
            if not self._is_valid_url_format(input_str):
                score += 2.0
        
        elif 'phone' in context_lower:
            if not self._is_valid_phone_format(input_str):
                score += 1.0
        
        elif 'name' in context_lower:
            # Names shouldn't contain HTML or scripts
            if '<' in input_str or '>' in input_str:
                score += 3.0
        
        elif 'search' in context_lower:
            # Search queries are often targets for XSS
            if 'script' in input_lower or 'javascript' in input_lower:
                score += 4.0
        
        return score

    def _get_type_validation_score(self, input_str: str, input_type: InputType) -> float:
        """Get validation score based on input type."""
        if input_type in self.type_validators:
            is_valid = self.type_validators[input_type](input_str)
            return 0.0 if is_valid else 2.0
        return 0.0

    def _determine_result(self, score: float, patterns: List[str]) -> Tuple[ValidationResult, float]:
        """Determine validation result based on score and patterns."""
        # Critical patterns always result in BLOCKED
        critical_patterns = [p for p in patterns if 'script' in p or 'xss' in p]
        if critical_patterns and score >= 8.0:
            return ValidationResult.BLOCKED, 0.95
        
        # High score threshold
        if score >= 15.0:
            return ValidationResult.MALICIOUS, 0.9
        elif score >= 8.0:
            return ValidationResult.SUSPICIOUS, 0.8
        elif score >= 3.0:
            return ValidationResult.SUSPICIOUS, 0.6
        else:
            return ValidationResult.SAFE, 0.95 - (score / 10.0)

    def _sanitize_input(self, input_str: str, input_type: InputType, patterns: List[str]) -> str:
        """Sanitize input based on detected patterns."""
        sanitized = input_str
        
        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'<script[^>]*/?>', '', sanitized, flags=re.IGNORECASE)
        
        # Remove event handlers
        sanitized = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'\son\w+\s*=\s*[^>\s]+', '', sanitized, flags=re.IGNORECASE)
        
        # Remove javascript: and similar protocols
        sanitized = re.sub(r'(javascript|vbscript|mocha|livescript):', '', sanitized, flags=re.IGNORECASE)
        
        # Type-specific sanitization
        if input_type == InputType.HTML:
            # Allow some HTML but remove dangerous elements
            dangerous_tags = ['script', 'iframe', 'object', 'embed', 'applet', 'form']
            for tag in dangerous_tags:
                sanitized = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
                sanitized = re.sub(f'<{tag}[^>]*/?>', '', sanitized, flags=re.IGNORECASE)
        
        elif input_type == InputType.URL:
            # Ensure URL uses safe protocol
            if not sanitized.startswith(('http://', 'https://', '/')):
                sanitized = 'https://' + sanitized.lstrip('/')
        
        return sanitized

    def _generate_recommendation(self, result: ValidationResult, score: float, patterns: List[str]) -> str:
        """Generate security recommendation."""
        if result == ValidationResult.BLOCKED:
            return "BLOCK: Input contains critical security threats and should be rejected"
        elif result == ValidationResult.MALICIOUS:
            return "REJECT: Input appears malicious and should not be processed"
        elif result == ValidationResult.SUSPICIOUS:
            return f"SANITIZE: Input is suspicious (score: {score:.1f}), sanitize before use"
        else:
            return "ALLOW: Input appears safe for processing"

    # Type-specific validators
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        return self._is_valid_email_format(email)

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        return self._is_valid_url_format(url)

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone format."""
        return self._is_valid_phone_format(phone)

    def _validate_json(self, json_str: str) -> bool:
        """Validate JSON format."""
        try:
            json.loads(json_str)
            return True
        except:
            return False

    def _validate_xml(self, xml_str: str) -> bool:
        """Validate XML format."""
        try:
            import xml.etree.ElementTree as ET
            ET.fromstring(xml_str)
            return True
        except:
            return False

    def _validate_filename(self, filename: str) -> bool:
        """Validate filename format."""
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.js', '.vbs']
        return not any(filename.lower().endswith(ext) for ext in dangerous_extensions)

    # Format validation helpers
    def _is_valid_email_format(self, email: str) -> bool:
        """Check if email format is valid."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email)) and len(email) <= 254

    def _is_valid_url_format(self, url: str) -> bool:
        """Check if URL format is valid."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))

    def _is_valid_phone_format(self, phone: str) -> bool:
        """Check if phone format is valid."""
        # Remove common separators
        cleaned_phone = re.sub(r'[\s\-\(\)\+\.]', '', phone)
        # Check if remaining characters are digits and reasonable length
        return cleaned_phone.isdigit() and 7 <= len(cleaned_phone) <= 15


# Global instance
advanced_validator = AdvancedInputValidator()
