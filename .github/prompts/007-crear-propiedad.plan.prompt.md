---
name: 007-crear-propiedad-plan
agent: speckit.plan
---

Ejecuta planificación técnica para la spec 007-crear-propiedad y genera únicamente el archivo plan.md.

Reglas obligatorias:
1. Lee y aplica la constitución del proyecto antes de planificar.
2. Usa como entrada la spec y sus clarificaciones ya cerradas.
3. Si detectas decisiones estructurales no resueltas, entra en modo interactivo y pregunta una por una (A/B/C/D o S/N); si no hay bloqueos, genera el plan directamente.
4. No implementes código, no generes tasks.md, no modifiques otros artefactos.
5. Escribe todo en español, concreto y verificable.

Objetivo funcional a planificar:
- Crear flujo de alta de propiedad desde el botón Nueva propiedad del navbar.
- Alta con id autogenerado.
- Validaciones obligatorias: titulo, direccion, precio_mensual, habitaciones, banos.
- estado por defecto: disponible.
- generación automática de imagen usando picsum.photos.
- manejo explícito de errores de validación y de fallo del servicio de imagen.

Estructura obligatoria de salida en plan.md:
1. Resumen técnico.
2. Contexto técnico (stack, módulos, restricciones).
3. Artefactos y archivos a tocar por vertical slice:
- routes.py
- schemas.py
- service.py
- repository.py
- app/modules/propiedades/templates/
- app/modules/propiedades/tests/
- _navbar.html
4. Contratos esperados (entrada/salida de creación y errores).
5. Diseño de validaciones:
- campos requeridos
- reglas numéricas
- normalización de strings (incluye solo espacios)
6. Diseño de generación de imagen con picsum:
- estrategia elegida
- fallback ante error
- impacto en consistencia de datos
7. Estrategia de navegación y UX post-creación.
8. Fases de implementación con criterios de salida por fase.
9. Estrategia de pruebas:
- unitarias (servicio/repository)
- integración (rutas GET/POST)
- render/UI (formulario, errores, éxito, navegación)
10. Riesgos, dependencias y mitigaciones.
11. Complexity Tracking (si hay excepciones o trade-offs).
12. Definición de listo para pasar a tasks.md.

Criterio de calidad del plan:
- trazable a requisitos de la spec
- sin scope creep (sin editar/eliminar propiedades)
- alineado a FastAPI + Jinja2 + HTMX + SQLAlchemy async + Pydantic v2
- listo para descomponerse en tareas accionables.