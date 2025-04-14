from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.bulk import const


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestGroupEntityManagerSearch:
    def test_filter_is(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_IS, "value": "test"}]
        )

        assert result

    def test_filter_is_not(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_IS_NOT, "value": "test"}]
        )

        assert not result

    def test_filter_ends_with(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_ENDS_WITH, "value": "st"}]
        )

        assert result

    def test_filter_stars_with(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_STARTS_WITH, "value": "te"}]
        )

        assert result

    def test_filter_contains(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_CONTAINS, "value": "es"}]
        )

        assert result

    def test_filter_doesnt_contain(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_DOES_NOT_CONTAIN, "value": "es"}]
        )

        assert not result

    def test_filter_is_empty(self, group_entity_manager, group_factory):
        group_factory(name="test", image_url="")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "image_url", "operator": const.OP_IS_EMPTY, "value": ""}]
        )

        assert result

    def test_filter_is_not_empty(self, group_entity_manager, group_factory):
        group_factory(name="test", image_url="test")

        result = group_entity_manager.search_entities_by_filters(
            [{"field": "image_url", "operator": const.OP_IS_NOT_EMPTY, "value": ""}]
        )

        assert result

    def test_combine_filters_1(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [
                {"field": "name", "operator": const.OP_IS, "value": "test"},
                {"field": "name", "operator": const.OP_IS_NOT, "value": "test"},
            ]
        )

        assert not result

    def test_combine_filters_2(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [
                {"field": "name", "operator": const.OP_IS, "value": "test"},
                {"field": "name", "operator": const.OP_ENDS_WITH, "value": "st"},
            ]
        )

        assert result

    def test_combine_filters_3(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [
                {"field": "name", "operator": const.OP_IS, "value": "test"},
                {"field": "name", "operator": const.OP_DOES_NOT_CONTAIN, "value": "es"},
            ]
        )

        assert not result

    def test_combine_filters_4(self, group_entity_manager, group_factory):
        group_factory(name="test")

        result = group_entity_manager.search_entities_by_filters(
            [
                {"field": "name", "operator": const.OP_IS, "value": "test"},
                {"field": "name", "operator": const.OP_CONTAINS, "value": "es"},
            ]
        )

        assert result

    def test_multiple_items_1(self, group_entity_manager, group_factory):
        group_factory(name="test")
        group_factory(name="test2")

        result = group_entity_manager.search_entities_by_filters(
            [
                {"field": "name", "operator": const.OP_IS, "value": "test"},
                {"field": "name", "operator": const.OP_IS, "value": "test2"},
                {"field": "name", "operator": const.OP_IS_NOT, "value": "test3"},
                {"field": "title", "operator": const.OP_IS_NOT, "value": "test title"},
            ]
        )

        assert len(result) == 0

    def test_multiple_items_2(self, group_entity_manager, group_factory):
        group_factory(name="test")
        group_factory(name="test2")

        result = group_entity_manager.search_entities_by_filters(
            [
                {"field": "name", "operator": const.OP_IS, "value": "test"},
                {"field": "name", "operator": const.OP_IS_NOT, "value": "test2"},
            ]
        )

        assert len(result) == 1

    def test_multiple_items_3(self, group_entity_manager, group_factory):
        group_factory(name="test")
        group_factory(name="test2")

        result = group_entity_manager.search_entities_by_filters(
            [
                {"field": "name", "operator": const.OP_STARTS_WITH, "value": "te"},
                {"field": "name", "operator": const.OP_ENDS_WITH, "value": "st"},
            ]
        )

        assert len(result) == 1


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestGroupEntityManagerUpdate:
    def test_update_group(self, group_entity_manager, group_factory):
        group = group_factory()

        result = group_entity_manager.update_entity(
            group["id"], [{"field": "name", "value": "xxx"}]
        )

        assert result["name"] == "xxx"

    def test_update_group_doesnt_exist(self, group_entity_manager, group_factory):
        group_factory()

        with pytest.raises(tk.ObjectNotFound):
            group_entity_manager.update_entity("no-match", {"name": "new name"})

    def test_update_group_invalid_field(self, group_entity_manager, group_factory):
        group = group_factory()

        result = group_entity_manager.update_entity(
            group["id"], [{"field": "new_field", "value": "xxx"}]
        )

        assert "new_field" not in result

    def test_update_id_field(self, group_entity_manager, group_factory):
        group_factory()

        with pytest.raises(tk.ObjectNotFound):
            group_entity_manager.update_entity("no-match", {"id": "new-id"})


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestGroupEntityManagerDelete:
    def test_delete_group(self, group_entity_manager, group_factory):
        group = group_factory()

        assert group_entity_manager.delete_entity(group["id"]) is True
        assert model.Group.get(group["id"]).state == model.State.DELETED  # type: ignore

    def test_delete_group_doesnt_exist(self, group_entity_manager, group_factory):
        group_factory()

        with pytest.raises(tk.ObjectNotFound):
            group_entity_manager.delete_entity("no-match")
