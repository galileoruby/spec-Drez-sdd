# Research: 006-pagina-propiedades-cards

## Decision 1: Ruta canonica de pagina

- Decision: usar GET /propiedades como ruta principal navegable.
- Rationale: simplifica navegacion desde sidebar y pruebas de integracion.
- Alternatives considered:
  - /propiedades/cards: agrega complejidad sin valor funcional adicional.
  - /inventario/propiedades: introduce terminologia no requerida.

## Decision 2: Estrategia de componente visual

- Decision: reutilizar y ajustar app/templates/components/_card_propiedad.html.
- Rationale: evita duplicacion y conserva consistencia visual.
- Alternatives considered:
  - Crear nuevo componente: aumenta mantenimiento sin necesidad.
  - Markup inline en pagina: reduce reutilizacion y dificulta pruebas.

## Decision 3: Fuente y orden de datos

- Decision: listar propiedades reales desde repositorio/servicio, ordenadas por created_at descendente.
- Rationale: salida estable y verificable para pruebas y UX.
- Alternatives considered:
  - Sin orden explicito: resultados no deterministas.
  - Orden por titulo: no prioriza registros recientes.

## Decision 4: Fallback de imagen

- Decision: usar fallback local fijo del proyecto para imagen faltante.
- Rationale: evita dependencias externas y garantiza render estable.
- Alternatives considered:
  - URL externa: dependencia de red no requerida.
  - Sin fallback: cards incompletas y potencial ruptura visual.

## Decision 5: Regla para textos largos

- Decision: truncado multilinea con ellipsis (titulo maximo 2 lineas, direccion maximo 2 lineas).
- Rationale: preserva legibilidad y altura consistente de cards en responsive.
- Alternatives considered:
  - Texto completo sin limite: rompe layout en pantallas pequenas.
  - Truncado 1 linea: reduce legibilidad de informacion relevante.

## Resultado

No quedan decisiones bloqueantes para planificar tasks e implementacion.
