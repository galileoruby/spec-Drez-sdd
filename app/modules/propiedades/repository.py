"""Acceso a datos para propiedades."""

from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.propiedades.models import EstadoPropiedad, Propiedad
from app.modules.propiedades.service import normalizar_identidad_negocio


async def obtener_por_identidad_compuesta(
    session: AsyncSession,
    titulo: str,
    direccion: str,
    ciudad: str,
) -> Propiedad | None:
    """Obtiene una propiedad por su identidad de negocio compuesta."""

    titulo_norm, direccion_norm, ciudad_norm = normalizar_identidad_negocio(
        titulo,
        direccion,
        ciudad,
    )
    stmt = _select_base().where(
        Propiedad.titulo == titulo_norm,
        Propiedad.direccion == direccion_norm,
        Propiedad.ciudad == ciudad_norm,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def listar_por_filtros(
    session: AsyncSession,
    ciudad: str | None = None,
    estado: EstadoPropiedad | None = None,
) -> list[Propiedad]:
    """Lista propiedades filtradas por ciudad y estado cuando aplica."""

    stmt = _select_base()
    if ciudad is not None:
        stmt = stmt.where(Propiedad.ciudad == ciudad)
    if estado is not None:
        stmt = stmt.where(Propiedad.estado == estado)
    result = await session.execute(stmt)
    return list(result.scalars().all())


def _select_base() -> Select[tuple[Propiedad]]:
    """Retorna un select base para reutilizar filtros."""

    return select(Propiedad)
