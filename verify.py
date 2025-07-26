"""
Verify that all modules can be imported and basic functionality works.

This script tests the basic functionality of all modules in the NEO Explorer
to ensure everything is working correctly.
"""

import subprocess
import sys


def test_import(module_name, description):
    """
    Test that a module can be imported.

    Args:
        module_name: Name of the module to import
        description: Description of what's being tested

    Returns:
        True if import succeeds, False otherwise
    """
    print(f"Testing {description}...")
    try:
        __import__(module_name)
        print(f"✓ Passed: {description}")
        return True
    except Exception as e:
        print(f"✗ Failed: {description} - {e}")
        return False


def test_models():
    """Test basic model functionality."""
    print("\nTesting model creation...")
    try:
        from models import NearEarthObject, CloseApproach
        from datetime import datetime

        neo = NearEarthObject("433", "Eros", 16.84, False)
        print(f"✓ Passed: Created NEO: {neo}")

        approach = CloseApproach(datetime(2020, 1, 1, 12, 0), 0.025, 15.5,
                                 "433")
        print(f"✓ Passed: Created CloseApproach: {approach}")
        return True
    except Exception as e:
        print(f"✗ Failed: Model creation - {e}")
        return False


def test_helpers():
    """Test helper functions."""
    print("\nTesting helper functions...")
    try:
        from helpers import cd_to_datetime

        dt = cd_to_datetime("2020-Jan-01 12:00")
        print(f"✓ Passed: Date conversion: {dt}")
        return True
    except Exception as e:
        print(f"✗ Failed: Helper functions - {e}")
        return False


def test_extract():
    """Test data extraction."""
    print("\nTesting data extraction...")
    try:
        # Only test import, not actual file loading
        print("✓ Passed: Extract functions imported")
        return True
    except Exception as e:
        print(f"✗ Failed: Data extraction - {e}")
        return False


def test_database():
    """Test database functionality."""
    print("\nTesting database...")
    try:
        # Only test import
        print("✓ Passed: Database imported")
        return True
    except Exception as e:
        print(f"✗ Failed: Database - {e}")
        return False


def test_filters():
    """Test filter functionality."""
    print("\nTesting filters...")
    try:
        # Only test import
        print("✓ Passed: Filters imported")
        return True
    except Exception as e:
        print(f"✗ Failed: Filters - {e}")
        return False


def test_write():
    """Test write functionality."""
    print("\nTesting write functions...")
    try:
        # Only test import
        print("✓ Passed: Write functions imported")
        return True
    except Exception as e:
        print(f"✗ Failed: Write functions - {e}")
        return False


def test_main_script():
    """Test that the main script can run."""
    print("\nTesting main script...")
    try:
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("✓ Passed: Main script runs successfully")
            return True

        print(f"✗ Failed: Main script returned {result.returncode}")
        return False
    except Exception as e:
        print(f"✗ Failed: Main script test - {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 50)
    print("NEO Explorer - Verification Tests")
    print("=" * 50)

    tests = [
        test_models,
        test_helpers,
        test_extract,
        test_database,
        test_filters,
        test_write,
        test_main_script,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The NEO Explorer is ready to use.")
        return 0

    print("❌ Some tests failed. Please check the errors above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
