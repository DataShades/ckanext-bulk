from __future__ import annotations

import logging
from typing import Any

import ckan.plugins.toolkit as tk

from ckanext.bulk import const
from ckanext.bulk.entity_managers import base

log = logging.getLogger(__name__)


class DatasetEntityManager(base.EntityManager):
    entity_type = "dataset"
    show_action = "package_show"
    patch_action = "package_patch"
    delete_action = "package_delete"

    @classmethod
    def get_fields(cls) -> list[base.FieldItem]:
        if fields := cls.get_fields_from_redis():
            return fields

        result = tk.get_action("package_search")(
            {"ignore_auth": True},
            {"rows": 1, "include_private": True, "q": f'type:"{cls.entity_type}"'},
        )

        if not result["results"]:
            return []

        fields = [
            base.FieldItem(value=field, text=field) for field in result["results"][0]
        ]

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
                q_list.append(f"(*:* AND -{f['field']}:*)")
            elif operator == const.OP_IS_NOT_EMPTY:
                q_list.append(f"{f['field']}:*")

        return cls._fetch_search_results(
            f'type:"{cls.entity_type}" AND ({f" {global_operator} ".join(q_list)})'
        )

    @classmethod
    def _fetch_search_results(cls, query: str) -> list[dict[str, Any]]:
        log.debug(f"Bulk. Performing search with query: {query} for {cls.entity_type}")

        rows = 1000
        start = 0
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
