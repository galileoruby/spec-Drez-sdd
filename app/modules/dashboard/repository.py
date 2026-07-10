"""Acceso de lectura para datos del dashboard."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.propiedades import repository as propiedades_repository
from app.modules.propiedades.models import EstadoPropiedad


async def obtener_conteos_operativos(session: AsyncSession) -> tuple[int, int]:
    """Retorna los conteos de propiedades disponibles y rentadas."""

    conteos = await propiedades_repository.contar_operativas_por_estado(session)
    return (
        conteos[EstadoPropiedad.DISPONIBLE],
        conteos[EstadoPropiedad.RENTADA],
    )
