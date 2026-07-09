# Quickstart — Validación de 001-bootstrap-proyecto

## Prerrequisitos
- Python 3.13+
- `uv` instalado
- Variables en `.env`:
  - `DATABASE_URL` (pooler 6543)
  - `DATABASE_URL_DIRECT` (directo 5432)
  - `APP_ENV`
  - `LOG_LEVEL`

## 1) Instalar dependencias

```bash
uv sync
```

Resultado esperado:
- Instalación exitosa sin errores.

## 1.1) Confirmar URLs de Supabase

Verifica que en `.env` se cumpla:

- `DATABASE_URL` usa pooler en puerto `6543` (runtime)
- `DATABASE_URL_DIRECT` usa conexión directa en puerto `5432` (migraciones)

Resultado esperado:
- Configuración separada correcta entre runtime y Alembic.

## 2) Aplicar migración baseline

```bash
uv run alembic upgrade head
```

Resultado esperado:
- Migración aplicada correctamente.
- Baseline con `pgcrypto` habilitado.

Comando de verificación opcional:

```bash
uv run alembic current
```

Resultado esperado:
- Revisión actual en `20260708_baseline`.

## 3) Levantar servidor

```bash
uv run uvicorn app.main:app --reload
```

Resultado esperado:
- Servidor disponible localmente.

## 4) Validar endpoint de salud

```bash
curl -i http://127.0.0.1:8000/health
```

Resultado esperado:
- En condición normal:

```json
{"status":"ok","db":"ok"}
```

- En falla de DB (simulada o real):

```json
{"status":"degraded","db":"error"}
```

## 5) Validar dashboard demo

Abrir en navegador:
- `http://127.0.0.1:8000/`

Resultado esperado:
- Sidebar + navbar + 3 tarjetas de métrica.
- Sidebar colapsa cuando viewport `< 1024px`.

## 6) Validar calidad estática

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy app/modules/
```

Resultado esperado:
- Checks sin errores críticos.

## 7) Validar smoke tests

```bash
uv run pytest -q
```

Resultado esperado:
- Smoke tests de `/health` y `/` en verde.

## 8) Checklist de cierre de la fase

- `ruff check` sin errores.
- `ruff format --check` sin diffs pendientes.
- `mypy app/modules/` sin errores.
- `pytest -q` con smoke tests en verde.
- `alembic upgrade head` y `alembic current` correctos.

## 9) Evidencia de aceptación técnica (Fase 6)

Fecha de ejecución: 2026-07-09

Comandos ejecutados:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy app/modules/
python -m pytest -q
python -m alembic upgrade head
python -m alembic current
```

Resultados registrados:

- `ruff check`: `All checks passed!`
- `ruff format --check`: `8 files already formatted`
- `mypy app/modules/`: `Success: no issues found in 1 source file`
- `pytest -q`: `3 passed`
- `alembic upgrade head`: ejecución correcta con `PostgresqlImpl`
- `alembic current`: `20260708_baseline (head)`

Observaciones:

- Se mantiene advertencia no bloqueante de `pytest-asyncio` sobre `asyncio_default_fixture_loop_scope` no definido explícitamente.
