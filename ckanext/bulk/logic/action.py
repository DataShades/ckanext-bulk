from __future__ import annotations

import copy
from typing import Any

from sqlalchemy.exc import DatabaseError

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.types import Context

from ckanext.bulk.interfaces import IBulk
from ckanext.bulk.utils import get_data, get_entity_manager, store_data

from . import schema


@validate(schema.bulk_update_entity)
def bulk_update_entity(context: Context, data_dict: dict[str, Any]):
    tk.check_access("bulk_manager", context, data_dict)

    entity_manager = get_entity_manager(data_dict["entity_type"])

    form_id = data_dict["bulk_form_id"]
    error = None
    result = None

    if data_dict["action"] == "update":
        try:
            result = entity_manager.update_entity(
                data_dict["entity_id"], data_dict["update_on"]
            )
        except tk.ObjectNotFound:
            error = tk._("Entity not found")
        except tk.ValidationError as e:
            error = str(e.error_dict)
    elif data_dict["action"] == "delete":
        try:
            result = entity_manager.delete_entity(data_dict["entity_id"])
        except tk.ObjectNotFound:
            error = tk._("Entity not found")
        except tk.ValidationError as e:
            error = str(e.error_dict)
    else:
        error = "Action is not supported"

    result = {
        "result": _format_result(result),
        "error": error,
        "action": data_dict["action"],
        "entity_type": data_dict["entity_type"],
        "entity_id": data_dict["entity_id"],
    }

    _cache_logs(form_id, copy.deepcopy(result))

    if error:
        result["error"] = error

    return result


def _format_result(
    result: dict[str, Any] | bool | None,
) -> dict[str, Any] | bool | None:
    if result is None or isinstance(result, bool):
        return result

    result.pop("resources", None)
    result.pop("organization", None)
    result.pop("groups", None)
    result.pop("packages", None)
    result.pop("relationships_as_subject", None)
    result.pop("relationships_as_object", None)
    result.pop("users", None)

    return result


def _cache_logs(form_id: str, log: dict[str, Any]) -> None:
    cached_result = get_data(f"bulk_logs_{form_id}")

    if cached_result:
        cached_result.append(log)
    else:
        cached_result = [log]

    # use the first implementation of the method, to allow plugins
    # to override the default implementation
    for plugin in p.PluginImplementations(IBulk):
        cached_result = plugin.prepare_csv_data(cached_result, "logs")
        return store_data(f"bulk_logs_{form_id}", cached_result)


@validate(schema.bulk_get_entities_by_filters)
def bulk_get_entities_by_filters(context: Context, data_dict: dict[str, Any]):
    tk.check_access("bulk_manager", context, data_dict)

    entity_manager = get_entity_manager(data_dict["entity_type"])

    try:
        result = entity_manager.search_entities_by_filters(
            data_dict["filters"], data_dict["global_operator"]
        )
    except (ValueError, tk.ValidationError) as e:
        return {
            "entities": [],
            "error": str(e),
        }
    except DatabaseError as e:
        return {
            "entities": [],
            "error": f"Database error: {e.statement}",
        }

    # use the first implementation of the method, to allow plugins
    # to override the default implementation
    for plugin in p.PluginImplementations(IBulk):
        data = plugin.prepare_csv_data(
            copy.deepcopy(result), "result", entity_manager.entity_type
        )
        break

    store_data(
        f"bulk_result_{data_dict['bulk_form_id']}",
        {"entities": data, "entity_type": entity_manager.entity_type},
    )

    return {"entities": result, "entity_type": entity_manager.entity_type}


@tk.side_effect_free
@validate(schema.bulk_search_fields)
def bulk_search_fields(context: Context, data_dict: dict[str, Any]):
    tk.check_access("bulk_manager", context, data_dict)

    entity_manager = get_entity_manager(data_dict["entity_type"])

    try:
        result = entity_manager.get_fields()
    except tk.ValidationError as e:
        return {
            "result": [],
            "error": str(e),
        }

    return {"result": result}


@validate(schema.bulk_export)
def bulk_export(context: Context, data_dict: dict[str, Any]):
    tk.check_access("bulk_manager", context, data_dict)

    form_id = data_dict["bulk_form_id"]
    export_type = data_dict["type"]

    if export_type == "result":
        result = get_data(f"bulk_result_{form_id}")

        return result.get("entities", []) if result else []
    elif export_type == "logs":
        return get_data(f"bulk_logs_{form_id}") or []
