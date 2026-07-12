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
    ErrorValidacionCreacionPropiedad,
    PropiedadCrearFormulario,
    construir_contexto_listado,
    crear_propiedad,
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


class _FakeSessionCreacion:
    def __init__(self) -> None:
        self.added: list[Propiedad] = []
        self.flush_count = 0
        self.commit_count = 0
        self.refresh_count = 0

    def add(self, propiedad: Propiedad) -> None:
        self.added.append(propiedad)

    async def flush(self) -> None:
        self.flush_count += 1

    async def commit(self) -> None:
        self.commit_count += 1

    async def refresh(self, _propiedad: Propiedad) -> None:
        self.refresh_count += 1


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


async def _provider_sin_existentes(
    _session: AsyncSession,
    _titulo: str,
    _direccion: str,
    _ciudad: str,
) -> Propiedad | None:
    return None


async def _guardar_propiedad_falsa(
    session: _FakeSessionCreacion,
    propiedad: Propiedad,
) -> Propiedad:
    session.add(propiedad)
    propiedad.id = uuid4()
    return propiedad


@pytest.mark.asyncio
async def test_crear_propiedad_persiste_con_datos_normalizados_y_estado_defecto() -> None:
    """Confirma que la creación exitosa normaliza y persiste una propiedad."""

    formulario = PropiedadCrearFormulario(
        titulo="  Penthouse   Marina  ",
        direccion="  123   Ocean Dr  ",
        ciudad="  Miami  ",
        precio_mensual="4500",
        habitaciones="3",
        banos="2.5",
        area_m2="150",
    )
    session = _FakeSessionCreacion()

    resultado = await crear_propiedad(
        cast(AsyncSession, session),
        formulario,
        obtener_existente=_provider_sin_existentes,
        guardar_propiedad=_guardar_propiedad_falsa,
        construir_imagen=lambda propiedad_id: f"https://picsum.photos/seed/{propiedad_id}/800/500",
    )

    assert resultado.redireccion == "/propiedades?creada=1"
    assert resultado.mensaje_exito == "Propiedad creada correctamente."
    assert session.flush_count == 1
    assert session.commit_count == 1
    assert session.refresh_count == 1
    assert session.added
    propiedad_persistida = session.added[0]
    assert propiedad_persistida.titulo == "Penthouse Marina"
    assert propiedad_persistida.direccion == "123 Ocean Dr"
    assert propiedad_persistida.ciudad == "Miami"
    assert propiedad_persistida.estado == EstadoPropiedad.DISPONIBLE
    assert propiedad_persistida.imagen_url.startswith("https://picsum.photos/seed/")


@pytest.mark.asyncio
async def test_crear_propiedad_rechaza_campos_invalidos_y_blancos() -> None:
    """Valida que los campos vacios o invalidos no pasen al flujo de persistencia."""

    formulario = PropiedadCrearFormulario(
        titulo="   ",
        direccion="  ",
        ciudad="Miami",
        precio_mensual="0",
        habitaciones="11",
        banos="5.5",
        area_m2="-1",
    )

    with pytest.raises(ErrorValidacionCreacionPropiedad) as error:
        await crear_propiedad(
            cast(AsyncSession, _FakeSessionCreacion()),
            formulario,
            obtener_existente=_provider_sin_existentes,
            guardar_propiedad=_guardar_propiedad_falsa,
        )

    contexto = error.value.contexto
    assert contexto.errores.titulo == "Este campo es obligatorio."
    assert contexto.errores.direccion == "Este campo es obligatorio."
    assert contexto.errores.precio_mensual == "Debe ser mayor que 0."
    assert contexto.errores.habitaciones == "Debe estar entre 1 y 10."
    assert contexto.errores.banos == "Debe estar entre 1.0 y 5.0."
    assert contexto.errores.area_m2 == "Debe ser mayor que 0."


@pytest.mark.asyncio
async def test_crear_propiedad_rechaza_identidad_duplicada() -> None:
    """Evita persistir una propiedad cuando la identidad de negocio ya existe."""

    formulario = PropiedadCrearFormulario(
        titulo="Penthouse Marina",
        direccion="123 Ocean Dr",
        ciudad="Miami",
        precio_mensual="4500",
        habitaciones="3",
        banos="2.5",
        area_m2="150",
    )
    existente = cast(
        Propiedad,
        _PropiedadFake(
            id=uuid4(),
            titulo="Penthouse Marina",
            direccion="123 Ocean Dr",
            ciudad="Miami",
            precio_mensual=Decimal("4500"),
            habitaciones=3,
            banos=Decimal("2.5"),
            area_m2=Decimal("150"),
            estado=EstadoPropiedad.DISPONIBLE,
            imagen_url="https://cdn.example.com/existente.jpg",
            created_at=datetime.now(UTC),
        ),
    )

    async def _provider_existente(
        _session: AsyncSession,
        _titulo: str,
        _direccion: str,
        _ciudad: str,
    ) -> Propiedad | None:
        return existente

    with pytest.raises(ErrorValidacionCreacionPropiedad) as error:
        await crear_propiedad(
            cast(AsyncSession, _FakeSessionCreacion()),
            formulario,
            obtener_existente=_provider_existente,
            guardar_propiedad=_guardar_propiedad_falsa,
        )

    assert error.value.contexto.errores.general == (
        "Ya existe una propiedad con la misma identidad de negocio."
    )


@pytest.mark.asyncio
async def test_crear_propiedad_usa_fallback_local_si_falla_picsum() -> None:
    """Comprueba que la imagen local cubre fallos de generacion externa."""

    formulario = PropiedadCrearFormulario(
        titulo="Casa Familiar",
        direccion="456 Coral Way",
        ciudad="Miami",
        precio_mensual="3200",
        habitaciones="4",
        banos="3.0",
        area_m2="210",
    )

    def _generador_fallido(_propiedad_id: object) -> str:
        raise RuntimeError("picsum caido")

    resultado = await crear_propiedad(
        cast(AsyncSession, _FakeSessionCreacion()),
        formulario,
        obtener_existente=_provider_sin_existentes,
        guardar_propiedad=_guardar_propiedad_falsa,
        construir_imagen=_generador_fallido,
    )

    assert resultado.redireccion == "/propiedades?creada=1"
