"""Pruebas de rutas HTTP para alta de propiedades."""

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
from app.modules.propiedades.schemas import (
    ListadoPropiedadesContexto,
    PropiedadCrearErrores,
    PropiedadCrearFormulario,
    PropiedadCrearVista,
    PropiedadCreadaResultado,
    PropiedadEditarErrores,
    PropiedadEditarFormulario,
    PropiedadEditarVista,
    PropiedadEditadaResultado,
)
from app.modules.propiedades.models import EstadoPropiedad


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
                    "banos": "8.5",
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
async def test_get_formulario_editar_propiedad_renderiza_la_pantalla() -> None:
    """Verifica que la ruta GET de edición entregue la vista correcta."""

    propiedad = _PropiedadEdicionFake(
        id=uuid4(),
        titulo="Penthouse Marina",
        direccion="123 Ocean Dr",
        ciudad="Miami",
        precio_mensual=4500,
        habitaciones=3,
        banos=2.5,
        area_m2=150,
        estado=EstadoPropiedad.DISPONIBLE,
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
    assert f'action="/propiedades/editar/{propiedad.id}"' in response.text
    assert 'name="estado"' in response.text


@pytest.mark.asyncio
async def test_post_editar_propiedad_exitosa_redirige_al_listado() -> None:
    """Confirma que la edición exitosa redirige al listado con 303."""

    propiedad_id = uuid4()
    resultado_edicion = PropiedadEditadaResultado(
        propiedad_id=propiedad_id,
        redireccion="/propiedades?editada=1",
        mensaje_exito="Propiedad editada correctamente.",
    )

    async def _editar_falso(_session, _propiedad_id, _formulario):
        return resultado_edicion

    original = service.editar_propiedad
    service.editar_propiedad = _editar_falso  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/propiedades/editar/{propiedad_id}",
                data={
                    "titulo": "Penthouse Marina",
                    "direccion": "123 Ocean Dr",
                    "ciudad": "Miami",
                    "precio_mensual": "4800",
                    "habitaciones": "4",
                    "banos": "3.0",
                    "area_m2": "155",
                    "estado": "rentada",
                    "updated_at": datetime.now(UTC).isoformat(),
                },
                follow_redirects=False,
            )
    finally:
        service.editar_propiedad = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 303
    assert response.headers["location"] == "/propiedades?editada=1"


@pytest.mark.asyncio
async def test_post_editar_propiedad_con_errores_re_renderiza_formulario() -> None:
    """Valida que los errores de negocio vuelvan a pintar la vista de edición."""

    propiedad_id = uuid4()
    propiedad = _PropiedadEdicionFake(
        id=propiedad_id,
        titulo="Penthouse Marina",
        direccion="123 Ocean Dr",
        ciudad="Miami",
        precio_mensual=4500,
        habitaciones=3,
        banos=2.5,
        area_m2=150,
        estado=EstadoPropiedad.DISPONIBLE,
        updated_at=datetime.now(UTC),
    )
    errores = PropiedadEditarErrores(
        titulo="Este campo es obligatorio.",
        estado="Debe seleccionar un estado válido.",
    )
    contexto = PropiedadEditarVista(
        propiedad_id=propiedad.id,
        formulario=PropiedadEditarFormulario(
            titulo=" ",
            direccion="123 Ocean Dr",
            ciudad="Miami",
            precio_mensual="0",
            habitaciones="16",
            banos="8.5",
            area_m2="-1",
            estado="",
            updated_at=propiedad.updated_at.isoformat(),
        ),
        errores=errores,
        estados=[estado.value for estado in EstadoPropiedad],
    )

    async def _editar_falso(_session, _propiedad_id, _formulario):
        raise service.ErrorValidacionEdicionPropiedad(contexto)

    original = service.editar_propiedad
    service.editar_propiedad = _editar_falso  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/propiedades/editar/{propiedad_id}",
                data={
                    "titulo": " ",
                    "direccion": "123 Ocean Dr",
                    "ciudad": "Miami",
                    "precio_mensual": "0",
                    "habitaciones": "16",
                    "banos": "8.5",
                    "area_m2": "-1",
                    "estado": "",
                    "updated_at": propiedad.updated_at.isoformat(),
                },
                follow_redirects=False,
            )
    finally:
        service.editar_propiedad = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "Este campo es obligatorio." in response.text


@pytest.mark.asyncio
async def test_post_editar_propiedad_con_formulario_vacio_re_renderiza_html() -> None:
    """Confirma que un envío vacío sigue el flujo HTML de validación de negocio."""

    propiedad_id = uuid4()
    contexto = PropiedadEditarVista(
        propiedad_id=propiedad_id,
        formulario=PropiedadEditarFormulario(),
        errores=PropiedadEditarErrores(
            titulo="Este campo es obligatorio.",
            direccion="Este campo es obligatorio.",
            ciudad="Este campo es obligatorio.",
            precio_mensual="Debe ser mayor que 0.",
            habitaciones="Debe estar entre 1 y 15.",
            banos="Debe estar entre 0.5 y 8.0.",
            area_m2="Debe ser mayor que 0.",
            estado="Este campo es obligatorio.",
        ),
        estados=[estado.value for estado in EstadoPropiedad],
    )

    async def _editar_falso(_session, _propiedad_id, _formulario):
        raise service.ErrorValidacionEdicionPropiedad(contexto)

    original = service.editar_propiedad
    service.editar_propiedad = _editar_falso  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/propiedades/editar/{propiedad_id}",
                data={},
                follow_redirects=False,
            )
    finally:
        service.editar_propiedad = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert "Editar propiedad" in response.text
    assert "Este campo es obligatorio." in response.text


@pytest.mark.asyncio
async def test_post_editar_propiedad_conflicto_muestra_html_con_errores() -> None:
    """Confirma que el conflicto optimista se renderiza como HTML y no como JSON técnico."""

    propiedad_id = uuid4()
    contexto = PropiedadEditarVista(
        propiedad_id=propiedad_id,
        formulario=PropiedadEditarFormulario(
            titulo="Penthouse Marina",
            direccion="123 Ocean Dr",
            ciudad="Miami",
            precio_mensual="4800",
            habitaciones="4",
            banos="3.0",
            area_m2="155",
            estado="rentada",
            updated_at=(datetime.now(UTC).replace(year=datetime.now(UTC).year - 1)).isoformat(),
        ),
        errores=PropiedadEditarErrores(
            general="La propiedad cambió desde la última lectura. Recarga la página e intenta de nuevo.",
        ),
        estados=[estado.value for estado in EstadoPropiedad],
    )

    async def _editar_falso(_session, _propiedad_id, _formulario):
        raise service.ErrorConflictoOptimistaEdicionPropiedad(contexto)

    original = service.editar_propiedad
    service.editar_propiedad = _editar_falso  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/propiedades/editar/{propiedad_id}",
                data={
                    "titulo": "Penthouse Marina",
                    "direccion": "123 Ocean Dr",
                    "ciudad": "Miami",
                    "precio_mensual": "4800",
                    "habitaciones": "4",
                    "banos": "3.0",
                    "area_m2": "155",
                    "estado": "rentada",
                    "updated_at": (datetime.now(UTC).replace(year=datetime.now(UTC).year - 1)).isoformat(),
                },
                follow_redirects=False,
            )
    finally:
        service.editar_propiedad = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert "La propiedad cambió desde la última lectura." in response.text


@pytest.mark.asyncio
async def test_get_editar_propiedad_inexistente_devuelve_404() -> None:
    """Asegura que un id inexistente corte el flujo con 404."""

    async def _propiedad_inexistente(_session, _propiedad_id):
        return None

    original = service.obtener_propiedad_por_id
    service.obtener_propiedad_por_id = _propiedad_inexistente  # type: ignore[assignment]
    app.dependency_overrides[get_session] = _override_session_sin_uso
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/propiedades/editar/{uuid4()}")
    finally:
        service.obtener_propiedad_por_id = original  # type: ignore[assignment]
        app.dependency_overrides.clear()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_propiedades_con_confirmacion_muestra_alerta_de_edicion() -> None:
    """Asegura que el listado renderice una alerta de éxito tras la edición."""

    app.dependency_overrides[get_session] = _override_session_listado_vacio
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/propiedades?editada=1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Propiedad editada correctamente." in response.text
    assert "alerta--success" in response.text


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