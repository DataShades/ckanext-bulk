from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.types import Context

from ckanext.bulk.entity_manager import get_entity_manager

from . import schema


def bulk_perform(context: Context, data_dict: dict[str, Any]):
    pass


@validate(schema.bulk_get_entities_by_filters)
def bulk_get_entities_by_filters(context: Context, data_dict: dict[str, Any]):
    entity_manager = get_entity_manager(data_dict["entity_type"])

    return entity_manager.search_entities_by_filters(
        data_dict["filters"], data_dict["global_operator"]
    )


@tk.side_effect_free
@validate(schema.bulk_search_fields)
def bulk_search_fields(context: Context, data_dict: dict[str, Any]):
    entity_manager = get_entity_manager(data_dict["entity_type"])

    return entity_manager.get_fields()
