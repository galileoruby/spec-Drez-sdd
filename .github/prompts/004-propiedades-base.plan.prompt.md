---
name: 004-propiedades-base-plan
agent: speckit.plan
---

## Prompt para `speckit.plan.agent` — Feature: 004-propiedades-base
Genera el plan técnico para la feature 004-propiedades-base.

## Entrada
- Spec aprobada: specs/004-propiedades-base/spec.md
- Constitution: .specify/memory/constitution.md (fuente de verdad,
  prevalece ante cualquier conflicto).
- Instrucciones de stack:
  - .github/copilot-instructions.md
  - .github/instructions/backend.instructions.md
  - .github/instructions/database.instructions.md
  - .github/instructions/frontend.instructions.md (sólo para descartar:
    esta feature NO toca UI).

## Salida esperada
- plan.md ubicado en specs/004-propiedades-base/plan.md (carpeta specs/
  en la RAÍZ del repo, NUNCA bajo .specify/specs/).
- 100% en español, sin mezclar idiomas.
- Estructura oficial del template de plan.md: Resumen técnico, Contexto
  técnico, Constitution Check (gate previo y re-check post diseño),
  Decisiones de diseño, Módulos y archivos afectados, Plan de
  migraciones Alembic, Estrategia de repositorio y servicio, Estrategia
  de pruebas, Calidad y validaciones, Riesgos técnicos y mitigaciones,
  Plan por fases, Trazabilidad explícita (decisiones -> FR/SC),
  Complexity Tracking.
- Cada decisión de diseño DEBE quedar trazada a un FR o SC numerado del
  spec. Está PROHIBIDO introducir features fuera del alcance del spec.

## Contexto técnico obligatorio (heredado, no negociable)
- Language: Python 3.13+, gestionado con uv (pyproject.toml + uv.lock).
- Backend: FastAPI (no aplica a esta feature, pero respetar el monolito).
- ORM: SQLAlchemy 2.x async con Mapped[...] + mapped_column +
  AsyncSession.
- DTOs: Pydantic v2 con model_config = ConfigDict(frozen=True).
- DB: PostgreSQL (Supabase) vía asyncpg.
  - Runtime usa DATABASE_URL (pooler 6543) con statement_cache_size=0
    y prepared_statement_cache_size=0.
  - Alembic usa DATABASE_URL_DIRECT (5432).
  - SSL=require obligatorio.
- Migraciones: Alembic única herramienta.
- Tests: pytest + pytest-asyncio + httpx.AsyncClient.
- Calidad: Ruff + mypy --strict en app/modules/propiedades.
- Arquitectura: Vertical slice en app/modules/propiedades/ con
  routes.py, schemas.py, models.py, repository.py, service.py,
  templates/, tests/. Esta feature NO crea routes.py ni schemas.py ni
  templates/ (no hay HTTP/UI), pero sí mantiene la estructura del slice.

## Decisiones de diseño cerradas (NO reabrir; provienen de constitution
+ lecciones aprendidas en specs previas)

### Modelo
- Entidad Propiedad en app/modules/propiedades/models.py con
  Mapped[...] + mapped_column. PROHIBIDO el estilo legacy Column-en-clase.
- EstadoPropiedad como StrEnum en Python + sa.Enum tipado en DB,
  nombre del tipo: estado_propiedad. Valores: disponible, rentada,
  mantenimiento, inactiva.
- Campos: id (UUID, server_default gen_random_uuid()), titulo,
  direccion, ciudad, precio_mensual (Numeric 12,2), habitaciones (int),
  banos (Numeric 4,1), area_m2 (Numeric 10,2), estado, imagen_url,
  created_at, updated_at (ambos DateTime(timezone=True) con
  server_default=now()).
- Restricciones: UniqueConstraint(titulo, direccion, ciudad) +
  Index(ciudad) + Index(estado).
- Nombres en snake_case en español (constitution).

### Migración de estructura (0002_create_propiedades.py)
- El tipo enum estado_propiedad se materializa EXACTAMENTE UNA VEZ vía
  el DDL implícito de create_table. La columna declara el sa.Enum y
  EL OTRO sa.Enum usado en la firma de la tabla DEBE llevar
  create_type=False. PROHIBIDO llamar Enum.create() además de
  declararlo en la columna sin create_type=False.
- create_table incluye PrimaryKeyConstraint(id), UniqueConstraint
  compuesta e índices operativos.
- downgrade real: drop_index x2, drop_table, DROP TYPE IF EXISTS
  estado_propiedad. PROHIBIDO downgrade vacío.

### Migración de seed (0003_seed_propiedades_miami.py)
- 10 registros de Miami con id UUID fijo por registro (datos versionados).
- Upsert por clave compuesta: ON CONFLICT (titulo, direccion, ciudad)
  DO UPDATE SET ... actualizando campos funcionales + updated_at=now().
- SQL parametrizado usando op.get_bind().execute(sa.text("..."), {...}).
  PROHIBIDO op.execute(sql, params).
- Casteos a UUID con CAST(:param AS uuid). PROHIBIDO :param::uuid en
  sa.text.
- NO enviar created_at desde Python. updated_at solo en la rama DO UPDATE
  vía now() server-side.
- imagen_url determinista: https://picsum.photos/seed/{id}/800/500.
- downgrade real: DELETE por lista de IDs sembrados, parametrizada
  con CAST(:ids AS uuid[]).

### Operación de migraciones
- alembic/script.py.mako DEBE estar versionado en el repo antes de
  generar nuevas revisiones.
- PROHIBIDO usar `alembic stamp` como atajo ante fallos. Ante estado
  inconsistente del historial: DROP SCHEMA public CASCADE; CREATE
  SCHEMA public; reaplicar `alembic upgrade head` desde base limpia.
- Todo script auxiliar de mantenimiento de DB DEBE usar asyncpg vía
  create_async_engine. PROHIBIDO depender de psycopg2/psycopg.

### Repositorio y servicio
- repository.py: funciones async con primer parámetro
  session: AsyncSession. Usa select() + await session.execute().
  Para uno: .scalar_one_or_none(). Para muchos: .scalars().all().
  PROHIBIDO session.query().
- service.py: contiene la lógica de negocio (normalización de
  identidad, política de seed idempotente, construcción de
  imagen_url determinista). Sin acceso directo a DB.
- Sin endpoints, sin schemas Pydantic, sin templates en esta feature
  (FR-013 del spec).

### Tests obligatorios
- app/modules/propiedades/tests/test_models.py
  - Valida campos requeridos.
  - Valida catálogo cerrado de EstadoPropiedad.
- app/modules/propiedades/tests/test_seed_rules.py
  - Valida formato exacto de imagen_url
    (https://picsum.photos/seed/{id}/800/500).
  - Valida que el script de seed contenga 10 registros de Miami.
  - Valida que el script use la URL parametrizada por id.
- app/modules/propiedades/tests/test_migrations_propiedades.py
  - Valida cadena de revisiones: 0003 depende de 0002.
  - Valida que el seed declare ON CONFLICT (titulo, direccion, ciudad)
    DO UPDATE SET.
  - Valida que el seed NO envíe created_at desde Python y SÍ use
    updated_at = now() en DO UPDATE.
  - Validación explícita de timezone: el upgrade completo no produce
    error naive/aware.

### Calidad
- uv run ruff check .
- uv run mypy --strict app/modules/propiedades
- uv run pytest app/modules/propiedades/tests -q
- uv run alembic upgrade head sobre `public` recién creado finaliza
  en verde en un solo paso.
- uv run alembic downgrade -2 + uv run alembic upgrade head reversible
  sin residuos.

## Riesgos y mitigaciones obligatorias
- Riesgo: conflicto por doble creación del tipo enum.
  Mitigación: enum se materializa solo vía create_table; segundo
  sa.Enum con create_type=False.
- Riesgo: op.execute con dict de parámetros (TypeError).
  Mitigación: op.get_bind().execute(sa.text(...), {...}).
- Riesgo: :param::uuid colisiona con parser de sa.text.
  Mitigación: CAST(:param AS uuid).
- Riesgo: estado inconsistente del historial Alembic vs DB.
  Mitigación: reset de schema public + upgrade head; PROHIBIDO stamp.
- Riesgo: drift de imagen entre ejecuciones.
  Mitigación: derivación determinista por id.
- Riesgo: errores de timezone.
  Mitigación: timestamps server-side; no enviar fechas desde Python.

## Constitution Check
Incluir bloque "Gate previo a investigación: PASS/FAIL" y "Re-check
post diseño: PASS/FAIL" cubriendo los principios I a VII. Marcar
explícitamente que no hay violaciones que requieran Complexity Tracking.

## Trazabilidad
Tabla obligatoria al final del plan: Decisión -> FR(s) -> SC(s).
Toda decisión técnica del plan debe quedar enlazada a un FR/SC del
spec; está PROHIBIDO introducir decisiones huérfanas o features no
declaradas en el spec.

## Recordatorios de proceso Speckit
- Antes de crear plan.md, ejecutar el hook obligatorio before_plan
  declarado en .specify/extensions.yml (si existe) y validar que
  exista specs/004-propiedades-base/spec.md aprobada.
- Tras crear plan.md, actualizar el marker SPECKIT START en
  .github/copilot-instructions.md apuntando a
  specs/004-propiedades-base/plan.md.
- NO generar tasks.md en esta fase: corresponde a speckit.tasks.
- NO escribir código de implementación: el plan declara cómo, no
  ejecuta el cómo.