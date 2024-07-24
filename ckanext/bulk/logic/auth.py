from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan.types import Context


def bulk_manager(context: Context, data_dict: dict[str, Any]):
    return {"success": False}
