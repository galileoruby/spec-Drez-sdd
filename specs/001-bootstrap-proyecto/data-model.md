# Data Model — 001-bootstrap-proyecto

## Entidades conceptuales de bootstrap

> Esta spec fundacional no introduce entidades de dominio de negocio persistentes.
> Define modelos conceptuales y contratos mínimos necesarios para arrancar.

## 1) AppSettings
- Descripción: Configuración de entorno cargada por Pydantic Settings.
- Campos:
  - `database_url: str` (runtime, pooler)
  - `database_url_direct: str` (migraciones)
  - `app_env: str`
  - `log_level: str`
- Reglas:
  - Deben obtenerse desde `.env`.
  - `database_url` y `database_url_direct` son obligatorias.

## 2) HealthStatus
- Descripción: Respuesta de salud para monitoreo técnico.
- Campos:
  - `status: Literal["ok", "degraded"]`
  - `db: Literal["ok", "error"]`
- Reglas:
  - Estado saludable: `{"status":"ok","db":"ok"}`.
  - Estado degradado por fallo de DB: `{"status":"degraded","db":"error"}`.

## 3) DashboardMetric
- Descripción: Tarjeta de métrica para dashboard demo.
- Campos:
  - `label: str`
  - `value: str`
  - `icon: str`
- Instancias fijas en bootstrap:
  - `Propiedades activas`, `12`, `building-2`
  - `Contratos vigentes`, `9`, `file-text`
  - `Ingresos estimados`, `$8,750`, `wallet`

## 4) UiComponentSpec
- Descripción: Componente visual estructural reutilizable.
- Campos:
  - `name: str`
  - `template_path: str`
  - `has_base_styles: bool`
  - `has_min_states: bool`
- Reglas:
  - En spec 001, todos los componentes estructurales incluyen HTML completo + clases base + estados mínimos.

## 5) BaselineMigration
- Descripción: Definición de arranque de migraciones.
- Campos:
  - `revision_id: str`
  - `enables_pgcrypto: bool`
- Reglas:
  - Debe ejecutar `CREATE EXTENSION IF NOT EXISTS pgcrypto;`.

## Relaciones

- `AppSettings` habilita inicialización de runtime DB y Alembic.
- `HealthStatus` depende de verificación async de conexión DB.
- `DashboardMetric` se renderiza en `GET /`.
- `UiComponentSpec` define capacidad de reutilización de la UI base.
- `BaselineMigration` habilita estrategia UUID para modelos futuros.
