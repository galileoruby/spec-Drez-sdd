"""Crea estructura base del dominio de propiedades."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_create_propiedades"
down_revision: str | None = "20260708_baseline"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Aplica la estructura persistente de propiedades."""

    op.create_table(
        "propiedades",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("direccion", sa.String(length=255), nullable=False),
        sa.Column("ciudad", sa.String(length=120), nullable=False),
        sa.Column("precio_mensual", sa.Numeric(12, 2), nullable=False),
        sa.Column("habitaciones", sa.Integer(), nullable=False),
        sa.Column("banos", sa.Numeric(4, 1), nullable=False),
        sa.Column("area_m2", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "disponible",
                "rentada",
                "mantenimiento",
                "inactiva",
                name="estado_propiedad",
            ),
            nullable=False,
        ),
        sa.Column("imagen_url", sa.String(length=500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_propiedades"),
        sa.UniqueConstraint(
            "titulo",
            "direccion",
            "ciudad",
            name="uq_propiedades_titulo_direccion_ciudad",
        ),
    )
    op.create_index("ix_propiedades_ciudad", "propiedades", ["ciudad"], unique=False)
    op.create_index("ix_propiedades_estado", "propiedades", ["estado"], unique=False)


def downgrade() -> None:
    """Revierte la estructura persistente de propiedades."""

    op.drop_index("ix_propiedades_estado", table_name="propiedades")
    op.drop_index("ix_propiedades_ciudad", table_name="propiedades")
    op.drop_table("propiedades")
    op.execute("DROP TYPE IF EXISTS estado_propiedad")
