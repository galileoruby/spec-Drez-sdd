# Tareas: 005-dashboard-datos-reales

**Input**: Artefactos de diseño desde `specs/005-dashboard-datos-reales/`

**Prerrequisitos**: plan.md (requerido), spec.md (requerido), research.md, data-model.md, contracts/home-context.md, quickstart.md

**Pruebas**: Obligatorias para esta feature por requerimiento explícito de alcance (unitarias e integración de render/cálculo).

**Organización**: Las tareas se agrupan por historia de usuario para mantener implementación incremental, trazable y verificable.

## Formato: `[ID] [P?] [Story] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos y sin dependencia directa)
- **[Story]**: Historia de usuario (`US1`, `US2`, `US3`)
- Todas las tareas incluyen ruta exacta de archivo

---

## Fase 1: Setup (Preparación de implementación)

**Propósito**: Preparar el slice de dashboard y eliminar ambigüedades de integración antes de tocar lógica funcional.

- [X] T001 Crear estructura del módulo `app/modules/dashboard/` con `__init__.py`, `routes.py`, `schemas.py`, `repository.py`, `service.py` y `tests/__init__.py`
  Dependencias: ninguna.
  Completado cuando: existe el árbol del módulo y los archivos base son importables sin errores de sintaxis.

- [X] T002 [P] Registrar en `specs/005-dashboard-datos-reales/quickstart.md` los escenarios operativos de prueba para dataset con datos y dataset vacío
  Dependencias: ninguna.
  Completado cuando: quickstart incluye pasos ejecutables para validar cálculo real, estado vacío y modo no operativo de ingresos/vencidos.

- [X] T003 [P] Definir contrato de trabajo interno en `app/modules/dashboard/schemas.py` para `MetricaHome` y `ContextoHomeDashboard`
  Dependencias: T001.
  Completado cuando: los DTOs son suficientes para representar métricas, orden contractual y bandera de estado vacío sin detalles de implementación pendientes.

**Checkpoint**: Base preparada para implementación funcional sin abrir alcance adicional.

---

## Fase 2: Foundational (Bloqueos técnicos compartidos)

**Propósito**: Establecer la infraestructura mínima de acceso a datos y composición de contexto que desbloquea todas las historias.

**⚠️ CRÍTICO**: No iniciar historias de usuario sin completar este bloque.

- [X] T004 Implementar en `app/modules/propiedades/repository.py` función async de conteo agregado por estado para `disponible` y `rentada`
  Dependencias: ninguna.
  Completado cuando: existe una API de repositorio que retorna conteos enteros por estado objetivo en una sola consulta agregada.

- [X] T005 [P] Implementar en `app/modules/dashboard/repository.py` adaptador de lectura para consumir conteos del repositorio de propiedades
  Dependencias: T001, T004.
  Completado cuando: el módulo dashboard puede solicitar conteos operativos sin acoplarse a detalles de SQL en el servicio.

- [X] T006 Implementar en `app/modules/dashboard/service.py` constructor de contexto base con orden contractual de métricas/accesos
  Dependencias: T003, T005.
  Completado cuando: el servicio compone contexto completo manteniendo orden/estructura y dejando ingresos/vencidos en modo no operativo explícito.

- [X] T007 [P] Crear en `app/modules/dashboard/tests/test_service.py` pruebas unitarias iniciales del servicio (conteo real, orden contractual, no operativo)
  Dependencias: T006.
  Completado cuando: las pruebas fallan inicialmente sin implementación final y cubren casos de disponibles/rentadas + ingresos/vencidos no operativos.

**Checkpoint**: Infraestructura funcional mínima lista para conectar la home con datos reales.

---

## Fase 3: User Story 1 - Métricas reales en home (Prioridad: P1) 🎯 MVP

**Objetivo**: Reemplazar el mock de disponibles/rentadas por conteos persistidos reales en la home.

**Prueba independiente**: Cargar la home con datos conocidos y verificar que disponibles/rentadas coinciden con base de datos.

### Pruebas (US1)

- [X] T008 [P] [US1] Completar en `app/modules/dashboard/tests/test_service.py` escenarios unitarios de cálculo real para `disponible` y `rentada`
  Dependencias: T007.
  Completado cuando: la suite valida que ambos conteos se derivan de datos persistidos y no de constantes.

- [X] T009 [P] [US1] Añadir en `tests/test_smoke.py` caso de integración para `/` con verificación de métricas operativas reales
  Dependencias: T007.
  Completado cuando: la prueba HTTP confirma render de home con valores de disponibles/rentadas provenientes del servicio.

### Implementación (US1)

- [X] T010 [US1] Implementar en `app/modules/dashboard/service.py` mapeo de conteos reales a tarjetas de métricas operativas
  Dependencias: T006, T008.
  Completado cuando: `metricas` incluye disponibles/rentadas con valores derivados del repositorio y formato compatible con template.

- [X] T011 [US1] Integrar en `app/main.py` la obtención del contexto de home mediante servicio de dashboard
  Dependencias: T010.
  Completado cuando: se elimina dependencia de `METRICAS_DASHBOARD` hardcodeadas para disponibles/rentadas.

- [X] T012 [US1] Ajustar `app/templates/pages/dashboard.html` para consumir exclusivamente `context.metricas` sin bloque local hardcodeado
  Dependencias: T011.
  Completado cuando: el template no define métricas demo internas y renderiza valores provistos por backend.

**Checkpoint**: Home usa datos reales para disponibles/rentadas y entrega MVP funcional.

---

## Fase 4: User Story 2 - Contrato de contexto estable (Prioridad: P2)

**Objetivo**: Mantener orden y estructura del contexto de la home, incluyendo estado explícito no operativo para ingresos/vencidos.

**Prueba independiente**: Verificar que la estructura de `metricas` y `accesos` se mantiene compatible y estable tras la integración.

### Pruebas (US2)

- [X] T013 [P] [US2] Añadir en `app/modules/dashboard/tests/test_service.py` validación de orden y estructura contractual de `metricas`
  Dependencias: T010.
  Completado cuando: la prueba falla si cambia el orden esperado o faltan claves requeridas por contrato.

- [X] T014 [P] [US2] Añadir en `app/modules/dashboard/tests/test_service.py` validación de ingresos/vencidos en modo no operativo explícito
  Dependencias: T010.
  Completado cuando: la prueba asegura que ingresos/vencidos no ejecutan cálculo real ni usan valores inventados.

### Implementación (US2)

- [X] T015 [US2] Endurecer en `app/modules/dashboard/service.py` el contrato de salida de home para preservar orden y claves
  Dependencias: T013, T014.
  Completado cuando: el servicio produce un contexto estable y trazable al contrato documentado en `contracts/home-context.md`.

- [X] T016 [US2] Actualizar `specs/005-dashboard-datos-reales/contracts/home-context.md` con ejemplo final de contexto efectivo
  Dependencias: T015.
  Completado cuando: el contrato refleja exactamente la salida implementada y no deja decisiones pendientes.

**Checkpoint**: Contrato de contexto preservado y métricas no operativas explicitadas sin ambigüedad.

---

## Fase 5: User Story 3 - Estado vacío real (Prioridad: P3)

**Objetivo**: Hacer que el banner/estado vacío responda al estado real de datos persistidos.

**Prueba independiente**: Con dataset vacío se muestra estado vacío; con dataset con datos operativos, no se muestra.

### Pruebas (US3)

- [X] T017 [P] [US3] Añadir en `app/modules/dashboard/tests/test_service.py` escenarios de `mostrar_estado_vacio` para datos vacíos y con datos
  Dependencias: T015.
  Completado cuando: la prueba cubre ambos caminos y asegura determinismo de la bandera de estado.

- [X] T018 [P] [US3] Extender `tests/test_smoke.py` con assertions de render para señal de estado vacío real
  Dependencias: T017.
  Completado cuando: la prueba de integración valida la señal de estado vacío sin depender de valores mock.

### Implementación (US3)

- [X] T019 [US3] Implementar en `app/modules/dashboard/service.py` cálculo final de `mostrar_estado_vacio` basado en datos operativos
  Dependencias: T017.
  Completado cuando: la bandera se deriva de conteos reales y no de indicadores estáticos.

- [X] T020 [US3] Ajustar en `app/templates/pages/dashboard.html` la condición de estado vacío para consumir la bandera del contexto
  Dependencias: T019.
  Completado cuando: el template responde al estado real de datos y elimina placeholders ambiguos de estado vacío para métricas.

**Checkpoint**: Estado vacío totalmente alineado con datos persistidos reales.

---

## Fase 6: Validación y checklist final de calidad

**Propósito**: Cerrar la implementación con validaciones técnicas, control de alcance y evidencia de calidad.

- [X] T021 Ejecutar `uv run pytest app/modules/dashboard/tests -q` y resolver fallos en `app/modules/dashboard/tests/test_service.py`
  Dependencias: T020.
  Completado cuando: todas las pruebas unitarias del módulo dashboard pasan.

- [X] T022 Ejecutar `uv run pytest tests/test_smoke.py -q` y resolver fallos de integración de render en `tests/test_smoke.py`
  Dependencias: T020.
  Completado cuando: la prueba de integración de home pasa con datos reales y estado vacío real.

- [X] T023 [P] Ejecutar `uv run ruff check .` y corregir hallazgos dentro del alcance de esta spec
  Dependencias: T020.
  Completado cuando: no quedan errores de lint atribuibles a archivos modificados por la feature.

- [X] T024 [P] Ejecutar `uv run mypy --strict app/modules` y corregir tipado en archivos tocados
  Dependencias: T020.
  Completado cuando: no hay errores de tipado en módulos afectados por dashboard/propiedades.

- [X] T025 Actualizar `specs/005-dashboard-datos-reales/quickstart.md` con evidencia de ejecución (unitarias, integración, lint, mypy)
  Dependencias: T021, T022, T023, T024.
  Completado cuando: quickstart contiene resultados verificables de validación final.

- [X] T026 Actualizar checklist final en `specs/005-dashboard-datos-reales/checklists/requirements.md` marcando cumplimiento de la implementación
  Dependencias: T025.
  Completado cuando: checklist refleja estado real, incluyendo control de no alcance (sin rediseño UI, sin nuevas dependencias, sin dominio rentas/pagos).

**Checkpoint**: Implementación lista para cierre con evidencia completa y sin scope creep.

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Setup (Fase 1)**: inicia sin dependencias.
- **Foundational (Fase 2)**: depende de Setup y bloquea historias.
- **US1 (Fase 3)**: depende de Foundational.
- **US2 (Fase 4)**: depende de US1 por contrato consolidado.
- **US3 (Fase 5)**: depende de US2 para cálculo final de estado vacío.
- **Validación final (Fase 6)**: depende de cierre de US3.

### Dependencias entre historias

- **US1 (P1)**: habilita reemplazo real del mock en home.
- **US2 (P2)**: estabiliza contrato y no operativo explícito.
- **US3 (P3)**: completa comportamiento real del estado vacío.

### Restricciones de alcance (antisc scope creep)

- No rediseñar UI ni tokens.
- No añadir dependencias.
- No crear módulos/dominio de rentas o pagos.
- No crear endpoint adicional en esta iteración.

### Oportunidades de paralelismo

- Setup: T002 y T003 en paralelo tras T001.
- Foundational: T005 en paralelo con preparación de pruebas T007 tras T004/T006.
- US1: T008 y T009 en paralelo.
- US2: T013 y T014 en paralelo.
- US3: T017 y T018 en paralelo.
- Validación: T023 y T024 en paralelo tras cierre funcional.

---

## Ejemplo de paralelismo: US1

```text
T008 [US1] Completar pruebas unitarias de cálculo real en app/modules/dashboard/tests/test_service.py
T009 [US1] Añadir prueba de integración de home en tests/test_smoke.py
```

## Ejemplo de paralelismo: Validación final

```text
T023 Ejecutar ruff check y corregir hallazgos de la feature
T024 Ejecutar mypy --strict y corregir tipado de la feature
```

---

## Estrategia de implementación

### MVP primero

1. Completar Setup y Foundational.
2. Completar US1 para reemplazar mock por datos reales.
3. Validar US1 de forma independiente antes de avanzar.

### Entrega incremental

1. US1: valor funcional principal (métricas reales).
2. US2: estabilidad contractual y modo no operativo explícito.
3. US3: estado vacío alineado a datos reales.
4. Validación final: calidad y evidencia completa para cierre.

## Notas

- Las tareas están redactadas para ejecución directa por `speckit.implement`.
- Cada tarea tiene criterio de done verificable.
- Se evita alcance fuera de la spec 005.

