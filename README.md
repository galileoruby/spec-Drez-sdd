# Realtor

Aplicación inmobiliaria server-rendered para operar propiedades con FastAPI, Jinja2 y HTMX. El estado actual del repositorio refleja el trabajo entregado mediante Spec-Driven Development: una base técnica estable, una home con datos reales, un listado de propiedades en cards, y flujos de alta y edición de propiedades con validación de dominio.

## Descripción del proyecto

Realtor organiza su interfaz y su dominio en slices verticales. La aplicación expone una home operativa, un listado de propiedades persistidas, formularios SSR para crear y editar propiedades, y una base técnica asíncrona sobre PostgreSQL/Supabase. La lógica de negocio vive en `service.py`, el acceso a datos en `repository.py` y las rutas se mantienen delgadas.

## Stack y arquitectura

- Python 3.13+ gestionado con `uv`.
- FastAPI para HTTP.
- Jinja2 server-rendered con HTMX local vendoreado.
- SQLAlchemy 2.x async con `AsyncSession` y estilo `Mapped[...]`.
- Pydantic v2 con DTOs inmutables (`frozen=True`).
- PostgreSQL con `asyncpg`.
- Alembic como única herramienta de migraciones.
- pytest, pytest-asyncio, httpx, Ruff y mypy `--strict` en el módulo `app/modules/`.

La arquitectura es vertical slice: cada feature vive dentro de `app/modules/<feature>/` con `routes.py`, `schemas.py`, `models.py`, `repository.py`, `service.py`, `templates/` y `tests/`. El arranque de la app se centraliza en `app/main.py`, y la conexión async a base de datos se configura en `app/database.py`.

## Funcionalidades implementadas por módulo

### 001-bootstrap-proyecto

Dejó lista la base técnica del proyecto: settings con Pydantic, engine async con `statement_cache_size=0`, `prepared_statement_cache_size=0` y `ssl=require`, bootstrap de FastAPI, estáticos, templates, `GET /health`, logging estructurado y la migración baseline con `pgcrypto`.

### 002-blindar-tokens-visuales

Blindó la gobernanza visual del frontend. La fuente operativa de tokens visuales quedó declarada en `.github/instructions/frontend.instructions.md`, y cualquier cambio en colores, sombras, radios o espaciados requiere autorización explícita y trazabilidad en `tasks.md`.

### 003-redisenar-home

Rediseñó la home principal con una estructura visual canónica y reutilizable. La página `app/templates/pages/dashboard.html` quedó organizada en cuatro secciones: tarjetas métricas, bloque de alertas, accesos rápidos y tarjetas de contenido de apoyo. También se ajustaron componentes compartidos y CSS responsive sin introducir tokens nuevos.

### 004-propiedades-base

Introdujo la base persistente del dominio de propiedades. Se creó el modelo `Propiedad`, el catálogo cerrado `EstadoPropiedad` con los valores `disponible`, `rentada`, `mantenimiento` e `inactiva`, la migración estructural `0002_create_propiedades.py`, y el seed idempotente `0003_seed_propiedades_miami.py` con 10 propiedades de Miami. La identidad de negocio quedó definida por `titulo + direccion + ciudad`, y el seed usa `INSERT ... ON CONFLICT ... DO UPDATE` para evitar duplicados.

### 005-dashboard-datos-reales

Conectó la home con datos reales de base de datos. El dashboard ahora calcula propiedades disponibles y rentadas desde el repositorio, conserva el contrato de contexto, mantiene ingresos y pagos vencidos como métricas no operativas explícitas y usa el estado vacío real derivado de los conteos persistidos.

### 006-pagina-propiedades-cards

Agregó `GET /propiedades` como página SSR dedicada al listado de propiedades. La vista renderiza cards con imagen, título, dirección, habitaciones, baños, área, precio de renta y estado; ordena por `created_at` descendente; aplica fallback local cuando `imagen_url` no es utilizable; y mantiene un layout responsive de 3 columnas en desktop, 2 en tablet y 1 en móvil.

### 007-crear-propiedad

Agregó el flujo SSR de alta de propiedades en `/propiedades/crear`. El formulario pide título, dirección, ciudad, precio mensual, habitaciones, baños y área; normaliza espacios en blanco; valida rangos de negocio; asigna `estado=disponible` por defecto; genera `imagen_url` determinista con Picsum; y redirige al listado con confirmación de éxito. La alta rechaza duplicados por identidad de negocio.

### 008-editar-propiedad

Agregó el flujo SSR de edición en `/propiedades/editar/{id}`. La edición precarga los datos actuales, permite modificar título, dirección, ciudad, precio mensual, habitaciones, baños, área y estado, conserva los cambios escritos cuando la validación falla, muestra errores inline, detecta conflicto optimista por `updated_at`, y responde con 404 claro cuando la propiedad no existe.

## Flujo Spec-Driven Development usado en el repositorio

El repositorio sigue un flujo de specs numeradas en `specs/`, con `spec.md`, `plan.md`, `tasks.md`, `quickstart.md` y contratos asociados. Cada feature se implementó en orden numérico y con trazabilidad hacia tareas y evidencia de validación.

Resumen del flujo aplicado:

1. Se definió la base técnica en la spec 001.
2. Se blindó la gobernanza visual en la spec 002.
3. Se rediseñó la home en la spec 003.
4. Se creó el dominio persistente de propiedades en la spec 004.
5. Se conectó la home a datos reales en la spec 005.
6. Se agregó el listado de propiedades en cards en la spec 006.
7. Se incorporaron los flujos de alta y edición en las specs 007 y 008.

## Guía de ejecución local

### 1. Instalar dependencias

```powershell
uv sync
```

### 2. Configurar variables de entorno

La aplicación espera `DATABASE_URL` para runtime y `DATABASE_URL_DIRECT` para Alembic. Ambas deben apuntar a PostgreSQL con SSL requerido.

### 3. Aplicar migraciones

```powershell
uv run alembic upgrade head
```

### 4. Levantar la aplicación

```powershell
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

La aplicación queda disponible en `http://127.0.0.1:8000/`.

## Pruebas y calidad

La evidencia del workspace muestra validaciones verdes en el alcance entregado:

- `uv run pytest app/modules/dashboard/tests -q`: `4 passed`.
- `uv run pytest app/modules/propiedades/tests -q`: `16 passed`.
- `uv run pytest tests/test_smoke.py -q`: `8 passed`.
- `uv run ruff check .`: `All checks passed!`.
- `uv run mypy --strict app/modules`: `Success: no issues found in 21 source files`.

También hay evidencia documentada en los quickstarts de:

- `specs/001-bootstrap-proyecto/quickstart.md`
- `specs/003-redisenar-home/quickstart.md`
- `specs/004-propiedades-base/quickstart.md`
- `specs/005-dashboard-datos-reales/quickstart.md`
- `specs/006-pagina-propiedades-cards/quickstart.md`

Para 007 y 008, la evidencia de implementación está trazada en `tasks.md` y en los tests del módulo `app/modules/propiedades/tests/`, pero no existen `quickstart.md` en esas carpetas dentro del workspace actual.

## Rutas y páginas principales

- `GET /` - Home principal con métricas reales, accesos rápidos y contenido de apoyo.
- `GET /health` - Healthcheck con respuesta `ok` o `degraded` según conectividad a base de datos.
- `GET /propiedades` - Listado SSR de propiedades en cards.
- `GET /propiedades/crear` - Formulario SSR de alta de propiedad.
- `POST /propiedades/crear` - Procesa el alta y redirige al listado.
- `GET /propiedades/editar/{id}` - Formulario SSR de edición de propiedad.
- `POST /propiedades/editar/{id}` - Procesa la edición y redirige al listado.

## Estado actual y próximas mejoras

Estado actual: la base técnica, la navegación principal y el flujo de propiedades están implementados y validados. La app ya no depende de datos mock para el dashboard principal ni para el listado de propiedades.

Próximas mejoras razonables:

1. Definir modelos reales para ingresos y pagos vencidos, que hoy permanecen explícitamente no operativos.
2. Ampliar el dominio de propiedades si surgen nuevas reglas de negocio o filtros.
3. Completar la documentación operativa de alta y edición con quickstarts equivalentes a las specs 007 y 008.
