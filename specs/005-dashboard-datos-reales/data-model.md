# Data Model: 005-dashboard-datos-reales

## Alcance del modelo

Esta feature no introduce tablas ni migraciones nuevas. Se define un modelo de lectura y composición para el contexto de home usando el dominio ya persistido de propiedades.

## Entidades lógicas de aplicación

## 1. ConteoPropiedadesPorEstado

- **Tipo**: Proyección de lectura (no persistente)
- **Campos**:
  - `disponibles: int` (>= 0)
  - `rentadas: int` (>= 0)
- **Origen**: Agregación SQL sobre `propiedades.estado`.
- **Reglas**:
  - Si no hay filas para un estado, su valor debe ser `0`.
  - Solo considera estados operativos para esta feature: `disponible`, `rentada`.

## 2. MetricaHome

- **Tipo**: DTO de salida para template de dashboard
- **Campos**:
  - `titulo: str`
  - `valor: str`
  - `icono: str`
  - `tendencia: str` (vacía cuando no aplica)
  - `operativa: bool` (true para disponibles/rentadas, false para ingresos/vencidos)
- **Reglas**:
  - Debe mantener orden de presentación contractual.
  - Debe permitir marcar métricas no operativas explícitas sin cálculo real.

## 3. ContextoHomeDashboard

- **Tipo**: Agregado de render (no persistente)
- **Campos**:
  - `metricas: list[MetricaHome]`
  - `accesos_rapidos: list[dict[str, str]]` (estructura existente sin cambios)
  - `mostrar_estado_vacio: bool`
- **Reglas**:
  - `mostrar_estado_vacio = true` cuando no existan datos base para métricas operativas.
  - `metricas` conserva orden y estructura vigente del contrato de la home.

## Relación con modelo persistente existente

- `Propiedad.estado` (existente) es la única fuente para cálculo de métricas operativas de esta spec.
- No se modifica `EstadoPropiedad` ni constraints existentes.

## Transiciones de estado relevantes

No se introducen transiciones nuevas. Solo se consumen estados ya existentes:
- `disponible`
- `rentada`

## Validaciones funcionales

- Conteos nunca negativos.
- Home no muestra valores hardcodeados para disponibles/rentadas.
- Ingresos/vencidos se mantienen en estado no operativo explícito.
