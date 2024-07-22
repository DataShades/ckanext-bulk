from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import model
from ckan.logic import validate
from ckan.types import Context

from ckanext.bulk.model import Something

from . import schema


@tk.side_effect_free
@validate(schema.get_sum)
def bulk_get_sum(context: Context, data_dict: dict[str, Any]):
    """Produce a sum of left and right.

    Args:
        left (int): firt argument
        right (int): second argument

    Returns:
        operation details
    """
    tk.check_access("bulk_get_sum", context, data_dict)

    return {
        "left": data_dict["left"],
        "right": data_dict["right"],
        "sum": data_dict["left"] + data_dict["right"],
    }


@validate(schema.something_create)
def bulk_something_create(context: Context, data_dict: dict[str, Any]):
    """Create something object.

    Args:
        hello (str): aliquam erat volutpat
        world: (str): nullam tempus
        plugin_data (dict[str, Any], optional): aliquam feugiat tellus ut neque

    Returns:
        details of the new something object
    """
    tk.check_access("bulk_something_create", context, data_dict)

    smth = Something(
        hello=data_dict["hello"],
        world=data_dict["world"],
        plugin_data=data_dict.get("plugin_data", {}),
    )
    model.Session.add(smth)
    model.Session.commit()

    return smth.dictize(context)
