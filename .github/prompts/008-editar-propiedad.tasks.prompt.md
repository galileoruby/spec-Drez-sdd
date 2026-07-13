---
name: 008-editar-propiedad-tasks
agent: speckit.tasks
---

Genera specs/008-editar-propiedad/tasks.md para la feature 008-editar-propiedad en la rama 008-editar-propiedad.

Usa como fuente principal:
- specs/008-editar-propiedad/spec.md
- specs/008-editar-propiedad/plan.md

Requisitos para tasks.md:
- Español, accionable y ordenado por dependencias.
- Tareas con checkboxes e identificadores únicos.
- Incluir trazabilidad a FR y AC de la spec.
- Cubrir rutas, dominio, repositorio, template de edición, botón Editar en card y tests del módulo propiedades.
- Incluir pruebas unitarias, integración HTTP y render.
- Respetar vertical slice, async-first, validaciones de dominio equivalentes a crear propiedad, no persistencia en inválidos, 404 para id inexistente, manejo de conflicto optimista y sin cambios de tokens visuales.
- Sin escribir código.

