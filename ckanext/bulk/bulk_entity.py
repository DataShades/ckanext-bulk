from __future__ import annotations

from abc import abstractmethod
from typing import Any, TypedDict

import ckan.plugins.toolkit as tk


class FilterItem(TypedDict):
    field: str
    operator: str
    value: str


class FieldItem(TypedDict):
    value: str
    text: str


class EntityMissingError(Exception):
    def __init__(self, entity_type: str):
        super().__init__(f"Entity type {entity_type} not found")


class SchemingEntityMissingError(Exception):
    def __init__(self, entity_type: str, object_type: str):
        super().__init__(f"Schema not found for {entity_type} {object_type}")


class Entity:
    entity_type = ""

    @staticmethod
    @abstractmethod
    def get_fields() -> list[FieldItem]:
        pass

    @staticmethod
    @abstractmethod
    def search_entities_by_filters(filters: list[FilterItem]) -> list[dict[str, Any]]:
        pass


class SchemingEntity(Entity):
    entity_type = ""

    @staticmethod
    def get_schema(entity_type: str, object_type: str) -> dict[str, Any]:
        schema = tk.h.scheming_get_schema(entity_type, object_type)

        if not schema:
            raise SchemingEntityMissingError(entity_type, object_type)

        return schema


class DatasetEntity(SchemingEntity):
    entity_type = "dataset"

    @staticmethod
    def get_fields() -> list[FieldItem]:
        schema = SchemingEntity.get_schema("dataset", DatasetEntity.entity_type)

        return [
            {
                "value": field["field_name"],
                "text": field["label"],
            }
            for field in schema.get("dataset_fields", [])
        ]

    @staticmethod
    def search_entities_by_filters(filters: list[FilterItem]) -> list[dict[str, Any]]:
        """Search entities by the provided filters.

        Example of filters:
        [
            {'field': 'author', 'operator': 'is', 'value': 'Alex'},
            {'field': 'author', 'operator': 'is_not', 'value': 'John'},
            {'field': 'title', 'operator': 'contains', 'value': 'data'},
        ]
        """
        fq_list = []

        for filter in filters:
            if filter["operator"] == "is":
                fq_list.append(f"{filter['field']}:\"{filter['value']}\"")
            elif filter["operator"] == "is_not":
                fq_list.append(f"-{filter['field']}:\"{filter['value']}\"")
            elif filter["operator"] == "contains":
                fq_list.append(f"{filter['field']}:*{filter['value']}*")
            elif filter["operator"] == "does_not_contain":
                fq_list.append(f"-{filter['field']}:*{filter['value']}*")
            elif filter["operator"] == "starts_with":
                fq_list.append(f"{filter['field']}:{filter['value']}*")
            elif filter["operator"] == "ends_with":
                fq_list.append(f"{filter['field']}:*{filter['value']}")

        fq = " AND ".join(fq_list)

        return tk.get_action("package_search")(
            {"ignore_auth": True}, {"fq": fq, "include_private": True}
        )["results"]


class OrganizationEntity(SchemingEntity):
    entity_type = "organization"

    def get_fields(self) -> list[str]:
        schema = SchemingEntity.get_schema("organization", self.entity_type)

        return list(schema["fields"].keys())


class GroupEntity(SchemingEntity):
    entity_type = "group"

    def get_fields(self) -> list[str]:
        schema = SchemingEntity.get_schema("group", self.entity_type)

        return list(schema["fields"].keys())


def get_entity_types() -> dict[str, type[Entity]]:
    return {
        "Dataset": DatasetEntity,
        "Organization": OrganizationEntity,
        "Group": GroupEntity,
    }


def get_entity_manager(entity_type: str) -> type[Entity]:
    for et in get_entity_types().values():
        if et.entity_type == entity_type:
            return et

    raise EntityMissingError(entity_type)
