# Data Model: Rediseñar Home Principal (003)

**Fase 1 — Contratos de datos de componentes y estructura de la Home**
**Fecha**: 2026-07-09

> Esta spec no introduce entidades de dominio ni migraciones. El "modelo de datos"
> son los contratos de variables Jinja2 que cada componente expone y consume.

---

## 1. Componentes y sus contratos de datos

### 1.1 `_tarjeta_metrica.html`

**Fuente**: `app/templates/components/_tarjeta_metrica.html`

**Variable de contexto**: `metrica` (objeto/dict)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `metrica.titulo` | string | Sí | Etiqueta del KPI (e.g. "Propiedades") |
| `metrica.valor` | string | Sí | Valor principal grande (e.g. "24") |
| `metrica.icono` | string | Sí | Nombre del SVG Lucide en `app/static/icons/` |
| `metrica.tendencia` | string | No (default `''`) | Texto de tendencia (e.g. "+3 este mes"); vacío oculta el campo |

**Cambio en esta spec**: Añadir campo `tendencia` al template con renderizado condicional y clase semántica.

**Valores de muestra** (hardcodeados en `dashboard.html`):
```jinja2
{% set metricas = [
  {"titulo": "Propiedades",      "valor": "24", "icono": "building-2",  "tendencia": "+3 este mes"},
  {"titulo": "Contratos activos","valor": "18", "icono": "file-text",   "tendencia": ""},
  {"titulo": "Pagos pendientes", "valor": "5",  "icono": "wallet",      "tendencia": "-2 desde ayer"},
] %}
```

---

### 1.2 `_alerta.html`

**Fuente**: `app/templates/components/_alerta.html`

**Variables de contexto**:

| Variable | Tipo | Obligatorio | Descripción |
|----------|------|-------------|-------------|
| `tipo` | string | No (default `'info'`) | Variante: `'success'`, `'warning'`, `'danger'`, `'info'` |
| `mensaje` | string | Sí | Texto del banner de alerta |
| `oob` | boolean | No (default `false`) | `true` activa `id="flash-zone"` + `hx-swap-oob="true"` para HTMX |

**Cambio en esta spec**: `id="flash-zone"` se convierte en condicional (`{% if oob %}`). Sin `oob`, la alerta se renderiza inline sin ID duplicado.

**Valor de muestra** (hardcodeado en `dashboard.html` sección 2):
```jinja2
{% set alerta_demo = {"tipo": "info", "mensaje": "Sistema operando con normalidad. Próxima revisión: 15 jul."} %}
{% with tipo=alerta_demo.tipo, mensaje=alerta_demo.mensaje %}
  {% include "components/_alerta.html" %}
{% endwith %}
```

---

### 1.3 `_accesos_rapidos.html`

**Fuente**: `app/templates/components/_accesos_rapidos.html`

**Sin variables de contexto**: el componente es autónomo, contiene los enlaces hardcodeados.

**Estado actual** (sin cambios en esta spec):
| Acceso | Icono | Destino |
|--------|-------|---------|
| Nuevo inquilino | `users` | `#` (placeholder) |
| Generar contrato | `file-text` | `#` (placeholder) |
| Crear ticket | `wrench` | `#` (placeholder) |

---

### 1.4 `_card_propiedad.html`

**Fuente**: `app/templates/components/_card_propiedad.html`

**Variable de contexto**: `propiedad` (objeto/dict, opcional)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `propiedad.titulo` | string | Sí (si propiedad existe) | Nombre de la propiedad |
| `propiedad.ubicacion` | string | Sí (si propiedad existe) | Dirección/zona |
| `propiedad.estado` | string | Sí (si propiedad existe) | Estado de dominio para badge |
| `propiedad.precio` | string | Sí (si propiedad existe) | Precio con formato (e.g. "$18,500/mes") |

**Sin cambios en esta spec**: el componente ya incluye `.estado-vacio` cuando `propiedad` es falsy.

**Valores de muestra** (hardcodeados en `dashboard.html` sección 4):
```jinja2
{% set propiedades_demo = [
  {"titulo": "Apto. Reforma 12A",  "ubicacion": "Col. Reforma, CDMX",  "estado": "Disponible",       "precio": "$18,500/mes"},
  {"titulo": "Casa Polanco",       "ubicacion": "Polanco, CDMX",       "estado": "Rentada",           "precio": "$32,000/mes"},
  {"titulo": "Local Condesa",      "ubicacion": "La Condesa, CDMX",    "estado": "En mantenimiento",  "precio": "$12,000/mes"},
] %}
```

---

### 1.5 `_badge_estado.html`

**Fuente**: `app/templates/components/_badge_estado.html`

**Variable de contexto**: `estado` (string, usado directamente vía `{% include %}` dentro de `_card_propiedad.html`)

| Estado | Clase CSS | Token de color |
|--------|-----------|----------------|
| `Disponible`, `Pagado` | `.badge-estado--success` | `--color-success` |
| `Pendiente`, `En mantenimiento` | `.badge-estado--warning` | `--color-warning` |
| `Vencido`, `Inactiva` | `.badge-estado--danger` | `--color-danger` |
| Cualquier otro | `.badge-estado--info` | `--color-info` |

**Sin cambios en esta spec**.

---

## 2. Estructura de la Home (`dashboard.html`) — contrato visual

```
layout-dashboard
├── sidebar (_sidebar.html)           — sin contexto de datos
└── main.main-content
    ├── navbar (_navbar.html)          — sin contexto de datos
    ├── section.metricas               — usa: metricas (list[dict])
    │   └── _tarjeta_metrica.html × N  — usa: metrica (dict)
    ├── section.seccion-alertas        — usa: tipo, mensaje (via with)
    │   ├── _alerta.html               — usa: tipo, mensaje, oob=false
    │   ├── <!-- TODO: estado-vacio -->
    │   └── <!-- TODO: estado-error -->
    ├── _accesos_rapidos.html          — autónomo
    └── section.tarjetas-contenido     — usa: propiedades_demo (list[dict])
        ├── _card_propiedad.html × N   — usa: propiedad (dict)
        └── <!-- TODO: estado-vacio -->
```

---

## 3. Clases CSS nuevas — contrato de estructura

| Clase | Descripción | Propiedad clave |
|-------|-------------|-----------------|
| `.seccion-alertas` | Wrapper de la sección de alertas | Sin estilos propios; hereda `gap` de `.main-content` |
| `.tarjetas-contenido` | Grid de tarjetas de contenido | `display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4)` |
| `.tarjeta-metrica__tendencia` | Línea de tendencia en tarjeta métrica | `font-size: 13px; margin-top: var(--space-1)` |
| `.tarjeta-metrica__tendencia--positiva` | Tendencia positiva | `color: var(--color-success)` |
| `.tarjeta-metrica__tendencia--negativa` | Tendencia negativa | `color: var(--color-danger)` |
| `.tarjeta-metrica__tendencia--neutra` | Tendencia neutra/vacía | `color: var(--color-text-muted)` |
| `.estado-vacio--bloque` | Estado vacío de sección completa | `display: flex; flex-direction: column; align-items: center; padding: var(--space-8); color: var(--color-text-muted)` |

---

## 4. Set de iconos Lucide utilizados en esta spec

Todos los iconos del set inicial (vendoreado en spec 001) ya están disponibles.
Esta spec no introduce nuevos iconos. Los iconos usados en los datos de muestra:

| Icono | Uso | Disponible |
|-------|-----|-----------|
| `building-2` | Métrica Propiedades | ✅ spec-001 |
| `file-text` | Métrica Contratos, Acceso "Generar contrato" | ✅ spec-001 |
| `wallet` | Métrica Pagos pendientes | ❌ **NO en set inicial** |
| `users` | Acceso "Nuevo inquilino" | ✅ spec-001 |
| `wrench` | Acceso "Crear ticket" | ✅ spec-001 |
| `info` | Icono de alerta tipo info | ✅ spec-001 |

> ⚠️ **Acción requerida en tarea T003-HOME-01**: El icono `wallet` no está en el set vendoreado de spec-001. La tarea debe incluir la descarga y registro del SVG `wallet.svg` en `app/static/icons/`, o usar `building-2` como sustituto temporal. Per Principio IV y §5 de `frontend.instructions.md`, cada nuevo icono requiere tarea explícita. Se crea sub-tarea dentro de T003-HOME-01.
