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

## 2) Aplicar migración baseline

```bash
uv run alembic upgrade head
```

Resultado esperado:
- Migración aplicada correctamente.
- Baseline con `pgcrypto` habilitado.

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
uv run mypy --strict app/modules/
```

Resultado esperado:
- Checks sin errores críticos.

## 7) Validar smoke tests

```bash
uv run pytest -q
```

Resultado esperado:
- Smoke tests de `/health` y `/` en verde.
