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
    assert "Propiedades activas" in response.text
    assert "12" in response.text
    assert "Contratos vigentes" in response.text
    assert "9" in response.text
    assert "Ingresos del mes" in response.text
    assert "$8,750" in response.text
