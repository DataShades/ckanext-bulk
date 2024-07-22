from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan.types import Context


@tk.auth_allow_anonymous_access
def bulk_get_sum(context: Context, data_dict: dict[str, Any]):
    """Any user can compute sum."""
    return {"success": True}


def bulk_something_create(context: Context, data_dict: dict[str, Any]):
    """Authenticated user can create something."""
    return {"success": True}
