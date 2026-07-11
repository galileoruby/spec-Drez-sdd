# Quickstart: 006-pagina-propiedades-cards

## Proposito

Validar de extremo a extremo el listado de propiedades en cards con datos reales, responsive 3/2/1 y navegacion correcta desde sidebar.

## Prerrequisitos

1. Entorno uv activo.
2. Base de datos accesible y migraciones en head.
3. Datos de propiedades disponibles para escenario con registros.

## Escenario A: listado con datos

1. Ejecutar pruebas de repository/service:

```bash
uv run pytest app/modules/propiedades/tests -q
```

Resultado esperado:
- Consulta de propiedades reales en orden created_at descendente.
- Contrato de contexto de cards valido.
- Fallback de imagen local aplicado cuando corresponda.

Resultado observado:
- `16 passed in 1.38s` en `app/modules/propiedades/tests`.

2. Ejecutar prueba de render y navegacion:

```bash
uv run pytest tests/test_smoke.py -q
```

Resultado esperado:
- GET /propiedades responde 200.
- Sidebar contiene enlace funcional a /propiedades.
- Render de cards contiene todos los campos obligatorios.

Resultado observado:
- `8 passed in 1.59s` en `tests/test_smoke.py`.
- Se valida presencia de `href="/propiedades"`, `aria-current="page"` y markup de card completo.

## Escenario B: estado vacio

1. Ejecutar caso sin propiedades.

Resultado esperado:
- mostrar_estado_vacio = true.
- Mensaje/estado vacio renderizado sin error.

## Verificacion responsive

1. Validar estilos para breakpoints:
- desktop: 3 columnas
- tablet: 2 columnas
- phone: 1 columna

Resultado esperado:
- La grilla respeta 3/2/1 sin romper layout base.

## Validaciones finales

```bash
uv run ruff check .
uv run mypy --strict app/modules
uv run pytest -q
```

Resultado esperado:
- Lint en verde.
- Type-check estricto en verde.
- Tests de modulos involucrados en verde.

Resultado observado:
- `uv run ruff check .` -> `All checks passed!`
- `uv run mypy --strict app/modules` -> `Success: no issues found in 21 source files`
- `uv run pytest app/modules/propiedades/tests -q` -> `16 passed`
- `uv run pytest tests/test_smoke.py -q` -> `8 passed`

## Confirmacion de no alcance

- No dominio nuevo de rentas/pagos.
- No filtros, busqueda, paginacion ni ordenamiento adicional.
- No nuevas dependencias.
- No rediseno de layout global.
- No cambios de tokens visuales globales.
