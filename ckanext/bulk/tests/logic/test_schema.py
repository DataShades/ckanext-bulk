"""Tests for ckanext.bulk.logic.schema.

If schema does not cover all the fields from user input, don't forget to test
validation inside the action.
"""

from __future__ import annotations

from typing import Any

import pytest

import ckan.plugins.toolkit as tk

from ckanext.bulk.logic import schema


@pytest.mark.parametrize(
    ("input", "expected", "failed"),
    [
        ({"left": 1, "right": 2}, {"left": 1, "right": 2}, set()),
        ({"left": 1}, {"left": 1, "right": tk.missing}, {"right"}),
        ({"right": 2}, {"right": 2, "left": tk.missing}, {"left"}),
        ({}, {"left": tk.missing, "right": tk.missing}, {"left", "right"}),
        ({"right": "10", "left": ""}, {"right": 10, "left": ""}, {"left"}),
        (
            {"right": "He", "left": None},
            {"right": "He", "left": None},
            {"right", "left"},
        ),
    ],
)
def test_get_sum(input: dict[str, Any], expected: dict[str, Any], failed: set[str]):
    """Test get_sum schema."""
    data, errors = tk.navl_validate(
        input,
        schema.get_sum(),
        {},
    )

    assert data == expected
    assert set(errors) == failed


@pytest.mark.parametrize(
    ("input", "expected", "failed"),
    [
        ({}, {"hello": tk.missing, "world": tk.missing}, {"hello", "world"}),
        # ... you got the idea
    ],
)
def test_something_create(
    input: dict[str, Any],
    expected: dict[str, Any],
    failed: set[str],
):
    """Test something_create schema."""
    data, errors = tk.navl_validate(
        input,
        schema.something_create(),
        {},
    )

    assert data == expected
    assert set(errors) == failed
