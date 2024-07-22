"""Tests for IPackageController implementation.

Here you should verify that any modifications from intterface implementations
work as expected.
"""

from __future__ import annotations

from typing import Any

import pytest


@pytest.mark.usefixtures("with_plugins", "clean_db")
def test_after_show(package: dict[str, Any]):
    assert package["fake"] == 42
