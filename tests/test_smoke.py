"""Smoke tests para endpoints base del bootstrap."""

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

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


async def _override_session_ok() -> AsyncIterator[_FakeSessionOk]:
    yield _FakeSessionOk()


async def _override_session_error() -> AsyncIterator[_FakeSessionError]:
    yield _FakeSessionError()


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
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Navegacion principal" in response.text
    assert "Propiedades" in response.text
    assert "24" in response.text
    assert "Contratos activos" in response.text
    assert "18" in response.text
    assert "Pagos pendientes" in response.text
    assert "5" in response.text
    assert "+3 este mes" in response.text
    assert "-2 desde ayer" in response.text
    assert "Sistema operando con normalidad. Proxima revision: 15 jul." in response.text
    assert "Apto. Reforma 12A" in response.text
    assert "Casa Polanco" in response.text
    assert "Local Condesa" in response.text
    assert response.text.count('id="flash-zone"') == 1
    assert response.text.count("<!-- TODO: estado-vacio -->") == 2
    assert response.text.count("<!-- TODO: estado-error -->") == 1
