---
name: 006-pagina-propiedades-cards-plan
agent: speckit.plan
---

Genera el plan técnico de la spec 006-pagina-propiedades-cards en specs/006-pagina-propiedades-cards/plan.md usando únicamente decisiones específicas de esta feature y el alcance aprobado en su spec.

Reglas:
1. No repetir principios globales ya definidos en la constitución ni en las instrucciones del repositorio.
2. Si una regla global aplica, solo indicar que aplica la gobernanza vigente.
3. Escribir en español y con enfoque implementable.
4. No introducir alcance nuevo fuera de la spec.
5. Mantener trazabilidad clara entre decisiones técnicas, historias y criterios de aceptación.
6. Si falta una decisión crítica para planificar, preguntar en modo interactivo antes de cerrar el plan.

Objetivo técnico del plan:
Implementar una página server-rendered de propiedades en formato cards con datos reales de base de datos, incluyendo:
- endpoint de lectura de propiedades
- render de cards con los campos definidos
- comportamiento responsive (desktop 3, tablet 2, phone 1)
- navegación lateral funcional hacia la nueva página de propiedades

Entregables mínimos del plan:
1. Resumen técnico de arquitectura propuesta.
2. Módulos y archivos afectados con responsabilidad concreta por archivo.
3. Secuencia de implementación por fases con dependencias explícitas.
4. Estrategia de pruebas por fase.
5. Riesgos, mitigaciones y criterios de salida por fase.
6. Lista de validaciones finales para considerar la implementación lista.
7. Sección explícita de no alcance para evitar scope creep.

Decisiones que debe reflejar el plan:
1. Orden de ejecución obligatorio:
   - primero endpoint
   - luego página/cards
   - luego navegación del sidebar
2. Endpoint server-rendered para listar propiedades reales desde base de datos.
3. Servicio y repositorio como capas de orquestación y acceso a datos; evitar lógica de negocio en templates.
4. Mantener layout global existente y acotar cambios visuales a la nueva página.
5. Responsive obligatorio:
   - desktop: 3 cards por fila
   - tablet: 2 cards por fila
   - phone: 1 card por fila
6. Campos obligatorios por card:
   - imagen
   - título
   - dirección
   - habitaciones
   - baños
   - área m²
   - precio de renta
   - estado
7. El enlace de Propiedades del menú lateral debe redirigir a la nueva ruta real.
8. Estado vacío definido y verificable cuando no existan propiedades.

Formato esperado:
1. Fases claras y accionables:
   - setup
   - implementación endpoint
   - implementación vista/cards responsive
   - integración navegación sidebar
   - pruebas y validación final
2. Cada fase con:
   - precondiciones
   - tareas técnicas
   - resultado verificable
   - criterio de salida
3. Criterios técnicos de aceptación trazables a la spec.
4. Riesgos y mitigaciones concretas.
5. No alcance explícito.

Cobertura mínima de pruebas en el plan:
1. Pruebas de repositorio/servicio para consulta de propiedades.
2. Pruebas de render de la página de propiedades.
3. Pruebas de contrato de contexto del template.
4. Prueba de navegación desde sidebar a la ruta de propiedades.
5. Verificación de responsive en 3 breakpoints.
6. Verificación de estado vacío y comportamiento con datos incompletos (por ejemplo imagen faltante).

No alcance que debe quedar explícito en el plan:
1. No crear dominio nuevo de rentas/pagos.
2. No agregar filtros avanzados, búsqueda, paginación ni ordenamiento (salvo aprobación posterior).
3. No agregar nuevas dependencias.
4. No rediseñar navbar/sidebar/layout global fuera del enlace requerido.
5. No tocar tokens visuales globales ni paleta.

Validaciones finales obligatorias:
1. Tests de módulos involucrados en verde.
2. Lint en verde.
3. Type-check estricto en verde.
4. Confirmación explícita de no scope creep.
5. Evidencia de que la ruta de propiedades está conectada desde el sidebar.

Si existe ambigüedad funcional o técnica bloqueante, hacer preguntas de clarificación antes de cerrar el plan.