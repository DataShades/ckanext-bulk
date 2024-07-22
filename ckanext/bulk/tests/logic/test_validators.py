"""Tests for ckanext.bulk.logic.validators."""

import pytest

import ckan.plugins.toolkit as tk

from ckanext.bulk.logic import validators


def test_required_with_valid_value():
    """Non-empty value is accepted."""
    assert validators.bulk_required("value") == "value"


def test_required_with_invalid_value():
    """Missing value is not accepted."""
    with pytest.raises(tk.Invalid):
        validators.bulk_required(None)


def test_complex():
    """Do something complex here."""
    key = ("name",)
    errors = {key: []}

    with pytest.raises(tk.StopOnError):
        validators.bulk_complex_validator(
            key,
            {key: tk.missing},
            errors,
            {},
        )

    assert errors[key] == ["Required"]
