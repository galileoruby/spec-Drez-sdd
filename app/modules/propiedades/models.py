"""Modelos del dominio de propiedades."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, Enum, Index, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EstadoPropiedad(StrEnum):
    """Catalogo cerrado de estados permitidos para una propiedad."""

    DISPONIBLE = "disponible"
    RENTADA = "rentada"
    MANTENIMIENTO = "mantenimiento"
    INACTIVA = "inactiva"


estado_propiedad_enum = Enum(
    EstadoPropiedad,
    name="estado_propiedad",
    create_type=False,
    values_callable=lambda enum_cls: [item.value for item in enum_cls],
    validate_strings=True,
)


class Propiedad(Base):
    """Entidad persistente de una propiedad inmobiliaria."""

    __tablename__ = "propiedades"
    __table_args__ = (
        UniqueConstraint(
            "titulo",
            "direccion",
            "ciudad",
            name="uq_propiedades_titulo_direccion_ciudad",
        ),
        Index("ix_propiedades_ciudad", "ciudad"),
        Index("ix_propiedades_estado", "estado"),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    ciudad: Mapped[str] = mapped_column(String(120), nullable=False)
    precio_mensual: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    habitaciones: Mapped[int] = mapped_column(nullable=False)
    banos: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False)
    area_m2: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    estado: Mapped[EstadoPropiedad] = mapped_column(
        estado_propiedad_enum,
        nullable=False,
    )
    imagen_url: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[object] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
