# Especificacion de la funcionalidad: Edicion de propiedad

**Rama de la funcionalidad**: `[008-editar-propiedad]`

**Creado**: 2026-07-12

**Estado**: Borrador

**Entrada**: Usuario solicita una nueva spec para editar propiedades desde el dashboard/listado, con formulario precargado, validaciones consistentes con la creacion y redireccion de exito al listado de propiedades.

## Clarificaciones

- La edicion se abre desde cada card de propiedad y recibe el id de la propiedad como identificador de la vista.
- La edicion incluye como campos editables titulo, direccion, ciudad, precio_mensual, habitaciones, banos y area_m2; estado se mantiene como selector desplegable.
- La ruta canónica de edicion es `/propiedades/editar/{id}`.
- La confirmacion de exito al volver al listado usa un query param especifico de edicion distinto al de alta.
- El formulario de edicion precarga los valores actuales de la propiedad antes de que el usuario cambie cualquier dato.
- En el flujo web, los errores de dominio se devuelven como HTML con mensajes inline por campo, no como JSON tecnico de validacion.

## Objetivo

Permitir que un usuario edite una propiedad existente desde el flujo actual del dashboard/listado, con un formulario consistente con el alta, validaciones de dominio equivalentes y una experiencia de error clara que conserve los cambios introducidos por el usuario cuando la validacion falle.

## Alcance

- Agregar una accion de edicion en cada card de propiedad del dashboard/listado.
- Abrir una pagina de edicion a partir del id de la propiedad seleccionada.
- Precargar el formulario con los datos actuales de la propiedad.
- Renderizar todos los campos como cajas de texto excepto el estado, que debe mostrarse como un desplegable con el valor actual seleccionado.
- Reutilizar las reglas de validacion de dominio ya establecidas para la creacion de propiedades.
- Rechazar cambios invalidos sin persistir modificaciones parciales.
- Mantener el formulario visible con errores inline por campo cuando la validacion falle.
- Redirigir al listado de propiedades con confirmacion visible cuando la edicion termine con exito.
- Evitar respuestas tecnicas JSON 422 en envios vacios o incompletos dentro del flujo web, sustituyendolas por HTML con errores de dominio.
- Mantener la coherencia con la experiencia visual y de navegacion existente.

## No alcance

- Crear propiedades nuevas.
- Eliminar propiedades.
- Cambiar el modelo de datos de la propiedad o agregar campos nuevos.
- Introducir nuevos filtros, busquedas o ordenamientos en el listado.
- Redisenar el dashboard o el layout global fuera de lo necesario para exponer la accion de edicion.
- Cambiar la paleta visual, tokens o sistema de iconos.
- Convertir el flujo en una SPA o mover la logica a un cliente separado.

## User Stories con Prioridad

### Historia 1 - Abrir y guardar edicion basica (Prioridad: P1)

Como usuario, quiero abrir la pantalla de edicion desde una card de propiedad y guardar cambios validos, para actualizar una propiedad sin abandonar el flujo de listado.

**Por que esta prioridad**: entrega el valor central de la feature y valida el recorrido completo de edicion exitoso.

**Prueba independiente**: desde el listado, abrir una propiedad existente, verificar que el formulario esta precargado y guardar cambios validos para confirmar que la edicion finaliza con redireccion al listado.

**Escenarios de aceptacion**:

1. **Dado** que el usuario ve una card de propiedad, **cuando** selecciona Editar, **entonces** se abre la pagina de edicion de esa propiedad.
2. **Dado** que la pagina de edicion se abre correctamente, **cuando** el formulario carga, **entonces** los campos muestran los valores actuales y el estado queda seleccionado segun la propiedad.
3. **Dado** que el usuario guarda una edicion valida, **cuando** el sistema procesa el cambio, **entonces** la propiedad se actualiza y el usuario vuelve al listado con confirmacion de exito.

### Historia 2 - Validacion de dominio y conservacion del formulario (Prioridad: P2)

Como usuario, quiero recibir errores claros si envio valores invalidos, para corregir la informacion antes de guardar.

**Por que esta prioridad**: evita cambios inconsistentes y mantiene la calidad del dato.

**Prueba independiente**: enviar la pagina de edicion con campos vacios, con espacios solamente o con valores fuera de rango y verificar que no se persiste ningun cambio.

**Escenarios de aceptacion**:

1. **Dado** que el usuario envia un valor vacio o compuesto solo por espacios, **cuando** el sistema valida el formulario, **entonces** marca el campo como obligatorio.
2. **Dado** que el precio mensual es menor o igual a cero, **cuando** se valida el formulario, **entonces** se rechaza la edicion.
3. **Dado** que habitaciones queda fuera del rango de 1 a 15, **cuando** se valida el formulario, **entonces** se rechaza la edicion.
4. **Dado** que banos queda fuera del rango de 0.5 a 8.0 o no respeta pasos de 0.5, **cuando** se valida el formulario, **entonces** se rechaza la edicion.
5. **Dado** que una edicion es invalida, **cuando** el sistema responde, **entonces** conserva los valores ingresados y muestra errores inline por campo.

### Historia 3 - Flujo web sin 422 tecnico (Prioridad: P3)

Como usuario del navegador, quiero que los envios incompletos o vacios me devuelvan la vista con errores de dominio, para no enfrentar respuestas tecnicas que rompan la experiencia.

**Por que esta prioridad**: protege la experiencia web y evita que el formulario exponga detalles tecnicos al usuario final.

**Prueba independiente**: enviar un formulario vacio o incompleto desde la interfaz y confirmar que la respuesta sigue siendo HTML con errores de negocio, no un payload tecnico de validacion.

**Escenarios de aceptacion**:

1. **Dado** que el formulario llega vacio o incompleto, **cuando** se procesa el envio web, **entonces** el sistema devuelve la misma pantalla con errores de dominio en HTML.
2. **Dado** que la validacion falla, **cuando** la respuesta llega al navegador, **entonces** el usuario conserva el contexto visual de edicion y no pierde la informacion ya escrita.

## Casos Limite

- La propiedad editada contiene espacios iniciales, finales o multiples espacios intermedios en texto libre.
- El usuario intenta guardar sin modificar ningun campo.
- El usuario cambia solo el estado y deja intactos los demas valores.
- El usuario introduce un valor numerico con formato no valido o fuera del rango permitido.
- El formulario se envia con campos vacios desde un navegador o cliente que omite partes del payload.
- Dos envios consecutivos intentan guardar la misma edicion casi al mismo tiempo.
- La propiedad ya no existe cuando se abre o se guarda la vista de edicion.
- El cambio propuesto entra en conflicto con la identidad de negocio de otra propiedad existente.

## Requisitos Funcionales

- **FR-001**: El sistema DEBE exponer una accion Editar en cada card de propiedad del listado o dashboard.
- **FR-002**: La vista de edicion DEBE recibir el id de la propiedad y cargar los datos actuales asociados a ese id.
- **FR-003**: El formulario DEBE mostrar todos los campos editables como cajas de texto, excepto estado, que DEBE mostrarse como un desplegable.
- **FR-004**: El desplegable de estado DEBE abrirse con el valor actual seleccionado.
- **FR-005**: El sistema DEBE precargar el formulario con los valores existentes de la propiedad antes de que el usuario edite nada.
- **FR-006**: El sistema DEBE aplicar la misma normalizacion de texto que la creacion, incluyendo el recorte de espacios innecesarios.
- **FR-007**: El sistema DEBE tratar como vacio cualquier campo que contenga solo espacios en blanco.
- **FR-008**: El sistema DEBE rechazar la edicion si falta cualquier campo requerido o si el formulario llega incompleto.
- **FR-009**: El sistema DEBE validar precio_mensual como un valor mayor que 0.
- **FR-010**: El sistema DEBE validar habitaciones dentro del rango de 1 a 15.
- **FR-011**: El sistema DEBE validar banos dentro del rango de 0.5 a 8.0 con incrementos de 0.5.
- **FR-012**: El sistema DEBE mostrar errores inline por campo cuando la validacion falle.
- **FR-013**: El sistema NO DEBE persistir cambios si la validacion de dominio falla.
- **FR-014**: El sistema DEBE conservar el formulario con los valores introducidos por el usuario cuando exista un error de validacion.
- **FR-015**: El flujo web DEBE devolver HTML con errores de dominio para envios vacios o incompletos, evitando una respuesta tecnica JSON 422 en la experiencia de usuario.
- **FR-016**: El sistema DEBE permitir guardar una edicion valida y redirigir al listado de propiedades con una confirmacion visible de exito.
- **FR-017**: Si una edicion altera la identidad de negocio de la propiedad, el sistema DEBE mantener la coherencia con la regla de unicidad vigente para propiedades.

## Criterios de Aceptacion

- El usuario puede abrir la edicion desde una card del listado y ver la propiedad precargada.
- El formulario presenta el estado actual ya seleccionado y el resto de campos como cajas de texto.
- Una edicion valida se guarda y retorna al listado con confirmacion de exito.
- Una edicion invalida no persiste cambios y muestra errores inline por campo.
- Los envios vacios o incompletos del flujo web devuelven HTML con errores de dominio, no una respuesta tecnica 422.
- Los criterios de validacion coinciden con la regla vigente de la creacion de propiedades.

## Key Entities

- **Propiedad**: Registro editable que representa un inmueble existente; incluye titulo, direccion, ciudad, precio_mensual, habitaciones, banos, area_m2 y estado.
- **Formulario de edicion de propiedad**: Vista con los valores actuales de la propiedad y los cambios introducidos por el usuario.
- **Errores de validacion de propiedad**: Mensajes asociados a cada campo cuando una edicion no cumple las reglas de dominio.
- **Estado de propiedad**: Catalogo cerrado de estados permitidos para la propiedad, con un valor actual seleccionado en la edicion.

## Criterios de Exito

- **SC-001**: El 100% de los recorridos validos de edicion terminan en redireccion al listado con confirmacion visible de exito.
- **SC-002**: El 100% de los envios invalidos se rechazan sin persistir cambios y muestran errores inline por campo.
- **SC-003**: El 100% de los formularios abiertos desde una card muestran los datos actuales de la propiedad antes de editarse.
- **SC-004**: El 100% de los envios vacios o incompletos desde el navegador reciben HTML con errores de dominio en lugar de una respuesta tecnica JSON 422.
- **SC-005**: El 100% de las validaciones de la edicion mantienen la misma politica de recorte, requeridos y rangos de negocio que el alta.

## Riesgos y Dependencias

- Dependencia del flujo actual del dashboard/listado para exponer la accion Editar en cada card.
- Dependencia de la estructura vigente del dominio de propiedades y de sus reglas de unicidad.
- Riesgo de inconsistencia si la edicion no reutiliza exactamente los mismos criterios de validacion que la creacion.
- Riesgo de exponer una experiencia confusa si el error inline no conserva los valores escritos por el usuario.
- Riesgo de romper la navegacion existente si la pagina de edicion no respeta el comportamiento visual y de retorno al listado.

## Preguntas Abiertas

No hay preguntas abiertas bloqueantes para esta especificacion.

## Assumptions

- Se reutiliza el layout, la navegacion y los estilos existentes sin cambios de tokens visuales.
- La edicion opera sobre una propiedad ya existente y valida en el sistema.
- La identidad de negocio de la propiedad sigue basandose en titulo, direccion y ciudad.
- El usuario accede a la edicion desde el flujo web actual, no desde una API publica independiente.
