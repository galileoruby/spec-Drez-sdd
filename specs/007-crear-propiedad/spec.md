# Especificacion de la funcionalidad: Alta de propiedad

**Rama de la funcionalidad**: `[007-crear-propiedad]`

**Creado**: 2026-07-11

**Estado**: Borrador

**Entrada**: Usuario solicita crear una nueva especificacion para dar de alta propiedades desde una nueva pagina/formulario, con validaciones obligatorias, valores por defecto, generacion automatica de imagen y navegacion desde el navbar.

## Clarifications

### Session 2026-07-11

- Q: Para la alta, ¿ciudad y area_m2 tambien deben pedirse o generarse, o quedan fuera de alcance? -> A: La alta debe pedir y validar tambien ciudad y area_m2.
- Q: ¿Que rango de negocio debe usarse para habitaciones y baños? -> A: habitaciones 1-10 y banos 1.0-5.0.
- Q: Tras crear la propiedad con exito, ¿a donde debe ir el usuario? -> A: Redirigir al listado /propiedades con confirmacion de exito.

## Objetivo

Habilitar una experiencia server-rendered para crear una nueva propiedad desde el modulo de propiedades, accesible desde el boton Nueva propiedad del navbar, con validaciones claras, valor por defecto de estado disponible, id autogenerado e imagen generada automaticamente.

## Alcance

- Crear una nueva pagina de alta de propiedades dentro del flujo actual del modulo propiedades.
- Permitir registrar una propiedad con validacion obligatoria de campos y mensajes de error claros.
- Generar automaticamente el identificador de la nueva propiedad sin entrada manual del usuario.
- Asignar el estado disponible como valor por defecto al crear.
- Generar automaticamente la imagen de la propiedad usando el servicio Picsum.
- Definir un comportamiento claro ante falla temporal de Picsum sin bloquear la creacion.
- Conectar la navegacion desde el boton Nueva propiedad del navbar hacia la pagina de alta.
- Mantener el enfoque server-rendered con FastAPI, Jinja2 y HTMX.
- Respetar la arquitectura vertical slice del modulo propiedades.
- Incluir pruebas de validacion, creacion exitosa, navegacion y fallback.

## No alcance

- Editar propiedades existentes.
- Eliminar propiedades.
- Agregar filtros, busquedas o ordenamientos.
- Redisenar la experiencia global fuera de lo minimo necesario para habilitar la navegacion.
- Introducir frameworks CSS o JS externos.
- Convertir el flujo en una SPA o mover la logica a un cliente pesado.

## Historias de usuario priorizadas

### Historia 1 - Acceso a la alta y creacion exitosa (Prioridad: P1)

Como usuario operativo, quiero entrar a la pagina de alta desde el navbar y crear una propiedad valida, para registrar nuevos inmuebles sin salir del flujo actual.

**Por que esta prioridad**: entrega el valor principal de la funcionalidad y habilita el alta completa de una propiedad nueva.

**Prueba independiente**: desde la pagina actual, hacer clic en Nueva propiedad, completar el formulario con datos validos y verificar que la propiedad queda creada con id autogenerado, estado disponible, imagen asociada y redireccion al listado.

**Escenarios de aceptacion**:

1. **Dado** que el usuario esta en la interfaz actual, **cuando** hace clic en Nueva propiedad, **entonces** se abre la pagina de alta.
2. **Dado** que el usuario completa el formulario con datos validos, **cuando** envia la solicitud, **entonces** el sistema crea la propiedad, confirma el exito, no pide un id manual y redirige al listado.

---

### Historia 2 - Validacion estricta de campos (Prioridad: P2)

Como usuario, quiero recibir errores claros si faltan datos o si algun valor es invalido, para corregir el formulario antes de guardar.

**Por que esta prioridad**: evita registros inconsistentes y hace confiable el proceso de alta.

**Prueba independiente**: enviar formularios con campos vacios, con espacios solamente, con precio invalido o con habitaciones y banos fuera de rango, y verificar que no se crea ningun registro.

**Escenarios de aceptacion**:

1. **Dado** que falta titulo, direccion, precio_mensual, habitaciones o banos, **cuando** se envia el formulario, **entonces** la creacion se rechaza y se muestran errores por campo.
2. **Dado** que un campo contiene solo espacios, **cuando** se envia el formulario, **entonces** el sistema lo trata como vacio.
3. **Dado** que precio_mensual es vacio, no numerico o menor o igual a cero, **cuando** se envia el formulario, **entonces** la creacion se rechaza.
4. **Dado** que habitaciones o banos estan vacios, no son numericos o estan fuera del rango de negocio, **cuando** se envia el formulario, **entonces** la creacion se rechaza.

---

### Historia 3 - Robustez ante falla de imagen externa (Prioridad: P3)

Como usuario, quiero que la alta siga funcionando aunque Picsum falle temporalmente, para no perder el registro por una dependencia externa.

**Por que esta prioridad**: protege el flujo principal frente a una dependencia externa no controlada por el usuario.

**Prueba independiente**: simular una falla temporal de Picsum y verificar que la propiedad se crea igual usando una imagen de respaldo local.

**Escenarios de aceptacion**:

1. **Dado** que Picsum no responde temporalmente, **cuando** el usuario crea una propiedad valida, **entonces** el sistema completa la alta usando una imagen de respaldo local.
2. **Dado** que la imagen externa falla, **cuando** termina la operacion, **entonces** la propiedad no queda parcialmente creada ni el usuario pierde el formulario por un error tecnico.

## Requisitos funcionales

- **FR-001**: El sistema DEBE ofrecer una pagina de alta accesible desde el boton Nueva propiedad del navbar.
- **FR-002**: La pagina de alta DEBE conservar el enfoque server-rendered existente, sin introducir una SPA ni dependencias externas de CSS o JS.
- **FR-003**: La alta DEBE respetar la arquitectura vertical slice del modulo propiedades, manteniendo separacion entre rutas, servicio y acceso a datos.
- **FR-004**: Al crear una propiedad, el sistema DEBE generar automaticamente un identificador nuevo sin solicitarlo al usuario.
- **FR-005**: El formulario DEBE rechazar cualquier envio si falta titulo, direccion, ciudad, area_m2, precio_mensual, habitaciones o banos.
- **FR-006**: El sistema DEBE considerar vacio cualquier campo que contenga solo espacios en blanco.
- **FR-007**: precio_mensual DEBE ser numerico y mayor que cero para permitir la creacion.
- **FR-008**: habitaciones DEBE ser un entero positivo dentro del rango de negocio acordado para la alta.
- **FR-009**: banos DEBE ser un numero positivo con precision valida para el dominio y dentro del rango de negocio acordado para la alta.
- **FR-010**: El estado por defecto al crear DEBE ser disponible.
- **FR-011**: La imagen de la propiedad DEBE generarse automaticamente usando Picsum, sin captura manual por parte del usuario.
- **FR-012**: Si Picsum falla temporalmente, el sistema DEBE usar una imagen de respaldo local y completar la creacion.
- **FR-013**: Los errores de validacion DEBEN mostrarse de forma clara y asociarse al campo correspondiente.
- **FR-014**: La alta DEBE crear la propiedad solo cuando todos los datos requeridos sean validos; en caso contrario, no se debe persistir ningun registro.
- **FR-015**: La funcionalidad DEBE incluir pruebas de navegacion desde el navbar, validacion de errores, creacion exitosa y fallback por fallo externo.
- **FR-016**: El formulario DEBE incluir ciudad y area_m2, ademas de los demas datos obligatorios de negocio, para poder persistir la propiedad.
- **FR-017**: Tras una creacion exitosa, el sistema DEBE redirigir al listado `/propiedades` y mostrar una confirmacion de exito.

## Casos limite

- precio_mensual vacio, no numerico o menor o igual a cero.
- ciudad vacia o compuesta solo por espacios.
- area_m2 vacio, no numerico o menor o igual a cero.
- habitaciones vacio, no numerico o fuera del rango de negocio.
- banos vacio, no numerico o fuera del rango de negocio.
- Campos que contienen solo espacios en blanco.
- Falla temporal de Picsum al momento de crear la imagen.
- Envio repetido del formulario por doble clic o reintento accidental.
- Falta de alguno de los datos adicionales que exige el modelo vigente para persistencia.

## Criterios de aceptacion

- Existe una nueva pagina de creacion accesible desde Nueva propiedad.
- Con datos validos, la propiedad se crea con id autogenerado, estado disponible, imagen generada y redireccion al listado.
- Con datos invalidos, no se crea la propiedad y se muestran errores claros por campo.
- Si Picsum falla temporalmente, la creacion sigue completandose con una imagen de respaldo local.
- Existen pruebas de navegacion, validacion y creacion exitosa antes de pasar a plan.

## Criterios de exito medibles

- **SC-001**: El 100% de los recorridos validos de alta completan la creacion de la propiedad con id autogenerado, estado disponible y redireccion al listado.
- **SC-002**: El 100% de los formularios con datos invalidos se rechazan sin persistir registros y muestran errores claros por campo.
- **SC-003**: El 100% de los casos de prueba que parten desde Nueva propiedad llegan a la pagina de alta correcta.
- **SC-004**: En el 100% de las simulaciones de falla temporal de Picsum, la propiedad se crea igual usando una imagen de respaldo local.
- **SC-005**: La funcionalidad queda cubierta por pruebas automatizadas de navegacion, validacion y creacion exitosa antes de iniciar la planificacion de implementacion.

## Riesgos y dependencias

- Dependencia de que el modulo propiedades mantenga su estructura actual y su flujo server-rendered.
- Dependencia del boton Nueva propiedad del navbar para abrir el flujo de alta.
- Dependencia del servicio externo Picsum para la generacion normal de imagen.
- Riesgo de inconsistencia si la validacion de alta no se alinea con el modelo vigente de propiedades.
- Riesgo de introducir cambios visuales innecesarios si se excede el alcance minimo de navegacion y formulario.
- Riesgo de perder trazabilidad si la planificacion posterior no desglosa cada requisito funcional en `tasks.md`.

## Preguntas abiertas

No hay preguntas abiertas bloqueantes para cerrar esta especificacion.

## Supuestos

- Se asume que la experiencia reutiliza el layout y la navegacion existentes sin cambios globales de diseno.