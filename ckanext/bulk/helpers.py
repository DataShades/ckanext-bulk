from __future__ import annotations

from ckanext.bulk import const
from ckanext.bulk.utils import get_entity_managers


def bulk_action_options() -> list[dict[str, str]]:
    return [
        {"value": "update", "text": "Update"},
        {"value": "delete", "text": "Delete"},
    ]


def bulk_operator_options() -> list[dict[str, str]]:
    return [
        {"text": "IS", "value": const.OP_IS},
        {"text": "IS NOT", "value": const.OP_IS_NOT},
        {"text": "CONTAINS", "value": const.OP_CONTAINS},
        {"text": "DOES NOT CONTAIN", "value": const.OP_DOES_NOT_CONTAIN},
        {"text": "STARTS WITH", "value": const.OP_STARTS_WITH},
        {"text": "ENDS WITH", "value": const.OP_ENDS_WITH},
        {"text": "IS EMPTY", "value": const.OP_IS_EMPTY},
        {"text": "IS NOT EMPTY", "value": const.OP_IS_NOT_EMPTY},
    ]


def bulk_entity_options() -> list[dict[str, str]]:
    return [
        {"value": v.entity_type, "text": _format_entity_type_for_display(k)}
        for k, v in get_entity_managers().items()
    ]


def _format_entity_type_for_display(entity_type: str) -> str:
    return entity_type.title().replace("_", " ")
