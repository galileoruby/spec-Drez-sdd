"""Pruebas de render para la plantilla de alta de propiedades."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_session
from app.main import app


class _FakeSessionListadoVacio:
    async def execute(self, _query):
        class _FakeScalars:
            def all(self):
                return []

        class _FakeResult:
            def scalars(self):
                return _FakeScalars()

        return _FakeResult()


async def _override_session_listado_vacio() -> AsyncIterator[_FakeSessionListadoVacio]:
    yield _FakeSessionListadoVacio()


@pytest.mark.asyncio
async def test_pantalla_crear_propiedad_muestra_campos_y_acciones() -> None:
    """Confirma que el formulario de alta se renderiza con los campos visibles."""

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/propiedades/crear")

    assert response.status_code == 200
    assert "Titulo" in response.text
    assert "Direccion" in response.text
    assert "Ciudad" in response.text
    assert "Precio mensual" in response.text
    assert "Habitaciones" in response.text
    assert "Banos" in response.text
    assert "Area m2" in response.text
    assert "Guardar propiedad" in response.text
    assert "Cancelar" in response.text


@pytest.mark.asyncio
async def test_listado_muestra_confirmacion_de_exito_post_alta() -> None:
    """Verifica que el listado renderice una alerta de éxito tras la creación."""

    app.dependency_overrides[get_session] = _override_session_listado_vacio
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/propiedades?creada=1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Propiedad creada correctamente." in response.text
    assert "alerta--success" in response.text