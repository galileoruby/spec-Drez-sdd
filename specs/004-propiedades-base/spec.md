# Feature Specification: Propiedades Base Persistentes

**Feature Branch**: `[004-propiedades-base]`

**Created**: 2026-07-09

**Status**: Draft

**Input**: User description: "Habilitar una base persistente de propiedades inmobiliarias con seed idempotente de 10 propiedades de Miami, catálogo cerrado de estados, reversibilidad real de evoluciones y cumplimiento estricto de la gobernanza técnica heredada para que features posteriores de listado, alta, búsqueda y dashboard real operen con datos existentes."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Base fundacional de propiedades (Priority: P1)

Como responsable operativa del producto, necesito que el sistema cuente con una base persistente de propiedades residenciales para dejar de operar con datos vacíos y habilitar validaciones funcionales con información realista.

**Why this priority**: Sin una base persistente del dominio, el dashboard y las siguientes features de propiedades no pueden evolucionar sobre datos confiables.

**Independent Test**: Puede validarse aplicando la evolución estructural en una base limpia y comprobando que existe una entidad persistente de propiedades con todos los atributos mínimos y un catálogo cerrado de estados.

**Acceptance Scenarios**:

1. **Given** un entorno limpio con el esquema público recién creado, **When** se aplica la actualización completa de base de datos, **Then** queda disponible una estructura persistente de propiedades apta para alquiler residencial.
2. **Given** una propiedad nueva o actualizada, **When** se registra en la base, **Then** conserva título, dirección, ciudad, precio mensual, habitaciones, baños, área, estado, imagen y marcas temporales gestionadas por la base de datos.

---

### User Story 2 - Seed inicial repetible y sin duplicados (Priority: P2)

Como equipo de producto, necesitamos una carga inicial de 10 propiedades de Miami para probar reportes y comportamiento funcional sin intervención manual y sin duplicar registros al reejecutar la carga.

**Why this priority**: La base fundacional aporta valor inmediato cuando puede poblarse de forma repetible y consistente en cualquier entorno limpio o parcialmente inicializado.

**Independent Test**: Puede validarse ejecutando la carga inicial dos veces consecutivas y comprobando que siguen existiendo exactamente 10 propiedades de Miami, con identidad de negocio estable e imágenes reproducibles.

**Acceptance Scenarios**:

1. **Given** una base ya inicializada parcialmente, **When** se ejecuta nuevamente la carga inicial, **Then** las propiedades existentes se actualizan en sitio usando la clave de negocio y no se crean duplicados.
2. **Given** una propiedad del set inicial, **When** se consulta después de múltiples ejecuciones del seed, **Then** mantiene una imagen asociada derivada de una semilla visual estable y reproducible.

---

### User Story 3 - Evolución segura, reversible y gobernada (Priority: P3)

Como equipo de plataforma, necesitamos que las evoluciones del dominio de propiedades sean reversibles, seguras frente a zonas horarias y compatibles con la gobernanza técnica del proyecto para evitar estados inconsistentes del historial.

**Why this priority**: Una base inicial sin reversibilidad ni disciplina técnica generaría deuda operativa y bloquearía features posteriores o recuperaciones confiables.

**Independent Test**: Puede validarse completando el ciclo upgrade/downgrade/upgrade en una base limpia y confirmando ausencia de errores por timestamps, conflictos de enums, scripts no autorizados o atajos prohibidos.

**Acceptance Scenarios**:

1. **Given** una base limpia, **When** se ejecuta el ciclo completo de actualización y reversión, **Then** todas las evoluciones finalizan con éxito y el sistema puede reconstruirse de nuevo sin intervención manual.
2. **Given** una base en estado inconsistente del historial, **When** se requiere recuperación, **Then** el procedimiento permitido es reiniciar el esquema público y reaplicar la actualización completa, nunca usar atajos de marcado artificial del historial.

---

### Edge Cases

- Intentar registrar una propiedad con estado fuera del catálogo permitido.
- Ejecutar la carga inicial varias veces en entornos con datos parcialmente presentes.
- Aplicar la actualización completa en un entorno donde el esquema previo quedó en estado inconsistente.
- Alembic reporta una revisión que no existe en `alembic/versions/`.
- La materialización del catálogo de estados choca con un enum preexistente.
- Inserciones con SQL parametrizado intentan usar casteos incompatibles con UUID.
- La carga inicial se interrumpe con solo una parte del set presente.
- La carga inicial se ejecuta dos veces consecutivas sobre el mismo entorno.
- Existen diferencias de zona horaria entre datos generados por aplicación y datos gestionados por la base de datos.

## Requirements *(mandatory)*

### Functional Requirements

#### Requisitos funcionales de negocio

- **FR-001**: El sistema DEBE introducir una base persistente de propiedades inmobiliarias orientada a alquiler residencial como dominio fundacional para features posteriores.
- **FR-002**: Cada propiedad DEBE incluir como mínimo título, dirección, ciudad, precio mensual, habitaciones, baños, área, estado, imagen, marca temporal de creación y marca temporal de actualización.
- **FR-003**: El sistema DEBE manejar un catálogo cerrado de estados de propiedad con exactamente cuatro valores permitidos: `disponible`, `rentada`, `mantenimiento` e `inactiva`.
- **FR-004**: El sistema DEBE rechazar cualquier intento de persistir o cargar propiedades con estados fuera del catálogo permitido.
- **FR-005**: La identidad de negocio de cada propiedad del seed DEBE estar definida por la combinación de título, dirección y ciudad.
- **FR-006**: El sistema DEBE contar con una carga inicial repetible de exactamente 10 propiedades de prueba ubicadas en Miami, USA.
- **FR-007**: Reejecutar la carga inicial NUNCA DEBE duplicar propiedades existentes; si una propiedad ya existe por identidad de negocio, DEBE actualizarse en sitio.
- **FR-008**: El sistema DEBE asociar a cada propiedad del set inicial una imagen determinista derivada de un identificador estable de la propiedad para conservar una semilla visual reproducible entre ejecuciones.
- **FR-009**: Las marcas temporales de creación y actualización DEBEN ser gestionadas por la base de datos y la carga inicial NUNCA DEBE enviarlas desde la aplicación.
- **FR-010**: Las evoluciones del dominio DEBEN poder aplicarse en un entorno limpio en un solo paso, sin intervención manual.
- **FR-011**: Las evoluciones del dominio DEBEN ser reversibles reales y seguras frente a mezclas de fechas con y sin zona horaria.
- **FR-012**: El alcance de esta feature NO DEBE incluir endpoints HTTP, vistas, templates ni cambios visibles en el dashboard.

#### Requisitos no funcionales y de gobernanza heredada

- **FR-013**: La materialización del catálogo de estados DEBE crear cada tipo enumerado del dominio exactamente una vez por evolución estructural; está prohibido declarar una creación explícita paralela del mismo tipo sin desactivar la creación implícita correspondiente.
- **FR-014**: El SQL parametrizado dentro de migraciones DEBE ejecutarse usando la conexión enlazada de la migración y NO mediante mecanismos de ejecución no autorizados con parámetros separados.
- **FR-015**: Los casteos a UUID en SQL parametrizado DEBEN expresarse mediante `CAST(:param AS uuid)` y NO con atajos incompatibles dentro del texto SQL.
- **FR-016**: La plantilla `alembic/script.py.mako` DEBE estar versionada en el repositorio antes de generar nuevas revisiones del dominio.
- **FR-017**: Está prohibido usar `alembic stamp` como atajo ante fallos del historial; la recuperación obligatoria ante inconsistencia DEBE reiniciar el esquema `public` y reaplicar `alembic upgrade head` desde una base limpia.
- **FR-018**: El seed inicial DEBE ser idempotente por clave de negocio y materializar actualizaciones in-place cuando encuentre conflictos sobre esa identidad compuesta.
- **FR-019**: Las migraciones, el seed y cualquier script auxiliar del dominio NO DEBEN enviar `created_at` ni `updated_at` desde Python.
- **FR-020**: El modelado del dominio DEBE usar SQLAlchemy 2.x async con tipado explícito, sesiones asíncronas y estilo moderno; están prohibidos los patrones legacy y las sesiones síncronas para I/O.
- **FR-021**: Los estados del dominio DEBEN modelarse como Enum tipado del dominio; están prohibidos los strings mágicos como contrato operativo.
- **FR-022**: Todo DTO del dominio de propiedades DEBE usar Pydantic v2 con configuración inmutable (`frozen=True`).
- **FR-023**: La implementación del dominio DEBE seguir arquitectura vertical slice dentro de `app/modules/propiedades/` con `routes.py`, `schemas.py`, `models.py`, `repository.py`, `service.py`, `templates/` y `tests/`.
- **FR-024**: La lógica de negocio del dominio DEBE residir exclusivamente en `service.py`; `routes.py` DEBE permanecer delgado y `repository.py` limitado a acceso a datos.
- **FR-025**: Las entidades persistentes del dominio NO DEBEN exponerse directamente como respuestas HTTP.
- **FR-026**: Toda operación con I/O en el dominio DEBE ejecutarse con funciones asíncronas; solo se permite `def` síncrono para cómputo puro en memoria.
- **FR-027**: La calidad de salida del módulo DEBE quedar libre de hallazgos de Ruff, sin errores de `mypy --strict` y con cobertura de validación vía pytest/pytest-asyncio/httpx.AsyncClient.
- **FR-028**: Cualquier script auxiliar de mantenimiento de base de datos autorizado por esta feature DEBE usar el driver asyncpg vía engine asíncrono; está prohibido depender de psycopg2 o psycopg.
- **FR-029**: Esta feature NO DEBE modificar tokens visuales, paleta, tipografía, espaciados, radios, sombras ni ningún otro activo VTG del sistema.

## Visual Tokens Governance *(mandatory)*

- **Token Impact**: Sin cambios. Esta feature no introduce ni modifica elementos visuales del producto.
- **Explicit Authorization**: No existe autorización para cambios visuales en esta spec; cualquier desviación VTG queda fuera de alcance y debe rechazarse.
- **Task Traceability**: `tasks.md` deberá incluir únicamente verificaciones explícitas de no cambio visual y de preservación de la gobernanza VTG durante la implementación.
- **Operational Source**: `.github/instructions/frontend.instructions.md` es la fuente operativa obligatoria de definición y uso de tokens visuales, aunque esta feature no los modifica.

### Key Entities *(include if feature involves data)*

- **Propiedad**: Activo inmobiliario residencial persistente con identidad de negocio compuesta por título, dirección y ciudad; incluye atributos económicos, físicos, estado operativo, imagen determinista y marcas temporales gestionadas por la base de datos.
- **Estado de Propiedad**: Catálogo cerrado que define el ciclo operativo permitido de una propiedad y restringe los únicos valores válidos a `disponible`, `rentada`, `mantenimiento` e `inactiva`.
- **Lote Inicial de Propiedades**: Conjunto canónico de 10 propiedades de Miami usado para poblar entornos limpios o parcialmente inicializados de manera repetible, idempotente y sin duplicados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `alembic upgrade head` sobre un esquema `public` recién creado finaliza en verde en el 100 % de las ejecuciones de validación, sin intervención manual y sin uso de `stamp`.
- **SC-002**: La carga inicial deja exactamente 10 propiedades de Miami y mantiene esa misma cardinalidad después de dos ejecuciones consecutivas del seed.
- **SC-003**: El 100 % de las propiedades iniciales queda con un estado perteneciente al catálogo permitido y con una imagen asociada derivada de una semilla estable.
- **SC-004**: El ciclo completo upgrade/downgrade/upgrade finaliza con éxito en el 100 % de las ejecuciones de validación previstas para la feature.
- **SC-005**: La actualización completa de base de datos no reporta errores por mezcla de fechas naive vs aware en ninguna validación de la feature.
- **SC-006**: `mypy --strict` sobre el módulo de propiedades no reporta errores.
- **SC-007**: Ningún script auxiliar de mantenimiento de base de datos del alcance usa psycopg2 ni psycopg.
- **SC-008**: La materialización del catálogo de estados no produce conflictos por declaración duplicada al aplicar la evolución estructural.
- **SC-009**: Ruff no reporta hallazgos en el alcance del módulo de propiedades y sus artefactos asociados.
- **SC-010**: La implementación deja trazabilidad completa de todas las reglas de negocio y restricciones heredadas en `tasks.md` antes de iniciar ejecución de código.

## Assumptions

- El dominio fundacional de propiedades se implementará sobre PostgreSQL administrado por las rutas y políticas ya definidas por la constitución del proyecto.
- Las 10 propiedades iniciales de Miami serán suficientes como set de validación para las siguientes features de listado, búsqueda, alta y dashboard real sin requerir cambios visibles en esta iteración.
- La recuperación obligatoria ante historial inconsistente de migraciones podrá ejecutarse sobre un entorno de desarrollo o validación sin preservar datos previos del esquema `public`.
- La imagen determinista de cada propiedad será derivable de un identificador estable de negocio o persistencia sin requerir carga manual de archivos binarios durante el seed.
- El módulo `app/modules/propiedades/` todavía no expone endpoints ni vistas al usuario final en esta spec; la persistencia y el seed son el entregable principal.
