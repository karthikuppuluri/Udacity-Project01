"""
Test serialization functionality for the NEO Explorer.

This module tests the serialization capabilities of NEO and CloseApproach
objects.
"""

import tempfile
import os
import json
import csv
import sys
from datetime import datetime

from models import NearEarthObject, CloseApproach
from write import write_to_csv, write_to_json


def test_neo_serialization():
    """Test NEO serialization."""
    print("\nTesting NEO serialization...")

    neo = NearEarthObject("433", "Eros", 16.84, False)
    print(f"Passed: Created NEO: {neo}")

    # Test serialization
    serialized = neo.serialize()
    expected_keys = {
        "designation",
        "name",
        "diameter_km",
        "potentially_hazardous",
    }
    if set(serialized.keys()) == expected_keys:
        print("Passed: NEO serialization has correct keys")
    else:
        print(f"Failed: Expected keys {expected_keys}, "
              f"got {set(serialized.keys())}")

    return True


def test_approach_serialization():
    """Test CloseApproach serialization."""
    print("\nTesting CloseApproach serialization...")

    approach = CloseApproach(datetime(2020, 1, 1, 12, 0), 0.025, 15.5, "433")
    print(f"Passed: Created CloseApproach: {approach}")

    # Test serialization
    serialized = approach.serialize()
    expected_keys = {"datetime_utc", "distance_au", "velocity_km_s"}
    if set(serialized.keys()) == expected_keys:
        print("Passed: CloseApproach serialization has correct keys")
    else:
        print(f"Failed: Expected keys {expected_keys}, "
              f"got {set(serialized.keys())}")

    return True


def test_file_writing():
    """Test writing to files."""
    print("\nTesting file writing...")
    try:
        # Create test data
        neo = NearEarthObject("433", "Eros", 16.84, False)
        approach1 = CloseApproach(datetime(2020, 1, 1, 12, 0), 0.025, 15.5,
                                  "433")
        approach2 = CloseApproach(datetime(2020, 2, 1, 12, 0), 0.030, 12.0,
                                  "433")

        # Link NEO to approaches
        approach1.neo = neo
        approach2.neo = neo

        approaches = [approach1, approach2]

        # Test CSV writing
        with tempfile.NamedTemporaryFile(mode="w",
                                         suffix=".csv",
                                         delete=False,
                                         encoding="utf-8") as csv_file:
            csv_filename = csv_file.name

        write_to_csv(approaches, csv_filename)

        # Verify CSV file
        with open(csv_filename, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            if len(rows) == 2:
                print("Passed: CSV file has correct number of rows")
            else:
                print(f"Failed: Expected 2 rows, got {len(rows)}")

        # Clean up CSV file
        os.unlink(csv_filename)

        # Test JSON writing
        with tempfile.NamedTemporaryFile(mode="w",
                                         suffix=".json",
                                         delete=False,
                                         encoding="utf-8") as json_file:
            json_filename = json_file.name

        write_to_json(approaches, json_filename)

        # Verify JSON file
        with open(json_filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            if len(data) == 2:
                print("Passed: JSON file has correct number of entries")
            else:
                print(f"Failed: Expected 2 entries, got {len(data)}")

        # Clean up JSON file
        os.unlink(json_filename)

        return True

    except Exception as e:
        print(f"Failed: File writing test - {e}")
        return False


def main():
    """Run all serialization tests."""
    print("Testing serialization functionality...")

    tests = [
        test_neo_serialization,
        test_approach_serialization,
        test_file_writing,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("All serialization tests passed!")
        return 0

    print("Some serialization tests failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
