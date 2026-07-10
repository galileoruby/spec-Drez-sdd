"""Preflight de base de datos para el flujo Speckit.

Detecta el estado real de la base apuntada por ``DATABASE_URL_DIRECT`` y
aplica automáticamente la acción correcta antes de ejecutar
``speckit.implement``. Emite un resumen JSON por stdout y un código de
salida discreto (0 sano, 10 corregido, 20 requiere intervención).

Reglas inquebrantables heredadas de la constitución:

- Prohibido ``alembic stamp`` como atajo para alinear historial.
- Prohibido bypass manual de migraciones pendientes.
- ``DROP SCHEMA public`` solo está permitido cuando ``--allow-reset`` es
  explícito y ``APP_ENV`` distinto de ``prod``.
- Toda conexión usa ``asyncpg`` vía ``create_async_engine`` con
  ``ssl=require``.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

from app.config import get_settings  # noqa: E402


@dataclass(frozen=True)
class EstadoBase:
    """Snapshot del estado actual de la base."""

    nombre: str
    version_actual: str | None
    head_objetivo: str | None
    tablas_app: int


def _to_asyncpg_url(url: str) -> str:
    """Asegura que la URL use el driver asyncpg."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _obtener_heads() -> list[str]:
    """Lista las revisiones marcadas como head en el historial local."""
    resultado = subprocess.run(
        [sys.executable, "-m", "alembic", "heads"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=True,
    )
    heads: list[str] = []
    for linea in resultado.stdout.splitlines():
        token = linea.strip()
        if not token:
            continue
        heads.append(token.split()[0])
    return heads


def _listar_revisiones() -> list[str]:
    """Devuelve todas las revisiones conocidas por Alembic."""
    resultado = subprocess.run(
        [sys.executable, "-m", "alembic", "history"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=True,
    )
    revisiones: list[str] = []
    for linea in resultado.stdout.splitlines():
        recorte = linea.strip()
        if "->" not in recorte:
            continue
        derecha = recorte.split("->", 1)[1].strip()
        rev = derecha.split(",", 1)[0].strip().split()[0]
        revisiones.append(rev)
    return revisiones


async def _detectar(head_objetivo: str) -> EstadoBase:
    """Consulta la base y clasifica el estado actual."""
    settings = get_settings()
    url = _to_asyncpg_url(settings.DATABASE_URL_DIRECT)
    engine = create_async_engine(
        url,
        connect_args={
            "ssl": "require",
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        },
    )
    try:
        async with engine.connect() as conn:
            existe_alembic = await conn.scalar(
                text("SELECT to_regclass('public.alembic_version')"),
            )
            tablas_app_raw = await conn.scalar(
                text(
                    "SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public' "
                    "AND table_name <> 'alembic_version'",
                ),
            )
            version_actual: str | None = None
            if existe_alembic is not None:
                version_actual = await conn.scalar(
                    text("SELECT version_num FROM alembic_version LIMIT 1"),
                )
    finally:
        await engine.dispose()

    tablas_app = int(tablas_app_raw or 0)

    if existe_alembic is None and tablas_app == 0:
        nombre = "EMPTY"
    elif existe_alembic is None and tablas_app > 0:
        nombre = "DRIFTED"
    elif version_actual == head_objetivo:
        nombre = "VERSIONED_OK"
    elif version_actual is not None:
        nombre = (
            "VERSIONED_BEHIND"
            if version_actual in _listar_revisiones()
            else "VERSIONED_AHEAD"
        )
    else:
        nombre = "DRIFTED"

    return EstadoBase(
        nombre=nombre,
        version_actual=version_actual,
        head_objetivo=head_objetivo,
        tablas_app=tablas_app,
    )


def _ejecutar_upgrade() -> None:
    """Ejecuta ``alembic upgrade head`` heredando stdout/stderr."""
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=REPO_ROOT,
        check=True,
    )


async def _ejecutar_reset() -> None:
    """Resetea el schema ``public``. Bloqueado en producción."""
    settings = get_settings()
    if settings.APP_ENV == "prod":
        raise RuntimeError(
            "Reset de schema bloqueado: APP_ENV=prod no admite acciones destructivas.",
        )
    url = _to_asyncpg_url(settings.DATABASE_URL_DIRECT)
    engine = create_async_engine(
        url,
        connect_args={
            "ssl": "require",
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        },
        isolation_level="AUTOCOMMIT",
    )
    try:
        async with engine.connect() as conn:
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
    finally:
        await engine.dispose()


def _resultado(
    estado: EstadoBase,
    accion: str,
    permite: bool,
    mensaje: str,
    pasos: list[str],
    exit_code: int,
) -> dict[str, Any]:
    """Empaqueta el resultado para serializar a JSON."""
    return {
        "estado": estado.nombre,
        "version_actual": estado.version_actual,
        "head_objetivo": estado.head_objetivo,
        "tablas_app": estado.tablas_app,
        "accion_ejecutada": accion,
        "permite_implement": permite,
        "mensaje": mensaje,
        "siguientes_pasos": pasos,
        "exit_code": exit_code,
    }


async def _ejecutar(allow_reset: bool) -> dict[str, Any]:
    """Aplica la matriz de decisión sobre el estado detectado."""
    heads = _obtener_heads()
    if len(heads) != 1:
        estado_vacio = EstadoBase("MULTI_HEADS", None, None, 0)
        return _resultado(
            estado_vacio,
            "abort",
            False,
            f"Se detectaron {len(heads)} heads en Alembic. Historial inconsistente.",
            [
                "Ejecuta 'alembic heads' y resuelve con 'alembic merge'.",
                "Vuelve a correr el preflight cuando exista un único head.",
            ],
            20,
        )

    head = heads[0]
    estado = await _detectar(head)

    if estado.nombre == "EMPTY":
        _ejecutar_upgrade()
        return _resultado(
            estado,
            "upgrade_head",
            True,
            "Base vacía detectada. Se aplicó 'alembic upgrade head'.",
            [],
            10,
        )

    if estado.nombre == "VERSIONED_OK":
        return _resultado(
            estado,
            "noop",
            True,
            "Base alineada con head. Listo para implement.",
            [],
            0,
        )

    if estado.nombre == "VERSIONED_BEHIND":
        _ejecutar_upgrade()
        return _resultado(
            estado,
            "upgrade_head",
            True,
            "Base detrás de head. Migraciones pendientes aplicadas.",
            [],
            10,
        )

    if estado.nombre == "VERSIONED_AHEAD":
        return _resultado(
            estado,
            "abort",
            False,
            (
                f"La base reporta la revisión '{estado.version_actual}' que no "
                "existe en el historial local."
            ),
            [
                "Sincroniza el repositorio con la rama que generó esa revisión.",
                "O re-ejecuta con --allow-reset si la base es desechable.",
            ],
            20,
        )

    if estado.nombre == "DRIFTED":
        if not allow_reset:
            return _resultado(
                estado,
                "abort",
                False,
                (
                    "Hay tablas en 'public' sin tabla 'alembic_version'. "
                    "Estado inconsistente."
                ),
                [
                    "Re-ejecuta con --allow-reset si la base es desechable.",
                    "Nunca uses 'alembic stamp' para enmascarar el drift.",
                ],
                20,
            )
        await _ejecutar_reset()
        _ejecutar_upgrade()
        return _resultado(
            estado,
            "reset_public",
            True,
            "Schema 'public' reseteado y 'alembic upgrade head' aplicado.",
            [],
            10,
        )

    return _resultado(
        estado,
        "abort",
        False,
        f"Estado no clasificado: {estado.nombre}.",
        ["Reporta este caso para extender la matriz de decisión."],
        20,
    )


def main() -> int:
    """Punto de entrada CLI del preflight."""
    parser = argparse.ArgumentParser(
        description="Preflight de base de datos para el flujo Speckit.",
    )
    parser.add_argument(
        "--allow-reset",
        action="store_true",
        help="Autoriza DROP/CREATE SCHEMA public en escenario DRIFTED.",
    )
    args = parser.parse_args()

    try:
        resultado = asyncio.run(_ejecutar(allow_reset=args.allow_reset))
    except subprocess.CalledProcessError as exc:
        resultado = {
            "estado": "ALEMBIC_FAIL",
            "version_actual": None,
            "head_objetivo": None,
            "tablas_app": 0,
            "accion_ejecutada": "abort",
            "permite_implement": False,
            "mensaje": f"Falló un comando de Alembic: {exc}",
            "siguientes_pasos": [
                "Revisa la salida de Alembic impresa arriba.",
                "Corrige la migración o el historial antes de reintentar.",
            ],
            "exit_code": 20,
        }
    except Exception as exc:  # noqa: BLE001 - reportar cualquier fallo de conexión
        resultado = {
            "estado": "CONN_FAIL",
            "version_actual": None,
            "head_objetivo": None,
            "tablas_app": 0,
            "accion_ejecutada": "abort",
            "permite_implement": False,
            "mensaje": f"Fallo de conexión o configuración: {exc}",
            "siguientes_pasos": [
                "Verifica DATABASE_URL_DIRECT y conectividad con Supabase.",
                "Confirma que el archivo .env esté presente y sea legible.",
            ],
            "exit_code": 20,
        }

    exit_code = int(resultado.pop("exit_code"))
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
