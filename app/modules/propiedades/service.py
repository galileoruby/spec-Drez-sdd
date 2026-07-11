"""Servicios de dominio para propiedades."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.propiedades import repository
from app.modules.propiedades.models import Propiedad
from app.modules.propiedades.schemas import (
    ListadoPropiedadesContexto,
    PropiedadCardView,
)

FALLBACK_IMAGEN_LOCAL = "/static/icons/building-2.svg"

CardsProvider = Callable[[AsyncSession], Awaitable[list[Propiedad]]]


def normalizar_identidad_negocio(
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


def construir_imagen_determinista(propiedad_id: UUID | str) -> str:
    """Construye la URL de imagen determinista derivada del identificador."""

    return f"https://picsum.photos/seed/{propiedad_id}/800/500"


def _imagen_url_utilizable(imagen_url: str | None) -> bool:
    """Valida si la URL de imagen puede renderizarse directamente."""

    if not imagen_url:
        return False
    return imagen_url.startswith(("http://", "https://", "/static/"))


def _texto_visible(valor: str | None, fallback: str) -> str:
    """Retorna texto saneado para evitar valores vacios en UI."""

    if valor is None:
        return fallback
    texto = " ".join(valor.strip().split())
    return texto or fallback


def _formatear_decimal(
    valor: Decimal | float | None,
    precision: int = 1,
    fallback: str = "0",
) -> str:
    """Formatea un decimal para salida de template sin trailing innecesario."""

    if valor is None:
        return fallback
    numero = float(valor)
    return f"{numero:.{precision}f}".rstrip("0").rstrip(".")


def _mapear_a_card(propiedad: Propiedad) -> PropiedadCardView:
    """Transforma una entidad de dominio en DTO de card renderizable."""

    imagen_url = (
        propiedad.imagen_url if _imagen_url_utilizable(propiedad.imagen_url) else None
    )
    titulo = _texto_visible(propiedad.titulo, "Propiedad sin titulo")
    direccion = _texto_visible(propiedad.direccion, "Direccion no disponible")
    ciudad = _texto_visible(propiedad.ciudad, "Ciudad no disponible")
    direccion_compuesta = f"{direccion}, {ciudad}"
    precio_renta = f"${float(propiedad.precio_mensual or 0):,.0f}/mes"
    estado = propiedad.estado.value.replace("_", " ").capitalize()
    habitaciones = max(int(propiedad.habitaciones or 0), 0)

    return PropiedadCardView(
        imagen_url=imagen_url or FALLBACK_IMAGEN_LOCAL,
        titulo=titulo,
        direccion=direccion_compuesta,
        habitaciones=habitaciones,
        banos=_formatear_decimal(propiedad.banos),
        area_m2=f"{_formatear_decimal(propiedad.area_m2)} m2",
        precio_renta=precio_renta,
        estado=estado,
    )


async def construir_contexto_listado(
    session: AsyncSession,
    cards_provider: CardsProvider = repository.listar_para_cards,
) -> ListadoPropiedadesContexto:
    """Construye el contexto de render para la pagina de propiedades."""

    propiedades = await cards_provider(session)
    cards = [_mapear_a_card(propiedad) for propiedad in propiedades]

    return ListadoPropiedadesContexto(
        propiedades=cards,
        total_propiedades=len(cards),
        mostrar_estado_vacio=len(cards) == 0,
    )
