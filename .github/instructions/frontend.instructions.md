---
applyTo: "app/modules/**/templates/**,app/templates/**,app/static/**"
---

# Frontend — Jinja2 + HTMX + sistema visual

Este archivo es la **fuente única de verdad** para todo lo relacionado con
presentación, estructura de templates, estilos y experiencia de usuario.
También es la **fuente operativa obligatoria** para la definición, uso y
gobernanza de los tokens visuales del proyecto.
Copilot lo aplica automáticamente al trabajar en cualquier archivo bajo
`app/modules/**/templates/`, `app/templates/` o `app/static/`.

Referencia visual: **Notion, Google Keep, dashboards de gestión modernos**.

---

## 1. Principios técnicos

- Server-rendered. La UI se compone en el servidor con Jinja2.
- Interactividad con HTMX, no con SPA frameworks ni JS custom complejo.
- CSS 100% propio en `app/static/css/app.css`. PROHIBIDO Bootstrap,
  Tailwind, Bulma, Foundation o similares.
- HTMX vendoreado en `app/static/vendor/htmx.min.js`. PROHIBIDO cargarlo
  desde CDN.

## 2. Principios de experiencia

- **Claridad sobre densidad**: prefiere espacio en blanco a empacar
  información.
- **Consistencia sobre creatividad puntual**: los mismos elementos se ven
  y comportan igual en toda la app.
- **Acciones evidentes**: botones primarios destacan, secundarios
  acompañan, destructivos avisan.
- **Estados explícitos**: cargando, vacío, error y éxito son siempre
  visibles, nunca implícitos.

## 3. Layout global

- **Desktop-first** con adaptación responsive a tablet y móvil.
- Composición: **sidebar lateral fija** + **área de contenido principal**.
- En tablet/móvil la sidebar colapsa a menú toggleable (hamburguesa).
- Ancho máximo del contenido principal: contenedor centrado con padding
  generoso (mínimo `var(--space-6)` lateral en desktop).

Estructura visual:

```
┌──────────┬───────────────────────────────────────┐
│          │  Navbar (breadcrumbs, acciones, user) │
│ Sidebar  ├───────────────────────────────────────┤
│  fija    │                                       │
│          │  Contenido principal                  │
│          │                                       │
└──────────┴───────────────────────────────────────┘
```

## 4. Sistema de diseño (tokens)

Todos los valores visuales se consumen vía variables CSS declaradas en
`:root` de `app/static/css/app.css`. NUNCA hardcodear colores, espaciados,
radios o sombras en componentes.

Regla operativa: cualquier cambio en tokens visuales DEBE estar explícitamente
autorizado por una spec aprobada y trazado a tareas concretas en `tasks.md`.

### Color (paleta neutra + acento)

| Token                  | Uso                                    |
|------------------------|----------------------------------------|
| `--color-bg`           | Fondo principal de la app              |
| `--color-surface`      | Fondo de cards y paneles               |
| `--color-text`         | Texto primario                         |
| `--color-text-muted`   | Texto secundario / labels              |
| `--color-border`       | Bordes sutiles                         |
| `--color-accent`       | Acción primaria, enlaces activos       |
| `--color-success`      | Estado éxito                           |
| `--color-warning`      | Estado advertencia                     |
| `--color-danger`       | Estado error                           |
| `--color-info`         | Estado informativo                     |

### Espaciado (escala)

`--space-1` 4px, `--space-2` 8px, `--space-3` 12px, `--space-4` 16px,
`--space-6` 24px, `--space-8` 32px, `--space-12` 48px.

### Radios

`--radius-sm` 6px, `--radius-md` 10px, `--radius-lg` 16px.

### Sombras

`--shadow-sm` (cards en reposo), `--shadow-md` (cards hover / dropdowns),
`--shadow-lg` (modales / popovers).

### Tipografía

- Familia: `system-ui` stack (sin fuentes custom en el bootstrap inicial).
- Tamaño base: 15px, line-height 1.55.
- Escala: h1 28px / h2 22px / h3 18px / body 15px / caption 13px.
- Pesos: 400, 500 (medio), 600 (semibold para títulos y acciones).

### Valores concretos obligatorios para `:root` de proyecto

Los siguientes tokens son canónicos y DEBEN mantenerse exactamente en `app/static/css/app.css`.
No se permite sustituir la paleta por variantes “equivalentes”, reinterpretaciones estéticas ni cambios implícitos durante la implementación.

Cualquier cambio de token visual requiere:
1. una spec aprobada,
2. actualización explícita de este archivo,
3. actualización explícita de `.specify/memory/constitution.md`,
4. trazabilidad en `tasks.md`.

```css
:root {
  --color-bg: #ffffff;
  --color-surface: #fafafa;
  --color-text: #1a1a1a;
  --color-text-muted: #6b7280;
  --color-border: #e5e7eb;
  --color-accent: #2563eb;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-danger: #ef4444;
  --color-info: #3b82f6;

  --space-1: 4px;  --space-2: 8px;   --space-3: 12px;
  --space-4: 16px; --space-6: 24px;  --space-8: 32px;
  --space-12: 48px;

  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 16px;

  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
  --shadow-lg: 0 10px 24px rgba(0,0,0,0.10);

  --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-size-base: 15px;
  --line-height-base: 1.55;
}
```

## 5. Iconografía

- **SVG outline**, vendoreados uno por archivo en `app/static/icons/`.
- Librería estándar: **Lucide** (https://lucide.dev), licencia ISC.
- Tamaño base: 20×20 o 24×24 según contexto. Trazo: 2px.
- Color: heredado vía `currentColor`. NUNCA hardcodear `fill` o `stroke`.
- Patrón de uso: macro Jinja2 `{{ icon("nombre") }}` que inyecta el SVG
  inline desde `app/static/icons/<nombre>.svg`.
- PROHIBIDO usar iconos como webfont, emojis o caracteres Unicode como
  íconos funcionales.

### Set inicial vendoreado en spec 001

`layout-dashboard`, `building-2`, `users`, `file-text`, `wallet`, `wrench`,
`settings`, `menu`, `x`, `check-circle-2`, `alert-triangle`, `alert-circle`,
`info`.

Cada nuevo icono se agrega en una tarea explícita de la spec que lo
necesite.

## 6. Componentes obligatorios y reutilizables

Viven en `app/templates/components/` como parciales Jinja2 reutilizables.

| Componente            | Archivo                       | Propósito                                              |
|-----------------------|-------------------------------|--------------------------------------------------------|
| Sidebar               | `_sidebar.html`               | Navegación principal lateral                           |
| Navbar                | `_navbar.html`                | Barra superior con breadcrumbs y acciones              |
| Card de propiedad     | `_card_propiedad.html`        | Vista compacta de una propiedad                        |
| Tarjeta de métrica    | `_tarjeta_metrica.html`       | KPI con número grande, label, tendencia, icono         |
| Accesos rápidos       | `_accesos_rapidos.html`       | Grid de atajos a acciones frecuentes                   |
| Badge de estado       | `_badge_estado.html`          | Píldora con color por estado del dominio               |
| Campo de formulario   | `_form_field.html`            | Label + input + error inline + helper text             |
| Alerta / flash        | `_alerta.html`                | Banner dismissible en 4 variantes                      |

Reglas comunes:

- Cada componente recibe sus datos por contexto Jinja2, no hace llamadas
  a servicios ni a la base de datos.
- Los componentes NO contienen lógica de negocio. Si necesitan formatear,
  lo hacen vía filtros Jinja2 declarados en `app/templates/macros/`.

## 7. Estados y feedback

- **Cargando**: indicadores HTMX (`hx-indicator`) con spinner SVG propio.
- **Vacío**: cuando una lista no tiene resultados, mostrar estado vacío
  con icono, mensaje y CTA cuando aplique.
- **Error**: mensajes de error inline en formularios; banner de alerta
  para errores globales.
- **Éxito**: mensajes flash post-acción vía `hx-swap-oob="true"` a un
  `#flash-zone` definido en `base.html`.

## 8. Estados del dominio y colores de badge

Los estados del dominio se modelan con `Enum` en el backend y se mapean
visualmente así (referencial; ajustar al introducir cada feature):

| Estado de propiedad   | Color token         |
|-----------------------|---------------------|
| Disponible            | `--color-success`   |
| Rentada               | `--color-accent`    |
| En mantenimiento      | `--color-warning`   |
| Inactiva              | `--color-text-muted`|

| Estado de pago        | Color token         |
|-----------------------|---------------------|
| Pagado                | `--color-success`   |
| Pendiente             | `--color-warning`   |
| Vencido               | `--color-danger`    |

## 9. Estructura de templates

```
app/templates/
  base.html                    # Layout base: sidebar + main + flash
  components/
    _sidebar.html
    _navbar.html
    _card_propiedad.html
    _tarjeta_metrica.html
    _accesos_rapidos.html
    _badge_estado.html
    _alerta.html
    _form_field.html
  macros/
    icons.html                 # Macro icon(nombre, size, class)
app/modules/<feature>/templates/
  *.html                       # Vistas del módulo
  _*.html                      # Parciales HTMX (fragmentos para swap)
```

## 10. Patrón HTMX

- Endpoints de página completa retornan template extendiendo `base.html`.
- Endpoints de fragmento retornan solo el partial sin layout.
- Atributos `hx-get`, `hx-post`, `hx-target`, `hx-swap` explícitos.
- Preferir `hx-swap="outerHTML"` para reemplazos de cards/filas completas.
- Mensajes flash post-acción: parcial de alerta con `hx-swap-oob="true"`
  apuntando a `#flash-zone` en `base.html`.

## 11. CSS — organización de `app.css`

```css
/* ============ 1. Reset y base ============ */
/* ============ 2. Variables (tokens) ============ */
/* ============ 3. Tipografía ============ */
/* ============ 4. Layout (sidebar + main) ============ */
/* ============ 5. Componentes ============ */
/* ============ 6. Utilidades ============ */
/* ============ 7. Responsive (media queries) ============ */
```

### Convenciones

- Nombres de clase en kebab-case: `.card-propiedad`,
  `.badge-estado--rentada`.
- Modificadores con doble guión: `.btn--primary`, `.alerta--danger`.
- **Desktop-first**: estilos base para desktop, media queries hacia abajo
  (`max-width`).
- PROHIBIDO estilos inline excepto estados controlados por HTMX (ej.
  `style="display:none"` como estado inicial).

## 12. Accesibilidad mínima

- `<label for>` asociado a cada input.
- Atributos `aria-*` cuando aplique (`aria-current`, `aria-label`,
  `aria-expanded`).
- Foco visible siempre. NUNCA `outline: none` sin reemplazo propio.
- Contraste mínimo AA en texto sobre fondo.
- Botones con `<button>`, enlaces con `<a>`. PROHIBIDO `<div onclick>`.