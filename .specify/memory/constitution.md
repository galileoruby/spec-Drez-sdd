<!--
Sync Impact Report
- Version change: 1.1.0 -> 1.2.0
- Principios modificados:
  - II. Spec-Driven Development (NO NEGOCIABLE)
- Secciones agregadas:
  - Principios Fundamentales: VIII. Gobernanza de Tokens Visuales
- Secciones eliminadas:
	- Ninguna
- Templates que requieren actualización:
  - ✅ .specify/templates/spec-template.md
  - ✅ .specify/templates/plan-template.md (sin cambio requerido tras validación)
  - ✅ .specify/templates/tasks-template.md (sin cambio requerido tras validación)
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

Para cambios de diseño visual, especialmente tokens visuales (color,
espaciado, tipografía, radios, sombras y derivados), la spec DEBE incluir
autorización explícita del cambio y trazabilidad completa en `tasks.md`.
Sin autorización explícita y tareas trazables, el cambio DEBE rechazarse.

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

### VIII. Gobernanza de Tokens Visuales
Los tokens visuales del sistema (variables CSS de color, espaciado, tipografía,
radios, sombras y equivalentes) son activos gobernados. Cualquier cambio en
tokens visuales DEBE tener autorización explícita en una spec aprobada y DEBE
quedar trazado a tareas verificables en `tasks.md` antes de su implementación.
No se permite modificar tokens por conveniencia local, ajuste ad hoc o criterio
estético aislado sin ese rastro formal.

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

El flujo obligatorio mínimo es: speckit.specify → speckit.plan →
speckit.tasks → speckit.implement. Para specs fundacionales o de alto
impacto se recomienda añadir speckit.clarify (entre specify y plan) y
speckit.analyze (entre plan y tasks). Ninguna fase obligatoria puede
saltarse.

Cada tarea completada DEBE marcarse como `[X]` en `tasks.md`.

### Modo Interactivo de Preguntas

Los comandos `speckit.specify` y `speckit.clarify` operan en **modo
interactivo obligatorio**: presentan sus preguntas de una en una y esperan
respuesta antes de continuar. El comando `speckit.plan` opera en **modo
interactivo condicional**: solo lanza preguntas si existen decisiones
estructurales que afecten todas las specs futuras y que no estén resueltas
en la constitution ni en la spec vigente.

Cuando un comando opera en modo interactivo, DEBE seguir este protocolo
sin excepción:

**Formato de pregunta con opciones:**

```
Pregunta [N de TOTAL] — [tema corto]
─────────────────────────────────────
[Enunciado claro de la pregunta]

Por qué importa: [1 línea sobre el impacto de decidir mal]

A) [opción concreta con valor específico]
B) [opción concreta con valor específico]  ← Recomendado
C) [opción concreta con valor específico]
D) Otro — escribe tu respuesta

> Responde con la letra (A, B, C o D) o escribe tu respuesta libre.
```

**Formato de pregunta Sí/No:**

```
Pregunta [N de TOTAL] — [tema corto]
─────────────────────────────────────
[Enunciado de la pregunta]

Por qué importa: [1 línea]

S) Sí  ← Recomendado
N) No

> Responde S o N.
```

**Reglas de las opciones:**

- Cada opción (A, B, C) DEBE ser concreta y ejecutable, nunca genérica.
  Ejemplo correcto: `1024px (tablet landscape)`.
  Ejemplo prohibido: `Un breakpoint estándar`.
- Las opciones DEBEN ser mutuamente excluyentes: cada una lleva a un
  resultado de código distinto.
- La opción marcada con `← Recomendado` DEBE ser la más adoptada por
  equipos que usan este stack (FastAPI + SQLAlchemy async + Supabase +
  Python 3.13) o la que mejor respeta los principios de esta constitution.
- La opción `D) Otro` SIEMPRE debe estar presente como escape hatch para
  respuesta personalizada.

**Reglas de respuesta:**

- Si el usuario responde con una letra (A, B, C, S o N): confirmar la
  elección en una línea con el valor concreto elegido y pasar
  inmediatamente a la siguiente pregunta.
- Si el usuario responde con texto libre o elige D): aceptar la respuesta,
  confirmarla en una línea y pasar a la siguiente pregunta.
- Al terminar todas las preguntas: mostrar un resumen de las decisiones
  tomadas y generar el artefacto correspondiente (`spec.md`, sección
  "Clarificaciones" en `spec.md`, o `plan.md`).

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

Toda PR o revisión DEBE verificar el cumplimiento de los **ocho principios
(I al VIII)** antes de aprobarse. Cualquier violación DEBE justificarse
explícitamente en la sección **Complexity Tracking** del `plan.md` de la
iniciativa correspondiente; en ausencia de justificación, la PR DEBE
rechazarse.

---
## Sistema Visual Canonico
Para todo trabajo frontend, la definición canónica de tokens visuales vive en .github/instructions/frontend.instructions.md.
La implementación en app.css DEBE respetar exactamente esa paleta y tokens.
No se aceptan cambios implícitos de color por criterio estético durante implementación.
Toda variación de tokens requiere spec aprobada, actualización de instrucciones y trazabilidad en tasks.md.
El incumplimiento de esta regla invalida la implementación de la spec en revisión.

---


## Historial de versiones
- **v1.0.0** — Versión inicial de la constitution.
- **v1.1.0** — Agregado protocolo de Modo Interactivo de Preguntas en
  Método de Trabajo. Define formato, reglas de opciones y reglas de
  respuesta para speckit.specify, speckit.clarify y speckit.plan.
- **v1.2.0** — Se agrega gobernanza global de tokens visuales: autorización
  explícita en spec aprobada y trazabilidad obligatoria en `tasks.md`.

