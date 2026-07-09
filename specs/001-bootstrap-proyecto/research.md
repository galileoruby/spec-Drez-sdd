# Research — 001-bootstrap-proyecto

## Decisiones

### 1) Contrato de `GET /health` cuando falle base de datos
- Decision: Responder `HTTP 200` con payload `{"status":"degraded","db":"error"}`.
- Rationale: Mantiene endpoint de salud compatible con chequeos de disponibilidad de aplicación y diferencia degradación de caída total del proceso.
- Alternatives considered:
  - `HTTP 503` con `db: down`: más estricto para dependencia crítica, descartado por decisión explícita de clarificación.
  - `HTTP 500` genérico: demasiado ambiguo para monitoreo y troubleshooting.

### 2) Breakpoint responsive para sidebar colapsable
- Decision: Colapsar sidebar en viewport `< 1024px`.
- Rationale: Cubre tablet y móvil con una sola regla y alinea criterios de aceptación de spec.
- Alternatives considered:
  - `< 768px`: insuficiente para tablets.
  - `< 1280px`: colapsa demasiado pronto en desktop pequeño.

### 3) Métricas hardcoded del dashboard demo
- Decision:
  - Propiedades activas: `12` (`building-2`)
  - Contratos vigentes: `9` (`file-text`)
  - Ingresos estimados: `$8,750` (`wallet`)
- Rationale: Valores simples, coherentes con demo administrativo y verificables por pruebas visuales.
- Alternatives considered:
  - Métricas de operaciones/tickets: menos alineadas al dominio Realtor.
  - Valores no fijados: genera ambigüedad en validación.

### 4) Alcance de componentes estructurales en spec 001
- Decision: Entregar HTML completo + clases CSS base + estados mínimos (hover/focus/empty).
- Rationale: Permite validar UX base sin sobreconstruir variantes avanzadas.
- Alternatives considered:
  - Solo esqueletos con placeholders: insuficiente para aceptación visual.
  - Componentes con microinteracciones avanzadas: fuera de alcance fundacional.

### 5) Estrategia para iconos Lucide
- Decision: Vendorear archivos SVG oficiales de Lucide, uno por archivo, sin edición estructural.
- Rationale: Asegura consistencia visual, licencia clara y reproducibilidad sin dependencia en runtime.
- Alternatives considered:
  - Generación manual por agente: riesgo de inconsistencias.
  - Descarga en build/runtime: introduce dependencia externa innecesaria.

### 6) Baseline Alembic
- Decision: Incluir `CREATE EXTENSION IF NOT EXISTS pgcrypto;` para habilitar `gen_random_uuid()`.
- Rationale: Estandariza generación UUID en Postgres/Supabase desde el arranque.
- Alternatives considered:
  - Baseline vacía: difiere una decisión estructural importante.
  - `uuid-ossp`: alternativa válida, descartada por preferencia acordada.

### 7) Política de logging inicial
- Decision: Logging estructurado INFO por request en `GET /health` y `GET /` (inicio/fin, ruta, status, duración), sin payload sensible.
- Rationale: Proporciona trazabilidad operacional desde bootstrap con ruido controlado.
- Alternatives considered:
  - Sin logs: baja observabilidad.
  - DEBUG detallado: ruido excesivo y potencial exposición de datos.

## Buenas prácticas aplicadas al stack

- FastAPI: handlers delgados y contrato de respuesta explícito para casos degradados.
- SQLAlchemy async + Supabase: separar URL de runtime y URL directa de migraciones.
- Alembic: baseline reversible y mínima, con extensión necesaria declarada.
- Jinja2 + HTMX: server-rendering con assets vendoreados (sin CDN).
- Calidad: definición temprana de lint, tipo estricto y smoke tests.
