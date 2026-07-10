"""Servicios de dominio para propiedades."""

from __future__ import annotations

from uuid import UUID


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
