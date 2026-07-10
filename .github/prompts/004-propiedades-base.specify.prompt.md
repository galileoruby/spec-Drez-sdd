---
name: 004-propiedades-base-spec
agent: speckit.specify
---

## Prompt para `speckit.specify` — Feature: 004-propiedades-base

**Nombre de la spec**: `004-propiedades-base`
## Contexto de negocio
El dashboard actual muestra métricas en cero porque no existe ninguna
fuente de datos de propiedades en el sistema. Necesitamos habilitar una
base inicial de propiedades inmobiliarias para que el producto deje de
operar con datos vacíos y podamos validar reportes y comportamiento
funcional con casos realistas. Esta feature es fundacional: habilita el
dominio "propiedades" para que features posteriores (listado, alta,
búsqueda, dashboard real) puedan apoyarse en datos existentes.

## Resultado esperado
Después de aplicar esta feature, el sistema debe contar con:
- Una base persistente de propiedades con todos los atributos de
  negocio relevantes para alquiler residencial.
- Un conjunto inicial de 10 propiedades de prueba ubicadas en Miami,
  USA, cargado de forma repetible y sin duplicados.
- Estados operativos de propiedad controlados por un catálogo cerrado.
- Evoluciones de datos reversibles y seguras frente a zonas horarias,
  aplicables en cualquier entorno limpio en un solo paso, sin
  intervención manual.

## Alcance explícito
- INCLUYE: definición de la entidad de propiedades, su estructura
  persistente, el catálogo de estados, la carga inicial idempotente
  de 10 propiedades de Miami con imágenes asociadas, y validaciones
  de calidad y reversibilidad.
- NO INCLUYE: endpoints HTTP, vistas, templates ni cambios visibles
  en el dashboard.
- NO MODIFICA tokens visuales (paleta, tipografía, espaciados,
  radios, sombras).

## Reglas de negocio obligatorias
1. Atributos mínimos de una propiedad: título, dirección, ciudad,
   precio mensual, habitaciones, baños, área, estado, imagen, marca
   temporal de creación y de actualización.
2. El estado solo puede tomar cuatro valores permitidos: disponible,
   rentada, mantenimiento, inactiva. Cualquier otro valor debe
   rechazarse.
3. Identidad de negocio del seed: combinación título + dirección +
   ciudad. Re-ejecutar la carga nunca debe duplicar; si una propiedad
   ya existe con esa identidad, debe actualizarse en sitio.
4. Marcas temporales gestionadas por la base de datos; la carga
   inicial nunca debe enviar fechas desde la aplicación.
5. Imagen determinista por identificador de la propiedad (semilla
   visual estable, reproducible entre ejecuciones).
6. Evoluciones aplicables y reversibles en entorno limpio, sin
   errores por mezcla de fechas con y sin zona horaria.

## Restricciones técnicas heredadas de la constitution (NO reabrir)
Las siguientes reglas vienen de .specify/memory/constitution.md y de
lecciones aprendidas previas; deben quedar enumeradas como FR
adicionales (categoría "no funcionales / gobernanza") para que
speckit.plan y speckit.tasks NO las reabran ni propongan alternativas:

### Migraciones de base de datos
- Cada tipo enumerado del dominio se crea EXACTAMENTE UNA VEZ por
  evolución de estructura: lo declara la columna y lo materializa el
  DDL de creación de tabla. Está PROHIBIDO invocar la creación
  explícita del tipo en paralelo a su declaración en columna sin
  desactivar la creación implícita.
- El SQL parametrizado dentro de migraciones se ejecuta usando la
  conexión enlazada (op.get_bind().execute(sa.text("..."), {...})).
  Está PROHIBIDO usar op.execute(sql, params).
- Los casteos a UUID en SQL parametrizado usan CAST(:param AS uuid).
  Está PROHIBIDO usar la forma ::uuid dentro de sa.text.
- La plantilla alembic/script.py.mako DEBE estar versionada en el
  repositorio antes de generar nuevas revisiones.
- Está PROHIBIDO usar `alembic stamp` como atajo ante fallos. Ante
  estado inconsistente del historial de evoluciones, la recuperación
  obligatoria es reiniciar el esquema (DROP SCHEMA public CASCADE +
  CREATE SCHEMA public) y reaplicar `alembic upgrade head` desde
  base limpia.
- Las migraciones DEBEN ser reversibles reales; downgrade nunca
  puede ser `pass`.
- El seed DEBE ser idempotente por clave de negocio usando
  ON CONFLICT (...) DO UPDATE.
- Los timestamps son server-side; NO enviar created_at/updated_at
  desde Python en migraciones ni en seed.

### Dominio y código
- SQLAlchemy 2.x async con Mapped[...] + mapped_column + AsyncSession.
  PROHIBIDO el estilo legacy (Column en clase, Query, sesiones sync).
- Estados de dominio como Enum tipado (StrEnum + Enum SQLAlchemy).
  PROHIBIDO strings mágicos.
- Pydantic v2 con model_config = ConfigDict(frozen=True) en DTOs.
- Vertical slice: todo en app/modules/<feature>/ con routes.py,
  schemas.py, models.py, repository.py, service.py, templates/,
  tests/.
- Lógica de negocio SOLO en service.py; routes.py delgado;
  repository.py solo acceso a datos.
- No exponer entidades SQLAlchemy en respuestas HTTP.
- Funciones async para I/O; def sync solo para cómputo puro.

### Calidad
- Ruff sin hallazgos.
- mypy --strict sin errores en app/modules/propiedades.
- pytest + pytest-asyncio + httpx.AsyncClient para tests.

### Herramientas autorizadas
- Cualquier script auxiliar de mantenimiento de base de datos DEBE
  usar el driver asyncpg vía create_async_engine. Está PROHIBIDO
  depender de psycopg2/psycopg.

## Success Criteria que DEBEN aparecer (mínimo, numerar como SC-XXX)
- alembic upgrade head sobre `public` recién creado finaliza en verde
  sin intervención manual y sin uso de `stamp`.
- La carga inicial deja exactamente 10 propiedades de Miami y
  mantiene esa cardinalidad después de dos ejecuciones consecutivas.
- El 100% de las propiedades iniciales tiene estado dentro del
  catálogo permitido y una imagen asociada con semilla estable.
- El ciclo upgrade/downgrade completo finaliza con éxito en el 100%
  de las ejecuciones de validación.
- La actualización completa de base de datos no reporta errores por
  fechas naive vs aware.
- mypy --strict en el módulo de propiedades no reporta errores.
- Ningún script auxiliar de mantenimiento usa psycopg2/psycopg.
- La materialización del catálogo de estados no produce conflictos
  por declaración duplicada al aplicar la evolución de estructura.

## Edge cases que DEBEN listarse
- Intentar registrar una propiedad con estado fuera del catálogo.
- Ejecutar la carga inicial varias veces en entornos con datos
  parcialmente presentes.
- Aplicar la actualización completa en un entorno donde el esquema
  previo quedó en estado inconsistente.
- Alembic reporta una revisión que no existe en alembic/versions/
  (mitigación: reset de schema public + upgrade head, NUNCA stamp).
- CREATE TYPE choca con un enum preexistente (mitigación: enum se
  crea una sola vez vía DDL implícito de la tabla).
- Inserciones con SQL parametrizado y :param::uuid (mitigación:
  CAST(:param AS uuid)).
- Carga parcial del seed (mitigación: upsert por clave compuesta de
  negocio).
- Ejecución del seed dos veces consecutivas (mitigación: cardinalidad
  estable y actualización in-place).
- Detección de diferencias de zona horaria entre datos generados por
  aplicación y datos gestionados por la base de datos.

## Entrega esperada
- Archivo spec.md ubicado en specs/004-propiedades-base/ (carpeta
  specs/ en la RAÍZ del repositorio, NUNCA bajo .specify/specs/).
- Redacción 100% en español, sin mezclar idiomas.
- Estructura completa del template oficial de spec.md: User Scenarios
  & Testing (con User Stories priorizadas P1/P2/P3), Functional
  Requirements (FR-XXX), Gobernanza de tokens visuales (VTG-XXX),
  Key Entities, Success Criteria (SC-XXX) y Assumptions.
- Sin código de implementación.
- Trazabilidad: cada regla de negocio y cada restricción técnica
  heredada queda como FR o SC numerado, para que speckit.plan y
  speckit.tasks no la reabran.

## Recordatorios de proceso Speckit
- Antes de crear el directorio de la spec o el archivo spec.md,
  ejecutar el hook obligatorio before_specify (incluye
  speckit.git.feature) para crear el branch de la feature y
  actualizar .specify/feature.json.
- Ubicación canónica: specs/004-propiedades-base/ en la raíz del
  repositorio. Está PROHIBIDO crearla bajo .specify/specs/, que está
  reservado a infraestructura de spec-kit.
- No actualizar todavía el marker SPECKIT START en
  .github/copilot-instructions.md: eso corresponde a la fase de plan.