from __future__ import annotations

import pytest

from ckanext.bulk import const


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestGroupEntityManager:
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
class TestOrganizationEntityManager:
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
class TestDatasetEntityManager:
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
