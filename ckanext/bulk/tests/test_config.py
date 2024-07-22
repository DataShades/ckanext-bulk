"""Tests for ckanext.bulk.config.

You don't have to write tests for this module, unless it does something
complex.
"""

import pytest

from ckanext.bulk import config


class TestOption:
    """Test option() accessor."""

    def test_default(self):
        """Default option is available."""
        assert config.option() == 10

    @pytest.mark.ckan_config(config.OPTION, 42)
    def test_modified(self):
        """Modified option is available."""
        assert config.option() == 42


class TestMultivalued:
    """Test multivalued() accessor."""

    def test_default(self):
        """Default option is available."""
        assert config.multivalued() == []

    @pytest.mark.ckan_config(config.MULTI, [1, 2, 3])
    def test_modified(self):
        """Modified option is available."""
        assert config.multivalued() == [1, 2, 3]
