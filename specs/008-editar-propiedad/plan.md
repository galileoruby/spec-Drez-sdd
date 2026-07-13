# Plan de implementación: Edición de propiedad

**Rama**: `008-editar-propiedad` | **Fecha**: 2026-07-12 | **Spec**: [spec.md](./spec.md)

**Entrada**: Especificación funcional de [edición de propiedad](./spec.md)

## Resumen técnico

La feature agrega una ruta SSR de edición para propiedades existentes dentro del módulo `propiedades`, reutilizando el mismo monolito FastAPI + Jinja2 + HTMX y el enfoque async-first del repositorio. La implementación debe permitir abrir la edición desde cada card del listado, precargar el formulario con los valores actuales, validar con reglas de dominio consistentes con el alta, evitar persistencia parcial y responder con HTML ante errores de negocio, incluyendo payloads vacíos o incompletos.

El cambio no introduce una API paralela ni separa frontend/backend. La edición debe integrarse en la vista actual del listado, usando el mismo layout y el mismo lenguaje visual que la alta de propiedades.

## Contexto técnico y restricciones

**Lenguaje/Versión**: Python 3.13+

**Dependencias principales**: FastAPI, Jinja2, HTMX vendoreado, SQLAlchemy 2.x async, Pydantic v2, PostgreSQL/asyncpg, pytest, pytest-asyncio, httpx.AsyncClient

**Almacenamiento**: PostgreSQL vía `AsyncSession`; la edición debe leer y actualizar la entidad `Propiedad` existente sin persistir estados intermedios si falla la validación.

**Pruebas**: unitarias de servicio, integración HTTP con `AsyncClient`, render de templates y regresión de listado/alta existente cuando cambie la validación compartida.

**Plataforma objetivo**: aplicación web server-rendered en el mismo monolito Python.

**Tipo de proyecto**: aplicación web modular con vertical slice.

**Restricciones clave**:
- La lógica de negocio vive en `service.py`.
- `routes.py` debe ser delgado y async.
- No debe aparecer JSON 422 técnico en el flujo web de edición.
- La edición debe devolver 404 claro cuando el id no exista.
- La validación de edición debe compartir criterio con la de alta para evitar reglas divergentes.
- No se pueden introducir cambios de tokens visuales.

**Alcance estimado**: una nueva pantalla, un nuevo flujo POST, una actualización del listado para enlazar la edición y la cobertura de pruebas del módulo `propiedades`.

## Constitution Check

Estado: cumple.

- Vertical slice: se mantiene dentro de `app/modules/propiedades/`.
- Async-first: todo acceso a datos seguirá siendo asíncrono.
- Seguridad de dominio: errores de validación no se persistirán.
- Documento y código: el plan, la spec y las respuestas de error permanecerán alineados en español.
- Tokens visuales: no se autorizan cambios de tokens.

No hay violaciones que justificar, así que no aplica `Complexity Tracking`.

## Artefactos y archivos a tocar

### Núcleo del módulo

- [app/modules/propiedades/routes.py](../../../app/modules/propiedades/routes.py)
  - Añadir `GET /propiedades/editar/{id}`.
  - Añadir `POST /propiedades/editar/{id}`.
  - Traducir el caso no encontrado a 404 claro.
  - Hacer que el listado reconozca el nuevo query param de éxito de edición.

- [app/modules/propiedades/schemas.py](../../../app/modules/propiedades/schemas.py)
  - Añadir DTOs de edición: formulario, errores, vista y resultado.
  - Extender `PropiedadCardView` con el identificador necesario para construir el enlace Editar.

- [app/modules/propiedades/service.py](../../../app/modules/propiedades/service.py)
  - Extraer o consolidar la validación de dominio en un helper compartido.
  - Reutilizar normalización, validación de rangos y verificación de identidad de negocio.
  - Implementar obtención de datos para precarga y actualización validada.
  - Lanzar errores de dominio sin mutar ni persistir si el formulario es inválido.

- [app/modules/propiedades/repository.py](../../../app/modules/propiedades/repository.py)
  - Agregar acceso por id para precarga y edición.
  - Agregar lectura de identidad para detectar duplicados excluyendo la propia propiedad.
  - Mantener la persistencia encapsulada en operaciones async y deterministas.

### Plantillas

- [app/modules/propiedades/templates/editar_propiedad.html](../../../app/modules/propiedades/templates/editar_propiedad.html)
  - Nueva pantalla SSR para la edición.
  - Debe mantener la composición visual del alta.

- [app/modules/propiedades/templates/_formulario_editar_propiedad.html](../../../app/modules/propiedades/templates/_formulario_editar_propiedad.html)
  - Parcial de formulario de edición, si se separa para no mutar el formulario de alta.
  - Debe renderizar inputs prellenados y un select para estado.

- [app/templates/components/_card_propiedad.html](../../../app/templates/components/_card_propiedad.html)
  - Añadir el enlace/botón Editar por card.
  - Debe apuntar a la ruta canónica `/propiedades/editar/{id}`.

### Pruebas

- [app/modules/propiedades/tests/test_service.py](../../../app/modules/propiedades/tests/test_service.py)
  - Cubrir validación, 404 lógico, duplicados y persistencia exitosa de edición.
  - Ajustar cualquier expectativa compartida por la validación del alta si se centraliza la regla.

- [app/modules/propiedades/tests/test_routes.py](../../../app/modules/propiedades/tests/test_routes.py)
  - Cubrir GET de edición, POST exitoso, POST inválido, payload vacío/incompleto e id inexistente.
  - Verificar la redirección y el mensaje de confirmación de edición.

- [app/modules/propiedades/tests/test_templates_crear_propiedad.py](../../../app/modules/propiedades/tests/test_templates_crear_propiedad.py)
  - Actualizar la regresión del alta si la validación compartida cambia los rangos.

- [app/modules/propiedades/tests/test_templates_editar_propiedad.py](../../../app/modules/propiedades/tests/test_templates_editar_propiedad.py)
  - Nueva prueba de render para la pantalla de edición y el botón Editar del card.

## Contratos esperados GET/POST

### GET `/propiedades/editar/{id}`

**Éxito**
- Responde `200 OK` con HTML.
- Renderiza la propiedad existente precargada.
- Muestra el estado actual ya seleccionado.
- Mantiene el mismo layout y la misma jerarquía visual que la alta.

**Id inexistente**
- Responde `404 Not Found` claro.
- No renderiza una edición vacía ni una vista parcial inconsistente.

### POST `/propiedades/editar/{id}`

**Éxito**
- Responde `303 See Other`.
- Redirige al listado con un query param de éxito propio de edición.
- El listado muestra confirmación visible de éxito.

**Validación inválida**
- Responde `422 Unprocessable Entity` con HTML, no con JSON técnico.
- Conserva los valores introducidos por el usuario.
- Muestra errores inline por campo.
- No persiste cambios parciales.

**Id inexistente**
- Responde `404 Not Found` claro.
- No modifica la base de datos.

**Payload vacío/incompleto**
- Se trata como error de dominio, no como error técnico de validación de FastAPI.
- La respuesta debe ser HTML con el formulario y los mensajes correspondientes.

## Diseño de validaciones de dominio

La edición debe reutilizar la lógica de normalización y validación del módulo para no duplicar criterios ni generar divergencias entre alta y edición.

### Normalización
- Recortar espacios al inicio y al final.
- Colapsar espacios múltiples intermedios en textos libres.
- Considerar vacío cualquier campo compuesto solo por espacios.

### Reglas obligatorias
- `titulo`, `direccion`, `ciudad`, `precio_mensual`, `habitaciones`, `banos`, `area_m2` y `estado` son requeridos en la edición.
- `precio_mensual` debe ser numérico y mayor que 0.
- `habitaciones` debe estar entre 1 y 15.
- `banos` debe estar entre 0.5 y 8.0, con saltos de 0.5.
- `area_m2` debe ser numérico y mayor que 0.
- `estado` debe pertenecer al catálogo cerrado vigente.

### Unicidad e identidad
- La edición debe comprobar la identidad de negocio contra otras propiedades existentes.
- Si la identidad resultante coincide con otra propiedad distinta, se debe rechazar con error de dominio.
- La propia propiedad en edición no debe bloquear su propio guardado si la identidad no cambia.

### Resultado esperado del helper de validación
- Entrada válida: devuelve datos normalizados listos para persistir.
- Entrada inválida: devuelve contexto con errores de campo y, si aplica, error general.
- Entrada vacía/incompleta: se convierte en error de dominio renderizable en HTML.

## Diseño de UI del formulario de edición

La pantalla de edición debe reutilizar el lenguaje visual de la alta y no introducir nuevas decisiones de diseño.

### Estructura de pantalla
- Encabezado con título claro de edición.
- Mensaje de error general solo si existe un conflicto de negocio.
- Formulario en la misma disposición visual que la alta.
- Acciones al final del formulario: cancelar y guardar cambios.

### Campos
- Todos los campos editables van como inputs de texto, salvo `estado`.
- `estado` va como select con el valor actual preseleccionado.
- El formulario debe renderizar los valores enviados por el usuario cuando haya error.
- Los errores deben ir inline, junto al campo correspondiente.

### Navegación
- El botón Editar de cada card debe llevar al formulario de edición.
- Cancelar debe devolver al listado sin cambios.
- Guardar exitoso debe volver al listado con confirmación de edición.

### Coherencia visual
- Debe reutilizar el contenedor, el grid y los componentes visuales existentes.
- No se cambia la paleta, tipografía, espaciado ni tokens.
- El botón Editar del card debe integrarse con el estilo actual de acciones del módulo.

## Fases de implementación con checkpoints verificables

### Fase 1 - Preparación del dominio y contratos

**Objetivo**: preparar DTOs, helpers y acceso a datos antes de tocar la UI.

Tareas esperadas:
- Añadir DTOs de edición.
- Extender el DTO de card con el id.
- Crear lectura por id y consulta de duplicado excluyente.
- Consolidar la validación compartida de alta/edición.

**Checkpoint**: el servicio puede obtener una propiedad para editar, validar un formulario de edición y detectar duplicados sin persistir cambios.

### Fase 2 - Rutas y flujo SSR

**Objetivo**: exponer las rutas GET/POST de edición y el retorno al listado.

Tareas esperadas:
- Añadir GET de edición.
- Añadir POST de edición.
- Traducir faltantes a 404.
- Reconocer el query param de éxito de edición en el listado.

**Checkpoint**: la edición abre, guarda y redirige sin exponer JSON técnico.

### Fase 3 - UI y navegación

**Objetivo**: presentar la experiencia visual completa.

Tareas esperadas:
- Crear la plantilla de edición.
- Añadir el botón Editar en cada card.
- Mantener el formulario precargado y con errores inline.

**Checkpoint**: el usuario puede navegar desde el listado a la edición y volver con confirmación visible.

### Fase 4 - Cobertura de pruebas

**Objetivo**: asegurar comportamiento y regresión.

Tareas esperadas:
- Probar el servicio con casos válidos, inválidos, duplicados y no encontrados.
- Probar rutas GET/POST.
- Probar render de la pantalla de edición y del botón Editar.
- Ajustar regresión de alta si cambian los rangos compartidos.

**Checkpoint**: el módulo queda cubierto para el nuevo flujo sin romper la experiencia existente.

### Fase 5 - Cierre y consistencia

**Objetivo**: revisar que el comportamiento coincida con la spec y que no haya desalineación entre alta y edición.

Tareas esperadas:
- Verificar mensajes de éxito.
- Verificar 404 claros.
- Verificar ausencia de persistencia parcial.
- Verificar que no existe JSON 422 técnico en el flujo web.

**Checkpoint**: el plan queda listo para descomponer en `tasks.md`.

## Estrategia de pruebas

### Unitarias
- Validación de campos con espacios, vacíos y formatos inválidos.
- Reglas de rango para `precio_mensual`, `habitaciones`, `banos` y `area_m2`.
- Detección de identidad duplicada excluyendo la propia propiedad.
- Manejo de propiedad inexistente.

### Integración HTTP
- GET de edición devuelve HTML con datos precargados.
- POST válido redirige al listado con mensaje de éxito.
- POST inválido devuelve HTML con errores inline.
- POST con payload vacío/incompleto no produce JSON técnico.
- GET/POST con id inexistente devuelve 404 claro.

### Render
- La vista de edición muestra el estado actual seleccionado.
- El formulario mantiene valores escritos cuando hay error.
- El card incluye el enlace Editar correcto.

### Regresión
- La validación compartida no rompe el alta existente.
- El listado sigue mostrando confirmación de alta y, ahora, confirmación de edición.

## Riesgos y mitigaciones

- **Riesgo**: la validación de edición y la de alta divergen por rangos distintos.
  - **Mitigación**: centralizar el helper de validación y cubrirlo con pruebas compartidas.

- **Riesgo**: la ruta POST recae en validación técnica de FastAPI y devuelve JSON 422.
  - **Mitigación**: leer `request.form()` manualmente, usar DTOs con defaults y manejar el error como negocio en el servicio.

- **Riesgo**: la edición bloquea el propio registro por duplicado cuando no cambia la identidad.
  - **Mitigación**: consulta de duplicidad excluyendo el id actual.

- **Riesgo**: el usuario pierde contexto al fallar la validación.
  - **Mitigación**: rehidratar la vista con los valores del submit y errores inline.

- **Riesgo**: la lista no muestra la confirmación de éxito de edición.
  - **Mitigación**: usar un query param de edición y ajustar la lectura en el endpoint del listado.

## Criterio de cierre

La implementación se considera cerrada cuando:

- Existe la ruta GET de edición y carga el formulario precargado.
- Existe la ruta POST de edición y guarda cambios válidos.
- El flujo inválido no persiste cambios y devuelve HTML con errores inline.
- El id inexistente devuelve 404 claro.
- El listado muestra confirmación visible tras guardar.
- El botón Editar existe en cada card.
- La cobertura de pruebas valida el flujo completo y la regresión sobre el alta compartida.
- No hay desalineación con la constitution, el stack ni los tokens visuales.
