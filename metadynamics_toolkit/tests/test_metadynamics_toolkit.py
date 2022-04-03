"""
Unit and regression test for the metadynamics_toolkit package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import metadynamics_toolkit


def test_metadynamics_toolkit_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "metadynamics_toolkit" in sys.modules
