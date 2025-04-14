from __future__ import annotations

import pytest

import ckan.model as model
import ckan.plugins.toolkit as tk

from ckanext.bulk import const


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestDatasetResourceEntityManagerSearch:
    def test_filter_is(self, dataset_resource_entity_manager, resource_factory):
        resource_factory(format="test")

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [{"field": "format", "operator": const.OP_IS, "value": "test"}]
        )

        assert result

    def test_filter_is_no_match(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory(format="test")

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [{"field": "format", "operator": const.OP_IS, "value": "no match"}]
        )

        assert not result

    def test_operator_is_not_supported(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory(format="test")

        with pytest.raises(ValueError, match="Operator contains not supported"):
            dataset_resource_entity_manager.search_entities_by_filters(
                [{"field": "format", "operator": const.OP_CONTAINS, "value": "test"}]
            )

    @pytest.mark.parametrize(
        ("field_name", "value"),
        [
            ("name", "new_name"),
            ("format", "new_format"),
            ("url", "http://example.com"),
            ("description", "test"),
        ],
    )
    def test_search_by_field(
        self, field_name, value, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory(**{field_name: value})

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [{"field": field_name, "operator": const.OP_IS, "value": value}]
        )

        assert result

    def test_search_similar_titles(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory(name="csv data")
        resource_factory(name="information csv")

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_IS, "value": "csv data"}]
        )

        assert len(result) == 1

    def test_search_title_exact_match(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory(name="csv data")

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_IS, "value": "csv data"}]
        )

        assert len(result) == 1

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [{"field": "name", "operator": const.OP_IS, "value": "csv"}]
        )

        assert not result

    def test_search_by_extra_field(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory(attribution="XXX111")

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [{"field": "attribution", "operator": const.OP_IS, "value": "XXX111"}]
        )

        assert result

    def test_search_with_or_operator(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory(format="CSV")
        resource_factory(format="XLSX")

        result = dataset_resource_entity_manager.search_entities_by_filters(
            [
                {"field": "format", "operator": const.OP_IS, "value": "CSV"},
                {"field": "format", "operator": const.OP_IS, "value": "XLSX"},
            ],
            const.GLOBAL_OR,
        )

        assert result


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestDatasetResourceEntityManagerUpdate:
    def test_update_dataset_resource(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource = resource_factory()

        result = dataset_resource_entity_manager.update_entity(
            resource["id"], [{"field": "format", "value": "xxx"}]
        )

        assert result["format"] == "xxx"

    def test_update_dataset_resource_doesnt_exist(
        self, dataset_resource_entity_manager, resource_factory
    ):
        with pytest.raises(tk.ObjectNotFound):
            dataset_resource_entity_manager.update_entity(
                "no-match", [{"field": "format", "value": "new"}]
            )

    def test_update_dataset_resource_new_field(
        self, dataset_resource_entity_manager, resource_factory
    ):
        """For some reason CKAN tend to save new fields for resources."""
        resource = resource_factory()

        result = dataset_resource_entity_manager.update_entity(
            resource["id"], [{"field": "new_field", "value": "xxx"}]
        )

        assert "new_field" in result

    def test_update_dataset_resource_empty_field(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource = resource_factory()

        result = dataset_resource_entity_manager.update_entity(
            resource["id"], [{"field": "format", "value": ""}]
        )

        assert not result["format"]

    def test_update_id_field(self, dataset_resource_entity_manager, resource_factory):
        resource_factory()

        with pytest.raises(tk.ObjectNotFound):
            dataset_resource_entity_manager.update_entity(
                "no-match", [{"field": "id", "value": "new-id"}]
            )


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestDatasetResourceEntityManagerDelete:
    def test_delete_dataset_resource(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource = resource_factory()

        assert dataset_resource_entity_manager.delete_entity(resource["id"]) is True
        assert model.Resource.get(resource["id"]).state == model.State.DELETED  # type: ignore

    def test_delete_dataset_resource_doesnt_exist(
        self, dataset_resource_entity_manager, resource_factory
    ):
        resource_factory()

        with pytest.raises(tk.ObjectNotFound):
            dataset_resource_entity_manager.delete_entity("no-match")
