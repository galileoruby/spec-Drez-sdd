"""Servicios de dominio para propiedades."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from decimal import Decimal, InvalidOperation
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.propiedades import repository
from app.modules.propiedades.models import EstadoPropiedad, Propiedad
from app.modules.propiedades.schemas import (
    ListadoPropiedadesContexto,
    PropiedadCrearErrores,
    PropiedadCrearFormulario,
    PropiedadCrearVista,
    PropiedadCreadaResultado,
    PropiedadCardView,
)

FALLBACK_IMAGEN_LOCAL = "/static/icons/building-2.svg"

CardsProvider = Callable[[AsyncSession], Awaitable[list[Propiedad]]]
PropiedadExistenteProvider = Callable[
    [AsyncSession, str, str, str], Awaitable[Propiedad | None]
]
CrearPropiedadProvider = Callable[[AsyncSession, Propiedad], Awaitable[Propiedad]]
ImagenDeterministaProvider = Callable[[UUID], str]


class ErrorValidacionCreacionPropiedad(Exception):
    """Señala que el formulario de alta contiene errores de negocio."""

    def __init__(self, contexto: PropiedadCrearVista) -> None:
        super().__init__("No fue posible validar la creación de la propiedad")
        self.contexto = contexto


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


def construir_imagen_determinista(propiedad_id: UUID) -> str:
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


def _limpiar_texto(valor: str) -> str:
    """Normaliza espacios para texto ingresado por formulario."""

    return " ".join(valor.strip().split())


def _agregar_error(errores: dict[str, str], campo: str, mensaje: str) -> None:
    """Agrega el primer error encontrado para un campo sin sobreescribirlo."""

    errores.setdefault(campo, mensaje)


def _parsear_decimal(valor: str, campo: str, errores: dict[str, str]) -> Decimal | None:
    """Intenta convertir un valor de formulario a Decimal."""

    if not valor:
        _agregar_error(errores, campo, "Este campo es obligatorio.")
        return None

    try:
        return Decimal(valor)
    except (InvalidOperation, ValueError):
        _agregar_error(errores, campo, "Debe ser un número válido.")
        return None


def _parsear_entero(valor: str, campo: str, errores: dict[str, str]) -> int | None:
    """Intenta convertir un valor de formulario a entero."""

    if not valor:
        _agregar_error(errores, campo, "Este campo es obligatorio.")
        return None

    try:
        return int(valor)
    except (TypeError, ValueError):
        _agregar_error(errores, campo, "Debe ser un entero válido.")
        return None


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


def construir_contexto_creacion(
    formulario: PropiedadCrearFormulario | None = None,
    errores: PropiedadCrearErrores | None = None,
) -> PropiedadCrearVista:
    """Construye el contexto base de la pantalla de alta."""

    return PropiedadCrearVista(
        formulario=formulario or PropiedadCrearFormulario(),
        errores=errores or PropiedadCrearErrores(),
    )


def _formulario_normativo(
    formulario: PropiedadCrearFormulario,
) -> tuple[dict[str, str], PropiedadCrearErrores]:
    """Valida y normaliza los campos de entrada del formulario."""

    errores: dict[str, str] = {}

    titulo = _limpiar_texto(formulario.titulo)
    direccion = _limpiar_texto(formulario.direccion)
    ciudad = _limpiar_texto(formulario.ciudad)
    precio_mensual = _parsear_decimal(formulario.precio_mensual.strip(), "precio_mensual", errores)
    habitaciones = _parsear_entero(formulario.habitaciones.strip(), "habitaciones", errores)
    banos = _parsear_decimal(formulario.banos.strip(), "banos", errores)
    area_m2 = _parsear_decimal(formulario.area_m2.strip(), "area_m2", errores)

    if not titulo:
        _agregar_error(errores, "titulo", "Este campo es obligatorio.")
    if not direccion:
        _agregar_error(errores, "direccion", "Este campo es obligatorio.")
    if not ciudad:
        _agregar_error(errores, "ciudad", "Este campo es obligatorio.")

    if precio_mensual is not None and precio_mensual <= 0:
        _agregar_error(errores, "precio_mensual", "Debe ser mayor que 0.")

    if habitaciones is not None and not 1 <= habitaciones <= 10:
        _agregar_error(errores, "habitaciones", "Debe estar entre 1 y 10.")

    if banos is not None:
        if banos.as_tuple().exponent < -1:
            _agregar_error(errores, "banos", "Debe tener como máximo un decimal.")
        elif not Decimal("1.0") <= banos <= Decimal("5.0"):
            _agregar_error(errores, "banos", "Debe estar entre 1.0 y 5.0.")

    if area_m2 is not None and area_m2 <= 0:
        _agregar_error(errores, "area_m2", "Debe ser mayor que 0.")

    if errores:
        return (
            {},
            PropiedadCrearErrores(
                titulo=errores.get("titulo"),
                direccion=errores.get("direccion"),
                ciudad=errores.get("ciudad"),
                precio_mensual=errores.get("precio_mensual"),
                habitaciones=errores.get("habitaciones"),
                banos=errores.get("banos"),
                area_m2=errores.get("area_m2"),
            ),
        )

    return (
        {
            "titulo": titulo,
            "direccion": direccion,
            "ciudad": ciudad,
            "precio_mensual": str(precio_mensual),
            "habitaciones": str(habitaciones),
            "banos": str(banos.quantize(Decimal("0.1"))),
            "area_m2": str(area_m2),
        },
        PropiedadCrearErrores(),
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


async def crear_propiedad(
    session: AsyncSession,
    formulario: PropiedadCrearFormulario,
    *,
    obtener_existente: PropiedadExistenteProvider = repository.obtener_por_identidad_compuesta,
    guardar_propiedad: CrearPropiedadProvider = repository.crear_propiedad,
    construir_imagen: ImagenDeterministaProvider = construir_imagen_determinista,
) -> PropiedadCreadaResultado:
    """Valida y persiste una nueva propiedad en el repositorio."""

    formulario_normalizado, errores = _formulario_normativo(formulario)
    contexto = construir_contexto_creacion(formulario, errores)
    if errores.model_dump(exclude_none=True):
        raise ErrorValidacionCreacionPropiedad(contexto)

    assert formulario_normalizado
    titulo = formulario_normalizado["titulo"]
    direccion = formulario_normalizado["direccion"]
    ciudad = formulario_normalizado["ciudad"]

    existente = await obtener_existente(session, titulo, direccion, ciudad)
    if existente is not None:
        errores = PropiedadCrearErrores(
            general="Ya existe una propiedad con la misma identidad de negocio.",
        )
        raise ErrorValidacionCreacionPropiedad(
            construir_contexto_creacion(formulario, errores)
        )

    propiedad = Propiedad(
        titulo=titulo,
        direccion=direccion,
        ciudad=ciudad,
        precio_mensual=Decimal(formulario_normalizado["precio_mensual"]),
        habitaciones=int(formulario_normalizado["habitaciones"]),
        banos=Decimal(formulario_normalizado["banos"]),
        area_m2=Decimal(formulario_normalizado["area_m2"]),
        estado=EstadoPropiedad.DISPONIBLE,
        imagen_url=FALLBACK_IMAGEN_LOCAL,
    )

    propiedad = await guardar_propiedad(session, propiedad)

    try:
        imagen_url = construir_imagen(propiedad.id)
    except Exception:
        imagen_url = FALLBACK_IMAGEN_LOCAL

    if not _imagen_url_utilizable(imagen_url):
        imagen_url = FALLBACK_IMAGEN_LOCAL

    propiedad.imagen_url = imagen_url
    await session.flush()
    await session.commit()
    await session.refresh(propiedad)

    return PropiedadCreadaResultado(
        propiedad_id=propiedad.id,
        redireccion="/propiedades?creada=1",
        mensaje_exito="Propiedad creada correctamente.",
    )
