from __future__ import annotations

from typing import Any

from sqlalchemy.exc import DatabaseError

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.types import Context

from ckanext.bulk.entity_manager import get_entity_manager

from . import schema


@validate(schema.bulk_update_entity)
def bulk_update_entity(context: Context, data_dict: dict[str, Any]):
    entity_manager = get_entity_manager(data_dict["entity_type"])

    if data_dict["action"] == "update":
        try:
            result = entity_manager.update_entity(
                data_dict["entity_id"], data_dict["update_on"]
            )
        except tk.ValidationError as e:
            return {
                "result": None,
                "error": str(e),
            }
    elif data_dict["action"] == "delete":
        try:
            entity_manager.delete_entity(data_dict["entity_id"])
        except tk.ValidationError as e:
            return {
                "result": None,
                "error": str(e),
            }
    else:
        return {
            "result": None,
            "error": "Action is not supported",
        }

    return {
        "result": result,
    }


@validate(schema.bulk_get_entities_by_filters)
def bulk_get_entities_by_filters(context: Context, data_dict: dict[str, Any]):
    entity_manager = get_entity_manager(data_dict["entity_type"])

    try:
        result = entity_manager.search_entities_by_filters(
            data_dict["filters"], data_dict["global_operator"]
        )
    except (ValueError, tk.ValidationError) as e:
        return {
            "fields": [],
            "error": str(e),
        }
    except DatabaseError as e:
        return {
            "fields": [],
            "error": f"Database error: {e.statement}",
        }

    return {"fields": result}


@tk.side_effect_free
@validate(schema.bulk_search_fields)
def bulk_search_fields(context: Context, data_dict: dict[str, Any]):
    entity_manager = get_entity_manager(data_dict["entity_type"])

    try:
        result = entity_manager.get_fields()
    except tk.ValidationError as e:
        return {
            "result": [],
            "error": str(e),
        }

    return {"result": result}
