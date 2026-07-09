"""Migración baseline inicial con extensión pgcrypto."""

from collections.abc import Sequence

from alembic import op

revision: str = "20260708_baseline"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Aplica la baseline de la base de datos."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")


def downgrade() -> None:
    """Revierte la baseline de la base de datos."""
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
