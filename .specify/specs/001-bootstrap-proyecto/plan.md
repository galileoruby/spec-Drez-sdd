# Plan de Implementación: 001-bootstrap-proyecto

**Branch**: `001-bootstrap-proyecto` | **Date**: 2026-07-08 | **Spec**: `.specify/specs/001-bootstrap-proyecto/spec.md`

**Input**: Especificación de funcionalidad desde `.specify/specs/001-bootstrap-proyecto/spec.md`

## Resumen

Se construirá el bootstrap técnico y visual del sistema Realtor como base obligatoria para las specs siguientes. El alcance incluye: inicialización FastAPI async-first, configuración con Pydantic Settings, conexión PostgreSQL/Supabase con SQLAlchemy async, baseline Alembic con `pgcrypto`, endpoints `GET /health` y `GET /`, sistema visual base con componentes reutilizables e iconos Lucide vendoreados, y configuración de calidad estática (Ruff, MyPy, pytest-asyncio).

## Contexto Técnico

**Lenguaje/Versión**: Python 3.13+

**Dependencias primarias**: FastAPI, SQLAlchemy 2.x async, asyncpg, Alembic, Pydantic v2, pydantic-settings, Jinja2, python-multipart

**Almacenamiento**: PostgreSQL (Supabase). Runtime en `DATABASE_URL` (pooler 6543) y migraciones en `DATABASE_URL_DIRECT` (directo 5432)

**Testing**: pytest, pytest-asyncio, httpx.AsyncClient

**Plataforma objetivo**: Servicio web backend-rendered (Linux/Windows/macOS en desarrollo; despliegue cloud)

**Tipo de proyecto**: Monolito modular FastAPI + Jinja2 + HTMX

**Objetivos de rendimiento**: Endpoint de salud con respuesta inmediata para monitoreo operativo; dashboard inicial server-rendered sin optimizaciones avanzadas en esta fase

**Restricciones**:
- Cumplir constitution v1.0.0 (Spec-Driven, Vertical Slice, async-first, idioma español)
- Sin frameworks CSS externos
- Sin CDN para HTMX
- Sin implementar dominios de negocio fuera del bootstrap

**Escala/Alcance**: Feature fundacional única, sin módulos de dominio; habilita el desarrollo de spec 002+

## Constitution Check

*GATE: Debe pasar antes de Fase 0 y re-validarse tras Fase 1.*

### Revisión previa (pre-Fase 0)

- ✅ Principio I (Solución única): se mantiene un solo proyecto y una sola base de código.
- ✅ Principio II (Spec-Driven): todo el alcance proviene de `spec.md` y clarificaciones aprobadas.
- ✅ Principio III (Vertical Slice): se planifica estructura por módulo/feature y templates transversales.
- ✅ Principio IV (Stack obligatorio): se respeta FastAPI + Jinja2 + HTMX vendoreado + SQLAlchemy async + Alembic + uv.
- ✅ Principio V (Contratos y dominio): rutas delgadas, comportamiento explícito de `GET /health`, logging estructurado.
- ✅ Principio VI (Idioma): artefactos de planificación redactados en español.
- ✅ Principio VII (Async-first): DB y operaciones I/O definidas en async.

### Revisión posterior (post-Fase 1)

- ✅ Sin nuevas violaciones detectadas tras definir contratos, modelo y guía de validación.
- ✅ Las decisiones de diseño siguen las clarificaciones registradas en la spec.

## Estructura del Proyecto

### Documentación (esta feature)

```text
.specify/specs/001-bootstrap-proyecto/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── http-endpoints.md
└── tasks.md                 # Se generará en /speckit.tasks
```

### Código fuente (raíz de repositorio)

```text
app/
├── __init__.py
├── main.py
├── config.py
├── database.py
├── modules/
│   └── __init__.py
├── static/
│   ├── css/
│   │   └── app.css
│   ├── vendor/
│   │   └── htmx.min.js
│   └── icons/
│       ├── layout-dashboard.svg
│       ├── building-2.svg
│       ├── users.svg
│       ├── file-text.svg
│       ├── wallet.svg
│       ├── wrench.svg
│       ├── settings.svg
│       ├── menu.svg
│       ├── x.svg
│       ├── check-circle-2.svg
│       ├── alert-triangle.svg
│       ├── alert-circle.svg
│       └── info.svg
└── templates/
    ├── base.html
    ├── components/
    │   ├── _sidebar.html
    │   ├── _navbar.html
    │   ├── _card_propiedad.html
    │   ├── _tarjeta_metrica.html
    │   ├── _accesos_rapidos.html
    │   ├── _badge_estado.html
    │   ├── _form_field.html
    │   └── _alerta.html
    └── macros/
        └── icons.html

alembic/
├── env.py
└── versions/
    └── 20260708_baseline.py

tests/
└── test_smoke.py
```

**Decisión de estructura**: proyecto web monolítico (FastAPI + Jinja2 + HTMX) con organización vertical-slice para módulos futuros y componentes transversales en `app/templates`.

## Plan por Fases

## Contrato obligatorio de implementación: GET /health

La implementación del endpoint GET /health DEBE cumplir exactamente este contrato:

- Éxito (HTTP 200):

```json
{"status": "ok", "db": "ok"}
```

- Error de DB (HTTP 200):

```json
{"status": "degraded", "db": "error"}
```

Este contrato es obligatorio y prevalece como definición de implementación para la fase de desarrollo y pruebas.

### Fase 0: Investigación y decisiones

Resultados documentados en `research.md`:
- Contrato explícito para `GET /health` (HTTP 200 en éxito y HTTP 503 en error de DB)
- Breakpoint responsive oficial (`<1024px`)
- Valores hardcoded de métricas demo
- Estrategia de vendorización SVG oficial Lucide
- Baseline Alembic con `pgcrypto`
- Política de logging estructurado INFO

### Fase 1: Diseño y contratos

Artefactos generados:
- `data-model.md` con entidades conceptuales de bootstrap
- `contracts/http-endpoints.md` con contrato HTTP de `GET /health` y `GET /`
- `quickstart.md` con validación operativa de punta a punta

### Actualización de contexto de agente

No existe script de actualización de contexto de agente en `.specify/scripts/powershell/` para este repositorio. Se adopta actualización manual mediante los artefactos de Fase 0 y Fase 1 como fuente de verdad para `/speckit.tasks`.

## Complexity Tracking

Sin violaciones de constitución que requieran excepción en esta fase.

## Cierre de consistencia (Fase 6)

- Se revisó coherencia entre `spec.md`, `plan.md` y `tasks.md`.
- Se consolidó el contrato final de `GET /health` con respuesta degradada en `HTTP 200`.
- La evidencia de validación técnica transversal quedó documentada en `quickstart.md`.
