"""Check that `query`ing an `NEODatabase` accurately produces close approaches.

There are many ways to combine the arguments to `create_filters`, which
correspond to different command-line options. This modules tests options
isolation, in pairs, and in more complicated combinations. Althought the tests
are not entirely exhaustive, any implementation that passes all of these tests
is most likely up to snuff.

To run these tests from the project root, run::

    $ python3 -m unittest --verbose tests.test_query

These tests should pass when Tasks 3a and 3b are complete.
"""

import datetime
import pathlib
import unittest

from database import NEODatabase
from extract import load_neos, load_approaches
from filters import create_filters

TESTS_ROOT = (pathlib.Path(__file__).parent).resolve()
TEST_NEO_FILE = TESTS_ROOT / "test-neos-2020.csv"
TEST_CAD_FILE = TESTS_ROOT / "test-cad-2020.json"


class TestQuery(unittest.TestCase):
    """Test NEODatabase query functionality with various filters."""

    # Set longMessage to True to enable lengthy diffs between set comparisons.
    longMessage = False

    @classmethod
    def setUpClass(cls):
        """Set up test class fixtures."""
        cls.neos = load_neos(TEST_NEO_FILE)
        cls.approaches = load_approaches(TEST_CAD_FILE)
        cls.db = NEODatabase(cls.neos, cls.approaches)

    def test_query_all(self):
        """Test querying all approaches without filters."""
        expected = set(self.approaches)
        self.assertGreater(len(expected), 0)

        filters = create_filters()
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    ###############################################
    # Single filters and pairs of related filters #
    ###############################################

    def test_query_approaches_on_march_2(self):
        """Test querying approaches on a specific date (March 2, 2020)."""
        date = datetime.date(2020, 3, 2)

        expected = set(approach for approach in self.approaches
                       if approach.time.date() == date)
        self.assertGreater(len(expected), 0)

        filters = create_filters(filter_date=date)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_after_april(self):
        """Test querying approaches after a start date (April 1, 2020)."""
        start_date = datetime.date(2020, 4, 1)

        expected = set(approach for approach in self.approaches
                       if start_date <= approach.time.date())
        self.assertGreater(len(expected), 0)

        filters = create_filters(start_date=start_date)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_before_july(self):
        """Test querying approaches before an end date (June 30, 2020)."""
        end_date = datetime.date(2020, 6, 30)

        expected = set(approach for approach in self.approaches
                       if approach.time.date() <= end_date)
        self.assertGreater(len(expected), 0)

        filters = create_filters(end_date=end_date)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_in_march(self):
        """Test querying approaches within a date range (March 2020)."""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 3, 31)

        expected = set(approach for approach in self.approaches
                       if start_date <= approach.time.date() <= end_date)
        self.assertGreater(len(expected), 0)

        filters = create_filters(start_date=start_date, end_date=end_date)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_conflicting_date_bounds(self):
        """Test querying with conflicting date bounds (should return empty)"""
        start_date = datetime.date(2020, 10, 1)
        end_date = datetime.date(2020, 4, 1)

        expected = set()

        filters = create_filters(start_date=start_date, end_date=end_date)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_bounds_and_a_specific_date(self):
        """Test querying with both date bounds and a specific date."""
        start_date = datetime.date(2020, 2, 1)
        filter_date = datetime.date(2020, 3, 2)
        end_date = datetime.date(2020, 4, 1)

        expected = set(approach for approach in self.approaches
                       if approach.time.date() == filter_date)
        self.assertGreater(len(expected), 0)

        filters = create_filters(filter_date=filter_date,
                                 start_date=start_date,
                                 end_date=end_date)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_distance(self):
        """Test querying with maximum distance filter."""
        distance_max = 0.4

        expected = set(approach for approach in self.approaches
                       if approach.distance <= distance_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(distance_max=distance_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_min_distance(self):
        """Test querying with minimum distance filter."""
        distance_min = 0.1

        expected = set(approach for approach in self.approaches
                       if distance_min <= approach.distance)
        self.assertGreater(len(expected), 0)

        filters = create_filters(distance_min=distance_min)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_distance_and_min_distance(self):
        """Test querying with both minimum and maximum distance filters."""
        distance_max = 0.4
        distance_min = 0.1

        expected = set(approach for approach in self.approaches
                       if distance_min <= approach.distance <= distance_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(distance_min=distance_min,
                                 distance_max=distance_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_distance_and_min_distance_conflicting(self):
        """Test querying with conflicting distance bounds."""
        distance_max = 0.1
        distance_min = 0.4

        expected = set()

        filters = create_filters(distance_min=distance_min,
                                 distance_max=distance_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_velocity(self):
        """Test querying with maximum velocity filter."""
        velocity_max = 20

        expected = set(approach for approach in self.approaches
                       if approach.velocity <= velocity_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(velocity_max=velocity_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_min_velocity(self):
        """Test querying with minimum velocity filter."""
        velocity_min = 10

        expected = set(approach for approach in self.approaches
                       if velocity_min <= approach.velocity)
        self.assertGreater(len(expected), 0)

        filters = create_filters(velocity_min=velocity_min)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_velocity_and_min_velocity(self):
        """Test querying with both minimum and maximum velocity filters."""
        velocity_max = 20
        velocity_min = 10

        expected = set(approach for approach in self.approaches
                       if velocity_min <= approach.velocity <= velocity_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(velocity_min=velocity_min,
                                 velocity_max=velocity_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_velocity_and_min_velocity_conflicting(self):
        """Test querying with conflicting velocity bounds."""
        velocity_max = 10
        velocity_min = 20

        expected = set()

        filters = create_filters(velocity_min=velocity_min,
                                 velocity_max=velocity_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_diameter(self):
        """Test querying with maximum diameter filter."""
        diameter_max = 1.5

        expected = set(approach for approach in self.approaches
                       if approach.neo.diameter <= diameter_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(diameter_max=diameter_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_min_diameter(self):
        """Test querying with minimum diameter filter."""
        diameter_min = 0.5

        expected = set(approach for approach in self.approaches
                       if diameter_min <= approach.neo.diameter)
        self.assertGreater(len(expected), 0)

        filters = create_filters(diameter_min=diameter_min)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_diameter_and_min_diameter(self):
        """Test querying with both minimum and maximum diameter filters."""
        diameter_max = 1.5
        diameter_min = 0.5

        expected = set(
            approach for approach in self.approaches
            if diameter_min <= approach.neo.diameter <= diameter_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(diameter_min=diameter_min,
                                 diameter_max=diameter_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_max_diameter_and_min_diameter_conflicting(self):
        """Test querying with conflicting diameter bounds."""
        diameter_max = 0.5
        diameter_min = 1.5

        expected = set()

        filters = create_filters(diameter_min=diameter_min,
                                 diameter_max=diameter_max)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_hazardous(self):
        """Test querying for potentially hazardous NEOs only."""
        expected = set(approach for approach in self.approaches
                       if approach.neo.hazardous)
        self.assertGreater(len(expected), 0)

        filters = create_filters(hazardous=True)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_with_not_hazardous(self):
        """Test querying for non-hazardous NEOs only."""
        expected = set(approach for approach in self.approaches
                       if not approach.neo.hazardous)
        self.assertGreater(len(expected), 0)

        filters = create_filters(hazardous=False)
        received = set(self.db.query(filters))

        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    ###########################
    # Combinations of filters #
    ###########################

    def test_query_approaches_on_march_2_with_max_distance(self):
        """Test querying approaches on March 2 with maximum distance."""
        filter_date = datetime.date(2020, 3, 2)
        distance_max = 0.4

        expected = set(approach for approach in self.approaches
                       if approach.time.date() == filter_date
                       and approach.distance <= distance_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(filter_date=filter_date,
                                 distance_max=distance_max)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_on_march_2_with_min_distance(self):
        """Test querying approaches on March 2 with minimum distance."""
        filter_date = datetime.date(2020, 3, 2)
        distance_min = 0.1

        expected = set(approach for approach in self.approaches
                       if approach.time.date() == filter_date
                       and distance_min <= approach.distance)
        self.assertGreater(len(expected), 0)

        filters = create_filters(filter_date=filter_date,
                                 distance_min=distance_min)
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_in_march_with_min_distance_and_max_distance(
            self):
        """Test querying March approaches with distance bounds."""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 3, 31)
        distance_max = 0.4
        distance_min = 0.1

        expected = set(approach for approach in self.approaches
                       if start_date <= approach.time.date() <= end_date
                       and distance_min <= approach.distance <= distance_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(
            start_date=start_date,
            end_date=end_date,
            distance_min=distance_min,
            distance_max=distance_max,
        )
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_in_march_with_distance_bounds_and_max_velocity(
            self):
        """Test querying March approaches with distance and max velocity."""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 3, 31)
        distance_max = 0.4
        distance_min = 0.1
        velocity_max = 20

        expected = set(approach for approach in self.approaches
                       if start_date <= approach.time.date() <= end_date
                       and distance_min <= approach.distance <= distance_max
                       and approach.velocity <= velocity_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(
            start_date=start_date,
            end_date=end_date,
            distance_min=distance_min,
            distance_max=distance_max,
            velocity_max=velocity_max,
        )
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_in_march_with_distance_and_velocity_bounds(
            self):
        """Test querying March approaches with distance and velocity bounds"""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 3, 31)
        distance_max = 0.4
        distance_min = 0.1
        velocity_max = 20
        velocity_min = 10

        expected = set(approach for approach in self.approaches
                       if start_date <= approach.time.date() <= end_date
                       and distance_min <= approach.distance <= distance_max
                       and velocity_min <= approach.velocity <= velocity_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(
            start_date=start_date,
            end_date=end_date,
            distance_min=distance_min,
            distance_max=distance_max,
            velocity_min=velocity_min,
            velocity_max=velocity_max,
        )
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_spring_distance_and_velocity_bound_max_diameter(
            self):
        """Test querying spring approaches with distance, velocity,
        max diameter."""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 5, 31)
        distance_max = 0.5
        distance_min = 0.05
        velocity_max = 25
        velocity_min = 5
        diameter_max = 1.5

        expected = set(approach for approach in self.approaches
                       if start_date <= approach.time.date() <= end_date
                       and distance_min <= approach.distance <= distance_max
                       and velocity_min <= approach.velocity <= velocity_max
                       and approach.neo.diameter <= diameter_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(
            start_date=start_date,
            end_date=end_date,
            distance_min=distance_min,
            distance_max=distance_max,
            velocity_min=velocity_min,
            velocity_max=velocity_max,
            diameter_max=diameter_max,
        )
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_spring_distance_velocity_and_diameter_bounds(
            self):
        """Test querying spring approaches with distance, velocity,
        diameter."""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 5, 31)
        distance_max = 0.5
        distance_min = 0.05
        velocity_max = 25
        velocity_min = 5
        diameter_max = 1.5
        diameter_min = 0.5

        expected = set(
            approach for approach in self.approaches
            if start_date <= approach.time.date() <= end_date
            and distance_min <= approach.distance <= distance_max
            and velocity_min <= approach.velocity <= velocity_max
            and diameter_min <= approach.neo.diameter <= diameter_max)
        self.assertGreater(len(expected), 0)

        filters = create_filters(
            start_date=start_date,
            end_date=end_date,
            distance_min=distance_min,
            distance_max=distance_max,
            velocity_min=velocity_min,
            velocity_max=velocity_max,
            diameter_min=diameter_min,
            diameter_max=diameter_max,
        )
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_spring_all_bounds_potentially_hazardous_neos(
            self):
        """Test querying spring approaches with all bounds and hazardous."""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 5, 31)
        distance_max = 0.5
        distance_min = 0.05
        velocity_max = 25
        velocity_min = 5
        diameter_max = 1.5
        diameter_min = 0.5

        expected = set(
            approach for approach in self.approaches
            if start_date <= approach.time.date() <= end_date
            and distance_min <= approach.distance <= distance_max
            and velocity_min <= approach.velocity <= velocity_max
            and diameter_min <= approach.neo.diameter <= diameter_max
            and approach.neo.hazardous)
        self.assertGreater(len(expected), 0)

        filters = create_filters(
            start_date=start_date,
            end_date=end_date,
            distance_min=distance_min,
            distance_max=distance_max,
            velocity_min=velocity_min,
            velocity_max=velocity_max,
            diameter_min=diameter_min,
            diameter_max=diameter_max,
            hazardous=True,
        )
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )

    def test_query_approaches_spring_all_bounds_not_potentially_hazardous_neo(
            self):
        """Test querying spring approaches with all bounds and
        non-hazardous."""
        start_date = datetime.date(2020, 3, 1)
        end_date = datetime.date(2020, 5, 31)
        distance_max = 0.5
        distance_min = 0.05
        velocity_max = 25
        velocity_min = 5
        diameter_max = 1.5
        diameter_min = 0.5

        expected = set(
            approach for approach in self.approaches
            if start_date <= approach.time.date() <= end_date
            and distance_min <= approach.distance <= distance_max
            and velocity_min <= approach.velocity <= velocity_max
            and diameter_min <= approach.neo.diameter <= diameter_max
            and not approach.neo.hazardous)
        self.assertGreater(len(expected), 0)

        filters = create_filters(
            start_date=start_date,
            end_date=end_date,
            distance_min=distance_min,
            distance_max=distance_max,
            velocity_min=velocity_min,
            velocity_max=velocity_max,
            diameter_min=diameter_min,
            diameter_max=diameter_max,
            hazardous=False,
        )
        received = set(self.db.query(filters))
        self.assertEqual(
            expected,
            received,
            msg="Computed results do not match expected results.",
        )


if __name__ == "__main__":
    unittest.main()
