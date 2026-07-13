---
name: 008-editar-propiedad-spec
agent: speckit.specify
---

Quiero crear la nueva spec 008-editar-propiedad, con branch exactamente llamado 008-editar-propiedad, y generar el archivo spec.md en la ruta specs/008-editar-propiedad/spec.md.
Contexto funcional: desde el dashboard/listado, cada card de propiedad tendrá un botón Editar; al hacer clic, se abre una página de edición recibiendo el id de la propiedad, se carga un formulario precargado con los datos actuales, todos los campos serán cajas de texto excepto estado, que será dropdown con el estado actual seleccionado; al guardar exitosamente se redirige al listado de propiedades con confirmación, y si hay errores se mantiene el formulario con errores inline por campo, igual al comportamiento de crear propiedad.
Requisitos obligatorios de esta spec: mantener consistencia con validaciones de dominio de crear propiedad (trim, requeridos, precio_mensual > 0, habitaciones 1..15, banos 0.5..8.0 en pasos de 0.5), no persistir cambios en caso inválido, y para flujo UI web evitar JSON 422 técnico en payload vacío/incompleto devolviendo HTML con errores de dominio.
Incluye en la spec: Objetivo, Alcance, No alcance, Clarifications, User Stories con prioridades y pruebas independientes, Edge Cases, Functional Requirements, Acceptance Criteria, Key Entities, Success Criteria, Riesgos/Dependencias, Preguntas abiertas y Assumptions.
Redacta todo en español, en formato listo para implementación posterior con plan/tasks, sin escribir código todavía y sin salirte del alcance de esta feature.
Si falta alguna decisión crítica, formula preguntas de clarificación concretas y orientadas a implementación.