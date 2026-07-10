# Plan de Implementación: 004-propiedades-base

**Rama**: `004-propiedades-base` | **Fecha**: 2026-07-09 | **Especificación**: [spec.md](spec.md)

**Entrada**: Especificación de funcionalidad desde `specs/004-propiedades-base/spec.md`

## Resumen técnico

La feature introduce el dominio fundacional de propiedades como un vertical slice backend-only, sin rutas HTTP ni UI. El trabajo se divide en cuatro bloques técnicos: (1) crear el slice `app/modules/propiedades/` con modelo, repositorio, servicio y pruebas del dominio; (2) agregar una migración estructural que materialice la tabla `propiedades` y el enum `estado_propiedad` exactamente una vez; (3) agregar una migración de seed idempotente con 10 propiedades de Miami usando upsert por clave compuesta y URLs de imagen deterministas; (4) validar calidad, reversibilidad y operación segura de Alembic sin `stamp`, sin psycopg y sin errores de timezone.

## Contexto técnico

**Lenguaje/versión**: Python 3.13+, gestionado con `uv`

**Dependencias principales**: SQLAlchemy 2.x async, asyncpg, Alembic, FastAPI, Pydantic v2, pytest, pytest-asyncio, httpx.AsyncClient, Ruff, mypy

**Almacenamiento**: PostgreSQL (Supabase). Runtime con `DATABASE_URL` al pooler 6543; migraciones con `DATABASE_URL_DIRECT` a 5432; SSL obligatorio

**Pruebas**: pytest, pytest-asyncio, httpx.AsyncClient, validaciones de migración Alembic y comprobaciones estáticas de seed/modelo

**Plataforma objetivo**: Monolito Python desplegado sobre servidor Linux con PostgreSQL gestionado externamente

**Tipo de proyecto**: Aplicación web monolítica server-rendered con vertical slices por módulo

**Objetivos de rendimiento**: Seed idempotente de 10 registros con ejecución repetible y sin degradación funcional; consultas base sobre ciudad y estado optimizadas mediante índices

**Restricciones**:
- Sin endpoints HTTP, sin templates y sin cambios visibles en dashboard
- Sin cambios de tokens visuales ni activos VTG
- Sin `alembic stamp`
- Sin psycopg2/psycopg
- Timestamps server-side exclusivamente
- Enum `estado_propiedad` materializado una sola vez por migración estructural

**Escala/alcance**: 1 módulo backend nuevo (`propiedades`), 2 migraciones Alembic nuevas, 3 suites de pruebas del módulo, 10 registros seed versionados

## Constitution Check

**Gate previo a investigación: PASS**

| Principio | Estado | Observación |
|-----------|--------|-------------|
| I. Solución Única y Compartida | PASS | La feature amplía el monolito existente; no introduce servicios paralelos |
| II. Spec-Driven Development | PASS | Todo el alcance deriva de FR-001 a FR-029 y SC-001 a SC-010 |
| III. Vertical Slice Architecture | PASS | El diseño crea `app/modules/propiedades/` respetando el patrón del proyecto |
| IV. Stack Tecnológico Obligatorio | PASS | Solo usa `uv`, SQLAlchemy async, asyncpg y Alembic |
| V. Calidad de Dominio y Contratos | PASS | Sin exposición directa de entidades; la lógica vive en `service.py` |
| VI. Idioma y Documentación | PASS | Artefactos de planificación 100 % en español |
| VII. Async-First | PASS | Repositorio y scripts auxiliares planeados sobre `AsyncSession`/engine async |

**Re-check post diseño: PASS**

No se detectan violaciones nuevas tras cerrar el diseño. El plan no requiere excepciones ni justificaciones en Complexity Tracking.

## Decisiones de diseño

1. **Slice backend dedicado `app/modules/propiedades/` sin superficie HTTP en esta fase**
   - Se crearán `models.py`, `repository.py`, `service.py` y `tests/` dentro del slice; `routes.py`, `schemas.py` y `templates/` existirán como artefactos estructurales mínimos pero no expondrán endpoints ni UI.
   - **Traza**: FR-001, FR-012, FR-023, FR-024, FR-026, SC-010.

2. **Modelo `Propiedad` con SQLAlchemy 2.x moderno y nombres en español**
   - La entidad usará `Mapped[...]` + `mapped_column`, tabla `propiedades`, `id` UUID con `server_default=gen_random_uuid()`, campos numéricos exactos para precio/baños/área y timestamps `DateTime(timezone=True)` con `server_default=now()`.
   - **Traza**: FR-002, FR-009, FR-020, FR-021, FR-023, SC-005.

3. **`EstadoPropiedad` como StrEnum + `sa.Enum` tipado en base**
   - El catálogo cerrado se definirá en Python y se persistirá como tipo `estado_propiedad` con valores `disponible`, `rentada`, `mantenimiento`, `inactiva`.
   - **Traza**: FR-003, FR-004, FR-013, FR-021, SC-003, SC-008.

4. **Identidad de negocio compuesta y operación de seed por upsert**
   - La tabla tendrá `UniqueConstraint(titulo, direccion, ciudad)`. El seed ejecutará `ON CONFLICT (titulo, direccion, ciudad) DO UPDATE SET ...` para mantener cardinalidad estable y actualización in-place.
   - **Traza**: FR-005, FR-006, FR-007, FR-018, SC-002, SC-010.

5. **Imagen determinista por UUID fijo versionado**
   - Cada registro de seed tendrá un UUID estable versionado en migración y `imagen_url = https://picsum.photos/seed/{id}/800/500`.
   - **Traza**: FR-008, FR-028, SC-003, SC-007.

6. **Migración estructural separada de migración de seed**
   - `0002_create_propiedades.py` creará tabla, constraints, índices y enum. `0003_seed_propiedades_miami.py` sembrará los datos y tendrá downgrade real por borrado de IDs sembrados.
   - **Traza**: FR-010, FR-011, FR-013, FR-017, FR-018, SC-001, SC-004, SC-008.

7. **SQL parametrizado de Alembic con bind explícito y cast seguro**
   - Toda ejecución SQL de seed y downgrade usará `op.get_bind().execute(sa.text(...), params)` y casteos `CAST(:param AS uuid)` / `CAST(:ids AS uuid[])`.
   - **Traza**: FR-014, FR-015, FR-017, SC-001, SC-004.

8. **Política explícita de recuperación ante drift de historial**
   - El plan documenta que la única recuperación válida ante historial inconsistente es reset del esquema `public` y `alembic upgrade head`; queda prohibido `stamp`.
   - **Traza**: FR-017, SC-001, SC-004.

9. **Pruebas del dominio centradas en reglas, migraciones y seed**
   - Se cubrirán modelo, seed y cadena de migraciones con pruebas del módulo y comandos de validación de Alembic/Ruff/mypy.
   - **Traza**: FR-027, SC-001, SC-002, SC-004, SC-005, SC-006, SC-009.

## Módulos y archivos afectados

### Documentación (esta feature)

```text
specs/004-propiedades-base/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md                  # Se crea en /speckit.tasks, no en esta fase
```

### Código fuente y base de datos

```text
app/
├── database.py                              # Referencia de engine async existente
└── modules/
    └── propiedades/
        ├── __init__.py
        ├── models.py
        ├── repository.py
        ├── service.py
        ├── routes.py                        # Sin endpoints funcionales en esta spec
        ├── schemas.py                       # DTOs mínimos/placeholder estructural
        ├── templates/                       # Sin vistas funcionales en esta spec
        └── tests/
            ├── test_models.py
            ├── test_seed_rules.py
            └── test_migrations_propiedades.py

alembic/
├── env.py                                   # Ya usa DATABASE_URL_DIRECT async
├── script.py.mako                           # Debe quedar versionado antes de nuevas revisiones
└── versions/
    ├── 20260708_baseline.py
    ├── 0002_create_propiedades.py
    └── 0003_seed_propiedades_miami.py
```

**Decisión estructural**: Se mantiene un único proyecto Python con vertical slice backend en `app/modules/propiedades/`. No se introduce `contracts/` porque la feature no expone interfaces externas; su contrato es interno entre modelo, repositorio, servicio y migraciones.

## Plan de migraciones Alembic

### Migración 0002: creación estructural

- Nombre propuesto: `0002_create_propiedades.py`
- Objetivo: crear tabla `propiedades`, tipo enum `estado_propiedad`, constraints e índices operativos.
- Contenido esperado:
  - `id` UUID con `server_default=gen_random_uuid()`.
  - `titulo`, `direccion`, `ciudad`, `imagen_url` como texto requerido.
  - `precio_mensual` `Numeric(12, 2)`.
  - `habitaciones` entero.
  - `banos` `Numeric(4, 1)`.
  - `area_m2` `Numeric(10, 2)`.
  - `estado` con `sa.Enum(..., name="estado_propiedad")`.
  - `created_at`, `updated_at` como `DateTime(timezone=True)` con `server_default=now()`.
  - `PrimaryKeyConstraint(id)`.
  - `UniqueConstraint(titulo, direccion, ciudad)`.
  - `Index(ciudad)` y `Index(estado)`.
- Regla crítica de enum:
  - El tipo `estado_propiedad` se materializa una sola vez mediante el DDL implícito de `create_table`.
  - Si se reutiliza una instancia separada de `sa.Enum` en la firma de tabla o downgrade, la secundaria DEBE declararse con `create_type=False`.
- Downgrade requerido:
  - `drop_index` de estado.
  - `drop_index` de ciudad.
  - `drop_table("propiedades")`.
  - `DROP TYPE IF EXISTS estado_propiedad`.

### Migración 0003: seed idempotente

- Nombre propuesto: `0003_seed_propiedades_miami.py`
- Objetivo: sembrar 10 propiedades de Miami usando UUID fijo por registro y actualización idempotente por clave de negocio.
- Contenido esperado:
  - Lista versionada de 10 registros con `id` fijo, ciudad `Miami`, datos funcionales y `imagen_url` determinista.
  - SQL con `INSERT ... ON CONFLICT (titulo, direccion, ciudad) DO UPDATE SET ...`.
  - `updated_at = now()` solo en la rama `DO UPDATE`.
  - Sin `created_at` ni `updated_at` enviados desde Python.
  - Ejecución vía `op.get_bind().execute(sa.text(...), params)`.
  - Casteos de UUID con `CAST(:param AS uuid)` y borrado por arreglo con `CAST(:ids AS uuid[])`.
- Downgrade requerido:
  - `DELETE FROM propiedades WHERE id = ANY(CAST(:ids AS uuid[]))` parametrizado.

### Operación segura

- Antes de generar nuevas revisiones, `alembic/script.py.mako` debe estar presente y versionado.
- Recuperación ante drift del historial:
  - `DROP SCHEMA public CASCADE;`
  - `CREATE SCHEMA public;`
  - `uv run alembic upgrade head`
- Queda explícitamente prohibido `alembic stamp`.

## Estrategia de repositorio y servicio

### repository.py

- API asíncrona con `session: AsyncSession` como primer parámetro.
- Operaciones previstas:
  - obtener propiedad por identidad compuesta.
  - listar propiedades por ciudad y/o estado.
  - persistir actualización funcional del seed si se reutiliza desde servicio.
- Estilo obligatorio:
  - `select()` + `await session.execute(stmt)`.
  - `scalar_one_or_none()` para una entidad.
  - `scalars().all()` para colecciones.
  - Sin `session.query()`.

### service.py

- Lógica exclusiva del dominio:
  - normalización de identidad de negocio.
  - construcción determinista de `imagen_url`.
  - validación del catálogo `EstadoPropiedad`.
  - preparación del set inicial si se reutiliza fuera de migraciones.
- Sin acceso directo a SQL bruto ni engine.

## Estrategia de pruebas

### app/modules/propiedades/tests/test_models.py

- Valida que `Propiedad` declara todos los campos requeridos.
- Valida que `EstadoPropiedad` contiene exactamente cuatro valores.
- Valida metadata crítica: uniqueness compuesta e índices declarados.

### app/modules/propiedades/tests/test_seed_rules.py

- Valida que la imagen cumple exactamente `https://picsum.photos/seed/{id}/800/500`.
- Valida que el seed contiene 10 registros de Miami.
- Valida que la URL de imagen se deriva del `id` parametrizado y no de valores aleatorios.

### app/modules/propiedades/tests/test_migrations_propiedades.py

- Valida que `0003` depende de `0002`.
- Valida que el seed contiene `ON CONFLICT (titulo, direccion, ciudad) DO UPDATE SET`.
- Valida que no se envía `created_at` desde Python.
- Valida que `updated_at = now()` aparece en la rama de conflicto.
- Valida que el upgrade completo no cae por errores naive/aware.

## Calidad y validaciones

Comandos de salida obligatorios:

```powershell
uv run ruff check .
uv run mypy --strict app/modules/propiedades
uv run pytest app/modules/propiedades/tests -q
uv run alembic upgrade head
uv run alembic downgrade -2
uv run alembic upgrade head
```

Validaciones adicionales del plan:

- Verificar que `alembic/script.py.mako` existe antes de generar `0002` y `0003`.
- Verificar que ninguna ruta de mantenimiento de DB depende de psycopg2/psycopg.
- Confirmar que el seed deja exactamente 10 registros tras dos ejecuciones consecutivas.

## Riesgos técnicos y mitigaciones

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Doble creación del tipo enum | Falla de migración en upgrade | Materializar enum una sola vez vía `create_table`; cualquier `sa.Enum` secundario con `create_type=False` |
| `op.execute(sql, params)` con dict | TypeError en ejecución | Usar `op.get_bind().execute(sa.text(...), {...})` |
| `:param::uuid` rompe parser de `sa.text` | Falla de seed o downgrade | Usar `CAST(:param AS uuid)` |
| Historial Alembic inconsistente | Bloqueo operativo | Reset de `public` y `upgrade head`; prohibido `stamp` |
| Drift de imagen entre ejecuciones | Datos no reproducibles | Derivar `imagen_url` determinísticamente del UUID fijo |
| Error naive/aware en timestamps | Falla de migración o validación | Timestamps server-side y sin fechas enviadas desde Python |

## Plan por fases

### Fase 0 — Preparación y guardrails

- Confirmar presencia/versionado de `alembic/script.py.mako`.
- Crear estructura del slice `app/modules/propiedades/`.
- Registrar `EstadoPropiedad` y contratos del modelo en `data-model.md`.

### Fase 1 — Estructura persistente

- Implementar `models.py` con `Propiedad` y `EstadoPropiedad`.
- Crear migración `0002_create_propiedades.py` con tabla, enum, índices y constraints.
- Asegurar downgrade real y materialización única del enum.

### Fase 2 — Seed y lógica del dominio

- Implementar helpers/servicio para identidad e imagen determinista.
- Crear `0003_seed_propiedades_miami.py` con 10 registros, UUID fijos y upsert.
- Asegurar downgrade por IDs y operación repetible.

### Fase 3 — Pruebas y calidad

- Escribir `test_models.py`, `test_seed_rules.py`, `test_migrations_propiedades.py`.
- Ejecutar Ruff, mypy y pytest del módulo.
- Ejecutar upgrade/downgrade/upgrade sobre base limpia.

### Fase 4 — Validación operativa final

- Validar cardinalidad estable de 10 propiedades tras doble seed.
- Validar ausencia de errores de timezone.
- Documentar comandos y recuperación segura en `quickstart.md`.

## Trazabilidad explícita

| Decisión | FR(s) | SC(s) |
|----------|-------|-------|
| Crear slice `app/modules/propiedades/` sin superficie HTTP | FR-001, FR-012, FR-023, FR-024, FR-026 | SC-010 |
| Modelar `Propiedad` con SQLAlchemy moderno y timestamps server-side | FR-002, FR-009, FR-020 | SC-005 |
| Definir `EstadoPropiedad` como StrEnum + `sa.Enum` tipado | FR-003, FR-004, FR-013, FR-021 | SC-003, SC-008 |
| Usar identidad compuesta + `ON CONFLICT DO UPDATE` | FR-005, FR-006, FR-007, FR-018 | SC-002 |
| Derivar `imagen_url` determinista por UUID fijo | FR-008, FR-028 | SC-003, SC-007 |
| Separar migración estructural y seed con downgrade real | FR-010, FR-011, FR-017, FR-018 | SC-001, SC-004 |
| Ejecutar SQL con bind explícito y casts `CAST()` | FR-014, FR-015 | SC-001, SC-004 |
| Prohibir `stamp` y documentar reset de `public` | FR-017 | SC-001, SC-004 |
| Cubrir el módulo con Ruff, mypy y pytest específico | FR-027 | SC-006, SC-009 |
| Preservar VTG sin cambios visuales | FR-029 | SC-010 |

## Complexity Tracking

No aplica. La Constitution Check previa y posterior al diseño permanece en PASS y no hay violaciones que requieran justificación.
