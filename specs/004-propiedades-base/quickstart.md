# Guía Rápida: Validación técnica — 004-propiedades-base

**Guía de validación end-to-end para implementación y revisión**
**Fecha**: 2026-07-09

---

## Prerrequisitos

1. Python 3.13+ y `uv` instalados.
2. Variables de entorno configuradas:
   - `DATABASE_URL` apuntando al pooler 6543 para runtime.
   - `DATABASE_URL_DIRECT` apuntando a conexión directa 5432 para Alembic.
3. SSL habilitado.
4. Branch activa: `004-propiedades-base`.

---

## Preparación inicial

```powershell
uv sync
git branch --show-current
Test-Path alembic/script.py.mako
```

**Esperado**:
- dependencias instaladas,
- branch `004-propiedades-base`,
- `alembic/script.py.mako` presente antes de generar nuevas revisiones.

---

## Escenarios de validación

### SC-P1 — Estructura del dominio creada correctamente

```powershell
uv run alembic upgrade head
```

**Esperado**:
- upgrade completo en verde,
- tabla `propiedades` creada,
- enum `estado_propiedad` materializado sin conflicto.

### SC-P2 — Seed idempotente de 10 propiedades

1. Ejecutar dos veces consecutivas el upgrade completo sobre una base limpia o recreada.
2. Consultar cardinalidad resultante de `propiedades`.

**Esperado**:
- exactamente 10 propiedades,
- ciudad `Miami` en todas,
- sin duplicados por clave compuesta.

### SC-P3 — Catálogo cerrado e imagen determinista

Validar mediante pruebas y/o consulta de datos sembrados:

- todos los estados pertenecen a `disponible`, `rentada`, `mantenimiento`, `inactiva`;
- todas las imágenes cumplen `https://picsum.photos/seed/{id}/800/500`.

### SC-P4 — Reversibilidad real de Alembic

```powershell
uv run alembic downgrade -2
uv run alembic upgrade head
```

**Esperado**:
- downgrade completo sin `pass`,
- upgrade posterior exitoso,
- sin residuos del enum ni de los datos seed fuera del flujo esperado.

### SC-P5 — Calidad del módulo

```powershell
uv run ruff check .
uv run mypy --strict app/modules/propiedades
uv run pytest app/modules/propiedades/tests -q
```

**Esperado**:
- Ruff sin hallazgos,
- mypy sin errores,
- pytest del módulo en verde.

### SC-P6 — Validación de timezone

Ejecutar el ciclo completo de migraciones y pruebas de migración.

**Esperado**:
- no aparece ningún error de mezcla entre fechas naive y aware,
- `created_at` y `updated_at` permanecen server-side.

---

## Recuperación ante historial inconsistente

Si Alembic reporta revisiones ausentes o el historial físico/lógico quedó desalineado:

1. Validar que el entorno sea desechable para reset de `public`.
2. Ejecutar reset explícito del esquema.
3. Reaplicar `alembic upgrade head`.
4. Verificar cardinalidad y calidad del módulo.

```powershell
uv run python -c "import asyncio; from sqlalchemy import text; from sqlalchemy.ext.asyncio import create_async_engine; from app.database import _build_async_database_url; from app.config import get_settings; async def main():\n s=get_settings();\n e=create_async_engine(_build_async_database_url(s.DATABASE_URL_DIRECT), connect_args={'ssl':'require'});\n async with e.begin() as conn:\n  await conn.execute(text('DROP SCHEMA public CASCADE;'))\n  await conn.execute(text('CREATE SCHEMA public;'))\n await e.dispose();\n asyncio.run(main())"
uv run alembic upgrade head
```

**Regla obligatoria**: nunca usar `alembic stamp` como atajo de recuperación.

---

## Evidencia de ejecución (2026-07-10)

```powershell
uv run ruff check .
# All checks passed!

uv run mypy --strict app/modules/propiedades
# Success: no issues found in 9 source files

uv run pytest app/modules/propiedades/tests -q
# 12 passed in 1.52s

uv run alembic upgrade head
# Running upgrade 20260708_baseline -> 0002_create_propiedades
# Running upgrade 0002_create_propiedades -> 0003_seed_propiedades_miami

uv run alembic downgrade -2
# Running downgrade 0003_seed_propiedades_miami -> 0002_create_propiedades
# Running downgrade 0002_create_propiedades -> 20260708_baseline

uv run alembic upgrade head
# Running upgrade 20260708_baseline -> 0002_create_propiedades
# Running upgrade 0002_create_propiedades -> 0003_seed_propiedades_miami

# Doble ejecución de upsert del seed y validación:
# {"total_miami": 10, "duplicados_identidad": 0}
```

Resultado: upgrade/downgrade/upgrade en verde, seed idempotente confirmado con 10 registros de Miami y 0 duplicados por identidad compuesta.

---

## Checklist de cierre

| Ítem | Estado |
|------|--------|
| `alembic/script.py.mako` versionado antes de crear revisiones | [x] |
| `0002_create_propiedades.py` crea tabla, enum, índices y downgrade real | [x] |
| `0003_seed_propiedades_miami.py` siembra 10 registros y usa upsert idempotente | [x] |
| `created_at` no se envía desde Python | [x] |
| `updated_at = now()` solo aparece en la rama de actualización | [x] |
| Seed usa `op.get_bind().execute(sa.text(...), params)` | [x] |
| Casts UUID usan `CAST()` y no `::uuid` | [x] |
| Ruff, mypy y pytest del módulo pasan | [x] |
| `alembic upgrade head` pasa en base limpia | [x] |
| `alembic downgrade -2` + `upgrade head` es reversible | [x] |

---

## Referencias cruzadas

| Artefacto | Ruta |
|-----------|------|
| Spec | [spec.md](spec.md) |
| Plan | [plan.md](plan.md) |
| Research | [research.md](research.md) |
| Data Model | [data-model.md](data-model.md) |