#!/usr/bin/env python3
"""
Test script to verify the decimal/float division fix in ml_service.py
"""

import sys
import os
from decimal import Decimal

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_service import MLService

def test_safe_float_method():
    """Test the _safe_float method with various input types."""
    ml_service = MLService()
    
    # Test with different input types
    test_cases = [
        (None, 0.0),                    # None should return default
        (Decimal('123.45'), 123.45),    # Decimal should convert to float
        (123.45, 123.45),               # Float should remain float
        (123, 123.0),                   # Int should convert to float
        ('123.45', 123.45),             # String number should convert
        ('invalid', 10.0),              # Invalid string should return default
        ([], 5.0),                      # Invalid type should return default
    ]
    
    for input_val, expected in test_cases:
        default = expected if input_val in [None, 'invalid', []] else 0.0
        result = ml_service._safe_float(input_val, default)
        
        print(f"Input: {input_val} (type: {type(input_val).__name__}) -> Output: {result}")
        
        if input_val in ['invalid', []]:
            assert result == default, f"Expected {default}, got {result}"
        else:
            assert abs(result - expected) < 0.001, f"Expected {expected}, got {result}"
    
    print("✅ All _safe_float tests passed!")

def test_division_operations():
    """Test that decimal/float division operations work correctly."""
    ml_service = MLService()
    
    # Simulate the problematic scenario
    decimal_price = Decimal('500000.00')  # Database price as Decimal
    decimal_sqft = Decimal('2000')        # Database sqft as Decimal
    
    # This should now work without errors
    try:
        result = ml_service._safe_float(decimal_price) / ml_service._safe_float(decimal_sqft)
        expected = 250.0  # 500000 / 2000
        assert abs(result - expected) < 0.001, f"Expected {expected}, got {result}"
        print(f"✅ Division test passed: {decimal_price} / {decimal_sqft} = {result}")
    except Exception as e:
        print(f"❌ Division test failed: {e}")
        return False
    
    # Test edge cases
    try:
        # Division by zero should be handled
        result = ml_service._safe_float(decimal_price) / ml_service._safe_float(0)
        print(f"⚠️  Division by zero resulted in: {result} (might be inf)")
    except ZeroDivisionError:
        print("⚠️  Division by zero raised ZeroDivisionError (expected)")
    
    # Test with None values
    try:
        result = ml_service._safe_float(None, 100.0) / ml_service._safe_float(None, 1.0)
        assert result == 100.0, f"Expected 100.0, got {result}"
        print(f"✅ None handling test passed: result = {result}")
    except Exception as e:
        print(f"❌ None handling test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing decimal/float division fix...")
    print("=" * 50)
    
    try:
        test_safe_float_method()
        print()
        
        if test_division_operations():
            print()
            print("✅ All tests passed! The decimal/float division issue should be fixed.")
        else:
            print()
            print("❌ Some tests failed. Please check the implementation.")
    
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
