# Tasks: Rediseñar Home Principal

**Input**: Design documents from `specs/003-redisenar-home/`

**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · quickstart.md ✅

**Tests**: No solicitados en spec. Se ejecuta únicamente el smoke test existente en Phase 6.

**Trazabilidad VTG spec**: T003-HOME-01 → T007+T003+T004 | T003-HOME-02 → T008 | T003-HOME-03 → T002+T011–T014 | T003-HOME-04 → T005+T006+T009+T016 | T003-HOME-05 → T016+T017+T018

---

## Formato de tarea

```
- [ ] TXXX [P?] [USN?] Descripción con ruta exacta del archivo
```

- `[P]` — paralelizable (archivos distintos, sin dependencias de tareas incompletas)
- `[USN]` — historia de usuario a la que pertenece la tarea (US1, US2, US3)
- Sin etiqueta `[USN]` en Setup y Fundacional

---

## Dependencias entre fases

```
Phase 1 (Setup)
  └─► Phase 2 (Fundacional)
        ├─► Phase 3 (US1) — T002 debe estar completa antes de T007
        │     T004 [P], T005 [P], T006 → T007
        ├─► Phase 4 (US2) — independiente de US1 en código; lógicamente posterior
        │     T008 [P] → T009 → T010
        └─► Phase 5 (US3) — T011–T014 paralelas entre sí; requieren T002 completa
              T011 [P], T012 [P], T013 [P], T014 [P]
Phase 6 (Polish & VTG) — requiere todas las phases anteriores completas
  T015 → T016 [P] → T017 → T018 [P]
```

---

## Phase 1: Setup

**Propósito**: Verificar el contexto antes de cualquier modificación.

- [X] T001 Confirmar branch activo (`git branch`), workspace limpio (`git status`) y que existen los 5 archivos afectados en sus rutas canónicas (`app/templates/pages/dashboard.html`, `app/templates/base.html`, `app/templates/components/_alerta.html`, `app/templates/components/_tarjeta_metrica.html`, `app/static/css/app.css`)

**Checkpoint**: Workspace confirmado — se puede iniciar Phase 2.

---

## Phase 2: Fundacional (Prerrequisitos bloqueantes)

**Propósito**: Corregir el bug crítico y añadir el icono faltante antes de cualquier tarea de historia de usuario.

**⚠️ CRÍTICO**: Ninguna tarea de US1/US2/US3 puede completarse correctamente sin que T002 esté completa.

- [X] T002 Corregir bug `id="flash-zone"` en `app/templates/components/_alerta.html`: hacer el atributo `id` condicional — agregar `{% if oob %} id="flash-zone"{% endif %}` en la etiqueta `<div class="alerta ...">` para que el ID solo aparezca cuando `oob=true` (mecanismo HTMX OOB swap); sin el ID el DOM no tendrá IDs duplicados al incluir la alerta inline

- [X] T003 [P] Descargar el SVG outline de `wallet` desde Lucide (https://lucide.dev/icons/wallet) y guardarlo como `app/static/icons/wallet.svg`; verificar que el SVG usa `currentColor` en `stroke` y no tiene `fill` ni `stroke` con valores hardcodeados; registrar el icono en el comentario de set en `frontend.instructions.md` §5 no es necesario — basta con que el archivo exista y sea invocable con `{{ icon("wallet") }}`

**Checkpoint**: Bug de ID corregido e icono disponible — historias de usuario pueden comenzar en paralelo.

---

## Phase 3: User Story 1 — Home clara y accionable para operación diaria (Priority: P1) 🎯 MVP

**Goal**: Reestructurar `dashboard.html` con el orden canónico de 4 secciones (FR-011), datos hardcodeados de muestra (FR-008), comentarios TODO para estados diferidos y la tendencia visible en tarjetas métricas.

**Independent Test**: Abrir `http://127.0.0.1:8000/` y verificar escenarios SC-V1 y SC-V2 de `specs/003-redisenar-home/quickstart.md` — 4 secciones en orden, datos de demo visibles incluyendo tendencia con color semántico.

- [X] T004 [P] [US1] Añadir campo `tendencia` al componente `app/templates/components/_tarjeta_metrica.html`: agregar `<p class="tarjeta-metrica__tendencia tarjeta-metrica__tendencia--{{ 'positiva' if metrica.tendencia.startswith('+') else ('negativa' if metrica.tendencia.startswith('-') else 'neutra') }}">{{ metrica.tendencia }}</p>` condicionado a `{% if metrica.tendencia | default('') %}` para que sea retrocompatible cuando el campo está vacío o ausente

- [X] T005 [P] [US1] Añadir estilos de tendencia en la sección `/* ============ 5. Componentes ============ */` de `app/static/css/app.css` inmediatamente después de `.tarjeta-metrica__valor`: clases `.tarjeta-metrica__tendencia` (font-size 13px, margin-top `var(--space-1)`), `.tarjeta-metrica__tendencia--positiva` (color `var(--color-success)`), `.tarjeta-metrica__tendencia--negativa` (color `var(--color-danger)`), `.tarjeta-metrica__tendencia--neutra` (color `var(--color-text-muted)`); PROHIBIDO usar valores literales de color

- [X] T006 [US1] Añadir en `app/static/css/app.css` sección `/* ============ 5. Componentes ============ */` las clases: `.seccion-alertas {}` (selector vacío — wrapper semántico que hereda `gap` de `.main-content`); `.tarjetas-contenido` (display grid, grid-template-columns repeat(3, minmax(0, 1fr)), gap `var(--space-4)`); `.estado-vacio--bloque` (display flex, flex-direction column, align-items center, justify-content center, padding `var(--space-8)` `var(--space-6)`, color `var(--color-text-muted)`, gap `var(--space-3)`); añadir en `@media (max-width: 1023px)` override de `.tarjetas-contenido` a grid-template-columns 1fr

- [X] T007 [US1] Reestructurar `app/templates/pages/dashboard.html` con el orden canónico FR-011: (1) añadir `{% set metricas = [...] %}` hardcodeado como primera línea de `{% block content %}` con los 3 objetos de muestra definidos en `data-model.md` §1.1 (incluyendo tendencia); (2) añadir `<section class="seccion-alertas">` entre `</section>` de métricas y el `include _accesos_rapidos.html`, con una alerta de demo tipo info usando `{% with %}` y los comentarios `<!-- TODO: estado-vacio -->` y `<!-- TODO: estado-error -->`; (3) añadir `<section class="tarjetas-contenido">` tras los accesos rápidos con `{% set propiedades_demo = [...] %}` (3 propiedades de muestra de `data-model.md` §1.4) y `{% for p in propiedades_demo %}{% set propiedad = p %}{% include "components/_card_propiedad.html" %}{% endfor %}` más el comentario `<!-- TODO: estado-vacio -->`; añadir comentario `{# DEMO: datos de muestra hardcodeados. Reemplazar con contexto de route en spec futura. #}` sobre el primer `{% set %}`

**Checkpoint**: US1 completa y verificable — `dashboard.html` renderiza sin errores Jinja2, 4 secciones en orden canónico, datos visibles con tendencia y color semántico.

---

## Phase 4: User Story 2 — Navegación transversal coherente desde el layout base (Priority: P2)

**Goal**: Verificar que `base.html` no tiene ID duplicados, que las zonas de layout son correctas y que el responsive de las secciones nuevas funciona en tablet/móvil.

**Independent Test**: Verificar escenario SC-V3 (DOM inspector: exactamente 1 `#flash-zone`) y SC-V7 (DevTools responsive iPad Air: columnas correctas) de `specs/003-redisenar-home/quickstart.md`.

- [X] T008 [P] [US2] Auditar `app/templates/base.html`: confirmar que el `<div id="flash-zone" class="flash-zone" aria-live="polite">` es el único elemento con ese ID en el layout base; verificar que `<script src="/static/vendor/htmx.min.js" defer>` carga el vendoreado (no CDN); verificar `lang="es"` en `<html>`; documentar cualquier hallazgo — no se esperan cambios estructurales pero si se encuentra una desviación debe corregirse

- [X] T009 [US2] Verificar en `app/static/css/app.css` dentro de `@media (max-width: 1023px)` que las nuevas secciones añadidas en T006 tienen sus overrides responsivos correctos: `.tarjetas-contenido` → `grid-template-columns: 1fr`; si el override no se añadió en T006, añadirlo ahora; comprobar también que `.seccion-alertas` no necesita override específico (hereda de `.main-content`)

- [X] T010 [US2] Levantar el servidor con `uv run uvicorn app.main:app --reload` y abrir `http://127.0.0.1:8000/` en navegador; ejecutar manualmente escenario SC-V3 (inspeccionar DOM — 1 solo `#flash-zone`) y SC-V7 (responsive 820×1180 — columnas correctas); anotar resultado en el checklist de `specs/003-redisenar-home/quickstart.md`

**Checkpoint**: US2 completa — layout base correcto, responsive verificado en tablet.

---

## Phase 5: User Story 3 — Componentes reutilizables y consistentes (Priority: P3)

**Goal**: Auditar los 4 componentes no modificados en el ciclo principal para confirmar que no hay desviaciones de tokens ni estilos ad hoc, garantizando consistencia antes de la validación final VTG.

**Independent Test**: Verificar escenario SC-V5 de `specs/003-redisenar-home/quickstart.md` — DevTools: ninguna propiedad CSS en los componentes tiene valor literal de color o espaciado.

- [X] T011 [P] [US3] Auditar `app/templates/components/_navbar.html`: confirmar que los botones "Exportar" y "Nueva propiedad" usan clases `btn--secondary` y `btn--primary` (tokens correctos); confirmar `aria-label` en el botón de toggle; confirmar que no hay estilos inline excepto los controlados por HTMX; sin cambios de código si la auditoría pasa

- [X] T012 [P] [US3] Auditar `app/templates/components/_accesos_rapidos.html`: confirmar que todos los `<a class="acceso" href="#">` tienen `href="#"` placeholder (cumple FR-012); confirmar que los iconos `users`, `file-text`, `wrench` están disponibles en `app/static/icons/`; confirmar texto de accesos en español; sin cambios de código si la auditoría pasa

- [X] T013 [P] [US3] Auditar `app/templates/components/_card_propiedad.html`: confirmar que el bloque `{% else %}` con `.estado-vacio` existe y usa `{{ icon("building-2", 20) }}`; confirmar que `_badge_estado.html` es incluido correctamente y que la variable `estado` se define antes del include; sin cambios de código si la auditoría pasa

- [X] T014 [P] [US3] Auditar `app/templates/components/_sidebar.html`: confirmar que los links de secciones futuras tienen `href="#"` y `aria-disabled="true"`; confirmar `aria-current="page"` en el link activo de Dashboard; auditar `app/templates/components/_badge_estado.html`: confirmar que las clases `.badge-estado--*` mapean a tokens `--color-success/warning/danger/info` en `app.css` sin hardcodes

**Checkpoint**: US3 completa — todos los componentes auditados, 0 desviaciones documentadas.

---

## Phase 6: Polish & Verificación Visual Canónica (VTG)

**Propósito**: Validar el trabajo completo contra gates de salida T003-HOME-04 y T003-HOME-05.

- [X] T015 Ejecutar `uv run pytest tests/test_smoke.py -v` desde la raíz del repo; confirmar que todos los tests pasan (exit code 0); si algún test falla por un cambio de template introducido en esta spec, corregir el template antes de continuar

- [X] T016 [P] Auditoría VTG línea a línea de los 5 archivos modificados (`dashboard.html`, `_alerta.html`, `_tarjeta_metrica.html`, `app.css`, `base.html` si hubo cambios): (a) ningún valor literal de color hexadecimal nuevo en `app.css`; (b) ningún valor literal de espaciado nuevo en `app.css`; (c) todos los `color:`, `background:`, `padding:`, `margin:`, `border-radius:` y `box-shadow:` nuevos usan `var(--)` exclusivamente; (d) ningún `style=""` inline en los templates salvo los controlados por HTMX (`style="display:none"`); registrar resultado pass/fail

- [X] T017 Levantar servidor y ejecutar los escenarios SC-V1 a SC-V8 del checklist en `specs/003-redisenar-home/quickstart.md`; marcar cada escenario como ✅ o documentar la desviación encontrada y corregirla; la tarea no cierra hasta que los 8 escenarios estén en ✅

- [X] T018 [P] Marcar todos los ítems del bloque "Checklist de revisión VTG" en `specs/003-redisenar-home/quickstart.md` como completados `[x]`; actualizar el `**Status**` del `spec.md` de `Draft` a `Ready for Review`

---

## Resumen de paralelismo

| Tareas paralelas | Condición |
|-----------------|-----------|
| T003 ‖ (T001 completada) | T003 no depende del bug fix |
| T004 ‖ T005 ‖ T003 | Archivos distintos; T002 completa |
| T005 ‖ T008 | CSS vs base.html — sin conflicto |
| T011 ‖ T012 ‖ T013 ‖ T014 | Componentes independientes |
| T016 ‖ T018 | Auditoría y actualización de quickstart |

---

## Métricas de trazabilidad

| User Story | Tareas | Gate de salida |
|-----------|--------|---------------|
| Fundacional | T002, T003 | Bug corregido; `wallet.svg` disponible |
| US1 (P1) — SC-001, SC-005 | T004, T005, T006, T007 | SC-V1 + SC-V2 de quickstart |
| US2 (P2) — SC-002 | T008, T009, T010 | SC-V3 + SC-V7 de quickstart |
| US3 (P3) — SC-003, SC-004 | T011, T012, T013, T014 | SC-V5 de quickstart; 0 desviaciones |
| Polish/VTG — SC-004, SC-006 | T015, T016, T017, T018 | Smoke test verde; 8/8 SC-Vx en ✅; VTG checklist completo |

**Total de tareas**: 18 (T001–T018)
**Tareas paralelizables**: 9 (T003, T004, T005, T008, T011, T012, T013, T014, T016, T018)
**MVP scope**: Phase 1 + Phase 2 + Phase 3 (T001–T007) — entrega US1 completa y verificable
