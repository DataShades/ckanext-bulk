from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.bulk import const


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestDatasetEntityManagerSearch:
    def test_filter_is(self, dataset_entity_manager, package_factory):
        package_factory(title="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "title", "operator": const.OP_IS, "value": "test"}]
        )

        assert result

    def test_filter_is_not(self, dataset_entity_manager, package_factory):
        package_factory(title="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "title", "operator": const.OP_IS_NOT, "value": "test"}]
        )

        assert not result

    def test_filter_ends_with(self, dataset_entity_manager, package_factory):
        package_factory(title="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "title", "operator": const.OP_ENDS_WITH, "value": "st"}]
        )

        assert result

    def test_filter_stars_with(self, dataset_entity_manager, package_factory):
        package_factory(title="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "title", "operator": const.OP_STARTS_WITH, "value": "te"}]
        )

        assert result

    def test_filter_contains(self, dataset_entity_manager, package_factory):
        package_factory(title="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "title", "operator": const.OP_CONTAINS, "value": "es"}]
        )

        assert result

    def test_filter_doesnt_contain(self, dataset_entity_manager, package_factory):
        package_factory(title="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "title", "operator": const.OP_DOES_NOT_CONTAIN, "value": "es"}]
        )

        assert not result

    def test_filter_is_empty(self, dataset_entity_manager, package_factory):
        package_factory(title="test", notes="")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "notes", "operator": const.OP_IS_EMPTY, "value": ""}]
        )

        assert result

    def test_filter_is_empty_or(self, dataset_entity_manager, package_factory):
        package_factory(title="test", notes="")

        result = dataset_entity_manager.search_entities_by_filters(
            [
                {"field": "notes", "operator": const.OP_IS_EMPTY, "value": ""},
                {"field": "title", "operator": const.OP_CONTAINS, "value": "test"},
            ],
            const.GLOBAL_OR,
        )

        assert result

    def test_filter_is_not_empty(self, dataset_entity_manager, package_factory):
        package_factory(title="test", notes="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "notes", "operator": const.OP_IS_NOT_EMPTY, "value": ""}]
        )

        assert result

    def test_filter_is_not_empty_or(self, dataset_entity_manager, package_factory):
        package_factory(title="test", notes="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [
                {"field": "notes", "operator": const.OP_IS_NOT_EMPTY, "value": ""},
                {"field": "title", "operator": const.OP_IS_NOT_EMPTY, "value": ""},
            ],
            const.GLOBAL_OR,
        )

        assert result


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestDatasetEntityManagerUpdate:
    def test_update_dataset(self, dataset_entity_manager, package_factory):
        dataset = package_factory(title="test")

        result = dataset_entity_manager.update_entity(
            dataset["id"], [{"field": "title", "value": "xxx"}]
        )

        assert result["title"] == "xxx"

    def test_update_dataset_doesnt_exist(self, dataset_entity_manager, package_factory):
        package_factory()

        with pytest.raises(tk.ObjectNotFound):
            dataset_entity_manager.update_entity("no-match", {"title": "new title"})

    def test_update_dataset_invalid_field(
        self, dataset_entity_manager, package_factory
    ):
        dataset = package_factory()

        result = dataset_entity_manager.update_entity(
            dataset["id"], [{"field": "new_field", "value": "xxx"}]
        )

        assert "new_field" not in result

    def test_update_dataset_empty_field(self, dataset_entity_manager, package_factory):
        dataset = package_factory()

        result = dataset_entity_manager.update_entity(
            dataset["id"], [{"field": "title", "value": ""}]
        )

        assert result["title"] == result["name"]

    def test_update_id_field(self, dataset_entity_manager, package_factory):
        """Try to provide an id as a filter.

        The id field is not updatable, because it will be merged into
        a final payload for the patch method and replace the id we're passing
        """
        package_factory(title="test")

        with pytest.raises(tk.ObjectNotFound):
            dataset_entity_manager.update_entity(
                "no-match", [{"field": "id", "value": "new-id"}]
            )


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestDatasetEntityManagerDelete:
    def test_delete_dataset(self, dataset_entity_manager, package_factory):
        dataset = package_factory()

        assert dataset_entity_manager.delete_entity(dataset["id"]) is True
        assert model.Package.get(dataset["id"]).state == model.State.DELETED  # type: ignore

    def test_delete_dataset_doesnt_exist(self, dataset_entity_manager, package_factory):
        package_factory()

        with pytest.raises(tk.ObjectNotFound):
            dataset_entity_manager.delete_entity("no-match")
