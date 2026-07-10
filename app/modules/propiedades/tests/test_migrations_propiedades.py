"""Pruebas de consistencia para migraciones del dominio propiedades."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import cast

from sqlalchemy import DateTime

from app.modules.propiedades.models import Propiedad

MIGRATION_0002 = (
    Path(__file__).resolve().parents[4]
    / "alembic"
    / "versions"
    / "0002_create_propiedades.py"
)
MIGRATION_0003 = (
    Path(__file__).resolve().parents[4]
    / "alembic"
    / "versions"
    / "0003_seed_propiedades_miami.py"
)


def _load_migration(path: Path, module_name: str) -> ModuleType:
    """Carga dinamicamente un modulo de migracion."""

    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cadena_de_revisiones_0002_a_0003() -> None:
    """Verifica orden y dependencia entre revisiones nuevas."""

    migration_0002 = _load_migration(MIGRATION_0002, "m0002")
    migration_0003 = _load_migration(MIGRATION_0003, "m0003")

    assert migration_0002.down_revision == "20260708_baseline"
    assert migration_0003.down_revision == migration_0002.revision


def test_0002_define_estructura_reversible() -> None:
    """Asegura presencia de indices, tabla y drop de enum en downgrade."""

    source = MIGRATION_0002.read_text(encoding="utf-8")

    assert "op.create_table(" in source
    assert "ix_propiedades_ciudad" in source
    assert "ix_propiedades_estado" in source
    assert "DROP TYPE IF EXISTS estado_propiedad" in source


def test_0003_define_upsert_idempotente_y_reglas_timestamps() -> None:
    """Valida sentencia ON CONFLICT y politica server-side de timestamps."""

    source = MIGRATION_0003.read_text(encoding="utf-8")

    assert "ON CONFLICT (titulo, direccion, ciudad) DO UPDATE SET" in source
    assert "updated_at = now()" in source
    assert "created_at" not in source
    assert "op.get_bind().execute(sa.text(" not in source
    assert "bind.execute(" in source


def test_0003_no_usa_timestamps_python_naive() -> None:
    """Evita drift por fechas generadas en Python."""

    source = MIGRATION_0003.read_text(encoding="utf-8")

    assert "datetime.utcnow" not in source
    assert "datetime.now" not in source


def test_modelo_declara_datetime_timezone_aware() -> None:
    """Corrobora que el modelo usa DateTime con zona horaria."""

    created_type = cast(DateTime, Propiedad.__table__.c.created_at.type)
    updated_type = cast(DateTime, Propiedad.__table__.c.updated_at.type)

    assert created_type.timezone is True
    assert updated_type.timezone is True
