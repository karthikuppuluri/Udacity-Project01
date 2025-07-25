#!/usr/bin/env python3
"""
Test script for serialize methods.

This script tests the serialize methods to ensure they work correctly.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_serialize_methods():
    """Test the serialize methods."""
    print("Testing serialize methods...")
    
    try:
        from models import NearEarthObject, CloseApproach
        from datetime import datetime
        
        # Test NEO serialize
        neo = NearEarthObject("433", "Eros", 16.84, False)
        neo_serialized = neo.serialize()
        print(f"Passed: NEO serialize: {neo_serialized}")
        
        # Test CloseApproach serialize
        approach = CloseApproach(
            datetime(2020, 1, 1, 12, 0),
            0.025,
            15.5,
            "433",
            neo
        )
        approach_serialized = approach.serialize()
        print(f"Passed: CloseApproach serialize: {approach_serialized}")
        
        # Test with missing data
        neo2 = NearEarthObject("99942", None, None, True)
        neo2_serialized = neo2.serialize()
        print(f"Passed: NEO with missing data serialize: {neo2_serialized}")
        
        approach2 = CloseApproach(
            datetime(2020, 1, 2, 12, 0),
            0.030,
            20.0,
            "99942",
            None  # No NEO attached
        )
        approach2_serialized = approach2.serialize()
        print(f"Passed: CloseApproach without NEO serialize: {approach2_serialized}")
        
        return True
        
    except Exception as e:
        print(f"Serialize test failed: {e}")
        return False

def test_write_functions():
    """Test the write functions with serialize methods."""
    print("\nTesting write functions...")
    
    try:
        from models import NearEarthObject, CloseApproach
        from datetime import datetime
        from write import write_to_csv, write_to_json
        import tempfile
        import os
        
        # Create test data
        neo = NearEarthObject("433", "Eros", 16.84, False)
        approach = CloseApproach(
            datetime(2020, 1, 1, 12, 0),
            0.025,
            15.5,
            "433",
            neo
        )
        
        approaches = [approach]
        
        # Test CSV writing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            csv_path = tmp_file.name
        
        try:
            write_to_csv(approaches, csv_path)
            print(f"Passed: CSV written to {csv_path}")
            
            # Check file content
            with open(csv_path, 'r') as f:
                content = f.read()
                print(f"Passed: CSV content: {content[:200]}...")
        
        finally:
            if os.path.exists(csv_path):
                os.unlink(csv_path)
        
        # Test JSON writing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json_path = tmp_file.name
        
        try:
            write_to_json(approaches, json_path)
            print(f"Passed: JSON written to {json_path}")
            
            # Check file content
            with open(json_path, 'r') as f:
                content = f.read()
                print(f"Passed: JSON content: {content[:200]}...")
        
        finally:
            if os.path.exists(json_path):
                os.unlink(json_path)
        
        return True
        
    except Exception as e:
        print(f"Write test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Serialize Methods\n")
    
    tests = [
        test_serialize_methods,
        test_write_functions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All serialize tests passed!")
    else:
        print("Some tests failed.")
    
    return passed == total

if __name__ == '__main__':
    main() 