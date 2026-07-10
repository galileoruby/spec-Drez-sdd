# Investigación: 004-propiedades-base

**Fase 0 — Decisiones técnicas cerradas y evidencia de diseño**
**Fecha**: 2026-07-09

---

## 1. Materialización del enum `estado_propiedad`

**Decisión**: El tipo `estado_propiedad` se crea exactamente una vez a través del DDL implícito de `create_table` en la migración estructural.

**Justificación**: El historial reciente del proyecto ya fijó esta regla para evitar conflictos de doble creación entre el `sa.Enum(...)` declarado en la columna y llamadas explícitas de creación del tipo.

**Alternativas consideradas**:
- Llamar `Enum.create()` manualmente además de `create_table`: descartado por riesgo directo de colisión de DDL.
- Persistir el estado como `String`: descartado porque rompe el catálogo cerrado y la gobernanza del dominio.

---

## 2. Timestamps server-side y timezone awareness

**Decisión**: `created_at` y `updated_at` serán `DateTime(timezone=True)` con `server_default=now()`. El seed no enviará timestamps desde Python.

**Justificación**: Evita mezclar valores naive y aware, mantiene consistencia entre entornos y simplifica la idempotencia del seed.

**Alternativas consideradas**:
- Generar timestamps en Python: descartado por riesgo de drift horario y fallos naive/aware.
- No persistir `updated_at`: descartado porque impide rastrear actualizaciones in-place del seed.

---

## 3. Idempotencia por clave de negocio compuesta

**Decisión**: La identidad de seed será `(titulo, direccion, ciudad)` y el seed usará `ON CONFLICT (...) DO UPDATE`.

**Justificación**: Es la identidad de negocio pedida por la spec y evita duplicados en cargas repetidas o parciales.

**Alternativas consideradas**:
- Resolver solo por UUID: descartado porque el UUID del seed es un detalle técnico, no la identidad de negocio exigida.
- Borrar y reinsertar: descartado porque rompe estabilidad operativa y auditoría temporal.

---

## 4. Imagen reproducible por UUID fijo

**Decisión**: La URL de imagen se derivará como `https://picsum.photos/seed/{id}/800/500` usando UUID fijo por registro del seed.

**Justificación**: Produce un resultado determinista y fácil de validar en pruebas sin depender de assets locales ni de lógica aleatoria.

**Alternativas consideradas**:
- Generar URLs aleatorias: descartado por drift entre ejecuciones.
- Versionar imágenes binarias en el repositorio: descartado por costo operativo y por no estar exigido por la spec.

---

## 5. SQL parametrizado en Alembic

**Decisión**: Toda sentencia SQL parametrizada en migraciones se ejecutará con `op.get_bind().execute(sa.text(...), params)` y casteos `CAST(:param AS uuid)`.

**Justificación**: Es la forma compatible con la configuración actual de Alembic/SQLAlchemy del repositorio y evita los errores ya identificados con `op.execute(sql, params)` y `:param::uuid`.

**Alternativas consideradas**:
- `op.execute(sql, params)`: descartado por incompatibilidad con el patrón de parámetros requerido.
- `:param::uuid`: descartado por colisiones con el parser de `sa.text`.

---

## 6. Recuperación ante historial inconsistente

**Decisión**: El procedimiento documentado será reset del esquema `public` y reaplicación de `alembic upgrade head`. Queda prohibido `alembic stamp`.

**Justificación**: La constitución y las lecciones previas ya cerraron esta decisión como política operativa obligatoria.

**Alternativas consideradas**:
- `alembic stamp head`: descartado por dejar divergencia entre historial lógico y estado físico.
- Correcciones manuales sobre tablas parciales: descartado por falta de reproducibilidad.

---

## 7. Estado del repositorio que impacta el plan

**Decisión**: El plan debe contemplar que `alembic/script.py.mako` no existe hoy en el repo y que su presencia/versionado es prerrequisito antes de generar nuevas revisiones.

**Justificación**: El prompt de planificación y las restricciones heredadas lo elevan a guardrail obligatorio.

**Alternativas consideradas**:
- Generar revisiones sin esa plantilla: descartado por incumplimiento directo de la decisión cerrada del proyecto.