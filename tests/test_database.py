"""Check that an `NEODatabase` can be constructed and responds to queries.

The `NEODatabase` constructor should cross-link NEOs and their close
approaches, as well as prepare any additional metadata needed to support
`get_neo_by_*` methods.

To run these tests from the project root, run:

    $ python3 -m unittest --verbose tests.test_database

These tests should pass when Task 2 is complete.
"""

import pathlib
import math
import unittest

from extract import load_neos, load_approaches
from database import NEODatabase

# Paths to the test data files.
TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()
TEST_NEO_FILE = TESTS_ROOT / "test-neos-2020.csv"
TEST_CAD_FILE = TESTS_ROOT / "test-cad-2020.json"


class TestDatabase(unittest.TestCase):
    """Test NEODatabase functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test class fixtures."""
        cls.neos = load_neos(TEST_NEO_FILE)
        cls.approaches = load_approaches(TEST_CAD_FILE)
        cls.db = NEODatabase(cls.neos, cls.approaches)

    def test_database_construction_links_approaches_to_neos(self):
        """Test that database construction links approaches to NEOs."""
        for approach in self.approaches:
            self.assertIsNotNone(approach.neo)

    def test_database_construction_ensures_neo_has_approaches_attribute(
            self):
        """Test that each NEO has an approaches attribute."""
        for neo in self.neos:
            self.assertTrue(hasattr(neo, "approaches"))

    def test_database_construction_ensures_neos_exhaust_approaches(
            self):
        """Test that NEOs collectively exhaust all approaches."""
        approaches = set()
        for neo in self.neos:
            approaches.update(neo.approaches)
        self.assertEqual(approaches, set(self.approaches))

    def test_database_construction_ensures_neos_mutually_exclude_approaches(
            self):
        """Test that NEOs mutually exclude approaches."""
        seen = set()
        for neo in self.neos:
            for approach in neo.approaches:
                if approach in seen:
                    self.fail(
                        f"{approach} appears in the approaches of multiple "
                        f"NEOs.")
                seen.add(approach)

    def test_get_neo_by_designation_fetches_designated_neo(self):
        """Test getting NEO by designation."""
        # Adonis - designation 2101, name "Adonis"
        adonis = self.db.get_neo_by_designation("2101")
        self.assertIsNotNone(adonis)
        self.assertEqual(adonis.designation, "2101")
        self.assertEqual(adonis.name, "Adonis")

    def test_get_neo_by_designation_fetches_neo_for_designation_without_name(
            self):
        """Test getting NEO by designation when NEO has no name."""
        # 2019 SC8 - designation "2019 SC8", name None
        neo = self.db.get_neo_by_designation("2019 SC8")
        self.assertIsNotNone(neo)
        self.assertEqual(neo.designation, "2019 SC8")
        self.assertIsNone(neo.name)

    def test_get_neo_by_designation_fetches_nothing_for_unknown_designation(
            self):
        """Test getting NEO by unknown designation returns None."""
        nonexistent = self.db.get_neo_by_designation("not an NEO designation")
        self.assertIsNone(nonexistent)

    def test_get_neo_by_name_fetches_named_neo(self):
        """Test getting NEO by name."""
        # Adonis - designation 2101, name "Adonis"
        adonis = self.db.get_neo_by_name("Adonis")
        self.assertIsNotNone(adonis)
        self.assertEqual(adonis.designation, "2101")
        self.assertEqual(adonis.name, "Adonis")

    def test_get_neo_by_name_fetches_neo_for_name_but_not_designation(self):
        """Test getting NEO by name when designation differs."""
        # Adonis - designation 2101, name "Adonis"
        adonis = self.db.get_neo_by_name("Adonis")
        self.assertIsNotNone(adonis)
        self.assertNotEqual(adonis.designation, "Adonis")

    def test_get_neo_by_name_fetches_nothing_for_unknown_name(self):
        """Test getting NEO by unknown name returns None."""
        nonexistent = self.db.get_neo_by_name("not an NEO name")
        self.assertIsNone(nonexistent)

    def test_get_neo_by_name_fetches_nothing_for_names_of_unnamed_neos(self):
        """Test getting NEO by name for unnamed NEO returns None."""
        # 2019 SC8 - designation "2019 SC8", name None
        nothing = self.db.get_neo_by_name("2019 SC8")
        self.assertIsNone(nothing)


if __name__ == "__main__":
    unittest.main()
