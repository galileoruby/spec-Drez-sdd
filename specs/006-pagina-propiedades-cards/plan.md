# Implementation Plan: 006-pagina-propiedades-cards

**Branch**: `[006-pagina-propiedades-cards]` | **Date**: 2026-07-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from specs/006-pagina-propiedades-cards/spec.md

## Summary

Se implementara una pagina server-rendered en GET /propiedades que lista propiedades reales en cards reutilizando y ajustando el componente existente de card. El flujo tecnico obligatorio sera: primero endpoint y acceso a datos, despues render de pagina/cards responsive, y finalmente integracion de navegacion lateral desde sidebar. El listado se entrega ordenado por created_at descendente, con estado vacio definido y fallback de imagen local cuando imagen_url no sea utilizable.

## Technical Context

**Language/Version**: Python 3.13

**Primary Dependencies**: FastAPI, Jinja2, SQLAlchemy 2.x async, asyncpg

**Storage**: PostgreSQL

**Testing**: pytest, pytest-asyncio, httpx.AsyncClient

**Target Platform**: Aplicacion web server-rendered

**Project Type**: Monolito modular con vertical slices

**Performance Goals**: Render estable del listado de propiedades sin bloqueos ni errores para volumen operativo esperado

**Constraints**:
- Mantener layout global existente
- Sin nuevas dependencias
- Sin cambios de tokens visuales globales
- Sin filtros, busqueda, paginacion u ordenamiento adicional

**Scale/Scope**: Una nueva ruta de lectura, un template de pagina, ajuste de componente card y enlace de sidebar

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0

- Aplica gobernanza vigente.
- Arquitectura por vertical slice preservada (modulo propiedades existente).
- Async en endpoint, servicio y repositorio.
- Sin dependencias nuevas.

**Resultado gate**: PASS.

### Post-Phase 1

- Contrato de contexto explicitado para template.
- Ajustes visuales acotados a la pagina objetivo sin tocar layout global ni paleta.
- No alcance preservado.

**Resultado gate**: PASS.

## Resumen tecnico de arquitectura propuesta

1. Endpoint GET /propiedades en capa de rutas del modulo propiedades.
2. Servicio de propiedades construye contrato de contexto para cards.
3. Repositorio obtiene listado real desde base, ordenado por created_at descendente.
4. Template de pagina renderiza grid responsive 3/2/1 reutilizando _card_propiedad.html.
5. Sidebar actualiza enlace Propiedades para redirigir a GET /propiedades.

## Modulos y archivos afectados

- app/modules/propiedades/routes.py
  - Declarar ruta GET /propiedades server-rendered.
  - Delegar lectura y mapeo al servicio.

- app/modules/propiedades/service.py
  - Orquestar listado y transformar entidad a contrato de card.
  - Resolver fallback de imagen local.
  - Resolver estado vacio.

- app/modules/propiedades/repository.py
  - Exponer consulta async de listado completo ordenada por created_at descendente.

- app/templates/pages/propiedades.html (nuevo)
  - Render de pagina de propiedades con grid responsive 3/2/1.
  - Estado vacio cuando no existan propiedades.

- app/templates/components/_card_propiedad.html
  - Ajustar markup para mostrar imagen, titulo, direccion, habitaciones, banos, area m2, precio y estado.
  - Aplicar regla de truncado 2 lineas titulo + 2 lineas direccion.

- app/templates/components/_sidebar.html
  - Cambiar href de Propiedades para navegar a /propiedades.

- app/static/css/app.css
  - Incorporar estilos de grid responsive 3/2/1 y truncado multilinea de textos largos, sin tocar tokens globales.

- tests/test_smoke.py
  - Verificar navegacion y render de GET /propiedades.

- app/modules/propiedades/tests/test_repository.py (nuevo)
  - Verificar consulta/orden de propiedades.

- app/modules/propiedades/tests/test_service.py (nuevo)
  - Verificar mapeo de contrato, fallback de imagen y estado vacio.

## Secuencia de implementacion por fases

## Fase 0: Setup

**Precondiciones**:
- Spec 006 con decisiones bloqueantes cerradas.

**Tareas tecnicas**:
1. Crear estructura de pruebas faltantes en modulo propiedades para repository/service.
2. Crear template de pagina propiedades base.
3. Registrar criterios de contrato en docs de feature.

**Resultado verificable**:
- Archivos base preparados para implementar sin ambiguedad.

**Criterio de salida**:
- Estructura minima lista para endpoint y render.

## Fase 1: Implementacion endpoint (obligatorio primero)

**Precondiciones**:
- Fase 0 completada.

**Tareas tecnicas**:
1. Implementar repository para listar propiedades ordenadas por created_at desc.
2. Implementar service para construir contrato PropiedadCardView y estado vacio.
3. Implementar route GET /propiedades server-rendered.

**Resultado verificable**:
- GET /propiedades responde 200 y retorna HTML usando datos reales persistidos.

**Criterio de salida**:
- Endpoint funcional, sin logica de negocio en template.

## Fase 2: Implementacion vista/cards responsive (obligatorio despues del endpoint)

**Precondiciones**:
- Fase 1 completada.

**Tareas tecnicas**:
1. Ajustar _card_propiedad.html para campos obligatorios por card.
2. Crear/ajustar propiedades.html para usar grid y estado vacio.
3. Aplicar estilos responsive: desktop 3, tablet 2, phone 1.
4. Aplicar truncado multilinea 2+2 para titulo/direccion.

**Resultado verificable**:
- Render de cards cumple campos requeridos y comportamiento responsive.

**Criterio de salida**:
- Vista operativa con datos reales y layout esperado.

## Fase 3: Integracion navegacion sidebar

**Precondiciones**:
- Fase 2 completada.

**Tareas tecnicas**:
1. Actualizar enlace Propiedades en _sidebar.html hacia /propiedades.
2. Verificar que la navegacion no altera comportamiento de otros enlaces.

**Resultado verificable**:
- Clic en Propiedades navega a ruta real.

**Criterio de salida**:
- Sidebar conectado a nueva pantalla sin regresiones visuales globales.

## Fase 4: Pruebas y validacion final

**Precondiciones**:
- Fases 1-3 completadas.

**Tareas tecnicas**:
1. Pruebas repository/service para consulta y contrato.
2. Pruebas de render de pagina propiedades.
3. Prueba de contrato de contexto enviado al template.
4. Prueba de navegacion desde sidebar a /propiedades.
5. Verificacion responsive en 3 breakpoints.
6. Verificacion de estado vacio e imagen faltante.

**Resultado verificable**:
- Suite definida en verde y evidencia registrada.

**Criterio de salida**:
- Implementacion lista para review.

## Estrategia de pruebas por fase

- Setup: validacion de estructura y compilacion de templates.
- Endpoint: pruebas unitarias repository/service y smoke de GET /propiedades.
- Vista/cards: pruebas de contenido HTML por card y assertions de campos visibles.
- Sidebar: prueba de enlace correcto en render.
- Validacion final: ruff, mypy strict y pytest en alcance de feature.

## Criterios tecnicos de aceptacion trazables

- CTA-001 (FR-001, FR-008, SC-004): ruta /propiedades y navegacion desde sidebar funcionales.
- CTA-002 (FR-002, FR-013, SC-001): endpoint async consume datos reales desde servicio/repositorio.
- CTA-003 (FR-003, FR-004, SC-002): una card por propiedad con campos obligatorios completos.
- CTA-004 (FR-005, FR-006, FR-007, SC-003): responsive 3/2/1 verificado.
- CTA-005 (FR-011, FR-012, SC-005): estado vacio e imagen faltante resueltos por contrato.
- CTA-006 (FR-016, SC-006): no scope creep y validaciones tecnicas en verde.

## Riesgos y mitigaciones por fase

- Riesgo: template acoplado a entidades ORM.
  - Mitigacion: contrato explicito de contexto en service.
- Riesgo: overflow visual por textos largos.
  - Mitigacion: truncado multilinea 2+2 con pruebas HTML/CSS.
- Riesgo: imagen faltante rompe card.
  - Mitigacion: fallback local obligatorio en service.
- Riesgo: regresion en sidebar.
  - Mitigacion: prueba de navegacion y validacion de enlace unico.

## No alcance explicito

- Sin nuevos dominios rentas/pagos.
- Sin filtros, busqueda, paginacion u ordenamiento adicional.
- Sin dependencias nuevas.
- Sin rediseno global de navbar/sidebar/layout.
- Sin cambios de tokens visuales globales o paleta.

## Validaciones finales obligatorias

1. Tests de modulos involucrados en verde.
2. Lint en verde.
3. Type-check estricto en verde.
4. Confirmacion explicita de no scope creep.
5. Evidencia de enlace sidebar -> /propiedades.

## Project Structure

### Documentation (this feature)

```text
specs/006-pagina-propiedades-cards/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── propiedades-page-context.md
└── tasks.md
```

### Source Code (repository root)

```text
app/
├── modules/
│   └── propiedades/
│       ├── routes.py
│       ├── repository.py
│       ├── service.py
│       └── tests/
│           ├── test_repository.py
│           └── test_service.py
├── templates/
│   ├── pages/
│   │   └── propiedades.html
│   └── components/
│       ├── _card_propiedad.html
│       └── _sidebar.html
└── static/
    └── css/
        └── app.css

tests/
└── test_smoke.py
```

**Structure Decision**: Se extiende el slice existente de propiedades, manteniendo separacion rutas/servicio/repositorio y render server-rendered con contrato explicito.

## Complexity Tracking

Sin violaciones de gobernanza que requieran excepcion.
