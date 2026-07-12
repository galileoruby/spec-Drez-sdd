# Plan Técnico: Alta de Propiedad

**Rama**: `[007-crear-propiedad]` | **Fecha**: 2026-07-11 | **Spec**: `specs/007-crear-propiedad/spec.md`

**Entrada**: Especificación de la funcionalidad y aclaraciones cerradas en la misma spec.

## 1. Resumen técnico

Implementar un flujo server-rendered de alta de propiedades en `/propiedades/crear`, con formulario GET/POST, validación de campos obligatorios, normalización de texto, creación de `Propiedad` con identificador autogenerado por base de datos, estado por defecto `disponible`, imagen generada a partir de Picsum y redirección al listado tras una creación exitosa.

La implementación se mantendrá dentro de la vertical slice `app/modules/propiedades/` y reutilizará el layout, la barra superior, el componente de alerta y la navegación existentes, sin introducir edición, eliminación ni cambios globales de diseño.

## 2. Contexto técnico

**Lenguaje/versión**: Python 3.13+

**Dependencias principales**: FastAPI, Jinja2, HTMX vendoreado, SQLAlchemy 2.x async, Pydantic v2, asyncpg, Alembic, pytest, pytest-asyncio, httpx.AsyncClient.

**Almacenamiento**: PostgreSQL administrado por SQLAlchemy async; el `id` de la propiedad se genera en la base de datos y el resto de los datos se persisten en la entidad existente.

**Pruebas**: pytest para servicio y repositorio, httpx.AsyncClient para rutas, validación de render server-side y de navegación.

**Tipo de proyecto**: aplicación web monolítica server-rendered con módulos verticales.

**Restricciones**:

- No usar frameworks CSS ni JS externos.
- No cargar HTMX desde CDN.
- No exponer entidades SQLAlchemy directamente como respuesta HTTP.
- Toda operación de I/O debe ser asíncrona.
- La lógica de negocio debe vivir en `service.py`.
- La documentación y docstrings deben permanecer en español.

**Alcance**: una sola feature funcional de alta, una página de formulario, una ruta GET, una ruta POST, persistencia de una entidad y pruebas de validación/render/navegación.

## 3. Artefactos y archivos a tocar por vertical slice

| Archivo | Cambio previsto | Motivo |
|---|---|---|
| `app/modules/propiedades/routes.py` | Agregar `GET /propiedades/crear` y `POST /propiedades/crear`, logging estructurado, manejo de errores y redirección post-éxito | Exponer el flujo de alta de forma delgada |
| `app/modules/propiedades/schemas.py` | Añadir DTOs de entrada/salida para alta y contrato de errores del formulario | Tipar el contrato del formulario y del resultado |
| `app/modules/propiedades/service.py` | Implementar orquestación de validaciones, normalización, generación de imagen, persistencia y mapeo a salida | Concentrar la lógica de negocio |
| `app/modules/propiedades/repository.py` | Añadir inserción y consulta de apoyo para el alta | Mantener el acceso a datos aislado |
| `app/modules/propiedades/templates/crear_propiedad.html` | Nueva pantalla server-rendered de alta | Dar soporte al flujo visual de creación |
| `app/modules/propiedades/templates/_formulario_crear_propiedad.html` | Parcial de formulario si se necesita actualización HTMX sin recargar toda la página | Simplificar errores y re-render parcial |
| `app/modules/propiedades/tests/test_service.py` | Ampliar pruebas de validación, normalización, fallback de imagen y éxito | Cubrir la lógica de negocio |
| `app/modules/propiedades/tests/test_repository.py` | Añadir pruebas de creación e inserción | Validar persistencia y contrato de datos |
| `app/modules/propiedades/tests/test_routes.py` | Nuevas pruebas de GET/POST, redirección y errores HTML | Verificar integración HTTP |
| `app/modules/propiedades/tests/test_templates_crear_propiedad.py` | Pruebas de render del formulario, errores y éxito | Validar UI server-rendered |
| `app/templates/components/_navbar.html` | Convertir “Nueva propiedad” en enlace navegable a `/propiedades/crear` | Habilitar el acceso al flujo |
| `app/templates/pages/propiedades.html` | Mostrar confirmación de éxito tras la redirección de creación | Completar la experiencia post-creación reutilizando la alerta existente |

## 4. Contratos esperados

### Entrada de creación

- `titulo`: cadena obligatoria, no vacía tras normalización.
- `direccion`: cadena obligatoria, no vacía tras normalización.
- `ciudad`: cadena obligatoria, no vacía tras normalización.
- `precio_mensual`: número obligatorio, mayor que cero.
- `habitaciones`: entero obligatorio, en el rango de negocio acordado.
- `banos`: número obligatorio con una cifra decimal, en el rango de negocio acordado.
- `area_m2`: número obligatorio, mayor que cero.

### Salida exitosa

- La creación persiste una nueva `Propiedad` con `id` autogenerado por la base de datos.
- El estado persistido por defecto es `disponible`.
- La imagen persistida se genera de forma automática a partir de Picsum o usa el fallback local si la estrategia elegida no produce una URL utilizable.
- La respuesta exitosa redirige al listado `/propiedades` y muestra una confirmación de éxito reutilizando la alerta del sistema.

### Salida con errores

- La validación de negocio devuelve la misma vista con errores asociados a cada campo y con los valores ya introducidos.
- La validación estructural o sintáctica devuelve error tipado del framework cuando el payload no puede convertirse al contrato esperado.
- Los errores de identidad duplicada se devuelven como error de formulario y no como excepción cruda de base de datos.

## 5. Diseño de validaciones

### Campos requeridos

- `titulo`, `direccion`, `ciudad`, `precio_mensual`, `habitaciones`, `banos` y `area_m2` son obligatorios para crear.
- Ningún campo vacío, ausente o compuesto solo por espacios debe aceptarse.

### Reglas numéricas

- `precio_mensual` debe ser mayor que cero.
- `habitaciones` debe ser entero entre 1 y 10.
- `banos` debe ser numérico con una cifra decimal entre 1.0 y 5.0.
- `area_m2` debe ser mayor que cero.

### Normalización de strings

- `titulo`, `direccion` y `ciudad` deben normalizarse recortando espacios al inicio y al final y colapsando múltiples espacios internos a uno solo.
- Si el resultado normalizado queda vacío, el campo se considera inválido.
- La identidad de negocio debe evaluarse sobre los valores normalizados para evitar duplicados aparentes.

### Validación de duplicados

- Si ya existe una propiedad con la misma combinación normalizada de `titulo`, `direccion` y `ciudad`, la creación debe rechazarse con un error de negocio claro.

## 6. Diseño de generación de imagen con Picsum

### Estrategia elegida

- Generar una URL determinista con Picsum usando la semilla del identificador de la nueva propiedad y un tamaño fijo, por ejemplo 800x500.
- No se introduce una dependencia visual distinta ni se manipula la imagen desde el cliente.

### Fallback ante error

- Si la URL generada no es utilizable o la estrategia de imagen no puede resolverse, se usa el fallback local ya disponible en el proyecto.
- La creación no se bloquea por una indisponibilidad temporal de Picsum.

### Impacto en consistencia de datos

- La imagen persistida queda estable y reproducible para cada alta.
- El fallback local garantiza que la entidad no se cree con imagen nula ni obligue a un segundo paso.
- No se realiza una verificación sincrónica de disponibilidad externa que convierta la alta en un flujo dependiente de red.

## 7. Estrategia de navegación y UX post-creación

- El botón “Nueva propiedad” del navbar debe navegar a `GET /propiedades/crear`.
- El formulario se presenta como vista server-rendered con posibilidad de mejora progresiva con HTMX.
- En errores de validación, el mismo formulario se re-renderiza con los mensajes por campo y sin perder los valores ya ingresados.
- En éxito, la respuesta debe dirigir al listado `/propiedades` y mostrar una confirmación visible usando la alerta reutilizable del sistema.
- La confirmación debe ser mínima y no introducir nuevo lenguaje visual ni componentes nuevos fuera de los ya existentes.

## 8. Fases de implementación con criterios de salida por fase

### Fase 1: Contratos y validación de entrada

- Definir DTOs de alta y contratos de errores en `schemas.py`.
- Alinear reglas numéricas y normalización de strings.
- Criterio de salida: los contratos de entrada y salida están tipados y cubren todos los campos obligatorios.

### Fase 2: Servicio de creación

- Implementar la orquestación de validación, normalización, detección de duplicados, generación de imagen y persistencia.
- Criterio de salida: el servicio crea una propiedad válida, devuelve un DTO de salida y traduce errores de negocio a mensajes claros.

### Fase 3: Rutas y navegación

- Agregar `GET /propiedades/crear` para renderizar el formulario.
- Agregar `POST /propiedades/crear` para procesar el alta.
- Actualizar el navbar para apuntar a la ruta nueva.
- Criterio de salida: la navegación desde “Nueva propiedad” funciona y la respuesta exitosa termina en el listado.

### Fase 4: Vistas y confirmación

- Crear la plantilla de alta y el parcial del formulario si el flujo HTMX lo requiere.
- Integrar la confirmación de éxito en el listado usando la infraestructura de alerta ya existente.
- Criterio de salida: el formulario muestra éxito y error sin romper el layout base.

### Fase 5: Pruebas y endurecimiento

- Cubrir servicio, repositorio, rutas y render con pruebas automatizadas.
- Criterio de salida: las pruebas de validación, persistencia, navegación y render están en verde.

## 9. Estrategia de pruebas

### Unitarias

- Servicio: validación de campos, normalización de strings, estado por defecto, generación de imagen, fallback local y rechazo de duplicados.
- Repositorio: inserción de la entidad, refresco del registro y soporte para comprobar identidad compuesta.

### Integración

- `GET /propiedades/crear` devuelve la vista de alta con estado 200.
- `POST /propiedades/crear` con datos válidos persiste y redirige al listado.
- `POST /propiedades/crear` con datos inválidos devuelve la vista con errores y sin persistencia.
- La navegación desde el navbar apunta a la ruta correcta.

### Render / UI

- El formulario muestra los campos requeridos y conserva valores al fallar validaciones.
- Los errores por campo son visibles y comprensibles.
- La confirmación de éxito aparece tras la redirección al listado.
- La vista sigue siendo server-rendered y no depende de JS externo.

## 10. Riesgos, dependencias y mitigaciones

| Riesgo o dependencia | Mitigación |
|---|---|
| El modelo actual ya exige campos adicionales para persistir | Incluir `ciudad` y `area_m2` en el contrato de alta y validarlos en el servicio |
| Conflicto por identidad compuesta duplicada | Validar antes de insertar y traducir el error de base a mensaje de formulario |
| Picsum no está disponible temporalmente | Usar URL determinista y fallback local sin bloquear la creación |
| La confirmación de éxito puede quedar perdida tras la redirección | Reutilizar la alerta existente y el `flash-zone` de la base para mostrar el resultado |
| Cambios visuales accidentales | No tocar tokens ni introducir nuevas dependencias visuales |
| Desalineación entre formulario y contratos | Añadir pruebas de contrato y render para los campos visibles |

## 11. Complexity Tracking

| Trade-off | Decisión | Motivo |
|---|---|---|
| Verificación sincrónica de disponibilidad de Picsum en el POST | No se hace | Evita convertir el alta en un flujo dependiente de latencia externa |
| Redirección con confirmación | Redirección a `/propiedades` con confirmación mínima reutilizable | Mantiene el flujo simple y consistente con el servidor renderizado |
| Manejo de duplicados | Rechazo temprano en el servicio antes del commit | Reduce errores de base y mejora el mensaje para el usuario |

## 12. Definición de listo para pasar a `tasks.md`

El plan queda listo para descomposición cuando:

- Todos los requisitos de la spec tienen un camino técnico claro.
- La ruta canónica de alta quedó fijada en `/propiedades/crear`.
- Los contratos de entrada, salida y errores están definidos.
- La validación de campos, la redirección post-éxito y el fallback de imagen tienen estrategia acordada.
- Los archivos a tocar quedaron identificados por vertical slice.
- La estrategia de pruebas cubre servicio, repositorio, rutas y render.
- No quedan decisiones estructurales abiertas que afecten el diseño de tareas.
