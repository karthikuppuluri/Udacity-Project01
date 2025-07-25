#!/usr/bin/env python3
"""
Basic functionality test for Project01.

This script tests the basic functionality to ensure everything is working.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from models import NearEarthObject, CloseApproach
        print("Passed: models.py imported successfully")
    except Exception as e:
        print(f"models.py import failed: {e}")
        return False
    
    try:
        from helpers import cd_to_datetime, datetime_to_str
        print("Passed: helpers.py imported successfully")
    except Exception as e:
        print(f"helpers.py import failed: {e}")
        return False
    
    try:
        from extract import load_neos, load_approaches
        print("Passed: extract.py imported successfully")
    except Exception as e:
        print(f"extract.py import failed: {e}")
        return False
    
    try:
        from database import NEODatabase
        print("Passed: database.py imported successfully")
    except Exception as e:
        print(f"database.py import failed: {e}")
        return False
    
    try:
        from filters import create_filters, limit
        print("Passed: filters.py imported successfully")
    except Exception as e:
        print(f"filters.py import failed: {e}")
        return False
    
    try:
        from write import write_to_csv, write_to_json
        print("Passed: write.py imported successfully")
    except Exception as e:
        print(f"write.py import failed: {e}")
        return False
    
    return True

def test_data_files():
    """Test that data files exist."""
    print("\nTesting data files...")
    
    neos_path = Path('data/neos.csv')
    cad_path = Path('data/cad.json')
    
    if neos_path.exists():
        print(f"Passed: neos.csv exists ({neos_path.stat().st_size} bytes)")
    else:
        print(f"neos.csv not found at {neos_path}")
        return False
    
    if cad_path.exists():
        print(f"Passed: cad.json exists ({cad_path.stat().st_size} bytes)")
    else:
        print(f"cad.json not found at {cad_path}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from models import NearEarthObject, CloseApproach
        from datetime import datetime
        
        # Test NEO creation
        neo = NearEarthObject("433", "Eros", 16.84, False)
        print(f"Passed: Created NEO: {neo}")
        
        # Test CloseApproach creation
        approach = CloseApproach(
            datetime(2020, 1, 1, 12, 0),
            0.025,
            15.5,
            "433"
        )
        print(f"Passed: Created CloseApproach: {approach}")
        
        # Test helpers
        from helpers import cd_to_datetime, datetime_to_str
        dt = cd_to_datetime("2020-Jan-01 12:00")
        print(f"Passed: Date conversion: {dt}")
        
        dt_str = datetime_to_str(dt)
        print(f"Passed: Date string: {dt_str}")
        
        return True
        
    except Exception as e:
        print(f"Basic functionality test failed: {e}")
        return False

def test_data_loading():
    """Test data loading functionality."""
    print("\nTesting data loading...")
    
    try:
        from extract import load_neos, load_approaches
        
        # Test loading a small sample
        neos = load_neos(Path('data/neos.csv'))
        print(f"Passed: Loaded {len(neos)} NEOs")
        
        approaches = load_approaches(Path('data/cad.json'))
        print(f"Passed: Loaded {len(approaches)} close approaches")
        
        return True
        
    except Exception as e:
        print(f"Data loading failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Running Project01 Basic Tests\n")
    
    tests = [
        test_imports,
        test_data_files,
        test_basic_functionality,
        test_data_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All basic tests passed! Project01 is ready.")
    else:
        print("Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == '__main__':
    main() 