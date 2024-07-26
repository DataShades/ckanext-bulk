from __future__ import annotations

import pytest

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

    def test_filter_is_not_empty(self, dataset_entity_manager, package_factory):
        package_factory(title="test", notes="test")

        result = dataset_entity_manager.search_entities_by_filters(
            [{"field": "notes", "operator": const.OP_IS_NOT_EMPTY, "value": ""}]
        )

        assert result


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
