#!/usr/bin/env python3
"""
Basic functionality test for Project01.

This script tests the basic functionality to ensure everything is working.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules to test
try:
    from models import NearEarthObject, CloseApproach
    from helpers import cd_to_datetime, datetime_to_str
    from extract import load_neos, load_approaches
    from database import NEODatabase
    from filters import create_filters, limit
    from write import write_to_csv, write_to_json
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    IMPORTS_AVAILABLE = False


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    if not IMPORTS_AVAILABLE:
        print("Failed: One or more modules could not be imported")
        return False

    # Test individual module functionality
    modules_to_test = [
        ("models", "NearEarthObject, CloseApproach"),
        ("helpers", "cd_to_datetime, datetime_to_str"),
        ("extract", "load_neos, load_approaches"),
        ("database", "NEODatabase"),
        ("filters", "create_filters, limit"),
        ("write", "write_to_csv, write_to_json"),
    ]

    for module_name, items in modules_to_test:
        try:
            # Test that we can access the imported items
            if module_name == "models":
                NearEarthObject("test", "test", 1.0, False)
            print(f"✓ Passed: {module_name}.py imported successfully")
        except (ImportError, AttributeError, TypeError) as e:
            print(f"{module_name}.py import failed: {e}")
            return False

    return True


def test_data_files():
    """Test that data files exist."""
    print("\nTesting data files...")

    neos_path = Path("data/neos.csv")
    cad_path = Path("data/cad.json")

    if neos_path.exists():
        print(f"✓ Passed: neos.csv exists ({neos_path.stat().st_size} bytes)")
    else:
        print(f"neos.csv not found at {neos_path}")
        return False

    if cad_path.exists():
        print(f"✓ Passed: cad.json exists ({cad_path.stat().st_size} bytes)")
    else:
        print(f"cad.json not found at {cad_path}")
        return False

    return True


def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")

    if not IMPORTS_AVAILABLE:
        print("Skipping: Modules not available")
        return False

    try:
        # Test NEO creation
        neo = NearEarthObject("433", "Eros", 16.84, False)
        print(f"✓ Passed: Created NEO: {neo}")

        # Test CloseApproach creation
        approach = CloseApproach(datetime(2020, 1, 1, 12, 0), 0.025, 15.5,
                                 "433")
        print(f"✓ Passed: Created CloseApproach: {approach}")

        # Test helpers
        dt = cd_to_datetime("2020-Jan-01 12:00")
        print(f"✓ Passed: Date conversion: {dt}")

        dt_str = datetime_to_str(dt)
        print(f"✓ Passed: Date string: {dt_str}")

        return True

    except (ValueError, TypeError, AttributeError) as e:
        print(f"Basic functionality test failed: {e}")
        return False


def test_data_loading():
    """Test data loading functionality."""
    print("\nTesting data loading...")

    if not IMPORTS_AVAILABLE:
        print("Skipping: Modules not available")
        return False

    try:
        # Test loading a small sample
        neos = load_neos(Path("data/neos.csv"))
        print(f"✓ Passed: Loaded {len(neos)} NEOs")

        approaches = load_approaches(Path("data/cad.json"))
        print(f"✓ Passed: Loaded {len(approaches)} close approaches")

        return True

    except (FileNotFoundError, ValueError, TypeError) as e:
        print(f"Data loading failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running Project01 Basic Tests\n")

    tests = [
        test_imports,
        test_data_files,
        test_basic_functionality,
        test_data_loading,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All basic tests passed! Project is ready.")
        return True

    print("Some tests failed. Please check the implementation.")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
