# Tasks: 001-bootstrap-proyecto

**Input**: Documentos de diseño desde `.specify/specs/001-bootstrap-proyecto/`

**Prerequisites**: `plan.md` (requerido), `spec.md` (requerido), `research.md`, `data-model.md`, `contracts/http-endpoints.md`, `quickstart.md`

**Tests**: Se incluyen tareas de test porque la spec solicita smoke test para `/health` y `/`.

**Organization**: Tareas agrupadas por historia de usuario para implementación y validación independiente.

## Fase 1: Setup (Inicialización de proyecto)

**Purpose**: Dejar estructura y configuración base listas para iniciar implementación.

- [ ] T001 Crear estructura inicial de app en `app/__init__.py`, `app/main.py`, `app/config.py`, `app/database.py` y `app/modules/__init__.py`
- [ ] T002 Crear estructura de plantillas base en `app/templates/base.html`, `app/templates/components/` y `app/templates/macros/icons.html`
- [ ] T003 [P] Crear estructura estática base en `app/static/css/app.css`, `app/static/vendor/` y `app/static/icons/`
- [ ] T004 Configurar dependencias y herramientas del proyecto en `pyproject.toml`

---

## Fase 2: Foundational (Prerequisitos bloqueantes)

**Purpose**: Implementar infraestructura mínima obligatoria antes de cualquier historia.

**⚠️ CRITICAL**: Ninguna historia de usuario inicia antes de completar esta fase.

- [ ] T005 Implementar settings con Pydantic Settings en `app/config.py` (DATABASE_URL, DATABASE_URL_DIRECT, APP_ENV, LOG_LEVEL)
- [ ] T006 Implementar engine async y `get_session` en `app/database.py` con `statement_cache_size=0`, `prepared_statement_cache_size=0` y `ssl=require`
- [ ] T007 Implementar bootstrap FastAPI y wiring de estáticos/templates en `app/main.py`
- [ ] T008 Configurar Alembic async con `DATABASE_URL_DIRECT` en `alembic/env.py`
- [ ] T009 Crear migración baseline con `pgcrypto` en `alembic/versions/20260708_baseline.py`

**Checkpoint**: Infraestructura técnica base lista para implementar historias.

---

## Fase 3: User Story 1 - Esqueleto técnico operativo (Prioridad: P1) 🎯 MVP

**Goal**: Exponer `/health` y `/` funcionales con contrato definido y smoke tests verdes.

**Independent Test**: Iniciar app, validar `GET /health` (ok y degradado) y `GET /` con dashboard demo.

### Tests para User Story 1

- [ ] T010 [US1] Escribir smoke tests iniciales para `GET /health` y `GET /` en `tests/test_smoke.py`

### Implementation para User Story 1

- [ ] T011 [US1] Implementar `GET /health` con chequeo async (`SELECT 1`) y respuesta degradada en `app/main.py`
- [ ] T012 [P] [US1] Crear plantilla de dashboard demo en `app/templates/pages/dashboard.html`
- [ ] T013 [US1] Implementar `GET /` con métricas hardcoded e integración de plantilla en `app/main.py`
- [ ] T014 [US1] Agregar logging estructurado INFO (inicio/fin, ruta, status, duración) para `/health` y `/` en `app/main.py`
- [ ] T015 [US1] Ajustar smoke tests al contrato final de endpoints en `tests/test_smoke.py`

**Checkpoint**: MVP funcional con endpoints base y verificación automática mínima.

---

## Fase 4: User Story 2 - Base visual reutilizable (Prioridad: P2)

**Goal**: Entregar layout y componentes reutilizables con sidebar responsive y set de iconos obligatorio.

**Independent Test**: Renderizar dashboard con sidebar/navbar/componentes y colapso de sidebar en viewport `< 1024px`.

### Implementation para User Story 2

- [ ] T016 [US2] Definir tokens y 7 secciones CSS en `app/static/css/app.css`
- [ ] T017 [P] [US2] Crear componente sidebar en `app/templates/components/_sidebar.html`
- [ ] T018 [P] [US2] Crear componente navbar en `app/templates/components/_navbar.html`
- [ ] T019 [P] [US2] Crear componente tarjeta métrica en `app/templates/components/_tarjeta_metrica.html`
- [ ] T020 [P] [US2] Crear componente card propiedad en `app/templates/components/_card_propiedad.html`
- [ ] T021 [P] [US2] Crear componente accesos rápidos en `app/templates/components/_accesos_rapidos.html`
- [ ] T022 [P] [US2] Crear componente badge estado en `app/templates/components/_badge_estado.html`
- [ ] T023 [P] [US2] Crear componente campo de formulario en `app/templates/components/_form_field.html`
- [ ] T024 [P] [US2] Crear componente alerta en `app/templates/components/_alerta.html`
- [ ] T025 [US2] Implementar macro `icon(nombre, size, class)` para SVG inline en `app/templates/macros/icons.html`
- [ ] T026 [US2] Vendorear HTMX local y referenciarlo sin CDN desde `app/static/vendor/htmx.min.js` y `app/templates/base.html`
- [ ] T027 [US2] Vendorear set de 13 SVG oficiales Lucide en `app/static/icons/`
- [ ] T028 [US2] Integrar layout base + componentes + zona flash en `app/templates/base.html` y `app/templates/pages/dashboard.html`
- [ ] T029 [US2] Implementar comportamiento responsive de sidebar `< 1024px` en `app/static/css/app.css`

**Checkpoint**: UI base reusable completa y consistente con el sistema visual definido.

---

## Fase 5: User Story 3 - Calidad y despliegue inicial (Prioridad: P3)

**Goal**: Garantizar lint, formato, tipado y migraciones listos para flujo de desarrollo.

**Independent Test**: Ejecutar ruff, mypy, pytest y alembic upgrade head sin errores críticos.

### Implementation para User Story 3

- [ ] T030 [US3] Configurar Ruff (`E,F,I,B,UP,ASYNC`, py313, line-length 88) en `pyproject.toml`
- [ ] T031 [US3] Configurar MyPy strict para `app/modules/` en `pyproject.toml`
- [ ] T032 [US3] Configurar pytest-asyncio con `asyncio_mode = "auto"` en `pyproject.toml`
- [ ] T033 [US3] Revisar configuración de Alembic para compatibilidad con Supabase en `alembic/env.py` y `alembic/versions/20260708_baseline.py`
- [ ] T034 [US3] Actualizar guía de validación operativa en `.specify/specs/001-bootstrap-proyecto/quickstart.md`

**Checkpoint**: Base técnica validable para iniciar specs de dominio.

---

## Fase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cerrar coherencia documental y validación final transversal.

- [ ] T035 [P] Verificar consistencia spec-plan-tasks y actualizar notas en `.specify/specs/001-bootstrap-proyecto/spec.md` y `.specify/specs/001-bootstrap-proyecto/plan.md`
- [ ] T036 Ejecutar checklist de aceptación técnica y dejar evidencia en `.specify/specs/001-bootstrap-proyecto/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Fase 1 (Setup)**: inicia de inmediato.
- **Fase 2 (Foundational)**: depende de Fase 1 y bloquea todas las historias.
- **Fases 3, 4, 5 (Historias)**: dependen de Fase 2.
- **Fase 6 (Polish)**: depende de completar historias objetivo.

### User Story Dependencies

- **US1 (P1)**: inicia tras Foundational, define MVP.
- **US2 (P2)**: inicia tras Foundational; se integra con US1 en templates/layout.
- **US3 (P3)**: inicia tras Foundational; endurece calidad y validaciones.

### Within Each User Story

- Tests primero cuando aplique (US1).
- Contrato/estructura antes que integración visual.
- Endpoint y logging antes de cierre de smoke tests.
- Criterios de aceptación de cada historia deben poder validarse de forma independiente.

### Parallel Opportunities

- **Setup**: T003 puede ir en paralelo con T002.
- **US1**: T012 puede ir en paralelo con T011.
- **US2**: T017–T024 pueden ejecutarse en paralelo (archivos distintos).
- **Polish**: T035 puede avanzar en paralelo con preparación de evidencia previa a T036.

---

## Parallel Example: User Story 2

```bash
# Componentes en paralelo (archivos independientes)
T017 _sidebar.html
T018 _navbar.html
T019 _tarjeta_metrica.html
T020 _card_propiedad.html
T021 _accesos_rapidos.html
T022 _badge_estado.html
T023 _form_field.html
T024 _alerta.html
```

---

## Implementation Strategy

### MVP First (Solo US1)

1. Completar Fase 1 (Setup)
2. Completar Fase 2 (Foundational)
3. Completar Fase 3 (US1)
4. Validar smoke tests de `/health` y `/`
5. Confirmar contrato y logging base

### Incremental Delivery

1. Base técnica (Fase 1+2)
2. MVP operativo (US1)
3. Capa visual reusable (US2)
4. Hardening de calidad (US3)
5. Cierre transversal (Fase 6)

### Parallel Team Strategy

Con varios desarrolladores:

1. Equipo completo en Fase 1 y 2
2. Luego distribuir:
   - Dev A: US1 (endpoints + smoke)
   - Dev B: US2 (componentes + CSS + iconos)
   - Dev C: US3 (tooling + validaciones)
3. Integrar y cerrar en Fase 6

---

## Notes

- `[P]` indica tareas en archivos independientes sin dependencia directa.
- `[US1]`, `[US2]`, `[US3]` mapean trazabilidad con historias de la spec.
- Evitar mover lógica de negocio a templates o repositorio global por capas.
- Mantener idioma español en documentación, comentarios y docstrings.