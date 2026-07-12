"""DTOs del modulo propiedades."""

from pydantic import BaseModel, ConfigDict
from uuid import UUID


class PropiedadCardView(BaseModel):
    """Representa la informacion visible de una propiedad en formato card."""

    model_config = ConfigDict(frozen=True)

    imagen_url: str
    titulo: str
    direccion: str
    habitaciones: int
    banos: str
    area_m2: str
    precio_renta: str
    estado: str


class ListadoPropiedadesContexto(BaseModel):
    """Contrato de contexto server-rendered para la pagina de propiedades."""

    model_config = ConfigDict(frozen=True)

    propiedades: list[PropiedadCardView]
    mostrar_estado_vacio: bool
    total_propiedades: int
    mostrar_exito: bool = False
    mensaje_exito: str | None = None


class PropiedadCrearFormulario(BaseModel):
    """Contrato de entrada cruda del formulario de alta de propiedades."""

    model_config = ConfigDict(frozen=True)

    titulo: str = ""
    direccion: str = ""
    ciudad: str = ""
    precio_mensual: str = ""
    habitaciones: str = ""
    banos: str = ""
    area_m2: str = ""


class PropiedadCrearErrores(BaseModel):
    """Errores asociados a cada campo del formulario de alta."""

    model_config = ConfigDict(frozen=True)

    titulo: str | None = None
    direccion: str | None = None
    ciudad: str | None = None
    precio_mensual: str | None = None
    habitaciones: str | None = None
    banos: str | None = None
    area_m2: str | None = None
    general: str | None = None


class PropiedadCrearVista(BaseModel):
    """Contexto server-rendered para la pantalla de alta de propiedades."""

    model_config = ConfigDict(frozen=True)

    formulario: PropiedadCrearFormulario
    errores: PropiedadCrearErrores


class PropiedadCreadaResultado(BaseModel):
    """Resultado funcional de una creacion exitosa de propiedad."""

    model_config = ConfigDict(frozen=True)

    propiedad_id: UUID
    redireccion: str
    mensaje_exito: str
