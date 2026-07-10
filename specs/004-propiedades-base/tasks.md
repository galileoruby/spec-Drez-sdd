# Tareas: 004-propiedades-base

**Entrada**: Artefactos de diseño desde `specs/004-propiedades-base/`

**Prerrequisitos**: plan.md (requerido), spec.md (requerido), research.md, data-model.md, quickstart.md

**Pruebas**: Obligatorios por definición del plan. Se incluyen pruebas de modelo, seed, migraciones, Ruff, mypy y validación Alembic.

**Organización**: Las tareas se agrupan por historia de usuario y, dentro de cada una, por `modelo`, `migración`, `seed` y `pruebas` para mantener trazabilidad técnica completa sin romper la entrega incremental.

## Formato: `[ID] [P?] [Story] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias de tareas incompletas)
- **[Story]**: Historia de usuario a la que pertenece la tarea (`US1`, `US2`, `US3`)
- Todas las tareas incluyen ruta exacta del archivo

---

## Fase 1: Preparación (Infraestructura compartida)

**Propósito**: Preparar el slice y los prerrequisitos de Alembic antes de tocar modelo, migraciones o seed.

- [X] T001 Crear la estructura base del slice `app/modules/propiedades/` con `__init__.py`, `routes.py`, `schemas.py`, `models.py`, `repository.py`, `service.py`, `templates/` y `tests/`
  Dependencias: ninguna.
  Completado cuando: existen todas las rutas del slice y el árbol respeta la arquitectura vertical definida en FR-023.

- [X] T002 Verificar y versionar `alembic/script.py.mako` en `alembic/script.py.mako` antes de generar nuevas revisiones
  Dependencias: ninguna.
  Completado cuando: `alembic/script.py.mako` existe en el repositorio y queda listo para sustentar `0002_create_propiedades.py` y `0003_seed_propiedades_miami.py` conforme a FR-016.

- [X] T003 [P] Documentar el procedimiento operativo de recuperación segura en `specs/004-propiedades-base/quickstart.md` alineado con reset de `public` + `alembic upgrade head`
  Dependencias: ninguna.
  Completado cuando: `quickstart.md` deja explícitamente prohibido `alembic stamp` y documenta el flujo de recuperación exigido por FR-017.

**Checkpoint**: Base de trabajo lista; ya se puede iniciar el bloque fundacional.

---

## Fase 2: Fundacional (Prerrequisitos bloqueantes)

**Propósito**: Establecer contratos comunes del dominio y las reglas que bloquean toda la feature.

**⚠️ CRÍTICO**: Ninguna historia puede completarse sin cerrar antes este bloque.

- [X] T004 Definir `EstadoPropiedad` como `StrEnum` y los contratos comunes del dominio en `app/modules/propiedades/models.py`
  Dependencias: T001.
  Completado cuando: el enum contiene exactamente `disponible`, `rentada`, `mantenimiento`, `inactiva`, usa nombres en español y queda listo para materializar `estado_propiedad` en DB según FR-003, FR-021.

- [X] T005 [P] Implementar utilidades puras de identidad de negocio e imagen determinista en `app/modules/propiedades/service.py`
  Dependencias: T001.
  Completado cuando: existe lógica pura para normalizar `(titulo, direccion, ciudad)` y construir `https://picsum.photos/seed/{id}/800/500` sin acceso directo a DB, trazando FR-005, FR-008, FR-024.

- [X] T006 [P] Crear el esqueleto del repositorio async en `app/modules/propiedades/repository.py` con firmas que reciban `session: AsyncSession` como primer parámetro
  Dependencias: T001.
  Completado cuando: el repositorio define la interfaz mínima para obtener por identidad compuesta y listar por filtros sin usar `session.query()`, cumpliendo FR-020, FR-024, FR-026.

**Checkpoint**: Contratos de dominio fijados; las historias pueden avanzar de forma incremental.

---

## Fase 3: User Story 1 - Modelo persistente de propiedades (Prioridad: P1) 🎯 MVP

**Objetivo**: Entregar el modelo fundacional y la migración estructural de `propiedades` con enum, constraints, índices y timestamps server-side.

**Prueba independiente**: Ejecutar `uv run alembic upgrade head` sobre base limpia y validar que existe la tabla `propiedades`, el enum `estado_propiedad`, la restricción única compuesta y los índices por `ciudad` y `estado`.

### Modelo

- [X] T007 [US1] Implementar la entidad `Propiedad` en `app/modules/propiedades/models.py` con `Mapped[...]`, `mapped_column`, `gen_random_uuid()`, `DateTime(timezone=True)` y nombres snake_case en español
  Dependencias: T004.
  Completado cuando: `Propiedad` declara todos los campos de FR-002, usa `Base` de `app/database.py` y no contiene estilo legacy.

- [X] T008 [P] [US1] Añadir constraints e índices operativos de `Propiedad` en `app/modules/propiedades/models.py` (`UniqueConstraint(titulo, direccion, ciudad)`, índice por `ciudad`, índice por `estado`)
  Dependencias: T007.
  Completado cuando: la metadata del modelo refleja la identidad compuesta y los índices previstos en `data-model.md` y FR-005.

### Migración

- [X] T009 [US1] Crear `alembic/versions/0002_create_propiedades.py` con tabla `propiedades`, enum `estado_propiedad`, PK, unique compuesta e índices operativos
  Dependencias: T002, T007, T008.
  Completado cuando: la migración crea la estructura completa y el enum se materializa exactamente una vez por DDL implícito de tabla, sin llamadas redundantes a creación de tipo, cumpliendo FR-013.

- [X] T010 [US1] Implementar el `downgrade()` real en `alembic/versions/0002_create_propiedades.py` con `drop_index`, `drop_table` y `DROP TYPE IF EXISTS estado_propiedad`
  Dependencias: T009.
  Completado cuando: la migración estructural es reversible de verdad y no deja `pass`, cumpliendo FR-011 y SC-004.

### Pruebas

- [X] T011 [P] [US1] Crear `app/modules/propiedades/tests/test_models.py` para validar campos requeridos, catálogo cerrado e índices/constraint del modelo
  Dependencias: T007, T008.
  Completado cuando: la prueba falla si falta un campo obligatorio, si el enum contiene valores no permitidos o si desaparece la unique compuesta.

- [X] T012 [US1] Añadir validaciones de cadena de revisiones y materialización única del enum en `app/modules/propiedades/tests/test_migrations_propiedades.py`
  Dependencias: T009, T010.
  Completado cuando: la prueba falla si `0002` no crea correctamente la estructura o si reaparece el riesgo de doble creación del tipo.

**Checkpoint**: El dominio persistente existe y puede levantarse en una base limpia sin tocar seed todavía.

---

## Fase 4: User Story 2 - Seed idempotente de 10 propiedades de Miami (Prioridad: P2)

**Objetivo**: Entregar la carga inicial versionada de 10 propiedades con identidad de negocio estable, upsert idempotente y `imagen_url` determinista.

**Prueba independiente**: Ejecutar el seed dos veces consecutivas y comprobar que siguen existiendo exactamente 10 propiedades de Miami, sin duplicados y con imágenes derivadas del `id`.

### Seed

- [X] T013 [US2] Crear el set canónico de 10 propiedades de Miami con UUID fijo y campos funcionales completos en `alembic/versions/0003_seed_propiedades_miami.py`
  Dependencias: T005, T009.
  Completado cuando: la migración declara exactamente 10 registros versionados con `ciudad = 'Miami'`, `estado` válido e `imagen_url` pendiente de upsert, cumpliendo FR-006.

- [X] T014 [US2] Implementar el `INSERT ... ON CONFLICT (titulo, direccion, ciudad) DO UPDATE SET ...` en `alembic/versions/0003_seed_propiedades_miami.py` usando `op.get_bind().execute(sa.text(...), params)`
  Dependencias: T013.
  Completado cuando: el seed es idempotente por clave de negocio, actualiza en sitio y no usa `op.execute(sql, params)`, cumpliendo FR-007, FR-014, FR-018.

- [X] T015 [US2] Incorporar casts seguros `CAST(:param AS uuid)` y política de timestamps server-side en `alembic/versions/0003_seed_propiedades_miami.py`
  Dependencias: T014.
  Completado cuando: la migración no envía `created_at` desde Python, usa `updated_at = now()` solo en la rama `DO UPDATE` y evita `:param::uuid`, cumpliendo FR-015, FR-019.

- [X] T016 [US2] Implementar el `downgrade()` del seed en `alembic/versions/0003_seed_propiedades_miami.py` borrando por lista de IDs con `CAST(:ids AS uuid[])`
  Dependencias: T015.
  Completado cuando: el seed puede revertirse sin residuos y con borrado parametrizado seguro, cumpliendo FR-011, SC-004.

### Pruebas

- [X] T017 [P] [US2] Crear `app/modules/propiedades/tests/test_seed_rules.py` para validar formato exacto de `imagen_url`, cardinalidad de 10 registros y parametrización por `id`
  Dependencias: T005, T013, T014, T015.
  Completado cuando: la prueba falla si la URL no es `https://picsum.photos/seed/{id}/800/500`, si el seed no contiene 10 registros o si la ciudad deja de ser Miami.

- [X] T018 [US2] Extender `app/modules/propiedades/tests/test_migrations_propiedades.py` para validar `ON CONFLICT`, ausencia de `created_at` desde Python y `updated_at = now()`
  Dependencias: T014, T015, T016.
  Completado cuando: la prueba falla si desaparece el upsert por clave compuesta o si los timestamps dejan de seguir la política server-side.

**Checkpoint**: El seed se puede ejecutar repetidamente sin duplicar datos y mantiene el contrato funcional del dominio.

---

## Fase 5: User Story 3 - Reversibilidad, operación segura y gobernanza técnica (Prioridad: P3)

**Objetivo**: Asegurar que el módulo y las migraciones son reversibles, seguras frente a timezone y conformes con Ruff, mypy, pytest y la política operativa del proyecto.

**Prueba independiente**: Ejecutar Ruff, mypy, pytest del módulo y el ciclo `alembic downgrade -2` + `alembic upgrade head` sin errores ni residuos.

### Migración

- [X] T019 [US3] Verificar en `alembic/versions/0002_create_propiedades.py` y `alembic/versions/0003_seed_propiedades_miami.py` que ambos `downgrade()` son reales y el orden de dependencia es `0002 -> 0003`
  Dependencias: T010, T016.
  Completado cuando: las dos migraciones son reversibles, `0003` depende de `0002` y el historial puede recorrerse hacia atrás sin `stamp`.

### Pruebas

- [X] T020 [US3] Completar `app/modules/propiedades/tests/test_migrations_propiedades.py` con validación explícita del upgrade completo sin error naive/aware
  Dependencias: T012, T018, T019.
  Completado cuando: la prueba falla si aparece mezcla de fechas naive/aware o si el ciclo de migraciones deja de ser seguro.

- [X] T021 [P] [US3] Crear o ajustar `app/modules/propiedades/routes.py` y `app/modules/propiedades/schemas.py` como placeholders estructurales sin endpoints ni DTOs funcionales fuera de alcance
  Dependencias: T001.
  Completado cuando: el slice cumple la forma estructural requerida por FR-023 sin introducir features HTTP no declaradas.

- [X] T022 [P] [US3] Ejecutar `uv run ruff check .` y corregir hallazgos del alcance en `app/modules/propiedades/`, `alembic/versions/` y pruebas asociadas
  Dependencias: T007, T009, T016, T020, T021.
  Completado cuando: Ruff queda en verde y no persisten hallazgos atribuibles a la feature, cumpliendo FR-027 y SC-009.

- [X] T023 [P] [US3] Ejecutar `uv run mypy --strict app/modules/propiedades` y corregir tipado en `models.py`, `repository.py`, `service.py` y pruebas si aplica
  Dependencias: T006, T007, T021.
  Completado cuando: mypy queda en verde para el módulo `propiedades`, cumpliendo SC-006.

- [X] T024 [US3] Ejecutar `uv run pytest app/modules/propiedades/tests -q` y corregir defectos locales hasta dejar el suite del módulo en verde
  Dependencias: T011, T017, T020, T022, T023.
  Completado cuando: todas las pruebas del módulo pasan y cubren modelo, seed y migraciones según el plan.

**Checkpoint**: El módulo cumple gobernanza técnica, reversibilidad y calidad estática/dinámica.

---

## Fase 6: Pulido y concerns transversales

**Propósito**: Validar operación completa sobre una base limpia y dejar evidencia de cierre técnica.

- [X] T025 Ejecutar `uv run alembic upgrade head` sobre esquema `public` recién creado y registrar el resultado en `specs/004-propiedades-base/quickstart.md`
  Dependencias: T019, T024.
  Completado cuando: el upgrade completo finaliza en verde sin intervención manual y queda documentado contra SC-001.

- [X] T026 Ejecutar `uv run alembic downgrade -2` seguido de `uv run alembic upgrade head` y registrar el ciclo de reversibilidad en `specs/004-propiedades-base/quickstart.md`
  Dependencias: T025.
  Completado cuando: el ciclo downgrade/upgrade termina sin residuos ni errores, cumpliendo SC-004.

- [X] T027 [P] Verificar cardinalidad estable de 10 propiedades y ausencia de duplicados tras doble ejecución del seed; documentar evidencia en `specs/004-propiedades-base/quickstart.md`
  Dependencias: T025, T026.
  Completado cuando: la evidencia confirma 10 registros exactos de Miami después de dos ejecuciones consecutivas, cumpliendo SC-002.

- [X] T028 [P] Actualizar el checklist de cierre en `specs/004-propiedades-base/quickstart.md` marcando cada ítem completado `[x]`
  Dependencias: T025, T026, T027.
  Completado cuando: todos los ítems del checklist final quedan en `[x]` y el quickstart refleja el estado real de validación.

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Setup (Phase 1)**: sin dependencias, inicia de inmediato.
- **Foundational (Phase 2)**: depende de Setup y bloquea el resto.
- **US1 Modelo (Phase 3)**: depende de Foundational y entrega el MVP estructural.
- **US2 Seed (Phase 4)**: depende de la migración estructural de US1.
- **US3 Pruebas y gobernanza (Phase 5)**: depende de US1 y US2.
- **Polish (Phase 6)**: depende de todas las fases anteriores.

### Dependencias entre historias de usuario

- **US1 (P1)**: puede completarse independientemente y habilita la base persistente del dominio.
- **US2 (P2)**: depende de US1 porque requiere tabla, enum y unique compuesta ya materializados.
- **US3 (P3)**: depende de US1 y US2 porque valida reversibilidad y calidad sobre la cadena completa de migraciones.

### Dependencias por grupo solicitado

- **Modelo**: T004 → T007 → T008 → T011.
- **Migración**: T002 → T009 → T010 → T019 → T025 → T026.
- **Seed**: T005 → T013 → T014 → T015 → T016 → T017 → T018 → T027.
- **Pruebas**: T011, T012, T017, T018, T020, T022, T023, T024, T028.

### Oportunidades de paralelismo

- T003 puede ejecutarse en paralelo con T001 y T002.
- T005 y T006 pueden ejecutarse en paralelo tras T001.
- T008 y T011 pueden avanzar en paralelo después de T007.
- T017 y la parte de assertions de T018 pueden desarrollarse en paralelo tras cerrar el seed.
- T022 y T023 pueden ejecutarse en paralelo cuando el código del módulo esté estable.
- T027 y T028 pueden correr en paralelo después de validar el ciclo Alembic.

---

## Ejemplo de paralelismo: User Story 1

```text
T008 [US1] Añadir constraints e índices operativos en app/modules/propiedades/models.py
T011 [US1] Crear app/modules/propiedades/tests/test_models.py
```

## Ejemplo de paralelismo: User Story 3

```text
T022 [US3] Ejecutar uv run ruff check . y corregir hallazgos del alcance
T023 [US3] Ejecutar uv run mypy --strict app/modules/propiedades y corregir tipado
```

---

## Estrategia de implementación

### MVP primero (solo User Story 1)

1. Completar Setup.
2. Completar Foundational.
3. Completar US1 (`modelo` + `migración` estructural + pruebas mínimas).
4. **STOP y VALIDAR**: `uv run alembic upgrade head` debe crear la estructura completa en base limpia.

### Entrega incremental

1. Añadir la estructura persistente del dominio (US1).
2. Añadir el seed idempotente y sus garantías (US2).
3. Cerrar reversibilidad, mypy, Ruff y pytest del módulo (US3).
4. Ejecutar validación operativa final y checklist de quickstart.

### Definición de terminado de la feature

1. El slice `app/modules/propiedades/` existe y respeta la forma del proyecto.
2. Las migraciones `0002` y `0003` son reversibles reales.
3. El seed deja exactamente 10 propiedades de Miami tras dos ejecuciones.
4. Ruff, mypy y pytest del módulo pasan.
5. `quickstart.md` contiene evidencia de upgrade/downgrade/upgrade y checklist final en `[x]`.