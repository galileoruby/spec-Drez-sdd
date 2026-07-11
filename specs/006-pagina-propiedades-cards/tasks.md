# Tareas: 006-pagina-propiedades-cards

**Input**: Artefactos de diseno desde `specs/006-pagina-propiedades-cards/`

**Prerrequisitos**: plan.md (requerido), spec.md (requerido), research.md, data-model.md, contracts/propiedades-page-context.md, quickstart.md

**Pruebas**: Obligatorias por alcance aprobado (repositorio/servicio, render, contrato, navegacion, responsive, estado vacio e imagen faltante).

**Organizacion**: Tareas agrupadas por historia de usuario para implementacion incremental y verificable.

## Formato: `[ID] [P?] [Story] Descripcion`

- **[P]**: Ejecutable en paralelo (archivos distintos y sin dependencia directa)
- **[Story]**: Historia de usuario (`US1`, `US2`, `US3`)
- Todas las tareas incluyen ruta exacta de archivo

---

## Fase 1: Setup (Preparacion)

**Proposito**: Preparar estructura y contrato base antes de cambiar comportamiento funcional.

- [x] T001 Crear estructura de pruebas del modulo propiedades con `app/modules/propiedades/tests/test_repository.py` y `app/modules/propiedades/tests/test_service.py`
  Dependencias: ninguna.
  Completado cuando: ambos archivos existen y el runner de pruebas los detecta.

- [x] T002 [P] Crear pagina base `app/templates/pages/propiedades.html` extendiendo layout existente sin rediseno global
  Dependencias: ninguna.
  Completado cuando: la pagina renderiza con base.html y no rompe navbar/sidebar.

- [x] T003 [P] Registrar contrato de contexto final en `specs/006-pagina-propiedades-cards/contracts/propiedades-page-context.md` con ruta, campos y reglas de fallback
  Dependencias: ninguna.
  Completado cuando: contrato explicita `propiedades`, `mostrar_estado_vacio`, `total_propiedades`, orden y fallback local.

**Checkpoint**: Estructura lista para implementar endpoint y render sin ambiguedad.

---

## Fase 2: Fundacional (Bloqueantes)

**Proposito**: Asegurar lectura de datos reales y contrato de salida antes de tocar UI final.

**CRITICO**: Ninguna historia inicia sin esta fase completada.

- [x] T004 Implementar en `app/modules/propiedades/repository.py` consulta async de listado ordenado por `created_at` descendente
  Dependencias: ninguna.
  Completado cuando: el repositorio retorna todas las propiedades en orden estable mas reciente primero.

- [x] T005 [P] Implementar en `app/modules/propiedades/service.py` mapeo `Propiedad -> PropiedadCardView` con campos obligatorios
  Dependencias: T004.
  Completado cuando: el servicio produce cards con imagen, titulo, direccion, habitaciones, banos, area_m2, precio_renta y estado.

- [x] T006 Implementar en `app/modules/propiedades/service.py` reglas de fallback local de imagen y bandera `mostrar_estado_vacio`
  Dependencias: T005.
  Completado cuando: imagen faltante usa fallback local y estado vacio refleja ausencia de registros.

- [x] T007 [P] Definir/ajustar en `app/modules/propiedades/schemas.py` DTOs inmutables para contexto de listado y card
  Dependencias: T005.
  Completado cuando: contrato del template queda tipado y sin acoplamiento a ORM.

**Checkpoint**: Datos reales y contrato de contexto listos para endpoint y vista.

---

## Fase 3: User Story 1 - Listado navegable de propiedades reales (Prioridad: P1) MVP

**Objetivo**: Exponer GET /propiedades y renderizar una card por propiedad con datos reales.

**Prueba independiente**: Acceder a /propiedades y validar cards con datos persistidos + enlace funcional desde sidebar.

### Pruebas (US1)

- [x] T008 [P] [US1] Implementar en `app/modules/propiedades/tests/test_repository.py` prueba de consulta real y orden `created_at` desc
  Dependencias: T004.
  Completado cuando: la prueba falla si se rompe el orden o falta algun registro.

- [x] T009 [P] [US1] Implementar en `app/modules/propiedades/tests/test_service.py` prueba de contrato de card con campos obligatorios
  Dependencias: T005, T007.
  Completado cuando: la prueba falla si falta algun campo requerido por card.

- [x] T010 [P] [US1] Extender `tests/test_smoke.py` con prueba de GET /propiedades y codigo 200
  Dependencias: T011.
  Completado cuando: smoke valida que la ruta existe y responde HTML.

### Implementacion (US1)

- [x] T011 [US1] Implementar en `app/modules/propiedades/routes.py` endpoint async GET /propiedades server-rendered
  Dependencias: T006, T007.
  Completado cuando: route delega a servicio y no contiene logica de negocio en template.

- [x] T012 [US1] Implementar en `app/templates/pages/propiedades.html` render de listado usando contexto del servicio
  Dependencias: T011.
  Completado cuando: se renderiza una card por propiedad y estado vacio cuando no hay datos.

- [x] T013 [US1] Ajustar en `app/templates/components/_sidebar.html` enlace Propiedades hacia `/propiedades`
  Dependencias: T011.
  Completado cuando: navegacion lateral redirige a la nueva ruta real.

**Checkpoint**: Ruta real operativa, cards con datos persistidos y navegacion lateral conectada.

---

## Fase 4: User Story 2 - Layout responsive y consistencia visual (Prioridad: P2)

**Objetivo**: Cumplir grilla responsive 3/2/1 y ajustar card reutilizada sin tocar layout global.

**Prueba independiente**: Verificar 3 columnas desktop, 2 tablet, 1 phone y campos visibles completos por card.

### Pruebas (US2)

- [x] T014 [P] [US2] Agregar en `tests/test_smoke.py` assertions del markup de card para imagen, titulo, direccion, habitaciones, banos, area, precio y estado
  Dependencias: T015.
  Completado cuando: la prueba falla si se pierde algun campo visual requerido.

- [x] T015 [P] [US2] Agregar en `tests/test_smoke.py` verificacion de estructura de grilla responsive (clases/selectores de 3/2/1)
  Dependencias: T016.
  Completado cuando: la prueba falla si no estan definidos los selectores de breakpoints esperados.

### Implementacion (US2)

- [x] T016 [US2] Ajustar `app/templates/components/_card_propiedad.html` reutilizada para mostrar campos obligatorios y estructura de imagen dominante
  Dependencias: T012.
  Completado cuando: componente reutilizado representa contrato completo de `PropiedadCardView`.

- [x] T017 [US2] Implementar en `app/static/css/app.css` grilla responsive de propiedades con 3 columnas desktop, 2 tablet, 1 phone
  Dependencias: T016.
  Completado cuando: estilos aplican 3/2/1 sin alterar tokens globales.

- [x] T018 [US2] Implementar en `app/static/css/app.css` truncado multilinea 2 lineas para titulo y 2 lineas para direccion
  Dependencias: T016.
  Completado cuando: textos largos no rompen layout y muestran ellipsis.

**Checkpoint**: Vista consistente, responsive 3/2/1 y card ajustada dentro del alcance.

---

## Fase 5: User Story 3 - Robustez ante datos incompletos y vacios (Prioridad: P3)

**Objetivo**: Asegurar estado vacio verificable y fallback de imagen local con datos incompletos.

**Prueba independiente**: Validar render estable con 0 propiedades y con propiedades sin imagen utilizable.

### Pruebas (US3)

- [x] T019 [P] [US3] Implementar en `app/modules/propiedades/tests/test_service.py` prueba de estado vacio cuando no hay propiedades
  Dependencias: T006.
  Completado cuando: la prueba falla si `mostrar_estado_vacio` no refleja total 0.

- [x] T020 [P] [US3] Implementar en `app/modules/propiedades/tests/test_service.py` prueba de fallback local para `imagen_url` faltante/invalida
  Dependencias: T006.
  Completado cuando: la prueba falla si no se asigna imagen fallback local.

- [x] T021 [P] [US3] Extender `tests/test_smoke.py` con prueba de render HTML de estado vacio en `/propiedades`
  Dependencias: T012, T019.
  Completado cuando: smoke valida mensaje/estado vacio sin error en respuesta.

### Implementacion (US3)

- [x] T022 [US3] Refinar en `app/modules/propiedades/service.py` normalizacion de datos incompletos visibles para no romper card
  Dependencias: T020.
  Completado cuando: servicio entrega valores renderizables para casos incompletos del contrato.

- [x] T023 [US3] Ajustar `app/templates/pages/propiedades.html` para mostrar bloque de estado vacio cuando `mostrar_estado_vacio` sea true
  Dependencias: T022.
  Completado cuando: pagina presenta estado vacio claro y verificable.

**Checkpoint**: Comportamiento robusto frente a datos vacios e incompletos.

---

## Fase 6: Pruebas y validacion final

**Proposito**: Cerrar la feature con evidencia tecnica y confirmacion de no scope creep.

- [x] T024 Ejecutar `uv run pytest app/modules/propiedades/tests -q` y corregir fallos de repository/service
  Dependencias: T023.
  Completado cuando: pruebas del modulo propiedades quedan en verde.

- [x] T025 Ejecutar `uv run pytest tests/test_smoke.py -q` y corregir fallos de render/navegacion
  Dependencias: T023.
  Completado cuando: smoke valida GET /propiedades, sidebar, estado vacio y estructura de cards.

- [x] T026 [P] Ejecutar `uv run ruff check .` y corregir hallazgos dentro del alcance de la spec 006
  Dependencias: T023.
  Completado cuando: lint queda en verde para archivos tocados por la feature.

- [x] T027 [P] Ejecutar `uv run mypy --strict app/modules` y corregir tipado en archivos afectados
  Dependencias: T023.
  Completado cuando: type-check estricto queda en verde.

- [x] T028 Actualizar `specs/006-pagina-propiedades-cards/quickstart.md` con evidencia de ejecucion y resultados finales
  Dependencias: T024, T025, T026, T027.
  Completado cuando: quickstart incluye resultados reales de tests/lint/type-check.

- [x] T029 Actualizar `specs/006-pagina-propiedades-cards/checklists/requirements.md` con cierre de implementacion y confirmacion de no scope creep
  Dependencias: T028.
  Completado cuando: checklist documenta que no se agregaron filtros, paginacion, dominios nuevos ni cambios globales no aprobados.

**Checkpoint**: Feature lista para `speckit.implement` y posterior review.

---

## Dependencias y orden de ejecucion

### Dependencias entre fases

- Setup (Fase 1): inicia sin dependencias.
- Fundacional (Fase 2): depende de Setup y bloquea historias.
- US1 (Fase 3): depende de Fundacional.
- US2 (Fase 4): depende de US1.
- US3 (Fase 5): depende de US2.
- Validacion final (Fase 6): depende de US3.

### Dependencias entre historias

- US1 entrega ruta funcional y base de render con datos reales.
- US2 añade consistencia visual responsive y card completa.
- US3 asegura robustez en casos vacios/incompletos.

### Restricciones de alcance

- Sin dominio rentas/pagos.
- Sin filtros/busqueda/paginacion/ordenamiento adicional.
- Sin nuevas dependencias.
- Sin rediseno global de navbar/sidebar/layout.
- Sin cambios de tokens visuales globales.

### Oportunidades de paralelismo

- Setup: T002 y T003 en paralelo.
- Fundacional: T005 y T007 en paralelo tras T004.
- US1: T008, T009 y T010 en paralelo segun dependencias.
- US2: T014 y T015 en paralelo tras T016/T017.
- US3: T019, T020 y T021 en paralelo segun dependencias.
- Validacion: T026 y T027 en paralelo.

---

## Ejemplo de paralelismo US2

```text
T014 [US2] Assertions de campos de card en tests/test_smoke.py
T015 [US2] Verificacion de estructura responsive en tests/test_smoke.py
```

## Ejemplo de paralelismo validacion final

```text
T026 Ruff check del alcance
T027 Mypy strict del alcance
```

---

## Estrategia de implementacion

### MVP primero

1. Completar Setup y Fundacional.
2. Completar US1 (ruta + render real + sidebar).
3. Validar US1 de forma independiente antes de continuar.

### Entrega incremental

1. US1: navegacion y datos reales.
2. US2: responsive y consistencia visual de cards.
3. US3: robustez ante vacio e incompletos.
4. Fase final: evidencia tecnica y cierre de alcance.

## Notas

- Todas las tareas estan redactadas para ejecucion directa por `speckit.implement`.
- Cada tarea incluye criterio verificable de completitud.
- Se mantiene trazabilidad con decisiones y criterios de la spec 006.
