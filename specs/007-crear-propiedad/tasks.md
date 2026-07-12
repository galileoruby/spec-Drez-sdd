# Tareas: Alta de Propiedad

**Entrada**: `specs/007-crear-propiedad/spec.md`, `specs/007-crear-propiedad/plan.md`, `specs/007-crear-propiedad/checklists/requirements.md`

**Objetivo**: implementar el flujo server-rendered de alta de propiedades desde el navbar, con validación estricta, id autogenerado, estado `disponible`, imagen automática con Picsum y fallback local.

**Organización**: las tareas están agrupadas por historia de usuario para permitir implementación y prueba independientes.

## Fase 1: Preparación compartida

**Propósito**: dejar listas las vistas compartidas del flujo de alta antes de entrar en la lógica de negocio.

- [X] T001 [P] Crear la plantilla base de alta en app/modules/propiedades/templates/crear_propiedad.html con el contenedor server-rendered, el área de mensajes y el punto de inclusión del formulario.
- [X] T002 [P] Crear el parcial reutilizable del formulario en app/modules/propiedades/templates/_formulario_crear_propiedad.html para render inicial y re-render con errores.
- [X] T003 [P] Actualizar app/templates/components/_navbar.html para convertir “Nueva propiedad” en un enlace a /propiedades/crear.

---

## Fase 2: Fundacional

**Propósito**: definir los contratos y helpers compartidos que bloquean a todas las historias de usuario.

- [X] T004 [P] Definir los DTOs de alta, salida y error de formulario en app/modules/propiedades/schemas.py para tipar la entrada, el resultado y la respuesta con errores.
- [X] T005 [P] Añadir utilidades compartidas de normalización de strings y construcción determinista de la URL de imagen en app/modules/propiedades/service.py.
- [X] T006 [P] Añadir en app/modules/propiedades/repository.py las operaciones de inserción y consulta de duplicados necesarias para la alta.

**Checkpoint**: la base técnica de la alta está lista y ya puede implementarse cada historia de forma independiente.

---

## Fase 3: Historia de Usuario 1 - Acceso a la alta y creación exitosa (Prioridad: P1) 🎯 MVP

**Objetivo**: entrar a la página de alta desde el navbar y crear una propiedad válida con id autogenerado, estado `disponible`, imagen asociada y redirección al listado.

**Prueba independiente**: abrir /propiedades/crear, completar el formulario con datos válidos y verificar que la propiedad se persiste, redirige a /propiedades y muestra confirmación de éxito.

### Pruebas para la Historia de Usuario 1

- [X] T007 [P] [US1] Agregar pruebas de GET y POST exitosos con redirección al listado en app/modules/propiedades/tests/test_routes.py.
- [X] T008 [P] [US1] Agregar pruebas de render del formulario de alta y de la confirmación de éxito reutilizando la alerta en app/modules/propiedades/tests/test_templates_crear_propiedad.py.

### Implementación para la Historia de Usuario 1

- [X] T009 [US1] Implementar la orquestación de creación feliz en app/modules/propiedades/service.py para generar la propiedad con estado disponible, id autogenerado e imagen válida.
- [X] T010 [US1] Implementar GET /propiedades/crear y POST /propiedades/crear en app/modules/propiedades/routes.py con logging estructurado y redirección al listado.
- [X] T011 [US1] Mostrar la confirmación de alta en app/templates/pages/propiedades.html usando la alerta existente y el flash-zone compartido.

**Checkpoint**: la alta funciona de extremo a extremo con datos válidos.

---

## Fase 4: Historia de Usuario 2 - Validación estricta de campos (Prioridad: P2)

**Objetivo**: rechazar entradas incompletas o inválidas con errores claros por campo, incluyendo espacios en blanco, números fuera de rango y campos obligatorios faltantes.

**Prueba independiente**: enviar payloads con campos vacíos, solo espacios, precios inválidos y valores fuera de rango, y verificar que no se persiste ningún registro y que la vista devuelve errores claros.

### Pruebas para la Historia de Usuario 2

- [X] T012 [P] [US2] Agregar pruebas de servicio para campos requeridos, espacios en blanco y rangos numéricos inválidos en app/modules/propiedades/tests/test_service.py.
- [X] T013 [P] [US2] Agregar pruebas de rutas para re-render del formulario con errores de validación en app/modules/propiedades/tests/test_routes.py.

### Implementación para la Historia de Usuario 2

- [X] T014 [US2] Implementar las validaciones de negocio y la normalización de strings en app/modules/propiedades/service.py.
- [X] T015 [US2] Mapear los errores de validación al formulario en app/modules/propiedades/routes.py y app/modules/propiedades/templates/_formulario_crear_propiedad.html.

**Checkpoint**: la alta rechaza datos inválidos sin persistir cambios y muestra errores útiles.

---

## Fase 5: Historia de Usuario 3 - Robustez ante falla de imagen externa (Prioridad: P3)

**Objetivo**: completar la alta aunque Picsum falle temporalmente, usando una imagen de respaldo local sin bloquear el flujo.

**Prueba independiente**: simular un fallo de Picsum y verificar que la propiedad se crea igual con una imagen de respaldo local.

### Pruebas para la Historia de Usuario 3

- [X] T016 [P] [US3] Agregar prueba de servicio para el fallback local cuando Picsum no produce una URL utilizable en app/modules/propiedades/tests/test_service.py.
- [X] T017 [P] [US3] Agregar prueba de integración del comportamiento de fallback de imagen en app/modules/propiedades/tests/test_routes.py.

### Implementación para la Historia de Usuario 3

- [X] T018 [US3] Implementar la generación determinista de la URL de Picsum y el fallback local en app/modules/propiedades/service.py.
- [X] T019 [US3] Asegurar que el repositorio persista la URL final de imagen calculada en app/modules/propiedades/repository.py.

**Checkpoint**: la alta no depende de la disponibilidad temporal de Picsum para completarse.

---

## Fase 6: Pulido y coherencia transversal

**Propósito**: cerrar trazabilidad, endurecer consistencia y evitar regresiones entre historias.

- [X] T020 [P] Afinar el manejo de errores y el logging estructurado en app/modules/propiedades/routes.py y app/modules/propiedades/service.py para que las respuestas de alta sean consistentes.
- [X] T021 [P] Revisar la cobertura final del módulo en app/modules/propiedades/tests/ para asegurar que validación, éxito, navegación y fallback quedan cubiertos.

---

## Dependencias y orden de ejecución

### Dependencias por fase

- Fase 1: no depende de otras tareas.
- Fase 2: depende de la Fase 1 y bloquea todas las historias de usuario.
- Fase 3: depende de la Fase 2 y constituye el MVP.
- Fase 4: depende de la Fase 2 y puede ejecutarse después de la Fase 3 sin romper la independencia funcional.
- Fase 5: depende de la Fase 2 y refuerza el comportamiento externo de la alta.
- Fase 6: depende de la finalización de las historias que se quieran liberar.

### Dependencias entre historias

- US1: no depende de US2 ni US3.
- US2: no depende de US1 para existir, pero usa los mismos contratos y vistas.
- US3: no depende de US2 y solo reutiliza la misma creación base.

### Orden dentro de cada historia

- Primero las pruebas.
- Después la lógica de negocio.
- Después la ruta o la vista que expone el comportamiento.
- Finalmente el ajuste de presentación o redirección asociado.

---

## Oportunidades de paralelismo

- Las tareas marcadas con `[P]` pueden ejecutarse en paralelo porque tocan archivos distintos y no dependen de otra tarea incompleta.
- T001, T002 y T003 pueden avanzar en paralelo.
- T004, T005 y T006 pueden avanzar en paralelo.
- T007 y T008 pueden avanzar en paralelo.
- T012 y T013 pueden avanzar en paralelo.
- T016 y T017 pueden avanzar en paralelo.
- T020 y T021 pueden avanzar en paralelo.

---

## Ejemplo de ejecución paralela

### Historia de Usuario 1

- `T007` y `T008` en paralelo para arrancar la cobertura de pruebas.
- Luego `T009`, `T010` y `T011` en secuencia lógica para cerrar la experiencia de alta exitosa.

### Historia de Usuario 2

- `T012` y `T013` en paralelo.
- Luego `T014` y `T015` para endurecer la validación y el re-render del formulario.

### Historia de Usuario 3

- `T016` y `T017` en paralelo.
- Luego `T018` y `T019` para completar la estrategia de imagen con fallback.

---

## Estrategia de implementación

### MVP primero

1. Completar Fase 1 y Fase 2.
2. Completar la Historia de Usuario 1.
3. Validar que `/propiedades/crear` crea una propiedad válida y redirige a `/propiedades`.
4. Detenerse si el MVP ya es demostrable.

### Entrega incremental

1. Entregar US1 como base funcional.
2. Añadir US2 para endurecer validación y errores.
3. Añadir US3 para robustez ante Picsum.
4. Cerrar con la fase de pulido y cobertura final.

### Estrategia de equipo paralelo

1. Un perfil puede cubrir las plantillas y la navegación.
2. Otro perfil puede trabajar en la lógica de servicio y repositorio.
3. Otro perfil puede preparar la cobertura de pruebas por historia.

---

## Lista de verificación de preparación

- [X] Todas las tareas están trazadas a archivos concretos.
- [X] Todas las tareas usan el formato `- [ ] T### [P] [US#] Descripción con ruta` cuando aplica.
- [X] La historia P1 puede entregarse como MVP independiente.
- [X] No hay tareas de edición o eliminación de propiedades.
- [X] No se introducen dependencias visuales o JS externos.
- [X] La validación y el fallback de imagen quedan cubiertos por pruebas.