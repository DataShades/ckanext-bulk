from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.bulk import const


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestOrganizationEntityManagerSearch:
    def test_filter_is(self, organization_entity_manager, organization_factory):
        organization_factory(name="test")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_IS, "value": "test"}]
        )

        assert result

    def test_filter_is_not(self, organization_entity_manager, organization_factory):
        organization_factory(name="test")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_IS_NOT, "value": "test"}]
        )

        assert not result

    def test_filter_ends_with(self, organization_entity_manager, organization_factory):
        organization_factory(name="test")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_ENDS_WITH, "value": "st"}]
        )

        assert result

    def test_filter_stars_with(self, organization_entity_manager, organization_factory):
        organization_factory(name="test")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_STARTS_WITH, "value": "te"}]
        )

        assert result

    def test_filter_contains(self, organization_entity_manager, organization_factory):
        organization_factory(name="test")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_CONTAINS, "value": "es"}]
        )

        assert result

    def test_filter_doesnt_contain(
        self, organization_entity_manager, organization_factory
    ):
        organization_factory(name="test")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_DOES_NOT_CONTAIN, "value": "es"}]
        )

        assert not result

    def test_filter_is_empty(self, organization_entity_manager, organization_factory):
        organization_factory(name="test", image_url="")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "image_url", "operator": const.OP_IS_EMPTY, "value": ""}]
        )

        assert result

    def test_filter_is_not_empty(
        self, organization_entity_manager, organization_factory
    ):
        organization_factory(name="test", image_url="test")

        result = organization_entity_manager.search_entities_by_filters(
            [{"field": "image_url", "operator": const.OP_IS_NOT_EMPTY, "value": ""}]
        )

        assert result


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestOrganizationEntityManagerUpdate:
    def test_update_group(self, organization_entity_manager, organization_factory):
        organization = organization_factory()

        result = organization_entity_manager.update_entity(
            organization["id"], [{"field": "name", "value": "xxx"}]
        )

        assert result["name"] == "xxx"

    def test_update_group_doesnt_exist(
        self, organization_entity_manager, organization_factory
    ):
        organization_factory()

        with pytest.raises(tk.ObjectNotFound):
            organization_entity_manager.update_entity("no-match", {"name": "new name"})

    def test_update_group_invalid_field(
        self, organization_entity_manager, organization_factory
    ):
        organization = organization_factory()

        result = organization_entity_manager.update_entity(
            organization["id"], [{"field": "new_field", "value": "xxx"}]
        )

        assert "new_field" not in result

    def test_update_id_field(self, organization_entity_manager, organization_factory):
        organization_factory()

        with pytest.raises(tk.ObjectNotFound):
            organization_entity_manager.update_entity("no-match", {"id": "new-id"})


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestOrganizationEntityManagerDelete:
    def test_delete_organization(
        self, organization_entity_manager, organization_factory
    ):
        organization = organization_factory()

        assert organization_entity_manager.delete_entity(organization["id"]) is True
        assert model.Group.get(organization["id"]).state == model.State.DELETED  # type: ignore

    def test_delete_organization_doesnt_exist(
        self, organization_entity_manager, organization_factory
    ):
        organization_factory()

        with pytest.raises(tk.ObjectNotFound):
            organization_entity_manager.delete_entity("no-match")
