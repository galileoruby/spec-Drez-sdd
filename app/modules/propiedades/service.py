"""Servicios de dominio para propiedades."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
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
    PropiedadEditarErrores,
    PropiedadEditarFormulario,
    PropiedadEditarVista,
    PropiedadEditadaResultado,
)

FALLBACK_IMAGEN_LOCAL = "/static/icons/building-2.svg"

CardsProvider = Callable[[AsyncSession], Awaitable[list[Propiedad]]]
PropiedadExistenteProvider = Callable[
    [AsyncSession, str, str, str], Awaitable[Propiedad | None]
]
PropiedadExistenteExcluyenteProvider = Callable[
    [AsyncSession, str, str, str, UUID], Awaitable[Propiedad | None]
]
PropiedadPorIdProvider = Callable[[AsyncSession, UUID], Awaitable[Propiedad | None]]
CrearPropiedadProvider = Callable[[AsyncSession, Propiedad], Awaitable[Propiedad]]
ActualizarPropiedadProvider = Callable[[AsyncSession, Propiedad], Awaitable[Propiedad]]
ImagenDeterministaProvider = Callable[[UUID], str]


class ErrorValidacionCreacionPropiedad(Exception):
    """Señala que el formulario de alta contiene errores de negocio."""

    def __init__(self, contexto: PropiedadCrearVista) -> None:
        super().__init__("No fue posible validar la creación de la propiedad")
        self.contexto = contexto


class ErrorValidacionEdicionPropiedad(Exception):
    """Señala que el formulario de edición contiene errores de negocio."""

    def __init__(self, contexto: PropiedadEditarVista) -> None:
        super().__init__("No fue posible validar la edición de la propiedad")
        self.contexto = contexto


class ErrorConflictoOptimistaEdicionPropiedad(Exception):
    """Señala que la propiedad fue modificada por otro proceso."""

    def __init__(self, contexto: PropiedadEditarVista) -> None:
        super().__init__("La propiedad cambió desde la última lectura")
        self.contexto = contexto


class PropiedadNoEncontradaError(Exception):
    """Señala que una propiedad solicitada no existe."""

    def __init__(self, propiedad_id: UUID) -> None:
        super().__init__(f"No existe una propiedad con id {propiedad_id}")
        self.propiedad_id = propiedad_id


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


def _propiedad_a_formulario_edicion(propiedad: Propiedad) -> PropiedadEditarFormulario:
    """Construye el formulario de edición a partir de una entidad persistida."""

    updated_at = ""
    if isinstance(propiedad.updated_at, datetime):
        updated_at = propiedad.updated_at.isoformat()

    return PropiedadEditarFormulario(
        titulo=propiedad.titulo,
        direccion=propiedad.direccion,
        ciudad=propiedad.ciudad,
        precio_mensual=str(propiedad.precio_mensual),
        habitaciones=str(propiedad.habitaciones),
        banos=str(propiedad.banos),
        area_m2=str(propiedad.area_m2),
        estado=propiedad.estado.value,
        updated_at=updated_at,
    )


def _errores_creacion_desde_dict(errores: dict[str, str]) -> PropiedadCrearErrores:
    """Convierte un diccionario de errores en el contrato de alta."""

    return PropiedadCrearErrores(
        titulo=errores.get("titulo"),
        direccion=errores.get("direccion"),
        ciudad=errores.get("ciudad"),
        precio_mensual=errores.get("precio_mensual"),
        habitaciones=errores.get("habitaciones"),
        banos=errores.get("banos"),
        area_m2=errores.get("area_m2"),
        general=errores.get("general"),
    )


def _errores_edicion_desde_dict(errores: dict[str, str]) -> PropiedadEditarErrores:
    """Convierte un diccionario de errores en el contrato de edición."""

    return PropiedadEditarErrores(
        titulo=errores.get("titulo"),
        direccion=errores.get("direccion"),
        ciudad=errores.get("ciudad"),
        precio_mensual=errores.get("precio_mensual"),
        habitaciones=errores.get("habitaciones"),
        banos=errores.get("banos"),
        area_m2=errores.get("area_m2"),
        estado=errores.get("estado"),
        general=errores.get("general"),
    )


def _es_estado_valido(estado: str) -> bool:
    """Indica si el valor recibido pertenece al catálogo de estados."""

    return estado in {item.value for item in EstadoPropiedad}


def _parsear_estado(valor: str, errores: dict[str, str]) -> str | None:
    """Intenta normalizar el estado recibido desde el formulario."""

    estado = _limpiar_texto(valor).casefold()
    if not estado:
        _agregar_error(errores, "estado", "Este campo es obligatorio.")
        return None
    if not _es_estado_valido(estado):
        _agregar_error(errores, "estado", "Debe seleccionar un estado válido.")
        return None
    return estado


def _formulario_normativo(
    formulario: PropiedadCrearFormulario | PropiedadEditarFormulario,
    *,
    requiere_estado: bool = False,
) -> tuple[dict[str, str], dict[str, str]]:
    """Valida y normaliza los campos de entrada del formulario."""

    errores: dict[str, str] = {}

    titulo = _limpiar_texto(formulario.titulo)
    direccion = _limpiar_texto(formulario.direccion)
    ciudad = _limpiar_texto(formulario.ciudad)
    precio_mensual = _parsear_decimal(formulario.precio_mensual.strip(), "precio_mensual", errores)
    habitaciones = _parsear_entero(formulario.habitaciones.strip(), "habitaciones", errores)
    banos = _parsear_decimal(formulario.banos.strip(), "banos", errores)
    area_m2 = _parsear_decimal(formulario.area_m2.strip(), "area_m2", errores)
    estado = _parsear_estado(getattr(formulario, "estado", ""), errores) if requiere_estado else EstadoPropiedad.DISPONIBLE.value

    if not titulo:
        _agregar_error(errores, "titulo", "Este campo es obligatorio.")
    if not direccion:
        _agregar_error(errores, "direccion", "Este campo es obligatorio.")
    if not ciudad:
        _agregar_error(errores, "ciudad", "Este campo es obligatorio.")

    if precio_mensual is not None and precio_mensual <= 0:
        _agregar_error(errores, "precio_mensual", "Debe ser mayor que 0.")

    if habitaciones is not None and not 1 <= habitaciones <= 15:
        _agregar_error(errores, "habitaciones", "Debe estar entre 1 y 15.")

    if banos is not None:
        if banos < Decimal("0.5") or banos > Decimal("8.0"):
            _agregar_error(errores, "banos", "Debe estar entre 0.5 y 8.0.")
        elif (banos * 2) % 1 != 0:
            _agregar_error(errores, "banos", "Debe avanzar en pasos de 0.5.")

    if area_m2 is not None and area_m2 <= 0:
        _agregar_error(errores, "area_m2", "Debe ser mayor que 0.")

    if errores or estado is None:
        return {}, errores

    return (
        {
            "titulo": titulo,
            "direccion": direccion,
            "ciudad": ciudad,
            "precio_mensual": str(precio_mensual),
            "habitaciones": str(habitaciones),
            "banos": str(banos.quantize(Decimal("0.1"))),
            "area_m2": str(area_m2),
            "estado": estado,
        },
        errores,
    )


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
        id=propiedad.id,
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


def construir_contexto_edicion(
    propiedad: Propiedad,
    formulario: PropiedadEditarFormulario | None = None,
    errores: PropiedadEditarErrores | None = None,
) -> PropiedadEditarVista:
    """Construye el contexto base de la pantalla de edición."""

    return PropiedadEditarVista(
        propiedad_id=propiedad.id,
        formulario=formulario or _propiedad_a_formulario_edicion(propiedad),
        errores=errores or PropiedadEditarErrores(),
        estados=[estado.value for estado in EstadoPropiedad],
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


def _parsear_updated_at(valor: str) -> datetime | None:
    """Intenta convertir el valor de control optimista recibido en el formulario."""

    if not valor:
        return None

    try:
        return datetime.fromisoformat(valor)
    except ValueError:
        return None


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
    errores_modelo = _errores_creacion_desde_dict(errores)
    contexto = construir_contexto_creacion(formulario, errores_modelo)
    if errores:
        raise ErrorValidacionCreacionPropiedad(contexto)

    assert formulario_normalizado
    titulo = formulario_normalizado["titulo"]
    direccion = formulario_normalizado["direccion"]
    ciudad = formulario_normalizado["ciudad"]

    existente = await obtener_existente(session, titulo, direccion, ciudad)
    if existente is not None:
        errores_modelo = PropiedadCrearErrores(
            general="Ya existe una propiedad con la misma identidad de negocio.",
        )
        raise ErrorValidacionCreacionPropiedad(
            construir_contexto_creacion(formulario, errores_modelo)
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


async def obtener_propiedad_por_id(
    session: AsyncSession,
    propiedad_id: UUID,
    *,
    obtener_por_id: PropiedadPorIdProvider = repository.obtener_por_id,
) -> Propiedad | None:
    """Obtiene una propiedad existente para edición o retorno 404."""

    return await obtener_por_id(session, propiedad_id)


async def editar_propiedad(
    session: AsyncSession,
    propiedad_id: UUID,
    formulario: PropiedadEditarFormulario,
    *,
    obtener_por_id: PropiedadPorIdProvider = repository.obtener_por_id,
    obtener_existente: PropiedadExistenteExcluyenteProvider = repository.obtener_por_identidad_compuesta_excluyendo_id,
    guardar_propiedad: ActualizarPropiedadProvider = repository.actualizar_propiedad,
) -> PropiedadEditadaResultado:
    """Valida y persiste una edición de propiedad existente."""

    propiedad = await obtener_por_id(session, propiedad_id)
    if propiedad is None:
        raise PropiedadNoEncontradaError(propiedad_id)

    formulario_normalizado, errores = _formulario_normativo(formulario, requiere_estado=True)
    errores_modelo = _errores_edicion_desde_dict(errores)
    contexto = construir_contexto_edicion(propiedad, formulario, errores_modelo)
    if errores:
        raise ErrorValidacionEdicionPropiedad(contexto)

    updated_at_formulario = _parsear_updated_at(formulario.updated_at)
    if updated_at_formulario is None or updated_at_formulario != propiedad.updated_at:
        errores_modelo = PropiedadEditarErrores(
            general="La propiedad cambió desde la última lectura. Recarga la página e intenta de nuevo.",
        )
        raise ErrorConflictoOptimistaEdicionPropiedad(
            construir_contexto_edicion(propiedad, formulario, errores_modelo)
        )

    existente = await obtener_existente(
        session,
        formulario_normalizado["titulo"],
        formulario_normalizado["direccion"],
        formulario_normalizado["ciudad"],
        propiedad_id,
    )
    if existente is not None:
        errores_modelo = PropiedadEditarErrores(
            general="Ya existe una propiedad con la misma identidad de negocio.",
        )
        raise ErrorValidacionEdicionPropiedad(
            construir_contexto_edicion(propiedad, formulario, errores_modelo)
        )

    propiedad.titulo = formulario_normalizado["titulo"]
    propiedad.direccion = formulario_normalizado["direccion"]
    propiedad.ciudad = formulario_normalizado["ciudad"]
    propiedad.precio_mensual = Decimal(formulario_normalizado["precio_mensual"])
    propiedad.habitaciones = int(formulario_normalizado["habitaciones"])
    propiedad.banos = Decimal(formulario_normalizado["banos"])
    propiedad.area_m2 = Decimal(formulario_normalizado["area_m2"])
    propiedad.estado = EstadoPropiedad(formulario_normalizado["estado"])
    propiedad.updated_at = datetime.now(UTC)

    propiedad = await guardar_propiedad(session, propiedad)
    await session.commit()
    await session.refresh(propiedad)

    return PropiedadEditadaResultado(
        propiedad_id=propiedad.id,
        redireccion="/propiedades?editada=1",
        mensaje_exito="Propiedad editada correctamente.",
    )
