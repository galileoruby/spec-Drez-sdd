# Implementation Plan: Rediseñar Home Principal

**Branch**: `003-redisenar-home` | **Date**: 2026-07-09 | **Spec**: [spec.md](../../.specify/specs/003-redisenar-home/spec.md)

**Input**: Feature specification from `.specify/specs/003-redisenar-home/spec.md`

## Summary

Rediseño visual de la Home principal (`app/templates/pages/dashboard.html`) para mejorar la jerarquía operativa y la consistencia de componentes. El alcance es 100 % presentación: no se modifican routes, services ni repositories. La aproximación ejecuta cuatro cambios secuenciales: (1) corregir un bug de ID duplicado en `_alerta.html`, (2) añadir el campo `tendencia` a `_tarjeta_metrica.html`, (3) reestructurar `dashboard.html` con el orden canónico de secciones y datos hardcodeados, (4) extender `app.css` con clases faltantes usando exclusivamente tokens canónicos.

## Technical Context

**Language/Version**: Python 3.13+

**Primary Dependencies**: FastAPI, Jinja2, HTMX (vendoreado en `app/static/vendor/htmx.min.js`)

**Storage**: N/A — sin cambios de base de datos ni migraciones en esta spec

**Testing**: pytest + httpx.AsyncClient; test de humo existente en `tests/test_smoke.py`

**Target Platform**: Servidor Linux (Supabase cloud); navegadores modernos desktop-first

**Project Type**: Monolito web server-rendered (FastAPI + Jinja2 + HTMX)

**Performance Goals**: N/A — sin cambios de backend; sin nuevas peticiones HTTP

**Constraints**: Sin nuevas dependencias. Sin cambios de tokens canónicos. Sin framework CSS externo. Sin CDN externo. Datos de demo hardcodeados en template; route handler no se toca.

**Scale/Scope**: 5 archivos modificados, 0 archivos nuevos de código (solo artefactos de plan en `specs/`).

## Constitution Check

*GATE: Evaluado antes de Phase 0. Re-evaluado tras Phase 1.*

| Principio | Estado | Observación |
|-----------|--------|-------------|
| I. Solución Única | ✅ PASA | Solo modifica templates y CSS del monolito existente; sin repos ni servicios paralelos |
| II. Spec-Driven | ✅ PASA | Cada cambio rastrea a FR-001–FR-012 y T003-HOME-01–T003-HOME-05 |
| III. Vertical Slice | ✅ PASA | No se crean módulos nuevos; `app/templates/` globales son la ubicación canónica para templates transversales |
| IV. Stack Obligatorio | ✅ PASA | Jinja2 server-rendered, HTMX vendoreado, CSS propio, sin deps nuevas |
| V. Calidad de Dominio | ✅ PASA | Sin lógica de negocio en templates; datos de demo son literales estáticos |
| VI. Idioma | ✅ PASA | Toda la documentación y los templates en español |
| VII. Async-First | N/A | Sin modificaciones de backend en esta spec |
| VIII. VTG | ✅ PASA | Auditoría confirma 0 cambios de tokens; nuevas clases CSS solo consumen `var(--)` existentes |

**Resultado: NINGUNA VIOLACIÓN. Plan puede ejecutarse.**

## Project Structure

### Documentation (esta feature)

```text
specs/003-redisenar-home/
├── plan.md              # Este archivo
├── research.md          # Phase 0: análisis de inconsistencias en codebase
├── data-model.md        # Phase 1: contratos de datos de cada componente
├── quickstart.md        # Phase 1: guía de validación visual
└── tasks.md             # Phase 2 (generado por /speckit.tasks — NO por este comando)
```

### Source Code (archivos afectados)

```text
app/
  templates/
    base.html                          # verificar — sin cambio estructural necesario
    pages/
      dashboard.html                   # PRINCIPAL: restructura + hardcode datos + TODO markers
    components/
      _alerta.html                     # BUG FIX: id="flash-zone" condicional a oob=true
      _tarjeta_metrica.html            # MEJORA: añadir campo tendencia (opcional, retrocompatible)
      _accesos_rapidos.html            # SIN CAMBIO — href="#" ya correcto (clarificación Q4)
      _card_propiedad.html             # SIN CAMBIO — estado-vacio ya implementado
      _badge_estado.html               # SIN CAMBIO
      _sidebar.html                    # SIN CAMBIO
      _navbar.html                     # SIN CAMBIO — CTAs permanecen placeholder
  static/
    css/
      app.css                          # EXTENSIÓN: añadir .seccion-alertas, .tarjetas-contenido,
                                       #            .tarjeta-metrica__tendencia, .estado-vacio--bloque
```

**Structure Decision**: Monolito único. Templates globales en `app/templates/` según estructura canónica del Principio III. No se crean módulos nuevos ya que el rediseño es de la Home compartida, no de una feature de negocio.

## Complexity Tracking

> No aplica: la Constitution Check no tiene violaciones.

---

## Riesgos y Mitigaciones

| Riesgo | Prob. | Impacto | Mitigación |
|--------|-------|---------|------------|
| IDs duplicados `#flash-zone` rompen mensajes flash HTMX | ALTA (bug activo) | Alto | Corregir `_alerta.html` en T003-HOME-03a antes de integrar alertas en dashboard |
| `{% set metricas %}` hardcodeado sobreescribe variable de contexto en runtime futuro | MEDIA | Bajo | Documentar en el bloque con comentario `{# DEMO: reemplazar con contexto de route en spec futura #}` |
| CSS nuevo introduce hardcodes de color o espaciado | MEDIA | Alto | T003-HOME-04: revisión explícita contra checklist de tokens; gate SC-004 antes de cerrar tarea |
| Campo `tendencia` en `_tarjeta_metrica.html` rompe includes en otras vistas | BAJA | Bajo | Usar `metrica.tendencia \| default('')` — retrocompatible; ningún otro template consume este componente actualmente |

## Gates de Salida por Bloque de Tarea

| Tarea | Gate de salida | SC mapeado |
|-------|---------------|-----------|
| T003-HOME-01 (dashboard.html) | Renderiza sin error Jinja2; 4 secciones en orden correcto; datos de demo visibles | SC-001, SC-005 |
| T003-HOME-02 (base.html) | `#flash-zone` único en DOM; `hx-swap-oob` funciona sin conflicto | SC-002 |
| T003-HOME-03 (componentes) | `_alerta.html` sin ID duplicado; `_tarjeta_metrica.html` muestra tendencia; todos los componentes visibles en Home | SC-003 |
| T003-HOME-04 (app.css) | 0 colores hardcodeados nuevos; 0 espaciados hardcodeados; todas las nuevas clases usan `var(--)` | SC-004 |
| T003-HOME-05 (VTG) | Inspección visual confirma paleta canónica sin desviación; SC-003 y SC-004 marcados OK | SC-004, SC-006 |

---

## Orden de Implementación Recomendado

```
T003-HOME-03a  →  T003-HOME-03b  →  T003-HOME-04  →  T003-HOME-01  →  T003-HOME-02 (verificación)  →  T003-HOME-05
(fix alerta)      (tendencia)        (css nuevo)       (dashboard)      (base ok)                       (VTG audit)
```

**Rationale del orden**: El bug de `_alerta.html` se corrige primero para evitar que el dashboard integre el componente con el defecto. Los estilos se añaden antes de modificar el template para que al abrir en navegador todo renderice correctamente en un solo paso.
