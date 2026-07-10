"""Smoke tests para endpoints base del bootstrap."""

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.modules.propiedades.models import EstadoPropiedad

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres.test:pass@localhost:6543/postgres",
)
os.environ.setdefault(
    "DATABASE_URL_DIRECT",
    "postgresql+asyncpg://postgres.test:pass@localhost:5432/postgres",
)

from app.database import get_session
from app.main import app


class _FakeSessionOk:
    async def execute(self, _query):
        return None


class _FakeSessionError:
    async def execute(self, _query):
        raise RuntimeError("db error")


class _FakeCountResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeSessionHomeConDatos:
    async def execute(self, query):
        if "SELECT 1" in str(query):
            return None
        return _FakeCountResult(
            [
                (EstadoPropiedad.DISPONIBLE, 24),
                (EstadoPropiedad.RENTADA, 18),
            ]
        )


class _FakeSessionHomeSinDatos:
    async def execute(self, query):
        if "SELECT 1" in str(query):
            return None
        return _FakeCountResult([])


async def _override_session_ok() -> AsyncIterator[_FakeSessionOk]:
    yield _FakeSessionOk()


async def _override_session_error() -> AsyncIterator[_FakeSessionError]:
    yield _FakeSessionError()


async def _override_session_home_con_datos() -> AsyncIterator[_FakeSessionHomeConDatos]:
    yield _FakeSessionHomeConDatos()


async def _override_session_home_sin_datos() -> AsyncIterator[_FakeSessionHomeSinDatos]:
    yield _FakeSessionHomeSinDatos()


@pytest.mark.asyncio
async def test_get_health_ok() -> None:
    app.dependency_overrides[get_session] = _override_session_ok
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_health_degraded() -> None:
    app.dependency_overrides[get_session] = _override_session_error
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "degraded", "db": "error"}
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_root_dashboard_demo() -> None:
    app.dependency_overrides[get_session] = _override_session_home_con_datos
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Navegacion principal" in response.text
    assert "Propiedades disponibles" in response.text
    assert "24" in response.text
    assert "Propiedades rentadas" in response.text
    assert "18" in response.text
    assert "Ingresos del mes" in response.text
    assert "Pagos vencidos" in response.text
    assert "No operativo" in response.text
    assert "Pendiente de modelado en spec futura" in response.text
    assert "Metricas operativas actualizadas desde datos persistidos." in response.text
    assert (
        "Ingresos y vencidos permanecen en modo no operativo en esta iteracion."
        in response.text
    )
    assert "Apto. Reforma 12A" in response.text
    assert "Casa Polanco" in response.text
    assert "Local Condesa" in response.text
    assert response.text.count('id="flash-zone"') == 1
    assert response.text.count("<!-- TODO: estado-vacio -->") == 1
    assert response.text.count("<!-- TODO: estado-error -->") == 1
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_root_dashboard_muestra_estado_vacio_real() -> None:
    app.dependency_overrides[get_session] = _override_session_home_sin_datos
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert (
        "No hay propiedades disponibles o rentadas para mostrar metricas operativas."
        in response.text
    )
    app.dependency_overrides.clear()
