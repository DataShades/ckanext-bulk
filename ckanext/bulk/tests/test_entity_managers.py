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
class TestDatasetEntityManagerDelete:
    def test_delete_dataset(self, dataset_entity_manager, package_factory):
        dataset = package_factory()

        assert dataset_entity_manager.delete_entity(dataset["id"]) is True
        assert model.Package.get(dataset["id"]).state == model.State.DELETED  # type: ignore

    def test_delete_dataset_doesnt_exist(self, dataset_entity_manager, package_factory):
        package_factory()

        with pytest.raises(tk.ObjectNotFound):
            dataset_entity_manager.delete_entity("no-match")


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
