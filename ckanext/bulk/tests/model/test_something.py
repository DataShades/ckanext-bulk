"""Tests for Something model."""

from __future__ import annotations

from typing import Any

import pytest
from faker import Faker

from ckan import model

from ckanext.bulk.model import Something


# Always include `with_plugins` before `clean_db`
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestSomething:
    def test_by_hello(self, faker: Faker, something_factory: Any):
        """Filter `.by_hello` works."""
        first = something_factory()
        second = something_factory()

        smth = model.Session.scalar(Something.by_hello(first["hello"]))
        assert smth.id == first["id"]

        smth = model.Session.scalar(Something.by_hello(second["hello"]))
        assert smth.id == second["id"]

    def test_dictization(self, something: dict[str, Any]):
        """Plugin data excluded from dictized form by default."""
        smth = model.Session.get(Something, something["id"])
        assert smth.dictize({}) == {
            "id": something["id"],
            "hello": something["hello"],
            "world": something["world"],
        }

        assert smth.dictize({"include_plugin_data": True}) == {
            "id": something["id"],
            "hello": something["hello"],
            "world": something["world"],
            "plugin_data": smth.plugin_data,
        }
