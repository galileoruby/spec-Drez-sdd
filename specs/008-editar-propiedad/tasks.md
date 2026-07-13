# Tasks: Edición de propiedad

**Input**: `specs/008-editar-propiedad/spec.md` y `specs/008-editar-propiedad/plan.md`
**Branch**: `008-editar-propiedad`
**Objetivo**: implementar el flujo SSR de edición de propiedades, con validación de dominio compartida, 404 claro, prevención de persistencia parcial, manejo de conflicto optimista y cobertura de pruebas del módulo `propiedades`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: preparar los artefactos base de la pantalla y la cobertura de pruebas sin tocar aún la lógica de negocio.

- [X] T001 [P] Crear los artefactos base de UI y pruebas en `app/modules/propiedades/templates/editar_propiedad.html`, `app/modules/propiedades/templates/_formulario_editar_propiedad.html` y `app/modules/propiedades/tests/test_templates_editar_propiedad.py` para habilitar el nuevo flujo de edición (FR-001, FR-003, AC-H1.1, AC-H1.2)
- [X] T002 [P] Extender los contratos de `app/modules/propiedades/schemas.py` para añadir DTOs de edición y el `id` en `PropiedadCardView` (FR-001, FR-002, FR-003, FR-004, FR-005, AC-H1.1, AC-H1.2)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: dejar listas las piezas compartidas que bloquean todos los recorridos de edición.

- [X] T003 [P] Añadir en `app/modules/propiedades/repository.py` la lectura por id y la búsqueda de identidad excluyendo la propia propiedad para soportar precarga, edición y detección de duplicados (FR-002, FR-017, AC-H1.1, AC-H1.3, AC-H3.1)
- [X] T004 Consolidar en `app/modules/propiedades/service.py` un helper compartido de normalización y validación para alta y edición, actualizando los rangos de negocio a `habitaciones 1..15` y `banos 0.5..8.0` con pasos de `0.5`, y asegurando que los inválidos no se persistan (FR-006, FR-007, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, AC-H2.1, AC-H2.2, AC-H2.3, AC-H2.4, AC-H2.5)
- [X] T005 [P] Preparar en `app/modules/propiedades/routes.py` el reconocimiento del query param de éxito de edición y el mapeo de ids inexistentes a 404 claro para el flujo web (FR-002, FR-015, FR-016, AC-H1.3, AC-H3.1)

**Checkpoint**: el dominio ya puede leer una propiedad existente, validar un formulario de edición y distinguir duplicados antes de persistir.

---

## Phase 3: User Story 1 - Abrir y guardar edición básica (Priority: P1)

**Goal**: abrir la edición desde una card, mostrar el formulario precargado y guardar cambios válidos con redirección al listado y confirmación visible.

**Independent Test**: desde el listado, abrir una propiedad existente, verificar que el formulario muestra los datos actuales y guardar una edición válida para regresar al listado con confirmación de éxito.

### Implementation for User Story 1

- [X] T006 [US1] Implementar en `app/modules/propiedades/routes.py` los endpoints `GET /propiedades/editar/{id}` y `POST /propiedades/editar/{id}`, incluyendo precarga de datos, render SSR, persistencia exitosa y redirección `303` al listado con confirmación de edición (FR-001, FR-002, FR-003, FR-004, FR-005, FR-016, AC-H1.1, AC-H1.2, AC-H1.3)
- [X] T007 [P] [US1] Construir la experiencia visual de edición en `app/modules/propiedades/templates/editar_propiedad.html`, `app/modules/propiedades/templates/_formulario_editar_propiedad.html` y `app/templates/components/_card_propiedad.html`, agregando el botón Editar por card, el selector de estado preseleccionado y la navegación al formulario canónico `/propiedades/editar/{id}` (FR-001, FR-003, FR-004, FR-005, AC-H1.1, AC-H1.2)
- [X] T008 [P] [US1] Añadir pruebas de render e integración en `app/modules/propiedades/tests/test_routes.py` y `app/modules/propiedades/tests/test_templates_editar_propiedad.py` para cubrir apertura de edición, precarga de valores y guardado exitoso con redirección al listado (FR-001, FR-002, FR-003, FR-004, FR-005, FR-016, AC-H1.1, AC-H1.2, AC-H1.3)

**Checkpoint**: la edición abre, muestra datos reales y permite guardar cambios válidos sin salir del flujo del listado.

---

## Phase 4: User Story 2 - Validación de dominio y conservación del formulario (Priority: P2)

**Goal**: rechazar valores inválidos, conservar lo que el usuario escribió y mostrar errores inline por campo sin persistir cambios parciales.

**Independent Test**: enviar la pantalla de edición con campos vacíos, con espacios solamente o con valores fuera de rango y verificar que no se persiste nada y que los errores quedan visibles en HTML.

### Implementation for User Story 2

- [X] T009 [US2] Completar en `app/modules/propiedades/service.py` el flujo de edición invalida para conservar los valores enviados, poblar errores inline por campo y evitar persistencia parcial, reutilizando el helper compartido de validación (FR-006, FR-007, FR-009, FR-010, FR-011, FR-012, FR-013, FR-014, AC-H2.1, AC-H2.2, AC-H2.3, AC-H2.4, AC-H2.5)
- [X] T010 [P] [US2] Añadir pruebas de dominio en `app/modules/propiedades/tests/test_service.py` para trim, campos requeridos, rangos de `precio_mensual`, `habitaciones` y `banos`, duplicidad de identidad y no persistencia en edición inválida (FR-006, FR-007, FR-009, FR-010, FR-011, FR-013, FR-017, AC-H2.1, AC-H2.2, AC-H2.3, AC-H2.4, AC-H2.5)
- [X] T011 [P] [US2] Añadir pruebas HTTP y de render en `app/modules/propiedades/tests/test_routes.py` y `app/modules/propiedades/tests/test_templates_editar_propiedad.py` para verificar errores inline, conservación del formulario y ausencia de persistencia parcial cuando la validación falla (FR-012, FR-013, FR-014, AC-H2.5)

**Checkpoint**: la edición inválida no modifica la base de datos y devuelve HTML con errores útiles por campo.

---

## Phase 5: User Story 3 - Flujo web sin 422 técnico (Priority: P3)

**Goal**: evitar JSON 422 técnico en envíos vacíos o incompletos, devolver HTML con errores de dominio y manejar ids inexistentes con 404 claro y conflicto optimista sin persistencia parcial.

**Independent Test**: enviar un formulario vacío o incompleto desde la UI, verificar que el resultado es HTML con errores de negocio, y comprobar que un id inexistente responde 404 claro.

### Implementation for User Story 3

- [X] T012 [US3] Implementar en `app/modules/propiedades/routes.py` el tratamiento de id inexistente como `404 Not Found` claro y el manejo de payload vacío o incompleto como HTML con errores de dominio, evitando la respuesta técnica JSON 422 en el flujo web (FR-008, FR-015, AC-H3.1, AC-H3.2)
- [X] T013 [P] [US3] Añadir en `app/modules/propiedades/service.py` y `app/modules/propiedades/repository.py` el control de conflicto optimista para ediciones concurrentes y la resolución segura de cambios desfasados sin persistencia parcial (FR-013, FR-017, AC-H3.1, AC-H3.2)
- [X] T014 [P] [US3] Cubrir en `app/modules/propiedades/tests/test_routes.py` y `app/modules/propiedades/tests/test_service.py` los casos de id inexistente, payload vacío/incompleto y conflicto optimista para asegurar el comportamiento esperado del flujo web (FR-008, FR-013, FR-015, FR-017, AC-H3.1, AC-H3.2)

**Checkpoint**: el flujo web responde con HTML de dominio, no filtra errores técnicos y protege contra conflictos de edición.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: cerrar regresiones compartidas y validar que la edición no rompe el alta ni la navegación existente.

- [X] T015 [P] Ajustar la regresión compartida de alta en `app/modules/propiedades/tests/test_service.py`, `app/modules/propiedades/tests/test_routes.py` y `app/modules/propiedades/tests/test_templates_crear_propiedad.py` para reflejar los rangos comunes de validación y mantener consistencia entre alta y edición (FR-006, FR-007, FR-009, FR-010, FR-011, AC-H2.2, AC-H2.3, AC-H2.4)
- [X] T016 [P] Validar el recorrido completo de edición en `app/modules/propiedades/tests/test_routes.py` y `app/modules/propiedades/tests/test_templates_editar_propiedad.py`, confirmando el botón Editar, la redirección con éxito y la confirmación visible en el listado (FR-001, FR-016, AC-H1.1, AC-H1.3)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias; puede arrancar de inmediato.
- **Foundational (Phase 2)**: depende de Setup y bloquea todas las historias de usuario.
- **User Story 1 (Phase 3)**: depende de Foundational.
- **User Story 2 (Phase 4)**: depende de Foundational y de la base de UI/contratos que deja US1.
- **User Story 3 (Phase 5)**: depende de Foundational y del manejo de rutas/errores compartidos.
- **Polish (Phase 6)**: depende de las historias que se quieran cerrar y de la validación compartida.

### User Story Dependencies

- **US1**: puede empezar apenas termine Foundational.
- **US2**: puede avanzar en paralelo con US1, pero debe mantener compatibilidad con la validación compartida.
- **US3**: puede avanzar en paralelo con US1/US2, pero depende del contrato de rutas y de la política de errores.

### Within Each User Story

- Primero contratos y datos, luego servicio, luego rutas, luego templates, luego pruebas.
- Las pruebas de error deben cubrir el mismo slice que las rutas y el servicio tocan.
- La persistencia no debe ocurrir antes de que la validación esté cerrada.

## Parallel Opportunities

- `T001` y `T002` pueden ejecutarse en paralelo porque tocan artefactos distintos.
- `T003` y `T005` pueden ejecutarse en paralelo porque separan repositorio y ruta.
- `T007` y `T008` pueden ejecutarse en paralelo una vez exista el contrato de edición.
- `T010` y `T011` pueden ejecutarse en paralelo al cubrir servicio y render/HTTP por separado.
- `T013` y `T014` pueden ejecutarse en paralelo si el guardián de conflicto optimista ya está definido.
- `T015` y `T016` pueden ejecutarse en paralelo como cierre y regresión.

## Implementation Strategy

### MVP First

1. Completar Setup y Foundational.
2. Entregar US1 para abrir y guardar edición válida.
3. Validar visualmente y con pruebas el flujo básico.
4. Solo después abordar US2 y US3.

### Incremental Delivery

1. Base compartida de contratos y validación.
2. Edición funcional exitosa.
3. Manejo de errores inline y no persistencia parcial.
4. 404 claro, payload vacío/incompleto sin JSON técnico y control de conflicto optimista.
5. Regresión final del alta y del listado.

### Validation Gates

- La edición debe poder abrirse desde un card real del listado.
- La edición válida debe redirigir al listado con confirmación.
- La edición inválida debe mantener el formulario con errores.
- El payload vacío/incompleto no debe exponer JSON técnico.
- La alta existente no debe perder coherencia con la validación compartida.

## Evidencia de validación

- `uv run pytest app/modules/propiedades/tests -q`: `40 passed`
