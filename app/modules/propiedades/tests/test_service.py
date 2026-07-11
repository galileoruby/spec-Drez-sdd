"""Pruebas unitarias del servicio de listado de propiedades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.propiedades.models import EstadoPropiedad, Propiedad
from app.modules.propiedades.service import (
    FALLBACK_IMAGEN_LOCAL,
    construir_contexto_listado,
)


@dataclass(frozen=True)
class _PropiedadFake:
    id: object
    titulo: str
    direccion: str
    ciudad: str
    precio_mensual: Decimal
    habitaciones: int
    banos: Decimal
    area_m2: Decimal
    estado: EstadoPropiedad
    imagen_url: str
    created_at: datetime


class _FakeSession:
    async def execute(self, _stmt: object) -> None:
        return None


async def _provider_con_registros(_session: AsyncSession) -> list[Propiedad]:
    return [
        cast(
            Propiedad,
            _PropiedadFake(
                id=uuid4(),
                titulo="Penthouse con vista panoramica de la bahia",
                direccion="123 Brickell Ave",
                ciudad="Miami",
                precio_mensual=Decimal("4500"),
                habitaciones=3,
                banos=Decimal("2.5"),
                area_m2=Decimal("150"),
                estado=EstadoPropiedad.DISPONIBLE,
                imagen_url="https://cdn.example.com/penthouse.jpg",
                created_at=datetime.now(UTC),
            ),
        )
    ]


async def _provider_sin_registros(_session: AsyncSession) -> list[Propiedad]:
    return []


async def _provider_con_imagen_invalida(_session: AsyncSession) -> list[Propiedad]:
    return [
        cast(
            Propiedad,
            _PropiedadFake(
                id=uuid4(),
                titulo="Casa familiar",
                direccion="456 Ocean Dr",
                ciudad="Miami",
                precio_mensual=Decimal("3200"),
                habitaciones=4,
                banos=Decimal("3.0"),
                area_m2=Decimal("210"),
                estado=EstadoPropiedad.RENTADA,
                imagen_url="archivo-local-no-valido",
                created_at=datetime.now(UTC),
            ),
        )
    ]


@pytest.mark.asyncio
async def test_contexto_listado_expone_contrato_completo_de_card() -> None:
    """Valida que cada card entregue todos los campos obligatorios del contrato."""

    contexto = await construir_contexto_listado(
        cast(AsyncSession, _FakeSession()),
        cards_provider=_provider_con_registros,
    )

    assert contexto.total_propiedades == 1
    assert contexto.mostrar_estado_vacio is False
    card = contexto.propiedades[0]
    assert card.imagen_url
    assert card.titulo
    assert card.direccion
    assert card.habitaciones == 3
    assert card.banos == "2.5"
    assert card.area_m2 == "150 m2"
    assert card.precio_renta == "$4,500/mes"
    assert card.estado == "Disponible"


@pytest.mark.asyncio
async def test_contexto_listado_marca_estado_vacio_sin_registros() -> None:
    """Asegura que la bandera de estado vacio sea consistente con total 0."""

    contexto = await construir_contexto_listado(
        cast(AsyncSession, _FakeSession()),
        cards_provider=_provider_sin_registros,
    )

    assert contexto.total_propiedades == 0
    assert contexto.mostrar_estado_vacio is True
    assert contexto.propiedades == []


@pytest.mark.asyncio
async def test_contexto_listado_aplica_fallback_local_si_imagen_no_es_utilizable(
) -> None:
    """Confirma fallback local cuando la imagen entrante es faltante o invalida."""

    contexto = await construir_contexto_listado(
        cast(AsyncSession, _FakeSession()),
        cards_provider=_provider_con_imagen_invalida,
    )

    assert contexto.total_propiedades == 1
    assert contexto.propiedades[0].imagen_url == FALLBACK_IMAGEN_LOCAL
