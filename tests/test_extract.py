"""Check that data can be extracted from structured data files.

The `load_neos` function should load a collection of `NearEarthObject`s from a
CSV file, and the `load_approaches` function should load a collection of
`CloseApproach` objects from a JSON file.

To run these tests from the project root, run:

    $ python3 -m unittest --verbose tests.test_extract

These tests should pass when Task 2 is complete.
"""

import collections.abc
import datetime
import pathlib
import math
import unittest

from extract import load_neos, load_approaches
from models import NearEarthObject, CloseApproach

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()
TEST_NEO_FILE = TESTS_ROOT / "test-neos-2020.csv"
TEST_CAD_FILE = TESTS_ROOT / "test-cad-2020.json"


class TestLoadNEOs(unittest.TestCase):
    """Test loading NEOs from CSV file."""

    @classmethod
    def setUpClass(cls):
        """Set up test class fixtures."""
        cls.neos = load_neos(TEST_NEO_FILE)
        cls.neos_by_designation = {neo.designation: neo for neo in cls.neos}

    @classmethod
    def get_first_neo_or_none(cls):
        """Get the first NEO from the collection or None."""
        try:
            # Don't use __getitem__ in case the object is a set or a stream.
            return next(iter(cls.neos))
        except StopIteration:
            return None

    def test_neos_are_collection(self):
        """Test that loaded NEOs form a collection."""
        self.assertIsInstance(self.neos, collections.abc.Collection)

    def test_neos_contain_near_earth_objects(self):
        """Test that NEOs contain NearEarthObject instances."""
        neo = self.get_first_neo_or_none()
        self.assertIsNotNone(neo)
        self.assertIsInstance(neo, NearEarthObject)

    def test_neos_contain_all_elements(self):
        """Test that all NEOs are loaded."""
        self.assertEqual(len(self.neos), 4226)

    def test_neos_contain_2019_SC8_no_name_no_diameter(self):
        """Test specific NEO with no name and no diameter."""
        self.assertIn("2019 SC8", self.neos_by_designation)
        neo = self.neos_by_designation["2019 SC8"]

        self.assertEqual(neo.designation, "2019 SC8")
        self.assertEqual(neo.name, None)
        self.assertTrue(math.isnan(neo.diameter))
        self.assertFalse(neo.hazardous)

    def test_asclepius_has_name_no_diameter(self):
        """Test Asclepius NEO with name but no diameter."""
        self.assertIn("4581", self.neos_by_designation)
        asclepius = self.neos_by_designation["4581"]

        self.assertEqual(asclepius.designation, "4581")
        self.assertEqual(asclepius.name, "Asclepius")
        self.assertTrue(math.isnan(asclepius.diameter))
        self.assertTrue(asclepius.hazardous)

    def test_adonis_is_potentially_hazardous(self):
        """Test Adonis NEO hazardous status."""
        self.assertIn("2101", self.neos_by_designation)
        adonis = self.neos_by_designation["2101"]

        self.assertEqual(adonis.designation, "2101")
        self.assertEqual(adonis.name, "Adonis")
        self.assertAlmostEqual(adonis.diameter, 0.6, places=2)
        self.assertTrue(adonis.hazardous)


class TestLoadCloseApproaches(unittest.TestCase):
    """Test loading close approaches from JSON file."""

    @classmethod
    def setUpClass(cls):
        """Set up test class fixtures."""
        cls.approaches = load_approaches(TEST_CAD_FILE)

    @classmethod
    def get_first_approach_or_none(cls):
        """Get the first approach from the collection or None."""
        try:
            # Don't use __getitem__ in case the object is a set or a stream.
            return next(iter(cls.approaches))
        except StopIteration:
            return None

    def test_approaches_are_collection(self):
        """Test that loaded approaches form a collection."""
        self.assertIsInstance(self.approaches, collections.abc.Collection)

    def test_approaches_contain_close_approaches(self):
        """Test that approaches contain CloseApproach instances."""
        approach = self.get_first_approach_or_none()
        self.assertIsNotNone(approach)
        self.assertIsInstance(approach, CloseApproach)

    def test_approaches_contain_all_elements(self):
        """Test that all approaches are loaded."""
        self.assertEqual(len(self.approaches), 4700)

    def test_approach_time_is_datetime(self):
        """Test that approach time is a datetime object."""
        approach = self.get_first_approach_or_none()
        self.assertIsNotNone(approach)
        self.assertIsInstance(approach.time, datetime.datetime)

    def test_approach_distance_is_float(self):
        """Test that approach distance is a float."""
        approach = self.get_first_approach_or_none()
        self.assertIsNotNone(approach)
        self.assertIsInstance(approach.distance, float)

    def test_approach_velocity_is_float(self):
        """Test that approach velocity is a float."""
        approach = self.get_first_approach_or_none()
        self.assertIsNotNone(approach)
        self.assertIsInstance(approach.velocity, float)


if __name__ == "__main__":
    unittest.main()
