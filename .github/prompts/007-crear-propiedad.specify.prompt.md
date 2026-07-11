---
name: 007-crear-propiedad-spec
agent: speckit.specify
---

Quiero crear una nueva especificación siguiendo Spec-Driven Development para generar el archivo specs/007-crear-propiedad/spec.md.

Contexto funcional:
- Ya existe la página de listado de propiedades en /propiedades.
- El acceso para crear debe iniciarse desde el botón con label Nueva propiedad ubicado en app/templates/components/_navbar.html.
- Esta spec es para alta de propiedades (no edición, no eliminación).

Objetivo de la spec:
Definir la funcionalidad completa para crear una nueva propiedad desde una nueva página/formulario, con validaciones obligatorias, valores por defecto y generación automática de imagen.

Requisitos funcionales obligatorios:
1. Al crear una propiedad se debe generar automáticamente un nuevo id.
2. No se puede crear una propiedad si falta cualquiera de estos campos:
- titulo
- direccion
- precio_mensual
- habitaciones
- banos
3. El estado por defecto al crear debe ser disponible.
4. La imagen de la propiedad debe generarse automáticamente usando el servicio https://picsum.photos.
5. Debe existir navegación desde el botón Nueva propiedad del navbar hacia la nueva página de creación.
6. La solución debe respetar arquitectura vertical slice del módulo propiedades.
7. Debe mantenerse el enfoque server-rendered con FastAPI + Jinja2 + HTMX.
8. No agregar frameworks CSS ni JS externos.

Alcance y no alcance:
- Alcance: pantalla de creación, endpoint de creación, validaciones, defaults, generación de imagen, navegación desde navbar, pruebas.
- No alcance: editar propiedad, eliminar propiedad, filtros avanzados, cambios de diseño global fuera de lo mínimo para habilitar navegación.

Edge cases que quiero explícitos:
- precio_mensual inválido (vacío, no numérico o <= 0).
- habitaciones y banos inválidos (vacío, no numérico o fuera de rango de negocio).
- falla temporal del servicio picsum: definir política clara (fallback o comportamiento esperado).
- campos con solo espacios deben considerarse vacíos.

Criterios de aceptación mínimos:
- Existe una nueva página de creación accesible desde Nueva propiedad.
- Con datos válidos se crea la propiedad con id autogenerado, estado disponible e imagen generada.
- Con datos inválidos no se crea la propiedad y se muestran errores claros.
- Existen pruebas de validación y creación exitosa.
- Queda trazabilidad en tasks.md para implementación posterior.

Formato esperado de salida:
- Genera únicamente el contenido de spec.md en español, estructurado con:
1. Título y metadata de la feature
2. Objetivo
3. Alcance
4. No alcance
5. User stories priorizadas
6. Functional requirements
7. Edge cases
8. Criterios de aceptación
9. Success criteria medibles
10. Riesgos y dependencias
11. Preguntas abiertas (si aplica)
12. Assumptions

Importante:
- No implementes código ni plan ni tareas en esta etapa.
- Produce una especificación clara, verificable y lista para pasar a speckit.plan.
