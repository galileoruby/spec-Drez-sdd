"""DTOs del modulo propiedades (placeholders estructurales)."""

from pydantic import BaseModel, ConfigDict


class _PlaceholderSchema(BaseModel):
    """Schema interno para validar configuracion base del modulo."""

    model_config = ConfigDict(frozen=True)
