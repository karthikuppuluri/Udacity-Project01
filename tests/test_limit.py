"""Check that the `limit` function limits iterables.

To run these tests from the project root, run:

    $ python3 -m unittest --verbose tests.test_limit

It isn't guaranteed that `limit` is a generator function - it's possible to
implement it imperatively with the tools from the `itertools` module.

These tests should pass when Task 3c is complete.
"""

import collections.abc
import unittest

from filters import limit


class TestLimit(unittest.TestCase):
    """Test the limit function."""

    def setUp(self):
        """Set up test fixtures."""
        self.iterable = tuple(range(5))

    def test_limit_iterable_with_limit(self):
        """Test limiting an iterable with a specific limit."""
        self.assertEqual(tuple(limit(self.iterable, 3)), (0, 1, 2))

    def test_limit_iterable_without_limit(self):
        """Test limiting an iterable without a limit."""
        self.assertEqual(tuple(limit(self.iterable)), (0, 1, 2, 3, 4))
        self.assertEqual(tuple(limit(self.iterable, 0)), (0, 1, 2, 3, 4))
        self.assertEqual(tuple(limit(self.iterable, None)), (0, 1, 2, 3, 4))

    def test_limit_iterator_with_smaller_limit(self):
        """Test limiting an iterator with a smaller limit."""
        self.assertEqual(tuple(limit(iter(self.iterable), 3)), (0, 1, 2))

    def test_limit_iterator_with_matching_limit(self):
        """Test limiting an iterator with matching limit."""
        self.assertEqual(tuple(limit(iter(self.iterable), 5)), (0, 1, 2, 3, 4))

    def test_limit_iterator_with_larger_limit(self):
        """Test limiting an iterator with a larger limit."""
        self.assertEqual(tuple(limit(iter(self.iterable), 10)),
                         (0, 1, 2, 3, 4))

    def test_limit_iterator_without_limit(self):
        """Test limiting an iterator without a limit."""
        self.assertEqual(tuple(limit(iter(self.iterable))), (0, 1, 2, 3, 4))
        self.assertEqual(tuple(limit(iter(self.iterable), 0)), (0, 1, 2, 3, 4))
        self.assertEqual(tuple(limit(iter(self.iterable), None)),
                         (0, 1, 2, 3, 4))

    def test_limit_produces_an_iterable(self):
        """Test that limit produces an iterable."""
        self.assertIsInstance(limit(self.iterable, 3),
                              collections.abc.Iterable)
        self.assertIsInstance(limit(self.iterable, 5),
                              collections.abc.Iterable)
        self.assertIsInstance(limit(self.iterable, 10),
                              collections.abc.Iterable)
        self.assertIsInstance(limit(self.iterable), collections.abc.Iterable)
        self.assertIsInstance(limit(self.iterable, 0),
                              collections.abc.Iterable)
        self.assertIsInstance(limit(self.iterable, None),
                              collections.abc.Iterable)


if __name__ == "__main__":
    unittest.main()
