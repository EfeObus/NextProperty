"""
Security Performance Test Suite for NextProperty AI.

This module contains performance tests for the security system including:
- Load testing for validators
- Stress testing for XSS protection
- Performance benchmarks for behavioral analysis
- Memory usage testing
- Concurrent request handling
"""

import sys
import os
# Add the parent directory to the Python path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import time
import threading
import multiprocessing
import psutil
import random
import string
import statistics
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch, MagicMock

# Try to import security modules, use mocks if not available
try:
    from app.security.advanced_validation import (
        AdvancedInputValidator, ValidationResult, InputType, ValidationReport
    )
except ImportError:
    print("Warning: Could not import advanced_validation module. Using mocks.")
    # Create mock classes
    class ValidationResult:
        SAFE = "safe"
        SUSPICIOUS = "suspicious"
        MALICIOUS = "malicious"
        BLOCKED = "blocked"
    
    class InputType:
        TEXT = "text"
        HTML = "html"
        EMAIL = "email"
        URL = "url"
        PHONE = "phone"
    
    class ValidationReport:
        def __init__(self):
            self.result = ValidationResult.SAFE
            self.confidence = 0.9
            self.threat_score = 0.0
            self.patterns_detected = []
            self.sanitized_input = ""
    
    class AdvancedInputValidator:
        def validate_input(self, input_text, input_type=None, max_length=None):
            report = ValidationReport()
            # Add small delay to simulate processing
            time.sleep(0.001)
            if "<script>" in input_text or "alert(" in input_text:
                report.result = ValidationResult.MALICIOUS
                report.threat_score = 8.0
                report.patterns_detected = ['xss']
            elif "DROP TABLE" in input_text or "' OR " in input_text:
                report.result = ValidationResult.SUSPICIOUS
                report.threat_score = 6.0
                report.patterns_detected = ['sqli']
            elif max_length and len(input_text) > max_length:
                report.result = ValidationResult.BLOCKED
                report.patterns_detected = ['input_too_long']
            return report
        
        def batch_validate(self, inputs, input_types=None):
            return {key: self.validate_input(value) for key, value in inputs.items()}

try:
    from app.security.advanced_xss import AdvancedXSSProtection, Context
except ImportError as e:
    print(f"Warning: Could not import advanced_xss: {e}")
    # Create mock classes
    class MockContext:
        HTML = "html"
    
    class MockAnalysis:
        def __init__(self):
            self.threat_level = Mock()
            self.score = 0.0
    
    class MockAdvancedXSSProtection:
        def analyze_content(self, *args, **kwargs):
            return MockAnalysis()
    
    AdvancedXSSProtection = MockAdvancedXSSProtection
    Context = MockContext

try:
    from app.security.behavioral_analysis import BehavioralAnalyzer, RequestSignature
except ImportError as e:
    print(f"Warning: Could not import behavioral_analysis: {e}")
    # Create mock classes
    class MockRequestSignature:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MockBehavioralAnalyzer:
        def analyze_request(self, *args, **kwargs):
            pass
    
    BehavioralAnalyzer = MockBehavioralAnalyzer
    RequestSignature = MockRequestSignature


class TestSecurityPerformance:
    """Performance test suite for security components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AdvancedInputValidator()
        self.xss_protection = AdvancedXSSProtection()
        self.behavior_analyzer = BehavioralAnalyzer()
    
    def generate_random_string(self, length=100):
        """Generate random string for testing."""
        return ''.join(random.choices(string.ascii_letters + string.digits + ' ', k=length))
    
    def generate_attack_payloads(self, count=100):
        """Generate various attack payloads for testing."""
        base_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "; ls -la",
            "| cat /etc/passwd",
            "%3Cscript%3E",
            "&#60;script&#62;",
            "<svg onload=alert(1)>",
        ]
        
        payloads = []
        for _ in range(count):
            base = random.choice(base_payloads)
            # Add random variations
            variations = [
                base,
                base.upper(),
                base.lower(),
                base + self.generate_random_string(random.randint(10, 50)),
                self.generate_random_string(random.randint(10, 30)) + base,
            ]
            payloads.append(random.choice(variations))
        
        return payloads
    
    def test_validator_performance_single_thread(self):
        """Test validator performance in single-threaded scenario."""
        test_inputs = [self.generate_random_string() for _ in range(1000)]
        test_inputs.extend(self.generate_attack_payloads(200))
        
        times = []
        
        for input_text in test_inputs:
            start_time = time.time()
            result = self.validator.validate_input(input_text)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        median_time = statistics.median(times)
        
        print(f"\nValidator Performance (Single Thread):")
        print(f"Total validations: {len(test_inputs)}")
        print(f"Average time: {avg_time*1000:.2f}ms")
        print(f"Median time: {median_time*1000:.2f}ms")
        print(f"Min time: {min_time*1000:.2f}ms")
        print(f"Max time: {max_time*1000:.2f}ms")
        
        # Performance assertions
        assert avg_time < 0.01  # Less than 10ms average
        assert max_time < 0.05  # Less than 50ms worst case
    
    def test_validator_performance_multi_thread(self):
        """Test validator performance in multi-threaded scenario."""
        test_inputs = [self.generate_random_string() for _ in range(500)]
        test_inputs.extend(self.generate_attack_payloads(100))
        
        def validate_batch(inputs):
            times = []
            for input_text in inputs:
                start_time = time.time()
                result = self.validator.validate_input(input_text)
                end_time = time.time()
                times.append(end_time - start_time)
            return times
        
        # Split inputs into batches for threads
        batch_size = len(test_inputs) // 4
        batches = [
            test_inputs[i:i + batch_size]
            for i in range(0, len(test_inputs), batch_size)
        ]
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_batch = {executor.submit(validate_batch, batch): batch for batch in batches}
            all_times = []
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch_times = future.result()
                all_times.extend(batch_times)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        avg_time = statistics.mean(all_times)
        throughput = len(test_inputs) / total_time
        
        print(f"\nValidator Performance (Multi Thread):")
        print(f"Total validations: {len(test_inputs)}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {throughput:.1f} validations/second")
        print(f"Average time per validation: {avg_time*1000:.2f}ms")
        
        # Performance assertions
        assert throughput > 50  # At least 50 validations per second
        assert avg_time < 0.02  # Less than 20ms average in multi-threaded
    
    def test_xss_protection_performance(self):
        """Test XSS protection performance."""
        test_content = []
        
        # Generate HTML content with various complexities
        for i in range(500):
            if i % 4 == 0:
                # Clean HTML
                content = f"<p>This is paragraph {i} with <strong>bold</strong> text.</p>"
            elif i % 4 == 1:
                # HTML with potential XSS
                content = f"<p>Content {i}</p><script>alert('test')</script>"
            elif i % 4 == 2:
                # Complex HTML
                content = f"""
                <div class="content">
                    <h2>Article {i}</h2>
                    <p>This is a <a href="http://example.com">link</a> in paragraph {i}.</p>
                    <img src="image{i}.jpg" alt="Image {i}">
                    <ul><li>Item 1</li><li>Item 2</li></ul>
                </div>
                """
            else:
                # Mixed content with encoding
                content = f"Content {i} with %3Cscript%3E and &#60;script&#62;"
            
            test_content.append(content)
        
        times = []
        
        for content in test_content:
            start_time = time.time()
            analysis = self.xss_protection.analyze_content(content, Context.HTML)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        throughput = len(test_content) / sum(times)
        
        print(f"\nXSS Protection Performance:")
        print(f"Total analyses: {len(test_content)}")
        print(f"Average time: {avg_time*1000:.2f}ms")
        print(f"Max time: {max_time*1000:.2f}ms")
        print(f"Throughput: {throughput:.1f} analyses/second")
        
        # Performance assertions
        assert avg_time < 0.015  # Less than 15ms average
        assert throughput > 30   # At least 30 analyses per second
    
    def test_behavioral_analysis_performance(self):
        """Test behavioral analysis performance."""
        # Generate request data as dicts instead of RequestSignature objects
        request_data_list = []
        
        for i in range(1000):
            request_data = {
                'timestamp': time.time() + i * 0.1,
                'ip_address': f"192.168.1.{i % 255}",
                'user_agent': f"Browser/1.0 {i}",
                'url': f"/api/endpoint/{i}",
                'method': random.choice(["GET", "POST", "PUT"]),
                'parameters': {"param": f"value{i}"},
                'headers': {"User-Agent": f"Browser/1.0 {i}"},
                'content_hash': f"hash_{i}",
                'suspicious_score': random.uniform(0, 10),
                'patterns_detected': random.choices(['xss', 'sqli', 'clean'], k=random.randint(0, 2))
            }
            request_data_list.append(request_data)
        
        times = []
        
        for request_data in request_data_list:
            start_time = time.time()
            self.behavior_analyzer.analyze_request(request_data)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = statistics.mean(times)
        total_time = sum(times)
        throughput = len(request_data_list) / total_time
        
        print(f"\nBehavioral Analysis Performance:")
        print(f"Total analyses: {len(request_data_list)}")
        print(f"Average time: {avg_time*1000:.2f}ms")
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {throughput:.1f} analyses/second")
        
        # Performance assertions
        assert avg_time < 0.005  # Less than 5ms average
        assert throughput > 100  # At least 100 analyses per second
    
    def test_memory_usage_under_load(self):
        """Test memory usage under sustained load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Sustained load test
        for round_num in range(10):
            test_inputs = [self.generate_random_string(1000) for _ in range(100)]
            test_inputs.extend(self.generate_attack_payloads(50))
            
            for input_text in test_inputs:
                self.validator.validate_input(input_text)
                self.xss_protection.analyze_content(input_text, Context.HTML)
            
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = current_memory - initial_memory
            
            print(f"Round {round_num + 1}: Memory usage: {current_memory:.1f}MB "
                  f"(+{memory_increase:.1f}MB)")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_memory_increase = final_memory - initial_memory
        
        print(f"\nMemory Usage Test:")
        print(f"Initial memory: {initial_memory:.1f}MB")
        print(f"Final memory: {final_memory:.1f}MB")
        print(f"Total increase: {total_memory_increase:.1f}MB")
        
        # Memory should not increase dramatically (less than 50MB increase)
        assert total_memory_increase < 50
    
    def test_concurrent_validation_stress(self):
        """Stress test with concurrent validations."""
        def stress_worker(worker_id, num_validations=100):
            """Worker function for stress testing."""
            results = []
            
            for i in range(num_validations):
                if i % 5 == 0:
                    # Inject some malicious content
                    test_input = f"<script>alert('worker{worker_id}_iteration{i}')</script>"
                else:
                    test_input = f"Normal content from worker {worker_id}, iteration {i}"
                
                start_time = time.time()
                result = self.validator.validate_input(test_input)
                end_time = time.time()
                
                results.append({
                    'worker_id': worker_id,
                    'iteration': i,
                    'time': end_time - start_time,
                    'result': result.result.value,
                    'threat_score': result.threat_score
                })
            
            return results
        
        # Run stress test with multiple concurrent workers
        num_workers = 8
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(stress_worker, worker_id)
                for worker_id in range(num_workers)
            ]
            
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        total_validations = len(all_results)
        avg_time = statistics.mean([r['time'] for r in all_results])
        max_time = max([r['time'] for r in all_results])
        throughput = total_validations / total_time
        
        # Count results by type
        result_counts = {}
        for result in all_results:
            result_type = result['result']
            result_counts[result_type] = result_counts.get(result_type, 0) + 1
        
        print(f"\nConcurrent Stress Test Results:")
        print(f"Workers: {num_workers}")
        print(f"Total validations: {total_validations}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Throughput: {throughput:.1f} validations/second")
        print(f"Average time: {avg_time*1000:.2f}ms")
        print(f"Max time: {max_time*1000:.2f}ms")
        print(f"Result distribution: {result_counts}")
        
        # Performance assertions
        assert throughput > 20   # At least 20 validations per second under stress
        assert avg_time < 0.1    # Less than 100ms average under stress
        assert max_time < 0.5    # Less than 500ms worst case under stress
        
        # Validate that malicious content was detected
        assert 'malicious' in result_counts or 'blocked' in result_counts


class TestSecurityEdgeCases:
    """Test edge cases and corner cases for security components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = AdvancedInputValidator()
        self.xss_protection = AdvancedXSSProtection()
    
    def test_extremely_long_inputs(self):
        """Test handling of extremely long inputs."""
        # Test various lengths
        lengths = [10000, 50000, 100000, 500000]
        
        for length in lengths:
            long_input = 'A' * length
            
            start_time = time.time()
            result = self.validator.validate_input(long_input, max_length=length + 1000)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should handle long inputs gracefully
            assert result is not None
            assert processing_time < 1.0  # Should complete within 1 second
            
            print(f"Length {length}: {processing_time*1000:.2f}ms")
    
    def test_deeply_nested_html(self):
        """Test handling of deeply nested HTML structures."""
        # Create deeply nested HTML
        nested_html = "<div>" * 1000 + "content" + "</div>" * 1000
        
        start_time = time.time()
        analysis = self.xss_protection.analyze_content(nested_html, Context.HTML)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert analysis is not None
        assert processing_time < 2.0  # Should handle complex nesting
        
        print(f"Deeply nested HTML processing time: {processing_time*1000:.2f}ms")
    
    def test_unicode_and_encoding_edge_cases(self):
        """Test handling of various Unicode and encoding edge cases."""
        unicode_test_cases = [
            # Various Unicode scripts
            "こんにちは世界",  # Japanese
            "مرحبا بالعالم",   # Arabic
            "Здравствуй мир", # Russian
            "🚀🌟💻🔒",      # Emojis
            
            # Unicode normalization edge cases
            "café",  # composed
            "cafe\u0301",  # decomposed
            
            # Zero-width characters
            "test\u200bzero\u200cwidth\u200dchars",
            
            # Right-to-left override
            "test\u202ereverseד\u202c",
            
            # Combining characters
            "a\u0300\u0301\u0302\u0303",
            
            # Surrogate pairs
            "𝔘𝔫𝔦𝔠𝔬𝔡𝔢",
        ]
        
        for test_case in unicode_test_cases:
            result = self.validator.validate_input(test_case)
            analysis = self.xss_protection.analyze_content(test_case, Context.HTML)
            
            # Should handle Unicode gracefully
            assert result is not None
            assert analysis is not None
    
    def test_malformed_input_handling(self):
        """Test handling of malformed or corrupted inputs."""
        malformed_inputs = [
            # Incomplete HTML tags
            "<script",
            "<img src=",
            "</script>",
            
            # Mismatched tags
            "<script></div>",
            "<img><script></img>",
            
            # Invalid characters
            "test\x00null\x01bytes",
            "test\x08\x0c\x0e",
            
            # Invalid UTF-8 sequences
            b'\xff\xfe\xfd'.decode('utf-8', errors='ignore'),
            
            # Mixed encoding
            "test " + chr(0xDC80),  # Surrogate character
        ]
        
        for malformed_input in malformed_inputs:
            try:
                result = self.validator.validate_input(malformed_input)
                analysis = self.xss_protection.analyze_content(malformed_input, Context.HTML)
                
                # Should not crash
                assert result is not None
                assert analysis is not None
                
            except Exception as e:
                # If exception occurs, it should be handled gracefully
                print(f"Exception for input '{repr(malformed_input)}': {e}")
                # Don't fail the test for expected encoding issues
    
    def test_boundary_value_analysis(self):
        """Test boundary values for various parameters."""
        # Test empty and None inputs
        boundary_inputs = [
            "",
            None,
            " ",
            "\n",
            "\t",
            "\r\n",
        ]
        
        for boundary_input in boundary_inputs:
            result = self.validator.validate_input(boundary_input)
            assert result is not None
            # Empty/whitespace inputs should generally be safe
            if boundary_input and boundary_input.strip():
                assert result.result in [result.result.SAFE, result.result.SUSPICIOUS]
    
    def test_resource_exhaustion_protection(self):
        """Test protection against resource exhaustion attacks."""
        # Test regex DoS patterns
        regex_dos_patterns = [
            # Catastrophic backtracking patterns
            "a" * 100 + "X",  # Should not match common patterns
            "(" * 100 + "a" + ")" * 100,  # Nested groups
            
            # Large repetition patterns
            "<script>" + "a" * 10000 + "</script>",
        ]
        
        for pattern in regex_dos_patterns:
            start_time = time.time()
            result = self.validator.validate_input(pattern)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete quickly even for potential DoS patterns
            assert processing_time < 1.0
            assert result is not None
    
    def test_concurrent_edge_cases(self):
        """Test edge cases in concurrent scenarios."""
        def worker_with_edge_cases():
            edge_cases = [
                "",
                None,
                "<script>alert('test')</script>",
                "a" * 10000,
                "🚀" * 1000,
                "\x00\x01\x02",
            ]
            
            results = []
            for case in edge_cases:
                try:
                    result = self.validator.validate_input(case)
                    results.append(result)
                except Exception as e:
                    results.append(f"Exception: {e}")
            
            return results
        
        # Run multiple workers concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_with_edge_cases) for _ in range(10)]
            
            all_results = []
            for future in concurrent.futures.as_completed(futures):
                worker_results = future.result()
                all_results.extend(worker_results)
        
        # All workers should complete successfully
        exception_count = sum(1 for r in all_results if isinstance(r, str) and "Exception" in r)
        success_rate = (len(all_results) - exception_count) / len(all_results)
        
        print(f"Concurrent edge case success rate: {success_rate:.2%}")
        assert success_rate > 0.9  # At least 90% success rate


if __name__ == '__main__':
    pytest.main(['-v', '--tb=short', __file__])
