from __future__ import annotations

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic.schema import validator_args

from ckanext.bulk.bulk_entity import get_entity_types


@validator_args
def bulk_get_entities_by_filters(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    one_of: types.Validator,
) -> types.Schema:
    entity_types = [v.entity_type for v in get_entity_types().values()]
    actions = [opt["value"] for opt in tk.h.bulk_action_options()]
    operators = [opt["value"] for opt in tk.h.bulk_operator_options()]

    return {
        "entity_type": [not_empty, unicode_safe, one_of(entity_types)],  # type: ignore
        "action": [not_empty, unicode_safe, one_of(actions)],  # type: ignore
        "filters": {
            "field": [not_empty, unicode_safe],
            "operator": [not_empty, unicode_safe, one_of(operators)],  # type: ignore
            "value": [not_empty, unicode_safe],
        },
    }
