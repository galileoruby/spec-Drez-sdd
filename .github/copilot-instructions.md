# Instrucciones para GitHub Copilot — Proyecto Realtor

Este archivo resume las reglas obligatorias del proyecto. La fuente de verdad
completa es `.specify/memory/constitution.md`. Ante cualquier conflicto, la
constitution prevalece.

## Idioma

Todo el contenido `.md`, los comentarios y los docstrings DEBEN estar en
español. NUNCA mezclar idiomas dentro de un mismo archivo.

## Stack obligatorio (inmutable)

- Python 3.13+, gestionado con `uv` (`pyproject.toml` + `uv.lock`).
- FastAPI para HTTP, Jinja2 server-rendered + HTMX para vistas.
- SQLAlchemy 2.x async (estilo `Mapped[...]` + `mapped_column` + `select()` +
  `AsyncSession`). PROHIBIDO el estilo legacy (`Column(...)` en clase,
  `Query`, sesiones síncronas).
- Pydantic v2 con `model_config = ConfigDict(frozen=True)` en todos los DTOs.
- PostgreSQL vía asyncpg (proveedor: Supabase Postgres en cloud).
- Alembic única herramienta de migraciones.
- pytest + pytest-asyncio + httpx.AsyncClient para tests.
- Ruff + mypy `--strict` mínimo en `app/modules/`.
- Iconografía: SVG outline de Lucide vendoreados en `app/static/icons/`.

## Prohibiciones absolutas

- `pip`, `poetry`, `conda`, `pipenv`, `requirements.txt`, `setup.py`.
- Bootstrap, Tailwind, Bulma, Foundation o cualquier framework CSS.
- Cargar HTMX o cualquier JS de terceros desde CDN en runtime. HTMX vive
  en `app/static/vendor/htmx.min.js`.
- Iconos como webfont (Bootstrap Icons, Font Awesome, Material Icons font),
  emojis o caracteres Unicode como íconos funcionales.
- Funciones `def` síncronas en `routes.py`, `service.py` o `repository.py`
  cuando hagan I/O. Solo `def` sync para puro cómputo en memoria.
- Carpetas globales por capa técnica: `controllers/`, `services/`,
  `repositories/`, `handlers/`, `managers/` fuera de un módulo.
- Exponer entidades SQLAlchemy como respuesta HTTP. Siempre mapear a
  Pydantic.
- Retornar `dict` libres en errores. Usar `HTTPException` o modelo de error
  tipado.
- Strings mágicos para estados de dominio. Usar `Enum` o tipos explícitos.

## Arquitectura: Vertical Slice

Cada feature vive en `app/modules/<feature>/` con exactamente estos archivos:
`routes.py`, `schemas.py`, `models.py`, `repository.py`, `service.py`,
`templates/`, `tests/`.

La lógica de negocio vive SIEMPRE en `service.py`. `routes.py` es delgado:
parsea entrada, llama al servicio, retorna respuesta. `repository.py` solo
hace acceso a datos.

## Spec-Driven Development

NO implementar nada que no esté descrito en un `spec.md` aprobado bajo
`specs/` (carpeta en la **raíz** del repositorio). El orden de implementación
lo define el prefijo numérico de cada spec. Toda tarea debe rastrear a
`tasks.md`. PROHIBIDO crear specs bajo `.specify/specs/`: esa carpeta se
reserva exclusivamente para infraestructura de spec-kit (`memory/`,
`scripts/`, `templates/`, `extensions.yml`, `feature.json`).

## Base de datos (Supabase Postgres)

- `DATABASE_URL` apunta al **transaction pooler** (puerto 6543) y se usa
  en runtime. El engine DEBE tener `statement_cache_size=0` y
  `prepared_statement_cache_size=0` en `connect_args`.
- `DATABASE_URL_DIRECT` apunta a la **conexión directa** (puerto 5432) y
  se usa SOLO para Alembic.
- SSL es obligatorio (`ssl=require` en `connect_args`).



## Flujo Speckit — hooks obligatorios

<!-- SPECKIT START -->
Plan activo de ejecución: specs/004-propiedades-base/plan.md
<!-- SPECKIT END -->

Antes de ejecutar cualquier comando `speckit.*`, el agente DEBE revisar
`.specify/extensions.yml` y ejecutar todos los hooks `before_<comando>`
con `optional: false`.

Caso crítico: `before_specify` requiere ejecutar `speckit.git.feature`
ANTES de crear el directorio de la spec o `spec.md`. Este hook crea el
branch de la feature y actualiza `.specify/feature.json`.

PROHIBIDO crear archivos bajo `specs/<nueva-spec>/` sin haber
ejecutado previamente el hook obligatorio correspondiente.