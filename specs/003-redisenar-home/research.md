# Research: Rediseñar Home Principal (003)

**Fase 0 — Análisis de codebase y resolución de decisiones técnicas**
**Fecha**: 2026-07-09

---

## 1. Bug crítico: `id="flash-zone"` duplicado en `_alerta.html`

**Observación**: `_alerta.html` línea 4 escribe `id="flash-zone"` en todos los casos, sin condición. `base.html` línea 11 declara `<div id="flash-zone" class="flash-zone" aria-live="polite">`. Cuando `_alerta.html` se incluye directamente en un template (no vía HTMX OOB), el DOM resultante contiene dos elementos con el mismo id `flash-zone`, violando HTML5 y haciendo que `document.querySelector('#flash-zone')` y el mecanismo `hx-swap-oob` sean no determinísticos.

**Decisión**: Hacer el atributo `id` condicional al parámetro `oob`:
- Con `oob=true` (inclusión vía HTMX OOB swap): el `id="flash-zone"` es necesario como target.
- Sin `oob` (inclusión directa en template de página): el `id` debe omitirse.

**Cambio concreto en `_alerta.html`**:
```jinja2
{# Antes #}
<div class="alerta alerta--{{ tipo_alerta }}" role="status" id="flash-zone" ...>

{# Después #}
<div class="alerta alerta--{{ tipo_alerta }}" role="status"{% if oob %} id="flash-zone"{% endif %} ...>
```

**Alternativas descartadas**:
- Quitar el `id` permanentemente: rompería el mecanismo de mensajes flash HTMX para acciones POST futuras.
- Mover al layout base: introduciría lógica de presentación en `base.html`, violando separación de responsabilidades.

---

## 2. Campo `tendencia` faltante en `_tarjeta_metrica.html`

**Observación**: `frontend.instructions.md` §6 define el componente como "KPI con número grande, label, **tendencia**, icono". El template actual expone solo `titulo`, `valor`, `icono`. El campo `tendencia` nunca fue implementado.

**Decisión**: Añadir `metrica.tendencia | default('')` como campo opcional. Renderizar con clase semántica según el primer carácter del valor:
- `+` → `.tarjeta-metrica__tendencia--positiva` (usa `--color-success`)
- `-` → `.tarjeta-metrica__tendencia--negativa` (usa `--color-danger`)
- Cualquier otro (o vacío) → `.tarjeta-metrica__tendencia--neutra` (usa `--color-text-muted`)

**Retrocompatibilidad**: Default vacío garantiza que templates que no pasen `tendencia` no se vean afectados.

**Valores de demo para dashboard.html**:
| Métrica | Valor demo | Tendencia |
|---------|-----------|-----------|
| Propiedades | 24 | `+3 este mes` |
| Contratos activos | 18 | *(vacío)* |
| Pagos pendientes | 5 | `-2 desde ayer` |

---

## 3. Reestructura de secciones en `dashboard.html`

**Observación**: El template actual tiene dos secciones: `metricas` y `accesos-rapidos`. FR-011 establece 4 secciones en orden canónico. La sección de alertas y la de tarjetas de contenido de apoyo no existen.

**Decisión — estructura final de `dashboard.html`**:

```
{% block content %}
  {% set metricas = [...] %}          {# DEMO hardcodeado #}

  <div class="layout-dashboard">
    sidebar + navbar (sin cambio)

    <main class="main-content">
      navbar                           {# sección 0: navegación superior #}

      <!-- 1. Tarjetas métricas -->
      <section class="metricas">
        {% for m in metricas %}...{% endfor %}
      </section>

      <!-- 2. Alertas -->
      <section class="seccion-alertas">
        {% set alerta_demo = {...} %}
        {% include "_alerta.html" %}
        <!-- TODO: estado-vacio -->
        <!-- TODO: estado-error -->
      </section>

      <!-- 3. Accesos rápidos -->
      {% include "_accesos_rapidos.html" %}

      <!-- 4. Tarjetas de contenido de apoyo -->
      <section class="tarjetas-contenido">
        {% set propiedades_demo = [...] %}
        {% for p in propiedades_demo %}...{% endfor %}
        <!-- TODO: estado-vacio -->
      </section>
    </main>
  </div>
{% endblock %}
```

**Datos hardcodeados de alerta de demo**:
```python
tipo="info", mensaje="Sistema operando con normalidad. Próxima revisión: 15 jul."
```

**Datos hardcodeados de propiedades de demo** (3 tarjetas):
| Título | Ubicación | Estado | Precio |
|--------|-----------|--------|--------|
| Apto. Reforma 12A | Col. Reforma, CDMX | Disponible | $18,500/mes |
| Casa Polanco | Polanco, CDMX | Rentada | $32,000/mes |
| Local Condesa | La Condesa, CDMX | En mantenimiento | $12,000/mes |

---

## 4. Datos hardcodeados y coexistencia con el route handler

**Observación**: El route actual inyecta `{"metricas": [...]}` como contexto Jinja2. Si el template redefine `metricas` vía `{% set %}`, Jinja2 usa el valor local dentro del bloque donde se define, ignorando el contexto del route.

**Decisión**: Colocar todos los `{% set %}` de demo como primera instrucción dentro de `{% block content %}`, antes de cualquier uso. Añadir un comentario que documente la intención:

```jinja2
{# DEMO: datos de muestra hardcodeados. Reemplazar con contexto de route en spec futura. #}
{% set metricas = [...] %}
```

**Riesgo residual**: Nulo para el comportamiento actual. El contexto del route queda ignorado dentro del bloque pero no genera error.

---

## 5. Clases CSS nuevas requeridas

| Clase CSS | Archivo | Propósito | Tokens utilizados |
|-----------|---------|-----------|------------------|
| `.seccion-alertas` | `app.css` | Wrapper semántico del bloque de alertas; sin estilos adicionales (hereda gap de `.main-content`) | — |
| `.tarjetas-contenido` | `app.css` | Grid de 3 columnas para tarjetas de contenido de apoyo | `--space-4`, `--radius-lg` |
| `.tarjeta-metrica__tendencia` | `app.css` | Texto de tendencia en tarjeta métrica | `--space-1`, tamaño 13px |
| `.tarjeta-metrica__tendencia--positiva` | `app.css` | Tendencia positiva | `--color-success` |
| `.tarjeta-metrica__tendencia--negativa` | `app.css` | Tendencia negativa | `--color-danger` |
| `.tarjeta-metrica__tendencia--neutra` | `app.css` | Tendencia neutra o vacía | `--color-text-muted` |
| `.estado-vacio--bloque` | `app.css` | Estado vacío como sección de ancho completo (diferente al `inline-flex` existente) | `--color-text-muted`, `--space-8` |

**Regla**: Ninguna de estas clases usa valores de color o espaciado hardcodeados. Todas consumen variables CSS de `:root`.

---

## 6. Auditoría de tokens canónicos

Verificación de `app/static/css/app.css` contra `frontend.instructions.md` §4:

| Token | Valor canónico | Valor en app.css | Estado |
|-------|---------------|-----------------|--------|
| `--color-bg` | `#ffffff` | `#ffffff` | ✅ |
| `--color-surface` | `#fafafa` | `#fafafa` | ✅ |
| `--color-text` | `#1a1a1a` | `#1a1a1a` | ✅ |
| `--color-text-muted` | `#6b7280` | `#6b7280` | ✅ |
| `--color-border` | `#e5e7eb` | `#e5e7eb` | ✅ |
| `--color-accent` | `#2563eb` | `#2563eb` | ✅ |
| `--color-success` | `#10b981` | `#10b981` | ✅ |
| `--color-warning` | `#f59e0b` | `#f59e0b` | ✅ |
| `--color-danger` | `#ef4444` | `#ef4444` | ✅ |
| `--color-info` | `#3b82f6` | `#3b82f6` | ✅ |
| `--space-1..--space-12` (7 vars) | Spec §4 | app.css `:root` | ✅ |
| `--radius-sm/md/lg` | 6px/10px/16px | 6px/10px/16px | ✅ |
| `--shadow-sm/md/lg` | Spec §4 | app.css `:root` | ✅ |
| `--font-sans`, `--font-size-base`, `--line-height-base` | Spec §4 | app.css `:root` | ✅ |

**Veredicto: 0 desviaciones de tokens. No se modifica `:root` en esta spec.**

---

## 7. Resumen de decisiones

| Decisión | Elegida | Descartadas |
|----------|---------|------------|
| Archivo de Home | `dashboard.html` (existente) | Crear `index.html` nuevo |
| Origen de datos | `{% set %}` hardcodeado en template | Contexto de route, DB real |
| Estado vacío/error | Comentarios `<!-- TODO -->` en secciones | Bloques condicionales Jinja2 |
| Accesos rápidos destinos | `href="#"` placeholder | URLs hardcodeadas de módulos inexistentes |
| Tokens canónicos | Sin cambios | Cualquier variante de paleta |
