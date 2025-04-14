from __future__ import annotations

import json
from abc import abstractmethod
from typing import Any, TypedDict

import ckan.plugins.toolkit as tk
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
        cls, filters: list[FilterItem], global_operator: str = const.GLOBAL_AND
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

        return json.loads(fields)  # type: ignore
