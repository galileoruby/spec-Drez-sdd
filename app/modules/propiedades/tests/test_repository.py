"""Pruebas de acceso a datos para listado de propiedades."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.propiedades import repository
from app.modules.propiedades.models import EstadoPropiedad, Propiedad


@dataclass(frozen=True)
class _PropiedadFake:
    id: object
    titulo: str
    direccion: str
    ciudad: str
    precio_mensual: float
    habitaciones: int
    banos: float
    area_m2: float
    estado: EstadoPropiedad
    imagen_url: str
    created_at: datetime


class _FakeScalars:
    def __init__(self, values: list[_PropiedadFake]) -> None:
        self._values = values

    def all(self) -> list[_PropiedadFake]:
        return self._values


class _FakeResult:
    def __init__(self, values: list[_PropiedadFake]) -> None:
        self._values = values

    def scalars(self) -> _FakeScalars:
        return _FakeScalars(self._values)


class _FakeSession:
    def __init__(self, values: list[_PropiedadFake]) -> None:
        self.values = values
        self.last_stmt: object | None = None

    async def execute(self, stmt: object) -> _FakeResult:
        self.last_stmt = stmt
        return _FakeResult(self.values)


@pytest.mark.asyncio
async def test_listar_para_cards_compone_query_con_orden_desc() -> None:
    """Verifica que la consulta de cards ordene por created_at descendente."""

    rows = [
        _PropiedadFake(
            id=uuid4(),
            titulo="A",
            direccion="Dir A",
            ciudad="Miami",
            precio_mensual=1800,
            habitaciones=2,
            banos=1.0,
            area_m2=75.0,
            estado=EstadoPropiedad.DISPONIBLE,
            imagen_url="https://img/a.jpg",
            created_at=datetime.now(UTC),
        ),
        _PropiedadFake(
            id=uuid4(),
            titulo="B",
            direccion="Dir B",
            ciudad="Miami",
            precio_mensual=1900,
            habitaciones=3,
            banos=2.0,
            area_m2=90.0,
            estado=EstadoPropiedad.RENTADA,
            imagen_url="https://img/b.jpg",
            created_at=datetime.now(UTC),
        ),
    ]
    session = _FakeSession(rows)

    result = await repository.listar_para_cards(cast(AsyncSession, session))

    assert len(result) == len(rows)
    assert result[0].titulo == rows[0].titulo
    assert result[1].titulo == rows[1].titulo
    assert session.last_stmt is not None
    sql = str(session.last_stmt)
    assert "ORDER BY" in sql
    assert "created_at DESC" in sql


class _FakeSessionCrear:
    def __init__(self) -> None:
        self.added: list[Propiedad] = []
        self.flush_count = 0
        self.refresh_count = 0

    def add(self, propiedad: Propiedad) -> None:
        self.added.append(propiedad)

    async def flush(self) -> None:
        self.flush_count += 1

    async def refresh(self, propiedad: Propiedad) -> None:
        self.refresh_count += 1


@pytest.mark.asyncio
async def test_crear_propiedad_agrega_y_refresca_la_entidad() -> None:
    """Asegura que el repositorio materializa la inserción de una propiedad."""

    session = _FakeSessionCrear()
    propiedad = Propiedad(
        titulo="Casa Familiar",
        direccion="456 Coral Way",
        ciudad="Miami",
        precio_mensual=3200,
        habitaciones=4,
        banos=3.0,
        area_m2=210,
        estado=EstadoPropiedad.DISPONIBLE,
        imagen_url="https://picsum.photos/seed/abc/800/500",
    )

    resultado = await repository.crear_propiedad(cast(AsyncSession, session), propiedad)

    assert resultado is propiedad
    assert session.added == [propiedad]
    assert session.flush_count == 1
    assert session.refresh_count == 1


class _FakeSessionCrear:
    def __init__(self) -> None:
        self.added: list[Propiedad] = []
        self.flush_count = 0
        self.refresh_count = 0

    def add(self, propiedad: Propiedad) -> None:
        self.added.append(propiedad)

    async def flush(self) -> None:
        self.flush_count += 1

    async def refresh(self, propiedad: Propiedad) -> None:
        self.refresh_count += 1


@pytest.mark.asyncio
async def test_crear_propiedad_agrega_y_refresca_la_entidad() -> None:
    """Asegura que el repositorio materializa la inserción de una propiedad."""

    session = _FakeSessionCrear()
    propiedad = Propiedad(
        titulo="Casa Familiar",
        direccion="456 Coral Way",
        ciudad="Miami",
        precio_mensual=3200,
        habitaciones=4,
        banos=3.0,
        area_m2=210,
        estado=EstadoPropiedad.DISPONIBLE,
        imagen_url="https://picsum.photos/seed/abc/800/500",
    )

    resultado = await repository.crear_propiedad(cast(AsyncSession, session), propiedad)

    assert resultado is propiedad
    assert session.added == [propiedad]
    assert session.flush_count == 1
    assert session.refresh_count == 1
