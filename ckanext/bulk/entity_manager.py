from __future__ import annotations

from abc import abstractmethod
from typing import Any, TypedDict

import ckan.plugins.toolkit as tk

from ckanext.bulk import const


class FilterItem(TypedDict):
    field: str
    operator: str
    value: str


class CombinedFilter(TypedDict):
    field: str
    operator: str
    values: list[str]


class FieldItem(TypedDict):
    value: str
    text: str


class EntityMissingError(Exception):
    def __init__(self, entity_type: str):
        super().__init__(f"EntityManager type {entity_type} not found")


class SchemingEntityMissingError(Exception):
    def __init__(self, entity_type: str, object_type: str):
        super().__init__(f"Schema not found for {entity_type} {object_type}")


class EntityManager:
    entity_type = ""

    @classmethod
    @abstractmethod
    def get_fields(cls) -> list[FieldItem]:
        pass

    @classmethod
    @abstractmethod
    def search_entities_by_filters(
        cls, filters: list[FilterItem], global_operator: str = "AND"
    ) -> list[dict[str, Any]]:
        pass

    @classmethod
    def combine_filters(cls, filters: list[FilterItem]) -> list[CombinedFilter]:
        combined_filters = []

        current_field = None
        current_operator = None
        current_values = []

        for filter_item in filters:
            if (
                filter_item["field"] == current_field
                and filter_item["operator"] == current_operator
            ):
                current_values.append(filter_item["value"])
            else:
                if current_field and current_operator:
                    combined_filters.append(
                        {
                            "field": current_field,
                            "operator": current_operator,
                            "values": current_values,
                        }
                    )

                current_field = filter_item["field"]
                current_operator = filter_item["operator"]
                current_values = [filter_item["value"]]

        if current_field and current_operator:
            combined_filters.append(
                {
                    "field": current_field,
                    "operator": current_operator,
                    "values": current_values,
                }
            )

        return combined_filters


class DatasetEntityManager(EntityManager):
    entity_type = "dataset"

    @classmethod
    def get_fields(cls) -> list[FieldItem]:
        result = tk.get_action("package_search")(
            {"ignore_auth": True}, {"rows": 1, "include_private": True}
        )

        if not result["results"]:
            return []

        return [FieldItem(value=field, text=field) for field in result["results"][0]]

    @classmethod
    def search_entities_by_filters(
        cls, filters: list[FilterItem], global_operator: str = "AND"
    ) -> list[dict[str, Any]]:
        """Search entities by the provided filters.

        Example of filters:
        [
            {'field': 'author', 'operator': 'is', 'value': 'Alex'},
            {'field': 'author', 'operator': 'is_not', 'value': 'John'},
            {'field': 'title', 'operator': 'contains', 'value': 'data'},
        ]

        The filters are combined with an AND operator.
        """
        q_list = []

        for f in filters:
            operator = f["operator"]

            if operator == const.OP_IS:
                q_list.append(f"{f['field']}:\"{f['value']}\"")
            elif operator == const.OP_IS_NOT:
                q_list.append(f"-{f['field']}:\"{f['value']}\"")
            elif operator == const.OP_CONTAINS:
                q_list.append(f"{f['field']}:*{f['value']}*")
            elif operator == const.OP_DOES_NOT_CONTAIN:
                q_list.append(f"-{f['field']}:*{f['value']}*")
            elif operator == const.OP_STARTS_WITH:
                q_list.append(f"{f['field']}:{f['value']}*")
            elif operator == const.OP_ENDS_WITH:
                q_list.append(f"{f['field']}:*{f['value']}")
            elif operator == const.OP_IS_EMPTY:
                q_list.append(f"-{f['field']}:[* TO *]")
            elif operator == const.OP_IS_NOT_EMPTY:
                q_list.append(f"{f['field']}:[* TO *]")

        query = f" {global_operator} ".join(q_list)

        return tk.get_action("package_search")(
            {"ignore_auth": True}, {"q": query, "include_private": True}
        )["results"]


class GroupEntityManager(EntityManager):
    entity_type = "group"
    action = "group_list"

    @classmethod
    def get_fields(cls) -> list[FieldItem]:
        item_list = tk.get_action(cls.action)(
            {"ignore_auth": True}, {"all_fields": True}
        )

        if not item_list:
            return []

        return [
            {
                "value": field,
                "text": field,
            }
            for field in item_list[0]
        ]

    @classmethod
    def search_entities_by_filters(
        cls, filters: list[FilterItem], global_operator: str = "AND"
    ) -> list[dict[str, Any]]:
        """Search entities by the provided filters.

        Example of filters:
        [
            {'field': 'author', 'operator': 'is', 'value': 'Alex'},
            {'field': 'author', 'operator': 'is_not', 'value': 'John'},
            {'field': 'title', 'operator': 'contains', 'value': 'data'},
        ]

        The filters are combined with an AND operator. In theory we could
        support OR operators, but we're going to keep it simple for now.

        If we need an OR operator we should use `any` instead of `all` func.
        """
        # TODO: for now we're going to fetch only 25 groups
        item_list = tk.get_action(cls.action)(
            {"ignore_auth": True}, {"all_fields": True}
        )

        filltered_items = []
        combined_filters = cls.combine_filters(filters)
        check_func = all if global_operator == "AND" else any

        for item in item_list:
            add_item = False

            for f in combined_filters:
                operator = f["operator"]

                if f["field"] not in item:
                    break

                if operator == const.OP_IS:
                    add_item = check_func(
                        value == item[f["field"]] for value in f["values"]
                    )
                elif operator == const.OP_IS_NOT:
                    add_item = check_func(
                        value != item[f["field"]] for value in f["values"]
                    )
                elif operator == const.OP_CONTAINS:
                    add_item = check_func(
                        value in item[f["field"]] for value in f["values"]
                    )
                elif operator == const.OP_DOES_NOT_CONTAIN:
                    add_item = check_func(
                        value not in item[f["field"]] for value in f["values"]
                    )
                elif operator == const.OP_STARTS_WITH:
                    add_item = check_func(
                        item[f["field"]].startswith(value) for value in f["values"]
                    )
                elif operator == const.OP_ENDS_WITH:
                    add_item = check_func(
                        item[f["field"]].endswith(value) for value in f["values"]
                    )
                elif operator == const.OP_IS_EMPTY:
                    add_item = not item[f["field"]]
                elif operator == const.OP_IS_NOT_EMPTY:
                    add_item = bool(item[f["field"]])

                if not add_item:
                    break

            if add_item:
                filltered_items.append(item)

        return filltered_items


class OrganizationEntityManager(GroupEntityManager):
    entity_type = "organization"
    action = "organization_list"


def get_entity_managers() -> dict[str, type[EntityManager]]:
    return {
        "Dataset": DatasetEntityManager,
        "Organization": OrganizationEntityManager,
        "Group": GroupEntityManager,
    }


def get_entity_manager(entity_type: str) -> type[EntityManager]:
    for entity_manager in get_entity_managers().values():
        if entity_manager.entity_type == entity_type:
            return entity_manager

    raise EntityMissingError(entity_type)
