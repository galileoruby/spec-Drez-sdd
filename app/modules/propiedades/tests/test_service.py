"""Pruebas unitarias del servicio de propiedades."""

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
    ErrorConflictoOptimistaEdicionPropiedad,
    ErrorValidacionCreacionPropiedad,
    ErrorValidacionEdicionPropiedad,
    PropiedadCrearFormulario,
    PropiedadEditarFormulario,
    PropiedadNoEncontradaError,
    construir_contexto_listado,
    crear_propiedad,
    editar_propiedad,
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
    updated_at: datetime


def _crear_propiedad_real(
    *,
    propiedad_id: object | None = None,
    titulo: str = "Penthouse Marina",
    direccion: str = "123 Ocean Dr",
    ciudad: str = "Miami",
    precio_mensual: Decimal = Decimal("4500"),
    habitaciones: int = 3,
    banos: Decimal = Decimal("2.5"),
    area_m2: Decimal = Decimal("150"),
    estado: EstadoPropiedad = EstadoPropiedad.DISPONIBLE,
    imagen_url: str = "https://cdn.example.com/penthouse.jpg",
) -> Propiedad:
    """Crea una entidad real mutable para pruebas de edición."""

    propiedad = Propiedad(
        titulo=titulo,
        direccion=direccion,
        ciudad=ciudad,
        precio_mensual=precio_mensual,
        habitaciones=habitaciones,
        banos=banos,
        area_m2=area_m2,
        estado=estado,
        imagen_url=imagen_url,
    )
    propiedad.id = propiedad_id or uuid4()
    propiedad.created_at = datetime.now(UTC)
    propiedad.updated_at = datetime.now(UTC)
    return propiedad


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


class _FakeSessionEdicion:
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
                updated_at=datetime.now(UTC),
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
                updated_at=datetime.now(UTC),
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
    assert card.id
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
        habitaciones="16",
        banos="8.5",
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
    assert contexto.errores.habitaciones == "Debe estar entre 1 y 15."
    assert contexto.errores.banos == "Debe estar entre 0.5 y 8.0."
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
            updated_at=datetime.now(UTC),
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


async def _guardar_propiedad_edicion(
    session: _FakeSessionEdicion,
    propiedad: Propiedad,
) -> Propiedad:
    session.add(propiedad)
    await session.flush()
    return propiedad


@pytest.mark.asyncio
async def test_editar_propiedad_persiste_cambios_normalizados_y_estado() -> None:
    """Confirma que la edición exitosa normaliza, persiste y redirige."""

    propiedad = _crear_propiedad_real()
    session = _FakeSessionEdicion()
    nuevo_momento = propiedad.updated_at.isoformat()

    async def _provider_por_id(_session: AsyncSession, _propiedad_id: object) -> Propiedad | None:
        return propiedad

    async def _provider_sin_duplicado(
        _session: AsyncSession,
        _titulo: str,
        _direccion: str,
        _ciudad: str,
        _propiedad_id: object,
    ) -> Propiedad | None:
        return None

    formulario = PropiedadEditarFormulario(
        titulo="  Penthouse   Marina  ",
        direccion="  123   Ocean Dr  ",
        ciudad="  Miami  ",
        precio_mensual="4800",
        habitaciones="4",
        banos="3.0",
        area_m2="155",
        estado="rentada",
        updated_at=nuevo_momento,
    )

    resultado = await editar_propiedad(
        cast(AsyncSession, session),
        propiedad.id,
        formulario,
        obtener_por_id=_provider_por_id,
        obtener_existente=_provider_sin_duplicado,
        guardar_propiedad=_guardar_propiedad_edicion,
    )

    assert resultado.redireccion == "/propiedades?editada=1"
    assert resultado.mensaje_exito == "Propiedad editada correctamente."
    assert session.flush_count == 1
    assert session.commit_count == 1
    assert session.refresh_count == 1
    propiedad_persistida = session.added[0]
    assert propiedad_persistida.titulo == "Penthouse Marina"
    assert propiedad_persistida.direccion == "123 Ocean Dr"
    assert propiedad_persistida.ciudad == "Miami"
    assert propiedad_persistida.precio_mensual == Decimal("4800")
    assert propiedad_persistida.habitaciones == 4
    assert propiedad_persistida.banos == Decimal("3.0")
    assert propiedad_persistida.area_m2 == Decimal("155")
    assert propiedad_persistida.estado == EstadoPropiedad.RENTADA


@pytest.mark.asyncio
async def test_editar_propiedad_rechaza_invalidos_y_blancos() -> None:
    """Valida que la edición invalida no persista cambios y conserve errores."""

    propiedad = _crear_propiedad_real()

    async def _provider_por_id(_session: AsyncSession, _propiedad_id: object) -> Propiedad | None:
        return propiedad

    async def _provider_sin_duplicado(
        _session: AsyncSession,
        _titulo: str,
        _direccion: str,
        _ciudad: str,
        _propiedad_id: object,
    ) -> Propiedad | None:
        return None

    formulario = PropiedadEditarFormulario(
        titulo="   ",
        direccion="  ",
        ciudad="Miami",
        precio_mensual="0",
        habitaciones="16",
        banos="8.5",
        area_m2="-1",
        estado="",
        updated_at=propiedad.updated_at.isoformat(),
    )

    with pytest.raises(ErrorValidacionEdicionPropiedad) as error:
        await editar_propiedad(
            cast(AsyncSession, _FakeSessionEdicion()),
            propiedad.id,
            formulario,
            obtener_por_id=_provider_por_id,
            obtener_existente=_provider_sin_duplicado,
            guardar_propiedad=_guardar_propiedad_edicion,
        )

    contexto = error.value.contexto
    assert contexto.errores.titulo == "Este campo es obligatorio."
    assert contexto.errores.direccion == "Este campo es obligatorio."
    assert contexto.errores.precio_mensual == "Debe ser mayor que 0."
    assert contexto.errores.habitaciones == "Debe estar entre 1 y 15."
    assert contexto.errores.banos == "Debe estar entre 0.5 y 8.0."
    assert contexto.errores.area_m2 == "Debe ser mayor que 0."
    assert contexto.errores.estado == "Este campo es obligatorio."


@pytest.mark.asyncio
async def test_editar_propiedad_rechaza_identidad_duplicada() -> None:
    """Evita persistir la edición cuando otra propiedad comparte identidad."""

    propiedad = _crear_propiedad_real()
    duplicada = _crear_propiedad_real(
        propiedad_id=uuid4(),
        precio_mensual=Decimal("4600"),
        habitaciones=4,
        banos=Decimal("3.0"),
        area_m2=Decimal("155"),
        estado=EstadoPropiedad.RENTADA,
        imagen_url="https://cdn.example.com/otra.jpg",
    )

    async def _provider_por_id(_session: AsyncSession, _propiedad_id: object) -> Propiedad | None:
        return propiedad

    async def _provider_con_duplicado(
        _session: AsyncSession,
        _titulo: str,
        _direccion: str,
        _ciudad: str,
        _propiedad_id: object,
    ) -> Propiedad | None:
        return duplicada

    with pytest.raises(ErrorValidacionEdicionPropiedad) as error:
        await editar_propiedad(
            cast(AsyncSession, _FakeSessionEdicion()),
            propiedad.id,
            PropiedadEditarFormulario(
                titulo="Penthouse Marina",
                direccion="123 Ocean Dr",
                ciudad="Miami",
                precio_mensual="4600",
                habitaciones="4",
                banos="3.0",
                area_m2="155",
                estado="rentada",
                updated_at=propiedad.updated_at.isoformat(),
            ),
            obtener_por_id=_provider_por_id,
            obtener_existente=_provider_con_duplicado,
            guardar_propiedad=_guardar_propiedad_edicion,
        )

    assert error.value.contexto.errores.general == (
        "Ya existe una propiedad con la misma identidad de negocio."
    )


@pytest.mark.asyncio
async def test_editar_propiedad_detecta_conflicto_optimista() -> None:
    """Evita sobrescribir cambios si la edición llega con una versión vieja."""

    propiedad = _crear_propiedad_real()

    async def _provider_por_id(_session: AsyncSession, _propiedad_id: object) -> Propiedad | None:
        return propiedad

    async def _provider_sin_duplicado(
        _session: AsyncSession,
        _titulo: str,
        _direccion: str,
        _ciudad: str,
        _propiedad_id: object,
    ) -> Propiedad | None:
        return None

    formulario = PropiedadEditarFormulario(
        titulo="Penthouse Marina",
        direccion="123 Ocean Dr",
        ciudad="Miami",
        precio_mensual="4800",
        habitaciones="4",
        banos="3.0",
        area_m2="155",
        estado="rentada",
        updated_at=(propiedad.updated_at.replace(year=propiedad.updated_at.year - 1)).isoformat(),
    )

    with pytest.raises(ErrorConflictoOptimistaEdicionPropiedad) as error:
        await editar_propiedad(
            cast(AsyncSession, _FakeSessionEdicion()),
            propiedad.id,
            formulario,
            obtener_por_id=_provider_por_id,
            obtener_existente=_provider_sin_duplicado,
            guardar_propiedad=_guardar_propiedad_edicion,
        )

    assert error.value.contexto.errores.general == (
        "La propiedad cambió desde la última lectura. Recarga la página e intenta de nuevo."
    )


@pytest.mark.asyncio
async def test_editar_propiedad_rechaza_id_inexistente() -> None:
    """Asegura que una propiedad ausente corte el flujo con error explícito."""

    async def _provider_sin_propiedad(_session: AsyncSession, _propiedad_id: object) -> Propiedad | None:
        return None

    with pytest.raises(PropiedadNoEncontradaError):
        async def _provider_sin_duplicado(
            _session: AsyncSession,
            _titulo: str,
            _direccion: str,
            _ciudad: str,
            _propiedad_id: object,
        ) -> Propiedad | None:
            return None

        await editar_propiedad(
            cast(AsyncSession, _FakeSessionEdicion()),
            uuid4(),
            PropiedadEditarFormulario(),
            obtener_por_id=_provider_sin_propiedad,
            obtener_existente=_provider_sin_duplicado,
            guardar_propiedad=_guardar_propiedad_edicion,
        )
