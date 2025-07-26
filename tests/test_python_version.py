"""Check that the student is using Python 3.6+.

To run these tests from the project root, run:

    $ python3 -m unittest --verbose tests.test_python_version

This test should pass if you're using Python 3.6 or greater, and fail
otherwise.
"""

import sys
import unittest


class TestPythonVersion(unittest.TestCase):
    """Test Python version requirements."""

    def test_python_version_is_at_least_3_6(self):
        """Test that Python version is at least 3.6."""
        version = sys.version_info
        self.assertGreaterEqual(version.major, 3,
                                msg=f"Unexpected major version: "
                                    f"{version.major}.")
        if version.major == 3:
            self.assertGreaterEqual(version.minor, 6,
                                    msg=f"Unexpected minor version: "
                                        f"{version.minor}.")


if __name__ == '__main__':
    unittest.main()
