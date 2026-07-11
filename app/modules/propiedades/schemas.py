"""DTOs del modulo propiedades."""

from pydantic import BaseModel, ConfigDict


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
