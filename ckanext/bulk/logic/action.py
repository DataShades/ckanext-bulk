from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ckan.types import Context

from . import schema
from ckanext.bulk.bulk_entity import get_entity_manager


def bulk_perform(context: Context, data_dict: dict[str, Any]):
    print(data_dict)


@validate(schema.bulk_get_entities_by_filters)
def bulk_get_entities_by_filters(context: Context, data_dict: dict[str, Any]):
    entity_manager = get_entity_manager(data_dict["entity_type"])

    return {
        "count": len(entity_manager.search_entities_by_filters(data_dict["filters"]))
    }
