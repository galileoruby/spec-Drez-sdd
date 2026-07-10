# Quickstart: 005-dashboard-datos-reales

## Propósito

Validar de extremo a extremo que la home usa datos reales para métricas de propiedades disponibles/rentadas, mantiene contrato de contexto y conserva ingresos/vencidos en modo no operativo.

## Prerrequisitos

1. Entorno `uv` inicializado.
2. Base de datos lista y migraciones aplicadas (`alembic upgrade head`).
3. Seed/base de propiedades disponible (spec 004).

## Escenario A: Datos existentes

1. Ejecutar pruebas de servicio:

```bash
uv run pytest app/modules/dashboard/tests/test_service.py -q
```

Resultado esperado:
- Pasa cálculo de disponibles/rentadas con datos reales.
- Pasa bandera de estado vacío en falso cuando hay datos.

2. Ejecutar prueba de render de home:

```bash
uv run pytest tests/test_smoke.py -q
```

Resultado esperado:
- Home responde 200.
- Render incluye métricas de disponibles/rentadas con valores reales.
- No depende de bloque mock previo.

## Escenario B: Sin datos operativos

1. Ejecutar prueba con fixture sin propiedades operativas.

Resultado esperado:
- `mostrar_estado_vacio = true`.
- No falla el render de home.

## Validaciones de calidad

```bash
uv run ruff check .
uv run mypy --strict app/modules
```

Resultado esperado:
- Sin errores de lint en archivos afectados.
- Sin errores de tipado en alcance de módulos afectados.

## Evidencia mínima a registrar

1. Resultado de pruebas de servicio de dashboard.
2. Resultado de prueba de render en `/`.
3. Confirmación de contrato de contexto estable (métricas/accesos).
4. Confirmación explícita de ingresos/vencidos no operativos.

## Fuera de alcance validado

- No endpoint adicional de refresh parcial.
- No modelo de rentas/pagos/ingresos.
- No cambios visuales de UI/tokens.

## Evidencia de ejecucion

- `pytest app/modules/dashboard/tests -q`: `4 passed`
- `pytest tests/test_smoke.py -q`: `4 passed`
- `ruff check .`: `All checks passed!`
- `mypy --strict app/modules`: `Success: no issues found in 19 source files`

## Verificacion de alcance implementado

- Metrica real de `Propiedades disponibles` conectada a conteos persistidos.
- Metrica real de `Propiedades rentadas` conectada a conteos persistidos.
- Contrato y orden de `metricas` mantenido segun `contracts/home-context.md`.
- `Ingresos del mes` y `Pagos vencidos` en modo no operativo explicito.
- Estado vacio controlado por `mostrar_estado_vacio` basado en datos reales.
