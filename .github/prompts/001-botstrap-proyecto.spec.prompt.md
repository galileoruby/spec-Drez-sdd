---
name: 001-bootstrap-proyecto
---

/speckit.specify

Crea la spec 001-bootstrap-proyecto.

## OBJETIVO

Dejar el esqueleto técnico y visual del sistema Realtor en pie, listo
para recibir el primer módulo de dominio en la spec 002. Es la spec
fundacional: sin ella las siguientes no se sostienen.

## ALCANCE INCLUIDO

### Estructura del proyecto
- app/__init__.py, app/main.py, app/config.py, app/database.py
- app/modules/ vacío (preparado para feature modules futuros)
- app/static/css/app.css, app/static/vendor/, app/static/icons/
- app/templates/base.html, app/templates/components/,
  app/templates/macros/icons.html
- alembic/ inicializado en modo async

### Configuración
- app/config.py con pydantic-settings lee .env y expone:
  DATABASE_URL, DATABASE_URL_DIRECT, APP_ENV, LOG_LEVEL
- app/database.py con engine async configurado para Supabase
  transaction pooler: statement_cache_size=0,
  prepared_statement_cache_size=0, ssl=require
- Dependencia get_session que provee AsyncSession por request

### Base de datos
- Alembic env.py async, lee DATABASE_URL_DIRECT (puerto 5432)
- Migración baseline aplicada contra Supabase sin errores

### Endpoints
- GET /health: retorna JSON con estado app y DB, hace SELECT 1 async
- GET /: renderiza dashboard demo con sidebar + navbar + 3 tarjetas
  de métrica con datos hardcoded

### Sistema visual (según .github/instructions/frontend.instructions.md)
- app/static/css/app.css con tokens de diseño en :root y 7 secciones
  comentadas (reset, variables, tipografía, layout, componentes,
  utilidades, responsive)
- app/static/vendor/htmx.min.js vendoreado, sin CDN
- app/static/icons/ con 13 SVG outline de Lucide:
  layout-dashboard, building-2, users, file-text, wallet, wrench,
  settings, menu, x, check-circle-2, alert-triangle, alert-circle, info
- app/templates/base.html con layout sidebar fija + main + zona flash
- app/templates/macros/icons.html con macro icon(nombre, size, class)
- app/templates/components/ con 8 componentes estructurales:
  _sidebar.html, _navbar.html, _card_propiedad.html,
  _tarjeta_metrica.html, _accesos_rapidos.html, _badge_estado.html,
  _form_field.html, _alerta.html

### Calidad estática
- ruff configurado en pyproject.toml: target py313, line-length 88,
  reglas E, F, I, B, UP, ASYNC
- mypy --strict configurado para app/modules/ en pyproject.toml
- pytest-asyncio con asyncio_mode = "auto" en pyproject.toml

## CRITERIOS DE ACEPTACIÓN

1. uv sync instala todas las dependencias sin errores
2. uv run uvicorn app.main:app --reload arranca el servidor
3. GET /health responde 200 OK con {"status":"ok","db":"ok"}
4. GET / renderiza dashboard demo con sidebar visible y 3 tarjetas
5. Layout responsive: sidebar colapsable por debajo de 1024px
6. Todos los iconos son SVG inline desde app/static/icons/
7. alembic upgrade head aplica baseline contra Supabase sin errores
8. uv run ruff check . y uv run ruff format --check . pasan limpios
9. uv run mypy --strict app/modules/ pasa limpio
10. Ningún archivo .md del repo contiene texto en inglés

## ALCANCE NO INCLUIDO

- Módulos de dominio (propiedades, inquilinos, contratos, pagos)
- Autenticación de usuarios (decisión explícita: no se usa)
- Manejo de archivos/storage
- Tests de dominio (solo smoke test de /health y /)

## DEPENDENCIAS DE PRODUCCIÓN (rangos versionados con ~=)

- fastapi[standard]~=0.136.0
- sqlalchemy[asyncio]~=2.0.36
- asyncpg~=0.30.0
- alembic~=1.14.0
- pydantic~=2.10.0
- pydantic-settings~=2.7.0
- jinja2~=3.1.4
- python-multipart~=0.0.20

## DEPENDENCIAS DE DESARROLLO

- pytest~=8.3.0
- pytest-asyncio~=0.25.0
- httpx~=0.28.0
- ruff~=0.8.0
- mypy~=1.13.0

Stack inmutable según constitution v1.0.2.
Python target: 3.13.
Idioma: 100% español (spec, plan, tasks, comentarios, docstrings).