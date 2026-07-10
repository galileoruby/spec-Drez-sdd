---
name: db-preflight
description: >
  Valida el estado de la base de datos y aplica la acción correcta
  (upgrade, reset, abort) antes de ejecutar speckit.implement o
  cualquier operación que dependa de migraciones aplicadas. USE WHEN:
  el usuario va a ejecutar speckit.implement, va a correr tests que
  tocan la base, o reporta errores de "relation does not exist",
  "alembic_version", "table already exists", o estado inconsistente
  de migraciones.
---

# Preflight de base de datos

Antes de continuar, ejecuta `scripts/db_preflight.py` y razona sobre
su salida JSON. NUNCA uses `alembic stamp` ni bypass manual de
migraciones para atajar el resultado.

## Ejecución estándar

1. Lanza el preflight en modo no destructivo:

   ```pwsh
   uv run python scripts/db_preflight.py
   ```

2. Lee el JSON impreso. Los campos relevantes son `estado`,
   `accion_ejecutada`, `permite_implement` y `siguientes_pasos`.

3. Interpreta el exit code:
   - `0`: base alineada con head. Continúa con `speckit.implement`.
   - `10`: el preflight corrigió la base automáticamente. Continúa.
   - `20`: requiere intervención humana. NO continúes con implement.

## Matriz de decisión

| `estado` | Acción del skill | ¿Permite implement? |
|---|---|---|
| `EMPTY` | aplica `alembic upgrade head` | sí |
| `VERSIONED_OK` | noop | sí |
| `VERSIONED_BEHIND` | aplica `alembic upgrade head` | sí |
| `VERSIONED_AHEAD` | aborta y reporta | no |
| `DRIFTED` | aborta salvo `--allow-reset` | solo tras reset |
| `MULTI_HEADS` | aborta | no |
| `ALEMBIC_FAIL` | aborta | no |
| `CONN_FAIL` | aborta | no |

## Escenario DRIFTED

Si el preflight reporta `DRIFTED` (tablas presentes en `public` sin
tabla `alembic_version`) y la base es desechable (no producción):

1. Confirma con el usuario que autoriza el reset destructivo.
2. Re-ejecuta con la bandera explícita:

   ```pwsh
   uv run python scripts/db_preflight.py --allow-reset
   ```

3. El skill ejecutará `DROP SCHEMA public CASCADE`, `CREATE SCHEMA
   public` y `alembic upgrade head`.

Nunca uses `--allow-reset` sin consentimiento del usuario. Nunca lo
uses cuando `APP_ENV=prod` (el script lo bloquea por contrato).

## Reglas inquebrantables

- Prohibido `alembic stamp` para alinear historial sin migrar.
- Prohibido editar o borrar revisiones existentes en
  `alembic/versions/` para "saltarse" un error.
- Prohibido cargar variables de entorno distintas a las del `.env`
  del repo para evitar el chequeo.
- Si el estado es `VERSIONED_AHEAD`, la única salida válida es
  sincronizar el código con la rama que generó esa revisión, o
  resetear la base con autorización explícita.

## Reporte al usuario

Cuando termines, resume en español:

- Estado detectado.
- Acción ejecutada (o motivo del abort).
- Siguiente paso recomendado.
- Si `permite_implement` es `false`, indica explícitamente que
  `speckit.implement` queda bloqueado hasta resolver el escenario.
