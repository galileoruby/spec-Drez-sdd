# Quickstart: Validación Visual — Rediseñar Home Principal (003)

**Guía de validación end-to-end para revisor e implementador**
**Fecha**: 2026-07-09

---

## Prerrequisitos

1. **Entorno activo**: Python 3.13+, `uv` instalado.
2. **Dependencias instaladas**:
   ```powershell
   uv sync
   ```
3. **Variables de entorno**: `DATABASE_URL` y `DATABASE_URL_DIRECT` configuradas (requeridas por `app/config.py`), o ejecutar en modo sin DB si el smoke test lo permite.
4. **Branch correcto**:
   ```powershell
   git branch  # debe mostrar * 003-redisenar-home
   ```

---

## Levantar el servidor

```powershell
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abrir en navegador: **http://127.0.0.1:8000/**

---

## Escenarios de validación

### SC-V1 — Orden de secciones (mapea a FR-011, SC-001)

1. Abrir `http://127.0.0.1:8000/`.
2. **Esperado** (de arriba a abajo, sin scroll):
   - Fila de 3 tarjetas métricas con título, valor grande, icono y tendencia.
   - Bloque de alerta informativa con ícono `info`, mensaje de demo y botón de cierre.
   - Sección "Accesos rápidos" con 3 accesos en grid.
   - Fila de 3 tarjetas de propiedad con título, ubicación, badge de estado y precio.
3. **Falla si**: cualquier sección aparece fuera del orden anterior o no es visible sin scroll en viewport 1280×800.

**Resultado 2026-07-09**: ✅ Verificado en navegador (`metricas` → `seccion-alertas` → `accesos-rapidos` → `tarjetas-contenido`).

---

### SC-V2 — Datos hardcodeados presentes (mapea a FR-008, SC-005)

Verificar que los datos de demo son visibles:

| Elemento | Valor esperado |
|----------|---------------|
| Métrica 1 | "Propiedades · 24 · +3 este mes" |
| Métrica 2 | "Contratos activos · 18" (sin tendencia) |
| Métrica 3 | "Pagos pendientes · 5 · -2 desde ayer" |
| Alerta | Tipo info: "Sistema operando con normalidad. Próxima revisión: 15 jul." |
| Propiedad 1 | "Apto. Reforma 12A · Disponible (badge verde)" |
| Propiedad 2 | "Casa Polanco · Rentada (badge azul)" |
| Propiedad 3 | "Local Condesa · En mantenimiento (badge amarillo)" |

**Resultado 2026-07-09**: ✅ Verificado en render de `/` y smoke test.

---

### SC-V3 — Sin IDs duplicados en DOM (mapea a bug fix `_alerta.html`)

1. Abrir DevTools → pestaña Elements (o Inspect).
2. Buscar con `Ctrl+F` el texto `flash-zone` en el HTML del DOM.
3. **Esperado**: exactamente 1 ocurrencia (el `<div id="flash-zone">` de `base.html`).
4. **Falla si**: aparece `id="flash-zone"` también en el elemento `.alerta`.

**Resultado 2026-07-09**: ✅ `id="flash-zone"` aparece exactamente una vez en el HTML renderizado.

---

### SC-V4 — Tendencia en tarjetas métricas (mapea a FR-004)

1. Verificar visualmente:
   - Métrica "Propiedades": tendencia "+3 este mes" en color **verde** (`--color-success`).
   - Métrica "Contratos activos": sin campo de tendencia visible.
   - Métrica "Pagos pendientes": tendencia "-2 desde ayer" en color **rojo** (`--color-danger`).
2. **Falla si**: la tendencia tiene color hardcodeado o no respeta el token semántico.

**Resultado 2026-07-09**: ✅ Tendencias positiva/negativa renderizadas con clases semánticas y tokens.

---

### SC-V5 — Sin tokens violados en CSS (mapea a FR-006, FR-007, SC-003, SC-004)

1. Abrir DevTools → pestaña Elements → seleccionar cualquier elemento de las nuevas clases (`.seccion-alertas`, `.tarjetas-contenido`, `.tarjeta-metrica__tendencia`).
2. En el panel Styles, verificar que **ninguna** propiedad `color`, `background`, `padding`, `margin`, `border-radius` o `box-shadow` tenga un valor literal (e.g. `#hexcode`, `12px`). Todos deben ser `var(--)`.
3. **Falla si**: se encuentra cualquier literal de color o medida fuera de una variable CSS.

**Resultado 2026-07-09**: ✅ Nuevas clases de la spec (`.seccion-alertas`, `.tarjetas-contenido`, `.tarjeta-metrica__tendencia*`, `.estado-vacio--bloque`) usan `var(--)` para color/espaciado.

---

### SC-V6 — Comentarios TODO presentes (mapea a FR-008, clarificación Q5)

1. Ver código fuente de la página renderizada (`Ctrl+U` en navegador o `view-source:`).
2. Buscar `TODO:`.
3. **Esperado**: exactamente 3 comentarios:
   - `<!-- TODO: estado-vacio -->` en la sección de alertas.
   - `<!-- TODO: estado-error -->` en la sección de alertas.
   - `<!-- TODO: estado-vacio -->` en la sección de tarjetas de contenido.

**Resultado 2026-07-09**: ✅ Se verifican 3 marcadores TODO en el HTML renderizado.

---

### SC-V7 — Responsive tablet/móvil (mapea a FR-009)

1. Abrir DevTools → Toggle device toolbar → seleccionar "iPad Air" (820×1180).
2. **Esperado**:
   - Sidebar oculta; botón hamburguesa visible en navbar.
   - Métricas en columna única (1 tarjeta por fila).
   - Accesos rápidos en columna única.
   - Tarjetas de contenido en columna única.
3. **Falla si**: las columnas se solapan o el contenido desborda horizontalmente.

**Resultado 2026-07-09**: ✅ Verificado por reglas CSS activas para `@media (max-width: 1023px)` con columnas a 1fr en `.metricas`, `.accesos-rapidos__grid` y `.tarjetas-contenido`.

---

### SC-V8 — Test de humo automático (mapea a SC-002)

```powershell
$env:PYTHONPATH='.' ; uv run pytest tests/test_smoke.py -v
```

**Esperado**: todos los tests pasan. Ningún error de template Jinja2 ni de ruta HTTP.

**Resultado 2026-07-09**: ✅ `3 passed`.

---

## Checklist de revisión VTG (gate T003-HOME-05)

| Ítem | Estado |
|------|--------|
| Paleta `:root` sin modificaciones (0 cambios en 10 tokens de color) | [x] |
| Espaciado `:root` sin modificaciones (0 cambios en 7 tokens) | [x] |
| Radios y sombras `:root` sin modificaciones | [x] |
| Todas las clases CSS nuevas usan `var(--)` exclusivamente | [x] |
| No existe ningún `style=""` inline en los templates modificados (salvo los controlados por HTMX) | [x] |
| Icono `wallet.svg` registrado en `app/static/icons/` y referenciado vía macro `{{ icon() }}` | [x] |
| SC-V1 a SC-V8 marcados como pasados | [x] |

**Condición de cierre de la feature**: todos los ítems marcados.

---

## Referencias cruzadas

| Artefacto | Ruta |
|-----------|------|
| Spec | [spec.md](spec.md) |
| Plan | [plan.md](plan.md) |
| Research | [research.md](research.md) |
| Data Model | [data-model.md](data-model.md) |
| Tareas | [tasks.md](tasks.md) *(generado por /speckit.tasks)* |
| Frontend instructions | [frontend.instructions.md](../../.github/instructions/frontend.instructions.md) |
