---
applyTo: "app/modules/**/*.py"
---

# Backend — Reglas para módulos Python

## Estructura del módulo

Cada feature en `app/modules/<feature>/` contiene exactamente:
`routes.py`, `schemas.py`, `models.py`, `repository.py`, `service.py`,
`templates/`, `tests/`. No agregues otros archivos sin justificación en el
`plan.md` de la spec.

## routes.py (endpoints delgados)

- Async siempre (`async def`).
- Recibe `AsyncSession` vía `Depends(get_session)`.
- Valida entrada con schemas Pydantic.
- Llama al servicio del módulo. NUNCA contiene lógica de negocio.
- Retorna schema Pydantic o `HTTPException` tipada.
- Emite logging estructurado al inicio y fin de la operación.

Ejemplo:

```python
@router.post("/", response_model=PropiedadOut, status_code=201)
async def crear_propiedad(
    payload: PropiedadIn,
    session: AsyncSession = Depends(get_session),
) -> PropiedadOut:
    """Crea una nueva propiedad y retorna su representación pública."""
    return await service.crear_propiedad(session, payload)
```

## schemas.py (Pydantic v2)

- Todos los modelos con `model_config = ConfigDict(frozen=True)`.
- Sufijos claros: `In`, `Out`, `Update`, `Filter`.
- Validaciones de formato/tipo aquí; validaciones de negocio en
  `service.py`.

## models.py (SQLAlchemy 2.x async)

- Heredan de `Base` (de `app/database.py`).
- Usar `Mapped[...]` y `mapped_column(...)`. PROHIBIDO `Column(...)` legacy.
- `__tablename__` en plural y snake_case.
- Claves foráneas con `ondelete` explícito.

## repository.py

- Funciones async que reciben `AsyncSession` como primer parámetro.
- Solo acceso a datos: `select()`, `insert()`, `update()`, `delete()`.
- NO contiene reglas de negocio ni transformaciones de dominio.

## service.py (lógica de negocio)

- Orquesta repository + reglas de negocio + mapeos a schemas.
- Recibe `AsyncSession` y schemas Pydantic.
- Retorna schemas Pydantic, NUNCA entidades SQLAlchemy.
- Lanza `HTTPException` o errores de dominio tipados.

## Logging

Usar `logging.getLogger(__name__)` y formato estructurado:

```python
logger.info("propiedad.creada", extra={"propiedad_id": str(prop.id)})
```

NUNCA loggear contraseñas, tokens ni PII en claro.

## Docstrings

Todos los módulos, clases y funciones públicas con docstring en español.