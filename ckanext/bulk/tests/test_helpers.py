"""Tests for ckanext.bulk.helpers module.

You can either call helpers directly or use `tk.h` and `with_plugins` fixture
to register and call helpers. The former is simpler, the latter verifies that
helpers are registered.
"""

from __future__ import annotations

from ckanext.bulk import helpers


def test_hello():
    """Helper returns expected greeting."""
    assert helpers.bulk_hello() == "Hello, bulk!"
