---
applyTo: "app/modules/**/models.py,app/modules/**/repository.py,alembic/**"
---

# Base de datos — PostgreSQL (Supabase) + SQLAlchemy 2.x async + Alembic

## Conexiones (Supabase)

El proyecto usa dos URLs distintas:

- `DATABASE_URL` → **transaction pooler** (puerto 6543). SOLO para
  runtime. El engine en `app/database.py` desactiva prepared statements
  con `statement_cache_size=0` y `prepared_statement_cache_size=0`.
- `DATABASE_URL_DIRECT` → **conexión directa** (puerto 5432). SOLO para
  Alembic.

NUNCA uses la URL del pooler para migraciones ni la directa para runtime.

## models.py

- Heredar de `Base` de `app/database.py`.
- Estilo moderno OBLIGATORIO:

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
import uuid

class Propiedad(Base):
    """Propiedad inmobiliaria gestionada por el realtor."""

    __tablename__ = "propiedades"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    direccion: Mapped[str] = mapped_column(String(255), nullable=False)
    propietario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("propietarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
```

- Tipos explícitos siempre en `Mapped[...]`.
- `ondelete` explícito en cada FK.
- Índices declarados explícitamente cuando se filtre por una columna en
  consultas frecuentes.

## repository.py

- Funciones async, primer parámetro `session: AsyncSession`.
- Usar `select(...)` y `await session.execute(stmt)`.
- Para uno: `.scalar_one_or_none()`. Para muchos: `.scalars().all()`.
- NUNCA `session.query(...)` (estilo legacy).

## Alembic

- `alembic/env.py` configurado en modo async, leyendo
  `DATABASE_URL_DIRECT`.
- Cada migración con nombre descriptivo en español:
  `alembic revision --autogenerate -m "agrega tabla propiedades"`.
- **Revisar SIEMPRE** la migración generada antes de aplicarla.
  `autogenerate` no es infalible (índices, enums, tipos custom).
- Migraciones reversibles: implementar `downgrade()` real, no `pass`.
- Aplicar con `alembic upgrade head`.

## Convenciones de nombres

- Tablas en plural snake_case: `propiedades`, `inquilinos`,
  `contratos_renta`.
- Columnas snake_case: `fecha_inicio`, `monto_mensual`.
- FKs: `<tabla_singular>_id` → `propietario_id`, `inquilino_id`.
- Índices: `ix_<tabla>_<columna>`.
- Constraints únicos: `uq_<tabla>_<columna>`.