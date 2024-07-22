"""Tests for ckanext.bulk.logic.action."""

import pytest
from faker import Faker

from ckan import model
from ckan.tests.helpers import call_action

from ckanext.bulk.model import Something


@pytest.mark.ckan_config("ckan.plugins", "bulk")
@pytest.mark.usefixtures("with_plugins")
def test_get_sum():
    """Sum is correct."""
    result = call_action("bulk_get_sum", left=10, right=30)
    assert result["sum"] == 40


@pytest.mark.ckan_config("ckan.plugins", "bulk")
@pytest.mark.usefixtures("with_plugins")
def test_something_create(faker: Faker):
    """Something is created."""
    hello = faker.word()
    world = faker.word()

    # action tests use `call_action` to skip authorization check. All auth
    # functions are checked separately.
    result = call_action(
        "bulk_something_create",
        hello=hello,
        world=world,
    )

    # if validation covered by schema, do not verify it inside action
    # test. Basically, test the result of action, not it's internal
    # implementation details.
    assert result["hello"] == hello
    assert result["world"] == world

    smth = model.Session.get(Something, result["id"])
    assert smth.hello == hello
