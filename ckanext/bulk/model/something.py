from __future__ import annotations

import copy
from typing import Any

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped

from ckan.lib.dictization import table_dictize
from ckan.model.types import make_uuid

from .base import Base


class Something(Base):  # type: ignore
    """Model with details or something."""

    # define columns as a `__table__` attribute. It simplifies typing and you
    # can copy this definition almost unchanged into alembic migration.
    __table__ = sa.Table(
        "bulk_something",
        Base.metadata,
        sa.Column("id", sa.UnicodeText, primary_key=True, default=make_uuid),
        sa.Column("hello", sa.Text, nullable=False, default=""),
        sa.Column("world", sa.Text, nullable=False),
        sa.Column("plugin_data", JSONB, default=dict, server_default="{}"),
    )

    # typed models. You'll use it - you'll love it.
    id: Mapped[str]

    hello: Mapped[str]
    world: Mapped[str]

    plugin_data: Mapped[dict[str, Any]]

    def dictize(self, context: Any) -> dict[str, Any]:
        result = table_dictize(self, context)

        plugin_data = result.pop("plugin_data")
        if context.get("include_plugin_data"):
            result["plugin_data"] = copy.deepcopy(plugin_data)

        return result

    @classmethod
    def by_hello(cls, hello: str, world: str | None = None) -> sa.sql.Select:
        stmt = sa.select(cls).where(
            cls.hello == hello,
        )

        if world:
            stmt = stmt.where(cls.world == world)

        return stmt
