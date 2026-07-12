"""Pruebas de rutas HTTP para alta de propiedades."""

from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_session
from app.main import app
from app.modules.propiedades import service
from app.modules.propiedades.schemas import (
    ListadoPropiedadesContexto,
    PropiedadCrearErrores,
    PropiedadCrearFormulario,
    PropiedadCrearVista,
    PropiedadCreadaResultado,
)


class _FakeSessionSinUso:
    pass


class _FakeSessionListadoVacio:
    async def execute(self, _query):
        class _FakeScalars:
            def all(self):
                return []

        class _FakeResult:
            def scalars(self):
                return _FakeScalars()

        return _FakeResult()


async def _override_session_sin_uso() -> AsyncIterator[_FakeSessionSinUso]:
    yield _FakeSessionSinUso()


async def _override_session_listado_vacio() -> AsyncIterator[_FakeSessionListadoVacio]:
    yield _FakeSessionListadoVacio()


@pytest.mark.asyncio
async def test_get_formulario_crear_propiedad_renderiza_la_pantalla() -> None:
    """Verifica que la ruta GET de alta entregue la vista correcta."""

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/propiedades/crear")

    assert response.status_code == 200
    assert "Crear propiedad" in response.text
    assert "Guardar propiedad" in response.text
    assert "action=\"/propiedades/crear\"" in response.text


@pytest.mark.asyncio
async def test_post_crear_propiedad_exitosa_redirige_al_listado() -> None:
    """Confirma que la creación exitosa redirige al listado con 303."""

    async def _crear_falso(_session, _formulario):
        return PropiedadCreadaResultado(
            propiedad_id=uuid4(),
            redireccion="/propiedades?creada=1",
            mensaje_exito="Propiedad creada correctamente.",
        )

    original = service.crear_propiedad
    service.crear_propiedad = _crear_falso  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/propiedades/crear",
                data={
                    "titulo": "Penthouse Marina",
                    "direccion": "123 Ocean Dr",
                    "ciudad": "Miami",
                    "precio_mensual": "4500",
                    "habitaciones": "3",
                    "banos": "2.5",
                    "area_m2": "150",
                },
                follow_redirects=False,
            )
    finally:
        service.crear_propiedad = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/propiedades?creada=1"


@pytest.mark.asyncio
async def test_post_crear_propiedad_con_errores_re_renderiza_formulario() -> None:
    """Valida que los errores de negocio vuelvan a pintar la vista de alta."""

    errores = PropiedadCrearErrores(
        titulo="Este campo es obligatorio.",
        direccion="Este campo es obligatorio.",
    )
    contexto = PropiedadCrearVista(
        formulario=PropiedadCrearFormulario(),
        errores=errores,
    )

    async def _crear_falso(_session, _formulario):
        raise service.ErrorValidacionCreacionPropiedad(contexto)

    original = service.crear_propiedad
    service.crear_propiedad = _crear_falso  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/propiedades/crear",
                data={
                    "titulo": " ",
                    "direccion": " ",
                    "ciudad": "Miami",
                    "precio_mensual": "4500",
                    "habitaciones": "3",
                    "banos": "2.5",
                    "area_m2": "150",
                },
                follow_redirects=False,
            )
    finally:
        service.crear_propiedad = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "Este campo es obligatorio." in response.text


@pytest.mark.asyncio
async def test_get_propiedades_con_confirmacion_muestra_alerta_exito() -> None:
    """Asegura que la redirección post-alta muestre una confirmación visible."""

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