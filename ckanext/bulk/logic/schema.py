from __future__ import annotations

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic.schema import validator_args

from ckanext.bulk import const
from ckanext.bulk.entity_manager import get_entity_managers


@validator_args
def bulk_get_entities_by_filters(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    one_of: types.Validator,
    default: types.Validator,
) -> types.Schema:
    entity_types = [v.entity_type for v in get_entity_managers().values()]
    actions = [opt["value"] for opt in tk.h.bulk_action_options()]
    operators = [opt["value"] for opt in tk.h.bulk_operator_options()]

    return {
        "entity_type": [not_empty, unicode_safe, one_of(entity_types)],  # type: ignore
        "action": [not_empty, unicode_safe, one_of(actions)],  # type: ignore
        "filters": {
            "field": [not_empty, unicode_safe],
            "operator": [not_empty, unicode_safe, one_of(operators)],  # type: ignore
            "value": [default(""), unicode_safe],  # type: ignore
        },
        "global_operator": [
            not_empty,
            unicode_safe,
            one_of(
                [
                    const.GLOBAL_AND,
                    const.GLOBAL_OR,
                ]
            ),  # type: ignore
        ],
    }


@validator_args
def bulk_search_fields(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    one_of: types.Validator,
    default: types.Validator,
) -> types.Schema:
    entity_types = [v.entity_type for v in get_entity_managers().values()]

    return {
        "entity_type": [not_empty, unicode_safe, one_of(entity_types)],  # type: ignore
        "query": [default(""), unicode_safe],  # type: ignore
    }


@validator_args
def bulk_update_entity(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    one_of: types.Validator,
) -> types.Schema:
    entity_types = [v.entity_type for v in get_entity_managers().values()]
    actions = [opt["value"] for opt in tk.h.bulk_action_options()]

    return {
        "entity_type": [not_empty, unicode_safe, one_of(entity_types)],  # type: ignore
        "action": [not_empty, unicode_safe, one_of(actions)],  # type: ignore
        "entity_id": [not_empty, unicode_safe],
        "update_on": {
            "field": [not_empty, unicode_safe],
            "value": [not_empty, unicode_safe],
        },
    }
