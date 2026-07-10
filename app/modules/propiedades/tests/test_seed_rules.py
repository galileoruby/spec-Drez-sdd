"""Pruebas de reglas del seed de propiedades."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

MIGRATION_PATH = (
    Path(__file__).resolve().parents[4]
    / "alembic"
    / "versions"
    / "0003_seed_propiedades_miami.py"
)


def _load_seed_module() -> ModuleType:
    """Carga dinamicamente el modulo de migracion de seed."""

    spec = importlib.util.spec_from_file_location(
        "seed_propiedades_miami",
        MIGRATION_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_seed_contiene_exactamente_diez_propiedades_de_miami() -> None:
    """Valida cardinalidad y ciudad fija del set canonico."""

    seed_module = _load_seed_module()
    propiedades = seed_module.PROPIEDADES_MIAMI

    assert len(propiedades) == 10
    assert all(str(row["ciudad"]) == "Miami" for row in propiedades)


def test_seed_construye_imagen_determinista_por_id() -> None:
    """Valida el formato exacto de la URL de imagen."""

    seed_module = _load_seed_module()

    for row in seed_module.PROPIEDADES_MIAMI:
        expected = f"https://picsum.photos/seed/{row['id']}/800/500"
        assert seed_module._imagen_url(str(row["id"])) == expected


def test_seed_parametriza_por_id_en_sql() -> None:
    """Asegura que la sentencia use cast seguro para UUID."""

    source = MIGRATION_PATH.read_text(encoding="utf-8")

    assert "CAST(:id AS uuid)" in source
    assert "CAST(:ids AS uuid[])" in source
    assert ":id::uuid" not in source
