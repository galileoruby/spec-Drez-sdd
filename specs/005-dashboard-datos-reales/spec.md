# Feature Specification: Dashboard con datos reales

**Feature Branch**: `[005-dashboard-datos-reales]`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "Reemplazar el mock actual del dashboard principal por datos reales de base de datos para las métricas de propiedades, manteniendo la arquitectura vertical slice y el contrato de contexto de la home."

## Objetivo

Sustituir los valores mock del dashboard principal por métricas reales persistidas para propiedades disponibles y rentadas, sin ampliar el dominio funcional ni alterar el contrato de contexto que consume la vista principal.

## Alcance

- Obtener desde datos persistidos el conteo de propiedades en estado disponible.
- Obtener desde datos persistidos el conteo de propiedades en estado rentada.
- Reemplazar en la home los valores hardcodeados de ambas métricas.
- Mantener el orden y la estructura del contexto de render actual (métricas y accesos).
- Mantener ingresos y vencidos en estado no operativo explícito dentro del contexto de home.

## No Alcance

- Crear módulos nuevos de rentas, pagos o facturación.
- Rediseñar UI, tokens visuales o estilos.
- Introducir dependencias nuevas.
- Implementar reporting, series históricas o analítica avanzada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Métricas reales en home (Priority: P1)

Como usuario de operación, quiero ver en el dashboard principal los conteos reales de propiedades disponibles y rentadas para tomar decisiones con datos actualizados.

**Why this priority**: Es la corrección funcional principal de la feature y elimina el riesgo de decisiones basadas en datos ficticios.

**Independent Test**: Puede probarse cargando datos de propiedades en distintos estados y verificando que la home refleja exactamente esos conteos para disponibles y rentadas.

**Acceptance Scenarios**:

1. **Given** existen propiedades persistidas en distintos estados, **When** se carga la home, **Then** la métrica de disponibles coincide con el conteo real en base de datos.
2. **Given** existen propiedades persistidas en distintos estados, **When** se carga la home, **Then** la métrica de rentadas coincide con el conteo real en base de datos.
3. **Given** cambian los estados persistidos entre consultas, **When** se recarga la home, **Then** los valores de disponibles y rentadas reflejan el estado actual persistido.

---

### User Story 2 - Contrato de contexto estable (Priority: P2)

Como mantenedor del sistema, quiero conservar la estructura y orden del contexto de la home para evitar regresiones en el render y en componentes existentes.

**Why this priority**: Reduce riesgo de rompimientos colaterales y permite evolución segura sobre la UI existente.

**Independent Test**: Puede probarse comparando la estructura del contexto de métricas y accesos antes y después del cambio, validando compatibilidad.

**Acceptance Scenarios**:

1. **Given** la vista home espera un contrato de contexto definido, **When** se integra la fuente real de datos, **Then** se mantiene el mismo orden y estructura de métricas y accesos.
2. **Given** ingresos y vencidos no tienen modelo completo para cálculo real, **When** se renderiza la home, **Then** ambos permanecen en modo no operativo explícito sin simulaciones nuevas.

---

### User Story 3 - Señal de estado vacío real (Priority: P3)

Como usuario, quiero que el estado vacío del dashboard responda a la existencia real de datos para entender correctamente si hay información operativa.

**Why this priority**: Evita mensajes engañosos y mejora la confiabilidad percibida del dashboard.

**Independent Test**: Puede probarse con dos escenarios: base sin propiedades y base con propiedades, verificando el comportamiento del banner de estado vacío.

**Acceptance Scenarios**:

1. **Given** no existen propiedades persistidas, **When** se carga la home, **Then** el estado vacío se muestra de forma coherente con la ausencia real de datos.
2. **Given** existen propiedades persistidas, **When** se carga la home, **Then** el estado vacío no se muestra como si faltaran datos.

---

### Edge Cases

- ¿Qué ocurre cuando existen propiedades, pero ninguna está en estado disponible ni rentada?
- ¿Cómo se comporta la home si ocurre un fallo temporal de consulta de datos al calcular métricas?
- ¿Qué valor se presenta cuando hay estados no operativos (ingresos/vencidos) sin modelo de cálculo real?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE calcular y exponer para la home el conteo real de propiedades en estado disponible.
- **FR-002**: El sistema DEBE calcular y exponer para la home el conteo real de propiedades en estado rentada.
- **FR-003**: La home DEBE dejar de usar valores hardcodeados para disponibles y rentadas.
- **FR-004**: El sistema DEBE conservar el contrato de contexto de la home en orden y estructura de métricas y accesos.
- **FR-005**: El sistema DEBE mantener ingresos y vencidos en modo no operativo explícito durante esta feature, sin cálculos inventados.
- **FR-006**: El estado vacío de la home DEBE determinarse con base en la existencia real de datos persistidos.
- **FR-007**: El flujo de obtención de métricas DEBE resolverse en la capa de servicio del dashboard y consumir datos persistidos a través de acceso de datos del módulo.
- **FR-008**: En esta feature no se DEBEN crear nuevos dominios funcionales para rentas o pagos.
- **FR-009**: En esta feature no se DEBEN introducir cambios de diseño visual; aplica la gobernanza vigente.
- **FR-010**: La solución DEBE incluir pruebas que cubran cálculo de métricas y render de home con datos reales.
- **FR-011**: La spec DEBE dejar explícito lo pendiente para una spec futura sobre ingresos y vencidos reales.
- **FR-012**: Solo se DEBE definir endpoint adicional si aporta valor funcional concreto para refresco parcial; si no aporta valor, se DEBE documentar que no se requiere endpoint nuevo en esta spec.

## Visual Tokens Governance *(mandatory)*

- **Token Impact**: No changes.
- **Explicit Authorization**: No se autorizan cambios visuales en esta feature.
- **Task Traceability**: No aplica para cambios visuales; aplica la gobernanza vigente.
- **Operational Source**: `.github/instructions/frontend.instructions.md`.

### Key Entities *(include if feature involves data)*

- **MetricaDashboard**: Representa un valor de tarjeta de dashboard con su etiqueta operativa y estado de disponibilidad funcional.
- **ResumenPropiedades**: Agregado de conteos operativos de propiedades por estado (disponible y rentada) para render en home.
- **EstadoHome**: Representa la condición de datos para decidir si corresponde mostrar estado vacío.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En un conjunto de prueba con datos conocidos, el 100% de las cargas de home muestra el conteo correcto de disponibles y rentadas.
- **SC-002**: La home ya no presenta valores hardcodeados para disponibles y rentadas en ningún escenario validado de prueba.
- **SC-003**: El comportamiento del banner de estado vacío coincide con el estado real de datos en el 100% de escenarios de prueba (sin datos vs. con datos).
- **SC-004**: La suite de pruebas de la feature incluye cobertura verificable para cálculo de métricas y render de home con datos reales.
- **SC-005**: Queda documentado de forma explícita el pendiente funcional para ingresos y vencidos reales, sin deuda ambigua para la siguiente spec.

## Assumptions

- La base de propiedades y sus estados operativos ya están disponibles y consistentes para cómputo de métricas.
- El contrato actual del contexto de la home (orden y estructura) es el que se debe preservar para compatibilidad.
- Ingresos y vencidos permanecen visibles como métricas no operativas sin cálculo real durante esta feature.
- No se requiere endpoint adicional para esta iteración salvo que en planificación se demuestre un beneficio funcional concreto de refresco parcial.

## Riesgos y Dependencias

- **Dependencia**: Calidad y consistencia de los estados persistidos de propiedades para evitar conteos erróneos.
- **Dependencia**: Contrato de contexto existente en la home y componentes asociados.
- **Riesgo**: Introducir cambios de estructura del contexto podría romper render existente.
- **Riesgo**: Tratar ingresos/vencidos como operativos sin modelo de datos generaría expectativas incorrectas.

## Pendientes para Spec Futura

- Definir modelo funcional para cálculo real de ingresos.
- Definir modelo funcional para cálculo real de vencidos.
- Establecer reglas de negocio y fuentes de datos para métricas financieras y de cobranza.

## Preguntas Abiertas

No hay preguntas abiertas críticas para cerrar esta spec. Las decisiones no definidas se acotan en la sección "Pendientes para Spec Futura".
