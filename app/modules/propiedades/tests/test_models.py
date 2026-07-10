"""Pruebas unitarias de contratos del modelo Propiedad."""

from typing import cast

from sqlalchemy import DateTime, Table, UniqueConstraint

from app.modules.propiedades.models import EstadoPropiedad, Propiedad


def test_estado_propiedad_contiene_catalogo_cerrado() -> None:
    """Valida que el catalogo de estados sea exactamente el esperado."""

    assert [estado.value for estado in EstadoPropiedad] == [
        "disponible",
        "rentada",
        "mantenimiento",
        "inactiva",
    ]


def test_propiedad_declara_campos_requeridos() -> None:
    """Verifica los campos obligatorios definidos por la feature."""

    columnas = set(Propiedad.__table__.c.keys())
    assert columnas == {
        "id",
        "titulo",
        "direccion",
        "ciudad",
        "precio_mensual",
        "habitaciones",
        "banos",
        "area_m2",
        "estado",
        "imagen_url",
        "created_at",
        "updated_at",
    }


def test_propiedad_tiene_unique_compuesta_e_indices_operativos() -> None:
    """Asegura unicidad de negocio e indices de filtrado."""

    table = cast(Table, Propiedad.__table__)
    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert len(unique_constraints) == 1
    assert tuple(unique_constraints[0].columns.keys()) == (
        "titulo",
        "direccion",
        "ciudad",
    )

    index_names = {index.name for index in table.indexes}
    assert "ix_propiedades_ciudad" in index_names
    assert "ix_propiedades_estado" in index_names


def test_timestamps_timezone_aware() -> None:
    """Garantiza que created_at y updated_at sean timezone-aware."""

    created_type = Propiedad.__table__.c.created_at.type
    updated_type = Propiedad.__table__.c.updated_at.type

    assert isinstance(created_type, DateTime)
    assert isinstance(updated_type, DateTime)
    assert created_type.timezone is True
    assert updated_type.timezone is True
