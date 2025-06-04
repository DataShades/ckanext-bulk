from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.bulk import const
from ckanext.bulk.entity_managers import base
from ckanext.bulk.entity_managers.base import CombinedFilter


class GroupEntityManager(base.EntityManager):
    entity_type = "group"

    list_action = "group_list"
    show_action = "group_show"
    patch_action = "group_patch"
    delete_action = "group_delete"

    @classmethod
    def get_fields(cls) -> list[base.FieldItem]:
        if fields := cls.get_fields_from_redis():
            return fields

        item_list: list[dict[str, Any]] = tk.get_action(cls.list_action)(
            {"ignore_auth": True},
            {
                "all_fields": True,
                "include_extras": True,
                "limit": 1,
                "include_dataset_count": False,
            },
        )

        if not item_list:
            return []

        fields = [base.FieldItem(value=field, text=field) for field in item_list[0]]

        cls.cache_fields_to_redis(fields)

        return fields

    @classmethod
    def search_entities_by_filters(
        cls, filters: list[base.FilterItem], global_operator: str = const.GLOBAL_AND
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

        combined_filters = cls.combine_filters(filters)
        check_func = all if global_operator == const.GLOBAL_AND else any

        def _check_filter(item: dict[str, Any], filter_: CombinedFilter) -> bool:
            """Check if an item matches a single filter."""
            if filter_["field"] not in item:
                return False

            operator = filter_["operator"]
            field_value = item[filter_["field"]]

            operator_checks = {
                const.OP_IS: lambda v: v == field_value,
                const.OP_IS_NOT: lambda v: v != field_value,
                const.OP_CONTAINS: lambda v: v in field_value,
                const.OP_DOES_NOT_CONTAIN: lambda v: v not in field_value,
                const.OP_STARTS_WITH: lambda v: field_value.startswith(v),
                const.OP_ENDS_WITH: lambda v: field_value.endswith(v),
                const.OP_IS_EMPTY: lambda _: not field_value,
                const.OP_IS_NOT_EMPTY: lambda _: bool(field_value),
            }

            if operator not in operator_checks:
                return False

            return check_func(
                operator_checks[operator](value) for value in filter_["values"]
            )

        def _check_item(item: dict[str, Any]) -> bool:
            """Check if an item matches all filters."""
            return all(_check_filter(item, f) for f in combined_filters)

        return [item for item in item_list if _check_item(item)]
