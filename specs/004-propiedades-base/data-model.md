# Modelo de Datos: 004-propiedades-base

**Fase 1 — Contratos de datos del dominio de propiedades**
**Fecha**: 2026-07-09

---

## 1. Entidad `Propiedad`

**Representa**: un inmueble residencial disponible para operación futura dentro del producto.

| Campo | Tipo lógico | Obligatorio | Reglas |
|-------|-------------|-------------|--------|
| `id` | UUID | Sí | Generado server-side con `gen_random_uuid()` en estructura; UUID fijo solo para registros versionados del seed |
| `titulo` | texto | Sí | Parte de la identidad de negocio |
| `direccion` | texto | Sí | Parte de la identidad de negocio |
| `ciudad` | texto | Sí | Parte de la identidad de negocio; para el seed siempre `Miami` |
| `precio_mensual` | decimal | Sí | Monto mensual de alquiler |
| `habitaciones` | entero | Sí | Cantidad de habitaciones |
| `banos` | decimal | Sí | Permite medios baños |
| `area_m2` | decimal | Sí | Área construida en metros cuadrados |
| `estado` | enum | Sí | Debe pertenecer a `EstadoPropiedad` |
| `imagen_url` | texto | Sí | Determinista por UUID fijo del registro |
| `created_at` | timestamp tz | Sí | Gestionado por la base de datos |
| `updated_at` | timestamp tz | Sí | Gestionado por la base de datos; actualizado en upsert |

### Identidad de negocio

La identidad funcional del dominio y del seed es la combinación:

`(titulo, direccion, ciudad)`

Esta identidad se materializa con una restricción única compuesta y es la clave para `ON CONFLICT ... DO UPDATE`.

---

## 2. Catálogo `EstadoPropiedad`

**Representa**: el conjunto cerrado de estados operativos permitidos para una propiedad.

| Valor | Significado |
|-------|-------------|
| `disponible` | La propiedad puede ofrecerse para renta |
| `rentada` | La propiedad ya está ocupada por un contrato activo |
| `mantenimiento` | La propiedad está temporalmente fuera de operación |
| `inactiva` | La propiedad existe en catálogo pero no participa en operación actual |

**Restricción**: cualquier valor fuera de este catálogo debe rechazarse.

---

## 3. Índices y restricciones operativas

| Artefacto | Propósito |
|-----------|-----------|
| PK sobre `id` | Identidad técnica única |
| UQ sobre `titulo, direccion, ciudad` | Idempotencia del seed y unicidad de negocio |
| Índice por `ciudad` | Consultas operativas por ubicación |
| Índice por `estado` | Consultas operativas por estado |

---

## 4. Set inicial de datos versionados

El seed inicial contiene exactamente 10 propiedades de Miami. Cada una debe:

- tener UUID fijo versionado en la migración de seed,
- usar `ciudad = "Miami"`,
- incluir `imagen_url = https://picsum.photos/seed/{id}/800/500`,
- poder actualizarse in-place sin crear duplicados.

### Contrato mínimo del seed

| Campo | Regla de seed |
|-------|----------------|
| `id` | UUID fijo por registro |
| `titulo` | Estable entre ejecuciones |
| `direccion` | Estable entre ejecuciones |
| `ciudad` | `Miami` |
| `estado` | Uno de los cuatro valores permitidos |
| `imagen_url` | Derivada del `id` |

---

## 5. Reglas temporales

- `created_at` nunca se envía desde Python.
- `updated_at` no se envía en insert inicial.
- `updated_at = now()` solo se fuerza en la rama de actualización del upsert.
- Todos los timestamps son timezone-aware a nivel de base de datos.