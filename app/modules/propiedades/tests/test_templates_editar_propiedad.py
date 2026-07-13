"""Pruebas de render para la plantilla de edición de propiedades."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_session
from app.main import app
from app.modules.propiedades import service
from app.modules.propiedades.models import EstadoPropiedad
from app.modules.propiedades.schemas import (
    ListadoPropiedadesContexto,
    PropiedadCardView,
)


@dataclass(frozen=True)
class _PropiedadEdicionFake:
    id: object
    titulo: str
    direccion: str
    ciudad: str
    precio_mensual: object
    habitaciones: int
    banos: object
    area_m2: object
    estado: EstadoPropiedad
    updated_at: datetime


class _FakeSessionSinUso:
    pass


async def _override_session_sin_uso() -> AsyncIterator[_FakeSessionSinUso]:
    yield _FakeSessionSinUso()


@pytest.mark.asyncio
async def test_pantalla_editar_propiedad_muestra_formulario_precargado() -> None:
    """Confirma que la pantalla de edición renderiza campos precargados y acciones."""

    propiedad = _PropiedadEdicionFake(
        id=uuid4(),
        titulo="Penthouse Marina",
        direccion="123 Ocean Dr",
        ciudad="Miami",
        precio_mensual=4500,
        habitaciones=3,
        banos=2.5,
        area_m2=150,
        estado=EstadoPropiedad.RENTADA,
        updated_at=datetime.now(UTC),
    )

    async def _propiedad_por_id(_session, _propiedad_id):
        return propiedad

    original = service.obtener_propiedad_por_id
    service.obtener_propiedad_por_id = _propiedad_por_id  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/propiedades/editar/{propiedad.id}")
    finally:
        service.obtener_propiedad_por_id = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Editar propiedad" in response.text
    assert "Guardar cambios" in response.text
    assert "Cancelar" in response.text
    assert 'name="estado"' in response.text
    assert 'value="rentada"' in response.text
    assert f'action="/propiedades/editar/{propiedad.id}"' in response.text


@pytest.mark.asyncio
async def test_listado_muestra_boton_editar_en_cada_card() -> None:
    """Confirma que el listado expone el botón Editar en la card de propiedad."""

    propiedad_id = uuid4()
    contexto = ListadoPropiedadesContexto(
        propiedades=[
            PropiedadCardView(
                id=propiedad_id,
                imagen_url="https://cdn.example.com/penthouse.jpg",
                titulo="Penthouse Marina",
                direccion="123 Ocean Dr, Miami",
                habitaciones=3,
                banos="2.5",
                area_m2="150 m2",
                precio_renta="$4,500/mes",
                estado="Disponible",
            )
        ],
        mostrar_estado_vacio=False,
        total_propiedades=1,
    )

    async def _contexto_listado(_session):
        return contexto

    original = service.construir_contexto_listado
    service.construir_contexto_listado = _contexto_listado  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/propiedades")
    finally:
        service.construir_contexto_listado = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Editar" in response.text
    assert f'href="/propiedades/editar/{propiedad_id}"' in response.text
