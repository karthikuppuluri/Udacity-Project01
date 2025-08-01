"""Check that data files exist and are readable, nonempty, and well-formatted.

To run these tests from the project root, run:

    $ python3 -m unittest --verbose tests.test_data_files

These tests should pass on the starter code.
"""

import collections
import csv
import json
import os
import pathlib

import unittest

# The root of the project, containing `main.py`.
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()


class TestDataFiles(unittest.TestCase):
    """Test that data files exist and are properly formatted."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_root = PROJECT_ROOT / "data"
        self.neo_file = self.data_root / "neos.csv"
        self.cad_file = self.data_root / "cad.json"

    def test_data_files_exist(self):
        """Test that both data files exist."""
        self.assertTrue(self.neo_file.exists())
        self.assertTrue(self.cad_file.exists())

    def test_data_files_are_readable(self):
        """Test that both data files are readable."""
        self.assertTrue(os.access(self.neo_file, os.R_OK))
        self.assertTrue(os.access(self.cad_file, os.R_OK))

    def test_data_files_are_not_empty(self):
        """Test that both data files are not empty."""
        try:
            self.assertTrue(self.neo_file.stat().st_size > 0,
                            "Empty NEO file.")
            self.assertTrue(self.cad_file.stat().st_size > 0,
                            "Empty CAD file.")
        except OSError:
            self.fail("Unexpected OSError.")

    def test_data_files_are_well_formatted(self):
        """Test that data files are properly formatted."""
        # Check that the NEO data is CSV-formatted.
        try:
            with self.neo_file.open() as f:
                # Consume the entire sequence into length-0 deque.
                collections.deque(csv.reader(f), maxlen=0)
        except csv.Error:
            self.fail(f"The data file {self.neo_file} doesn't appear to be "
                      f"a well-formatted CSV file.")

        # Check that the CAD data is JSON-formatted.
        try:
            with self.cad_file.open() as f:
                json.load(f)
        except json.JSONDecodeError:
            self.fail(f"The data file {self.cad_file} doesn't appear to be "
                      f"a well-formatted JSON file.")


if __name__ == '__main__':
    unittest.main()
