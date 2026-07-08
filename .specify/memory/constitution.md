<!--
Sync Impact Report
- Version change: plantilla-inicial-sin-version -> 1.0.0
- Principios modificados:
	- Placeholder principio 1 -> I. Desarrollo guiado por especificaciones (Spec-Driven)
	- Placeholder principio 2 -> II. Arquitectura Vertical Slice obligatoria
	- Placeholder principio 3 -> III. Stack Python y dependencias gestionadas con uv
	- Placeholder principio 4 -> IV. Calidad verificable por slice
	- Placeholder principio 5 -> V. Persistencia asíncrona y consistencia de datos
- Secciones agregadas:
	- Ninguna (se consolidan las secciones existentes de la plantilla)
- Secciones eliminadas:
	- Ninguna
- Plantillas y artefactos revisados:
	- ✅ .specify/templates/plan-template.md (alineada; no requiere cambios)
	- ✅ .specify/templates/spec-template.md (alineada; no requiere cambios)
	- ✅ .specify/templates/tasks-template.md (alineada; no requiere cambios)
	- ✅ .specify/templates/commands/*.md (no existe en este repositorio)
	- ✅ README.md (sin contenido; sin referencias contradictorias)
- TODOs de seguimiento:
	- Ninguno
-->

# Realtor Constitution

## Principios Fundamentales

### I. Solución Única y Compartida
El sistema es un **único proyecto Python** que vive en un único repositorio. El
frontend (Jinja2 server-rendered + HTMX) y el backend (FastAPI) son partes del
**mismo monolito modular**, NO aplicaciones separadas. Toda iniciativa en
`.specify/` DEBE contribuir a este sistema único. Está PROHIBIDO crear servicios
paralelos, repositorios separados para frontend/backend o estructuras
divergentes por capa técnica. La solución se compila, prueba y despliega como
una sola unidad.

### II. Spec-Driven Development (NO NEGOCIABLE)
`.specify/` es la **única fuente de verdad** del proyecto. NO se DEBE
implementar ninguna funcionalidad que no esté descrita en el `spec.md` vigente.
El orden de implementación lo define el **prefijo numérico** de cada spec: el
número menor SIEMPRE se implementa antes que el mayor. Cualquier código,
template o migración que no rastree a una tarea en `tasks.md` de una spec
aprobada DEBE rechazarse en revisión.

### III. Vertical Slice Architecture (NO NEGOCIABLE)
El código de negocio DEBE organizarse por feature/módulo, NO por capa técnica.
Cada feature vive en `app/modules/<feature>/` y agrupa exactamente estos
artefactos:

- `routes.py` — endpoints FastAPI (delgados, sin lógica de negocio).
- `schemas.py` — DTOs Pydantic v2 (`frozen=True`).
- `models.py` — entidades SQLAlchemy 2.x (`Mapped[...]`, `mapped_column`).
- `repository.py` — acceso a datos async usando `AsyncSession` y `select()`.
- `service.py` — lógica de negocio del módulo.
- `templates/` — fragmentos Jinja2 + parciales HTMX del módulo.
- `tests/` — pruebas pytest del módulo (`test_*.py`).

Están **estrictamente prohibidas** las carpetas globales por capa técnica:
`controllers/`, `services/`, `repositories/`, `handlers/`, `managers/` o
similares fuera del módulo. La lógica compartida solo se extrae cuando existe
duplicación real demostrable, nunca por anticipación.

### IV. Stack Tecnológico Obligatorio (NO NEGOCIABLE)
El stack es inmutable y DEBE aplicarse sin excepción:

- **Lenguaje**: Python **3.13+**.
- **Gestor de paquetes y entorno**: **`uv`** con `pyproject.toml` y `uv.lock`.
  PROHIBIDO `pip`, `poetry`, `conda`, `pipenv`, `requirements.txt`, `setup.py`.
- **HTTP framework**: **FastAPI**.
- **Vista**: **Jinja2** server-rendered + **HTMX** vendoreado en
  `app/static/vendor/htmx.min.js`. PROHIBIDO cargar HTMX (o cualquier JS de
  terceros) desde CDN externo en runtime.
- **ORM**: **SQLAlchemy 2.x async**, estilo moderno con `Mapped[...]`,
  `mapped_column`, `select()`, `AsyncSession`. PROHIBIDO el estilo declarativo
  legacy (`Column(...)` en clase, `Query`, sesiones síncronas).
- **DTOs**: **Pydantic v2**, todos los schemas con
  `model_config = ConfigDict(frozen=True)`.
- **Migraciones**: **Alembic** (única herramienta de schema migration).
- **Base de datos**: **PostgreSQL** vía **asyncpg**.
- **Tests**: **pytest** + **pytest-asyncio** + **httpx.AsyncClient** para tests
  HTTP end-to-end.
- **Calidad estática**: **Ruff** (lint + format) y **mypy `--strict`** aplicado
  como mínimo a `app/modules/`.
- **CSS**: 100 % propio en `app/static/css/app.css`. PROHIBIDOS Bootstrap,
  Tailwind, Bulma, Foundation o cualquier framework CSS.
- **Iconografía**: **SVG outline** vendoreados en `app/static/icons/`,
  uno por archivo. La librería estándar del proyecto es **Lucide**
  (https://lucide.dev), licencia ISC. PROHIBIDO usar iconos como webfont
  (Bootstrap Icons, Font Awesome, Material Icons font), emojis o caracteres
  Unicode como íconos funcionales. Cada nuevo icono incorporado al proyecto
  DEBE rastrearse a una tarea explícita en el `tasks.md` de una spec aprobada.

Cualquier dependencia adicional DEBE justificarse en el `plan.md` de la spec
que la introduce.

### V. Calidad de Dominio y Contratos
La lógica de negocio VIVE en `service.py` del módulo. Está PROHIBIDO ubicarla
en `routes.py`, en templates Jinja2, en `repository.py` o en `models.py`. Los
schemas Pydantic son **inmutables** (`frozen=True`); los estados del dominio se
modelan con `Enum` o tipos explícitos, NUNCA con strings mágicos. Cada endpoint
DEBE:

1. Validar la entrada explícitamente (tipos Pydantic + validaciones de negocio
   delegadas al servicio).
2. Retornar errores con `HTTPException` o un modelo de error tipado bien
   definido — nunca devolver `dict` libres en caso de error.
3. Emitir **logging estructurado** (módulo, operación, identificadores
   relevantes; NUNCA datos sensibles en claro).

Las entidades SQLAlchemy NO se exponen como respuesta HTTP: siempre se mapean a
schemas Pydantic en el servicio.

### VI. Idioma y Documentación
Todo el contenido `.md` del repositorio DEBE estar escrito en **español**. Esto
incluye `.specify/`, `.github/`, `README.md` y cualquier documentación técnica.
Los **docstrings** de Python también DEBEN estar en español. Está PROHIBIDO
mezclar idiomas dentro de un mismo documento o docstring.

### VII. Async-First
Todo I/O (base de datos, HTTP saliente, sistema de archivos, colas) DEBE ser
**asíncrono**. Está PROHIBIDO declarar `def` sync en `routes.py`, `service.py`
o `repository.py` cuando la función toque I/O. Solo se permite `def` síncrono
para **puro cómputo en memoria** (mapeos, cálculos, validaciones sin I/O). Las
sesiones de base de datos DEBEN ser `AsyncSession`; los clientes HTTP DEBEN ser
`httpx.AsyncClient` u otro cliente async equivalente.

---

## Estructura del Repositorio

La estructura del proyecto Python es OBLIGATORIA y DEBE respetarse:

```text
app/
  main.py                     # FastAPI app + montaje de routers + middlewares
  database.py                 # AsyncEngine + AsyncSession + dependencia DB
  modules/
    <feature>/                # Un módulo por feature (properties, tenants, rentals, dashboard, ...)
      routes.py
      schemas.py
      models.py
      repository.py
      service.py
      templates/
        *.html                # Vistas y parciales HTMX del módulo
      tests/
        test_*.py
  static/
    css/
      app.css                 # CSS 100% propio del proyecto
    vendor/
      htmx.min.js             # HTMX vendoreado, sin CDN externo
    icons/
      *.svg                   # Iconos Lucide outline, uno por archivo
  templates/
    base.html                 # Layout base compartido
    components/
      _*.html                 # Componentes reutilizables transversales
    macros/
      *.html                  # Macros Jinja2 (icon(), etc.)
    *.html                    # Otros layouts/parciales transversales
alembic/
  env.py
  versions/                   # Migraciones generadas
pyproject.toml                # Gestionado por uv
uv.lock
```

`.specify/specs/` se mantiene como **lista secuencial plana** de iniciativas.
Cada spec vive en `.specify/specs/<numero>-<nombre>/` y contiene `spec.md`,
`plan.md` y `tasks.md`. NO se separan specs en subcarpetas por capa.

---

## Método de Trabajo

Cada iniciativa DEBE contener exactamente tres archivos:

- `spec.md` — objetivo, alcance, criterios de aceptación y dependencias.
- `plan.md` — decisiones técnicas, módulos afectados y orden de implementación.
- `tasks.md` — pasos secuenciales, accionables y verificables, marcables como
  completados.

El flujo obligatorio es: `speckit.specify` → `speckit.plan` → `speckit.tasks`
→ `speckit.implement`. Ninguna fase puede saltarse. Cada tarea completada DEBE
marcarse como `[X]` en `tasks.md`.

---

## Gobierno

Esta constitución es el documento rector del proyecto y tiene precedencia sobre
cualquier otra práctica, convención o preferencia personal. Las enmiendas DEBEN
documentarse con nueva versión semántica:

- **MAJOR**: eliminación o redefinición incompatible de un principio o del
  stack obligatorio.
- **MINOR**: nuevo principio o sección añadida; expansión material de un
  principio existente.
- **PATCH**: aclaraciones, redacción o correcciones no semánticas.

Toda PR o revisión DEBE verificar el cumplimiento de los **siete principios
(I al VII)** antes de aprobarse. Cualquier violación DEBE justificarse
explícitamente en la sección **Complexity Tracking** del `plan.md` de la
iniciativa correspondiente; en ausencia de justificación, la PR DEBE
rechazarse.

---

## Historial de versiones
- **v1.0.0** — Versión inicial de la constitution.