# Feature Specification: Pagina de propiedades en cards

**Feature Branch**: `[006-pagina-propiedades-cards]`

**Created**: 2026-07-10

**Status**: Draft

**Input**: User description: "Crear una pagina server-rendered de propiedades que liste todas las propiedades persistidas en la base de datos en formato de cards, con endpoint dedicado y navegacion lateral conectada."

## Clarifications

### Session 2026-07-10

- Q: Cual es la ruta canonica de la pagina de propiedades? -> A: `GET /propiedades`.
- Q: Cual es la estrategia de fallback de imagen cuando no exista `imagen_url` utilizable? -> A: usar imagen de fallback fija local del proyecto.
- Q: Cual es la estrategia de componente para las cards de propiedades? -> A: reutilizar y ajustar `app/templates/components/_card_propiedad.html`.
- Q: Cual es el orden del listado de propiedades? -> A: ordenar por `created_at` descendente (mas recientes primero).
- Q: Cual es la regla visual para textos largos en titulo/direccion? -> A: truncado multilinea con ellipsis (titulo maximo 2 lineas, direccion maximo 2 lineas).

## Objetivo

Habilitar una pagina navegable de propiedades server-rendered en la ruta `GET /propiedades` que consulte datos reales persistidos y los renderice en un grid responsive de cards dentro del layout existente, conectando el enlace "Propiedades" del sidebar a esa ruta.

## Alcance incluido

- Crear un endpoint `GET` dedicado para listar propiedades.
- Consultar propiedades persistidas desde base de datos mediante servicio y repositorio.
- Consultar propiedades persistidas desde base de datos mediante servicio y repositorio, ordenadas por `created_at` descendente.
- Renderizar una pagina server-rendered con cards de propiedades.
- Reutilizar el componente `app/templates/components/_card_propiedad.html` con los ajustes minimos requeridos por el contrato de datos de esta pagina.
- Mostrar por card: imagen, titulo, direccion, habitaciones, banos, area m2, precio de renta y estado.
- Cumplir comportamiento responsive: 3 columnas desktop, 2 tablet, 1 phone.
- Conectar el enlace de sidebar "Propiedades" hacia la nueva ruta.
- Definir contrato de contexto hacia template y pruebas minimas para endpoint + render.

## No alcance

- Crear dominio nuevo de rentas, pagos, inquilinos o contratos.
- Implementar filtros, busqueda, paginacion u ordenamiento.
- Introducir dependencias nuevas.
- Redisenar layout global, navbar o sidebar fuera del enlace necesario.
- Cambiar tokens visuales globales o paleta.
- Implementar acciones CRUD adicionales desde esta pantalla.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Listado navegable de propiedades reales (Priority: P1)

Como usuario operativo, quiero abrir una pagina de propiedades desde el menu lateral para ver todas las propiedades persistidas en formato de cards.

**Why this priority**: Entrega el valor funcional principal: ruta real + datos reales + visualizacion utilizable.

**Independent Test**: Navegar al endpoint de propiedades y verificar que cada registro persistido se renderiza como una card con los campos visibles requeridos.

**Acceptance Scenarios**:

1. **Given** existen propiedades persistidas, **When** el usuario abre la ruta de propiedades, **Then** el sistema consulta base de datos y renderiza una card por propiedad.
2. **Given** el usuario esta en dashboard, **When** hace clic en "Propiedades" en sidebar, **Then** navega correctamente a la nueva ruta de listado.

---

### User Story 2 - Layout responsive y consistencia visual (Priority: P2)

Como usuario en distintos dispositivos, quiero que las cards se distribuyan correctamente por columnas segun el tamano de pantalla.

**Why this priority**: Garantiza usabilidad y legibilidad en desktop, tablet y telefono sin romper el layout existente.

**Independent Test**: Validar en breakpoints definidos que la grilla muestra 3, 2 y 1 card por fila respectivamente, manteniendo el layout base.

**Acceptance Scenarios**:

1. **Given** viewport desktop, **When** se renderiza la pagina, **Then** se muestran 3 cards por fila.
2. **Given** viewport tablet, **When** se renderiza la pagina, **Then** se muestran 2 cards por fila.
3. **Given** viewport phone, **When** se renderiza la pagina, **Then** se muestra 1 card por fila.

---

### User Story 3 - Robustez ante datos incompletos y vacios (Priority: P3)

Como usuario, quiero que la pagina siga siendo clara cuando no hay propiedades o cuando algun dato visible no viene completo.

**Why this priority**: Evita pantallas rotas y reduce ambiguedad operativa en escenarios reales de datos.

**Independent Test**: Ejecutar escenarios sin propiedades y con propiedades con imagen faltante o textos largos y verificar salida consistente.

**Acceptance Scenarios**:

1. **Given** no existen propiedades, **When** se abre la pagina, **Then** se muestra estado vacio server-rendered sin error.
2. **Given** una propiedad no tiene imagen utilizable, **When** se renderiza la card, **Then** se muestra imagen de fallback definida por contrato.
3. **Given** titulo o direccion exceden longitud habitual, **When** se renderiza la card, **Then** la informacion se mantiene legible sin desbordar el layout.

---

### Edge Cases

- No existen propiedades en base de datos.
- Existe una propiedad sin imagen utilizable.
- Existen textos largos en titulo o direccion.
- Existen propiedades con estados distintos de disponible/rentada.
- Existen muchas propiedades y el usuario navega en pantalla pequena.
- Direccion o area exceden el espacio visual esperado de la card.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE exponer la ruta `GET /propiedades` como pagina navegable de propiedades.
- **FR-002**: La ruta DEBE consultar propiedades reales persistidas mediante servicio y repositorio.
- **FR-002**: La ruta DEBE consultar propiedades reales persistidas mediante servicio y repositorio, ordenadas por `created_at` descendente.
- **FR-003**: El sistema DEBE renderizar una card por cada propiedad obtenida.
- **FR-003**: El sistema DEBE renderizar una card por cada propiedad obtenida reutilizando y ajustando el componente existente `app/templates/components/_card_propiedad.html`.
- **FR-004**: Cada card DEBE mostrar exactamente: imagen, titulo, direccion, habitaciones, banos, area m2, precio de renta y estado.
- **FR-004**: Cada card DEBE mostrar exactamente: imagen, titulo, direccion, habitaciones, banos, area m2, precio de renta y estado.
- **FR-004a**: Para textos largos, el titulo DEBE truncarse visualmente a maximo 2 lineas con ellipsis y la direccion DEBE truncarse visualmente a maximo 2 lineas con ellipsis.
- **FR-005**: El layout de cards DEBE mostrar 3 columnas en desktop.
- **FR-006**: El layout de cards DEBE mostrar 2 columnas en tablet.
- **FR-007**: El layout de cards DEBE mostrar 1 columna en phone.
- **FR-008**: El enlace "Propiedades" del sidebar DEBE redirigir a `GET /propiedades`.
- **FR-009**: La nueva pagina DEBE reutilizar el layout base existente del sistema.
- **FR-010**: El template DEBE recibir un contrato de contexto explicito para evitar acoplamiento implicito.
- **FR-011**: Si no existen propiedades, el sistema DEBE renderizar un estado vacio claro sin error.
- **FR-012**: Si falta imagen utilizable, el sistema DEBE usar una imagen de fallback fija local del proyecto, definida explicitamente en contrato.
- **FR-013**: El endpoint DEBE ser async y no debe contener logica de negocio en template.
- **FR-014**: La feature DEBE incluir pruebas minimas para repositorio/servicio, render HTML y navegacion al endpoint correcto.
- **FR-015**: Esta spec NO DEBE introducir filtros, busqueda, paginacion ni ordenamiento.
- **FR-016**: Esta spec NO DEBE introducir dominios nuevos ni cambios de tokens visuales globales; aplica la gobernanza vigente.

## Visual Tokens Governance *(mandatory)*

- **Token Impact**: No changes.
- **Explicit Authorization**: No se autorizan cambios de tokens visuales en esta feature.
- **Task Traceability**: No aplica para cambios de tokens en esta spec.
- **Operational Source**: `.github/instructions/frontend.instructions.md`.

### Key Entities *(include if feature involves data)*

- **PropiedadCardView**: Proyeccion de una propiedad para visualizacion en card, con campos visibles requeridos y fallback de imagen local.
- **ListadoPropiedadesContexto**: Contexto server-rendered que contiene la coleccion de cards y bandera de estado vacio.
- **RutaPropiedades**: Punto de entrada HTTP `GET /propiedades` para renderizar la pagina de propiedades con datos persistidos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de propiedades persistidas en el dataset de prueba se renderiza como card en la pagina de propiedades.
- **SC-002**: Cada card muestra el 100% de los campos visibles obligatorios definidos en FR-004.
- **SC-002**: Cada card muestra el 100% de los campos visibles obligatorios definidos en FR-004.
- **SC-002a**: En casos de textos extensos, titulo y direccion respetan el truncado multilinea 2+2 con ellipsis sin romper la grilla.
- **SC-003**: En validacion por breakpoints definidos, la grilla cumple 3/2/1 columnas en desktop/tablet/phone respectivamente.
- **SC-004**: El enlace "Propiedades" del sidebar redirige correctamente a la nueva ruta en el 100% de pruebas de navegacion.
- **SC-005**: Escenarios de estado vacio e imagen faltante se resuelven sin error y, para imagen faltante, con fallback local definido por contrato.
- **SC-006**: La suite minima de pruebas de endpoint + render + navegacion + estado vacio queda en verde.

## Assumptions

- El dominio de propiedades existente ya contiene los datos requeridos para poblar cards sin crear nuevas tablas.
- El layout base (`base.html`) y la estructura actual de sidebar/navbar se reutilizan sin rediseno global.
- El componente actual de card puede reutilizarse con ajustes de markup si hace falta para cumplir campos visibles y responsividad.
- El fallback de imagen se resolvera con un asset local del proyecto definido en el contrato de contexto sin nuevas dependencias.

## Riesgos y dependencias

- **Dependencia**: Calidad y completitud de datos persistidos de propiedades.
- **Dependencia**: Componente de sidebar actual para activar navegacion a ruta real.
- **Riesgo**: Acoplar logica de presentacion en template en lugar de contrato explicito de servicio.
- **Riesgo**: Degradacion de legibilidad con textos largos o en pantallas pequenas.
- **Riesgo**: Divergencia visual de card respecto al layout existente si no se limita el ajuste al alcance.

## Preguntas abiertas

No hay decisiones bloqueantes pendientes para cerrar esta spec.
