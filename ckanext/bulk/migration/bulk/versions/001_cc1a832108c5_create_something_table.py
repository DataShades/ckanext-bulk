"""Create something table.

Revision ID: cc1a832108c5
Revises:
Create Date: 2024-07-22 15:44:28

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "cc1a832108c5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bulk_something",
        sa.Column("id", sa.UnicodeText, primary_key=True),
        sa.Column("hello", sa.UnicodeText, nullable=False, server_default=""),
        sa.Column("world", sa.UnicodeText, nullable=False),
        sa.Column("plugin_data", JSONB, server_default="{}"),
    )


def downgrade():
    op.drop_table("bulk_something")
