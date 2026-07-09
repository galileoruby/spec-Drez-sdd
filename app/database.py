"""Utilidades de base de datos con SQLAlchemy async."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()


def _build_async_database_url(raw_url: str) -> str:
    """Garantiza el driver asyncpg para URLs de PostgreSQL."""
    if raw_url.startswith("postgresql+asyncpg://"):
        return raw_url
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return raw_url


class Base(DeclarativeBase):
    """Base declarativa para modelos SQLAlchemy."""


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Crea el engine async de forma perezosa para evitar efectos en import."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            _build_async_database_url(settings.DATABASE_URL),
            pool_pre_ping=True,
            connect_args={
                "statement_cache_size": 0,
                "prepared_statement_cache_size": 0,
                "ssl": "require",
            },
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Crea el session factory async de forma perezosa."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Entrega una sesión async por request."""
    async with get_session_factory()() as session:
        yield session
