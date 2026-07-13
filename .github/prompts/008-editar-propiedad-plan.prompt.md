---
name: 008-editar-propiedad-plan
agent: speckit.plan
---
Quiero generar el archivo specs/008-editar-propiedad/plan.md para la feature 008-editar-propiedad, manteniendo la rama con el mismo nombre: 008-editar-propiedad.  
Toma como fuente principal specs/008-editar-propiedad/spec.md y produce un plan técnico completo, en español, listo para descomponer en tasks.md, sin escribir código todavía.

Contexto funcional a planificar:
1. Desde dashboard/listado, cada card de propiedad tendrá botón Editar.
2. La edición abre una página por id de propiedad.
3. El formulario carga datos existentes.
4. Campos editables en texto: titulo, direccion, precio_mensual, habitaciones, banos.
5. Campo estado como dropdown con estado actual preseleccionado.
6. Guardado exitoso redirige al listado con confirmación.
7. Si hay errores, se mantiene el formulario y se muestran errores inline por campo.
8. Para UI web con payload vacío/incompleto, el POST debe responder HTML con errores de dominio y evitar JSON 422 técnico.

Restricciones obligatorias del plan:
1. Respetar arquitectura vertical slice y async-first.
2. Mantener consistencia con validaciones de crear propiedad: trim/requeridos, precio_mensual > 0, habitaciones 1..15, banos 0.5..8.0 en pasos de 0.5.
3. No persistencia parcial cuando existan errores.
4. Definir manejo explícito de id inexistente (404 claro).
5. Mantener alineación visual y de UX con crear propiedad.

Archivos objetivo a considerar en el plan:
1. routes.py
2. schemas.py
3. service.py
4. repository.py
5. app/modules/propiedades/templates/editar_propiedad.html
6. _card_propiedad.html
7. Tests del módulo propiedades para flujo de edición.

Formato esperado del plan.md:
1. Resumen técnico.
2. Contexto técnico y restricciones.
3. Artefactos y archivos a tocar.
4. Contratos esperados GET/POST (éxito, validación inválida, id inexistente, payload vacío/incompleto).
5. Diseño de validaciones de dominio.
6. Diseño de UI del formulario de edición.
7. Fases de implementación con checkpoints verificables.
8. Estrategia de pruebas (unitarias, integración, render).
9. Riesgos y mitigaciones.
10. Criterio de cierre.

Si detectas decisiones críticas no resueltas en el spec, formula preguntas concretas mínimas antes de cerrar el plan.