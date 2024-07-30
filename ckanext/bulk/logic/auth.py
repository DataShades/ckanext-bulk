from __future__ import annotations

from typing import Any

from ckan.types import Context


def bulk_manager(context: Context, data_dict: dict[str, Any]):
    """Available to sysadmins only."""
    return {"success": False}
