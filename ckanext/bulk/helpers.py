from __future__ import annotations

from ckanext.bulk.bulk_entity import get_entity_types


def bulk_action_options() -> list[dict[str, str]]:
    return [
        {"value": "update", "text": "Update"},
        {"value": "delete", "text": "Delete"},
    ]


def bulk_operator_options() -> list[dict[str, str]]:
    return [
        {"value": "is", "text": "IS"},
        {"value": "is_not", "text": "IS NOT"},
        {"value": "contains", "text": "CONTAINS"},
        {"value": "does_not_contain", "text": "DOES NOT CONTAIN"},
        {"value": "starts_with", "text": "STARTS WITH"},
        {"value": "ends_with", "text": "ENDS WITH"},
        {"value": "is_empty", "text": "IS EMPTY"},
        {"value": "is_not_empty", "text": "IS NOT EMPTY"},
    ]


def bulk_entity_options() -> list[dict[str, str]]:
    return [{"value": v.entity_type, "text": k} for k, v in get_entity_types().items()]
