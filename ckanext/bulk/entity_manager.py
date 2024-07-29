from __future__ import annotations

import json
from abc import abstractmethod
from typing import Any, TypedDict

from attr import field

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.lib.redis import connect_to_redis

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


class UpdateItem(TypedDict):
    field: str
    value: str


class EntityMissingError(Exception):
    def __init__(self, entity_type: str):
        super().__init__(f"EntityManager type {entity_type} not found")


class EntityManager:
    entity_type = ""
    show_action = ""
    patch_action = ""
    delete_action = ""

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
    def get_entity_by_id(cls, entity_id: str) -> dict[str, Any] | None:
        try:
            group = tk.get_action(cls.show_action)(
                {"ignore_auth": True}, {"id": entity_id}
            )
        except tk.ObjectNotFound:
            return None

        return group

    @classmethod
    def combine_filters(cls, filters: list[FilterItem]) -> list[CombinedFilter]:
        combined_filters: list[CombinedFilter] = []

        current_field = ""
        current_operator = ""
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
                        CombinedFilter(
                            field=current_field,
                            operator=current_operator,
                            values=current_values,
                        )
                    )

                current_field = filter_item["field"]
                current_operator = filter_item["operator"]
                current_values = [filter_item["value"]]

        if current_field and current_operator:
            combined_filters.append(
                CombinedFilter(
                    field=current_field,
                    operator=current_operator,
                    values=current_values,
                )
            )

        return combined_filters

    @classmethod
    def update_entity(
        cls, entity_id: str, update_items: list[UpdateItem]
    ) -> dict[str, Any]:
        entity = cls.get_entity_by_id(entity_id)

        if not entity:
            raise tk.ObjectNotFound(f"Entity <{entity_id}> not found")

        return tk.get_action(cls.patch_action)(
            {"ignore_auth": True},
            {
                "id": entity_id,
                **cls.update_items_to_dict(update_items),
            },
        )

    @classmethod
    def update_items_to_dict(cls, update_items: list[UpdateItem]) -> dict[str, Any]:
        return {item["field"]: item["value"] for item in update_items}

    @classmethod
    def delete_entity(cls, entity_id: str) -> bool:
        tk.get_action(cls.delete_action)({"ignore_auth": True}, {"id": entity_id})

        return True

    @classmethod
    def cache_fields_to_redis(cls, fields: list[FieldItem], ttl: int = 3600):
        conn = connect_to_redis()
        conn.set(f"ckanext-bulk:fields:{cls.entity_type}", json.dumps(fields), ex=ttl)

    @classmethod
    def get_fields_from_redis(cls) -> list[FieldItem]:
        conn = connect_to_redis()

        fields = conn.get(f"ckanext-bulk:fields:{cls.entity_type}")

        if not fields:
            return []

        return json.loads(fields)


class DatasetEntityManager(EntityManager):
    entity_type = "dataset"
    show_action = "package_show"
    patch_action = "package_patch"
    delete_action = "package_delete"

    @classmethod
    def get_fields(cls) -> list[FieldItem]:
        if fields := cls.get_fields_from_redis():
            return fields

        result = tk.get_action("package_search")(
            {"ignore_auth": True},
            {"rows": 1, "include_private": True, "q": f'type:"{cls.entity_type}"'},
        )

        if not result["results"]:
            return []

        fields = [FieldItem(value=field, text=field) for field in result["results"][0]]

        cls.cache_fields_to_redis(fields)

        return fields

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
        query = f"type:\"{cls.entity_type}\" AND {query}"

        start = 0
        rows = 1000

        results = []

        while True:
            result = tk.get_action("package_search")(
                {"ignore_auth": True},
                {
                    "q": query,
                    "rows": rows,
                    "start": start,
                    "include_private": True,
                    "include_drafts": True,
                },
            )

            results.extend(result["results"])

            start += len(result["results"])

            if start >= result["count"]:
                break

        return results


class DatasetResourceEntityManager(EntityManager):
    entity_type = "dataset_resource"

    show_action = "resource_show"
    patch_action = "resource_patch"
    delete_action = "resource_delete"

    @classmethod
    def get_fields(cls) -> list[FieldItem]:
        if fields := cls.get_fields_from_redis():
            return fields

        resource: model.Resource | None = (
            model.Session.query(model.Resource)
            .join(model.Package)
            .filter(model.Package.type == "dataset")
            .first()
        )

        if not resource:
            return []

        fields = [
            FieldItem(value=field, text=field) for field in resource.get_columns()
        ]

        cls.cache_fields_to_redis(fields)

        return fields

    @classmethod
    def search_entities_by_filters(
        cls, filters: list[FilterItem], global_operator: str = "AND"
    ) -> list[dict[str, Any]]:
        """Search for entities by the provided filters.

        Since we are using CKAN resource_search action, we can't support
        all the operators that we have in the frontend.

        TODO: We should add support for more operators in the future.
        """
        supported_operators = [const.OP_IS]

        for f in filters:
            operator = f["operator"]

            if operator not in supported_operators:
                raise ValueError(f"Operator {operator} not supported")

        # TODO: throw away filters without value, because resource_search
        # could throw a DatabaseError for an empty filter query
        query = [f"{f['field']}:{f['value']}" for f in filters if f["value"]]

        return tk.get_action("resource_search")(
            {"ignore_auth": True}, {"query": query, "include_private": True}
        )["results"]


class GroupEntityManager(EntityManager):
    entity_type = "group"

    list_action = "group_list"
    show_action = "group_show"
    patch_action = "group_patch"
    delete_action = "group_delete"

    @classmethod
    def get_fields(cls) -> list[FieldItem]:
        if fields := cls.get_fields_from_redis():
            return fields

        item_list: list[dict[str, Any]] = tk.get_action(cls.show_action)(
            {"ignore_auth": True}, {"all_fields": True, "rows": 1}
        )

        if not item_list:
            return []

        fields = [FieldItem(value=field, text=field) for field in item_list[0]]

        cls.cache_fields_to_redis(fields)

        return fields

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
        # TODO: for now we're going to fetch only 25 groups due to some
        # core restrictions.
        item_list = tk.get_action(cls.list_action)(
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

    list_action = "organization_list"
    show_action = "organization_show"
    patch_action = "organization_patch"
    delete_action = "organization_delete"


def get_entity_managers() -> dict[str, type[EntityManager]]:
    return {
        "Dataset": DatasetEntityManager,
        "Resource": DatasetResourceEntityManager,
        "Organization": OrganizationEntityManager,
        "Group": GroupEntityManager,
    }


def get_entity_manager(entity_type: str) -> type[EntityManager]:
    for entity_manager in get_entity_managers().values():
        if entity_manager.entity_type == entity_type:
            return entity_manager

    raise EntityMissingError(entity_type)
