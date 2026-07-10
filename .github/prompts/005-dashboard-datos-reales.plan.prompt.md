---
name: 005-dashboard-datos-reales-plan
agent: speckit.plan
---

Genera el plan técnico de la spec 005-dashboard-datos-reales en specs/005-dashboard-datos-reales/plan.md usando únicamente decisiones específicas de esta feature.

Reglas:
1. No repetir principios globales ya definidos en la constitución ni en las instrucciones del repositorio.
2. Si una regla global aplica, solo referenciar que aplica la gobernanza vigente.
3. Escribir en español y con enfoque implementable.
4. No introducir alcance nuevo fuera de la spec y clarificaciones ya cerradas.

Objetivo técnico del plan:
Reemplazar el mock del dashboard principal por métricas reales desde base de datos para disponibles y rentadas, manteniendo contrato de contexto existente y dejando ingresos/vencidos como no operativos en esta iteración.

Entregables mínimos del plan:
1. Resumen técnico de arquitectura propuesta.
2. Módulos/archivos afectados con responsabilidad concreta por archivo.
3. Secuencia de implementación por fases con dependencias explícitas.
4. Estrategia de pruebas por fase.
5. Riesgos, mitigaciones y criterios de salida de cada fase.
6. Lista de validaciones finales para considerar la implementación lista.

Decisiones que debe reflejar el plan:
1. Home server-rendered: usar service del módulo dashboard para orquestar datos.
2. Repositorio de propiedades: obtener conteos por estado para disponibles y rentadas.
3. Mantener contrato y orden de métricas/accesos existente.
4. No crear endpoint adicional salvo necesidad funcional imprescindible (si no aplica, dejar explícitamente fuera de alcance en el plan).
5. Ingresos y vencidos quedan explícitamente en modo no operativo para esta spec.

Formato esperado:
1. Fases claras y accionables (setup, implementación, pruebas, validación).
2. Cada fase con precondiciones, tareas técnicas y resultado verificable.
3. Criterios de aceptación técnicos trazables a la spec 005.
4. Sección de no alcance para prevenir scope creep.

Si falta una decisión crítica para planificar, preguntar en modo interactivo antes de cerrar el plan.