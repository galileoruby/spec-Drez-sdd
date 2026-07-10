# Implementation Plan: 005-dashboard-datos-reales

**Branch**: `[005-dashboard-datos-reales]` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-dashboard-datos-reales/spec.md`

## Summary

Esta implementación elimina el mock actual del dashboard principal para las métricas de propiedades y lo reemplaza por datos persistidos reales (disponibles y rentadas), manteniendo intacto el contrato de contexto de la home. El cálculo se orquesta en un servicio de dashboard que consume conteos por estado desde el repositorio del módulo de propiedades. Ingresos y vencidos permanecen explícitamente en modo no operativo en esta iteración.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: FastAPI, Jinja2, SQLAlchemy 2.x async, asyncpg

**Storage**: PostgreSQL

**Testing**: pytest, pytest-asyncio, httpx.AsyncClient

**Target Platform**: Servicio web server-rendered sobre Linux/Windows en entorno de desarrollo

**Project Type**: Aplicación web monolítica modular

**Performance Goals**: Resolver métricas de home con consultas agregadas por estado sin degradar perceptiblemente el render del endpoint `/`

**Constraints**:
- Mantener orden y estructura del contexto actual de métricas/accesos (FR-004)
- No introducir dependencias nuevas ni rediseño visual (FR-008, FR-009)
- No crear endpoint adicional salvo necesidad imprescindible (FR-012)
- Ingresos/vencidos permanecen no operativos (FR-005)

**Scale/Scope**: Una vista principal (`/`) y un conjunto pequeño de archivos backend/templates; sin cambios de esquema en base de datos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0

- Governanza vigente: aplica sin excepciones.
- Vertical slice: se mantiene al introducir módulo `dashboard` para orquestación de negocio.
- Async-first: acceso a datos y servicio en flujo asíncrono.
- Stack obligatorio: sin nuevas dependencias.
- Spec-driven: alcance restringido a FR-001..FR-012 de la spec 005.

**Resultado gate**: PASS.

### Post-Phase 1 (re-check)

- Artefactos de diseño no abren nuevos dominios (rentas/pagos/reporting).
- Contrato de home documentado sin romper compatibilidad.
- Decisión de endpoint adicional documentada como fuera de alcance en esta spec.

**Resultado gate**: PASS.

## Resumen técnico de arquitectura propuesta

1. Crear/usar un servicio de dashboard server-rendered para componer contexto de la home.
2. Obtener conteos reales de propiedades disponibles y rentadas mediante repositorio con consulta agregada por estado.
3. Mapear esos conteos al contrato existente de métricas, preservando orden y estructura.
4. Mantener ingresos y vencidos en modo no operativo explícito, sin cálculo ficticio ni nuevos modelos.
5. No crear endpoint de refresco parcial en esta iteración: no aporta valor funcional imprescindible con el alcance actual.

## Módulos y archivos afectados

### Backend

- `app/main.py`
  - Mantener endpoint `/` y delegar construcción de contexto al servicio de dashboard.
  - Eliminar uso de métricas hardcodeadas para disponibles/rentadas.

- `app/modules/dashboard/routes.py` (nuevo)
  - Encapsular route de home para mantener la arquitectura vertical slice.
  - Inyectar dependencias y renderizar `pages/dashboard.html` con contexto del servicio.

- `app/modules/dashboard/service.py` (nuevo)
  - Orquestar obtención de métricas operativas.
  - Consolidar contrato de contexto de home y estados no operativos de ingresos/vencidos.
  - Resolver bandera de estado vacío basada en datos reales.

- `app/modules/dashboard/repository.py` (nuevo o adaptación mínima)
  - Exponer lectura agregada necesaria para home cuando se requiera desacople del repositorio de propiedades.

- `app/modules/propiedades/repository.py`
  - Añadir función de conteo por estado para `disponible` y `rentada` sin duplicar lógica de acceso.

- `app/modules/dashboard/schemas.py` (nuevo)
  - Definir DTOs inmutables de contexto de dashboard (métrica, resumen y estado de home).

### Frontend server-rendered

- `app/templates/pages/dashboard.html`
  - Dejar de definir métricas hardcodeadas dentro del template.
  - Consumir métricas desde `context.metricas` preservando estructura y orden.

### Tests

- `app/modules/dashboard/tests/test_service.py` (nuevo)
  - Probar cálculo de métricas desde repositorio/servicio.
  - Probar estado vacío según existencia de datos.

- `tests/test_smoke.py`
  - Actualizar assertions de home para valores provenientes de datos reales/overrides.
  - Verificar que la home ya no depende del bloque mock previo.

## Secuencia de implementación por fases

## Fase 0 - Setup técnico

**Precondiciones**:
- `spec.md` de 005 en estado Draft sin preguntas críticas abiertas.
- Base de propiedades disponible por spec 004.

**Tareas técnicas**:
1. Crear estructura del slice `app/modules/dashboard/`.
2. Definir contrato mínimo de contexto (schemas) para métricas y estado.
3. Identificar en `app/main.py` los puntos de desacople del mock.

**Estrategia de pruebas de fase**:
- Validación estática de imports y estructura de módulos.

**Riesgos y mitigaciones**:
- Riesgo: mover demasiado código desde `app/main.py` y romper arranque.
  - Mitigación: cambio incremental manteniendo endpoint `/` operativo en todo momento.

**Criterio de salida**:
- Slice dashboard creado y enlazable sin tocar todavía el comportamiento funcional de métricas.

## Fase 1 - Implementación de datos reales

**Precondiciones**:
- Fase 0 completada.
- Repositorio de propiedades accesible por sesión async.

**Tareas técnicas**:
1. Implementar conteo por estado (`disponible`, `rentada`) en repositorio de propiedades.
2. Implementar servicio dashboard que compone contexto final.
3. Integrar route de home para usar servicio dashboard y eliminar mock.
4. Dejar ingresos/vencidos en estado no operativo explícito en contexto.

**Estrategia de pruebas de fase**:
- Unit tests del servicio con dobles/fakes de repositorio.
- Verificación de contrato de contexto (orden/estructura) a nivel de prueba.

**Riesgos y mitigaciones**:
- Riesgo: romper orden de métricas esperado por template/componentes.
  - Mitigación: snapshot/assertions sobre orden y claves del contexto.
- Riesgo: consultas ineficientes por múltiples round-trips.
  - Mitigación: usar consulta agregada por estado en una operación.

**Criterio de salida**:
- Home renderiza disponibles/rentadas desde DB y mantiene contrato existente (FR-001..FR-005).

## Fase 2 - Pruebas integradas y regresión funcional

**Precondiciones**:
- Fase 1 completada.

**Tareas técnicas**:
1. Crear pruebas de servicio para escenarios con y sin datos.
2. Actualizar smoke test de `/` para validar render real.
3. Cubrir caso edge: propiedades existentes sin estados objetivo.

**Estrategia de pruebas de fase**:
- `pytest app/modules/dashboard/tests -q`
- `pytest tests/test_smoke.py -q`

**Riesgos y mitigaciones**:
- Riesgo: tests frágiles por depender de strings no contractuales.
  - Mitigación: validar señales contractuales (métricas clave, estado vacío, no hardcode).

**Criterio de salida**:
- Cobertura de cálculo y render validada (FR-010, SC-004).

## Fase 3 - Validación final y cierre

**Precondiciones**:
- Fase 2 en verde.

**Tareas técnicas**:
1. Ejecutar lint y tipado en alcance modificado.
2. Verificar manualmente estado de home con dataset vacío y con datos.
3. Documentar pendiente explícito de ingresos/vencidos para spec futura.

**Estrategia de pruebas de fase**:
- `uv run ruff check .`
- `uv run mypy --strict app/modules`
- `uv run pytest -q` (o subset acordado de la feature)

**Riesgos y mitigaciones**:
- Riesgo: introducir alcance accidental de reporting.
  - Mitigación: revisar cambios y validar contra sección de no alcance.

**Criterio de salida**:
- Implementación lista para pasar a `tasks.md` sin brechas de alcance.

## Estrategia de pruebas consolidada

1. **Unitarias (servicio dashboard)**: validan cálculo de disponibles/rentadas, estado vacío y métricas no operativas.
2. **Integración ligera (repositorio)**: valida consulta agregada por estado.
3. **HTTP/render smoke (`/`)**: valida salida HTML coherente con datos reales y contrato de contexto.
4. **Calidad estática**: Ruff + mypy strict en módulos afectados.

## No alcance técnico (control de scope creep)

- No se crean endpoints adicionales de refresh parcial en esta spec.
- No se crean modelos/migraciones para ingresos o vencidos.
- No se modifica diseño visual, componentes estéticos ni tokens.
- No se implementa analítica histórica ni reporting.

## Criterios de aceptación técnicos trazables

- **CA-001 (FR-001, FR-002, SC-001)**: disponibles y rentadas se calculan desde datos persistidos y se reflejan correctamente en home.
- **CA-002 (FR-003, SC-002)**: se elimina dependencia de métricas hardcodeadas para esos dos indicadores.
- **CA-003 (FR-004)**: se mantiene orden y estructura del contexto de métricas/accesos.
- **CA-004 (FR-005, FR-011, SC-005)**: ingresos y vencidos permanecen no operativos y queda pendiente documentado para futura spec.
- **CA-005 (FR-006, SC-003)**: banner/estado vacío responde a existencia real de datos.
- **CA-006 (FR-010, SC-004)**: pruebas cubren cálculo de métricas y render de home.
- **CA-007 (FR-012)**: no se agrega endpoint nuevo al no existir necesidad funcional imprescindible en este alcance.

## Validaciones finales (Definition of Done de implementación)

1. Home renderiza conteos reales de disponibles y rentadas.
2. Se confirma ausencia de bloque mock de métricas en template/controlador.
3. Contrato de contexto de home permanece compatible (orden/estructura).
4. Estado vacío se comporta correctamente con y sin datos.
5. Ingresos/vencidos visibles en modo no operativo explícito.
6. Pruebas unitarias e integración de la feature en verde.
7. `ruff` y `mypy --strict` en verde para alcance modificado.
8. Pendiente de ingresos/vencidos reales documentado para próxima spec.

## Project Structure

### Documentation (this feature)

```text
specs/005-dashboard-datos-reales/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── home-context.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── main.py
├── modules/
│   ├── dashboard/
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── tests/
│   │       └── test_service.py
│   └── propiedades/
│       └── repository.py
└── templates/
    └── pages/
        └── dashboard.html

tests/
└── test_smoke.py
```

**Structure Decision**: Se adopta una expansión mínima del monolito modular existente incorporando un slice `dashboard` para orquestación de datos de home y reutilizando el repositorio de `propiedades` para conteos por estado.

## Complexity Tracking

Sin violaciones de gobernanza que requieran excepción.
