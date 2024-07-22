"""Template helpers of the bulk plugin.

All non-private functions defined here are registered inside `tk.h` collection.
"""

from __future__ import annotations


def bulk_hello() -> str:
    """Greet the user.

    Returns:
        greeting with the plugin name.
    """
    return "Hello, bulk!"
