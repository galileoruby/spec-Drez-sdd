"""Acceso a datos para propiedades."""

from __future__ import annotations

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.propiedades.models import EstadoPropiedad, Propiedad


def _normalizar_identidad_negocio(
    titulo: str,
    direccion: str,
    ciudad: str,
) -> tuple[str, str, str]:
    """Normaliza la identidad funcional para comparaciones deterministas."""

    return (
        " ".join(titulo.strip().split()).casefold(),
        " ".join(direccion.strip().split()).casefold(),
        " ".join(ciudad.strip().split()).casefold(),
    )


async def obtener_por_identidad_compuesta(
    session: AsyncSession,
    titulo: str,
    direccion: str,
    ciudad: str,
) -> Propiedad | None:
    """Obtiene una propiedad por su identidad de negocio compuesta."""

    titulo_norm, direccion_norm, ciudad_norm = _normalizar_identidad_negocio(
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


async def contar_operativas_por_estado(
    session: AsyncSession,
) -> dict[EstadoPropiedad, int]:
    """Retorna conteos de propiedades disponibles y rentadas."""

    conteos: dict[EstadoPropiedad, int] = {
        EstadoPropiedad.DISPONIBLE: 0,
        EstadoPropiedad.RENTADA: 0,
    }
    estados_objetivo = [EstadoPropiedad.DISPONIBLE, EstadoPropiedad.RENTADA]

    stmt = (
        select(Propiedad.estado, func.count(Propiedad.id))
        .where(Propiedad.estado.in_(estados_objetivo))
        .group_by(Propiedad.estado)
    )
    result = await session.execute(stmt)

    for estado, total in result.all():
        conteos[estado] = int(total)

    return conteos


async def listar_para_cards(session: AsyncSession) -> list[Propiedad]:
    """Lista propiedades para vista de cards ordenadas por fecha de creacion."""

    stmt = select(Propiedad).order_by(Propiedad.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def crear_propiedad(session: AsyncSession, propiedad: Propiedad) -> Propiedad:
    """Persiste una nueva propiedad y materializa el id generado por la base."""

    session.add(propiedad)
    await session.flush()
    await session.refresh(propiedad)
    return propiedad
