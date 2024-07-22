from __future__ import annotations

from ckan import types
from ckan.logic.schema import validator_args


@validator_args
def get_sum(
    convert_int: types.Validator,
    not_empty: types.Validator,
) -> types.Schema:
    """Schema for bulk_get_sum action."""
    return {
        "left": [not_empty, convert_int],
        "right": [not_empty, convert_int],
    }


@validator_args
def something_create(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    ignore_empty: types.Validator,
    convert_to_json_if_string: types.Validator,
    dict_only: types.Validator,
) -> types.Schema:
    """Schema for bulk_something_create action."""
    return {
        "hello": [not_empty, unicode_safe],
        "world": [not_empty, unicode_safe],
        "plugin_data": [ignore_empty, convert_to_json_if_string, dict_only],
    }
