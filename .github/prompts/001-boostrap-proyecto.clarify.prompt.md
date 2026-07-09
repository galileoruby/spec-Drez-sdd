---
name: 001-bootstrap-proyecto-clarify
---
/speckit.clarify

Revisa la spec 001-bootstrap-proyecto.

Identifica ambigüedades, decisiones implícitas o gaps que vayan
a aflorar durante el plan o la implementación.

Áreas con foco especial:
- Breakpoints exactos del responsive (sidebar colapsable)
- Comportamiento de GET /health cuando la DB falla
  (código HTTP + forma del JSON)
- Valores de las 3 tarjetas de métrica (label, número, icono)
- Alcance de los "componentes estructurales":
  ¿HTML + CSS completo o esqueletos con placeholders?
- Generación de los 13 SVG de Lucide:
  ¿inline por el agente o descargados manualmente?
- Migración baseline: ¿vacía o con pgcrypto para gen_random_uuid()?
- Política de logging en /health y /

MODO INTERACTIVO — REGLAS OBLIGATORIAS

1. HAZ UNA SOLA PREGUNTA A LA VEZ.
   No lances todas las preguntas juntas. Espera mi respuesta antes
   de pasar a la siguiente.

2. FORMATO DE CADA PREGUNTA:

   Pregunta [N de TOTAL] — [tema corto]
   ─────────────────────────────────────
   [Enunciado claro de la pregunta]

   Por qué importa: [1 línea explicando el impacto de decidir mal]

   A) [opción concreta con valor específico]
   B) [opción concreta con valor específico]  ← Recomendado
   C) [opción concreta con valor específico]
   D) Otro — escribe tu respuesta

   > Responde con la letra (A, B, C o D) o escribe tu respuesta libre.

3. LA OPCIÓN RECOMENDADA siempre debe estar marcada con ← Recomendado
   Es la que usan la mayoría de empresas con este stack o la que
   sigue las mejores prácticas de FastAPI + Supabase + Python 3.13.

4. SI RESPONDO "D" O ESCRIBO TEXTO LIBRE:
   Acepta mi respuesta, confírmala en una línea y pasa a la siguiente.

5. SI RESPONDO CON SOLO UNA LETRA (A, B o C):
   Confirma la elección en una línea con el valor concreto elegido
   y pasa inmediatamente a la siguiente pregunta.

6. DESPUÉS DE LA ÚLTIMA PREGUNTA:
   Muestra un resumen de todas las decisiones tomadas y luego
   actualiza spec.md añadiendo la sección "Clarificaciones" con
   las respuestas integradas.

7. PREGUNTAS SÍ/NO:
   Cuando la decisión sea binaria, usa este formato simplificado:

   Pregunta [N de TOTAL] — [tema corto]
   ─────────────────────────────────────
   [Enunciado de la pregunta]

   Por qué importa: [1 línea]

   S) Sí  ← Recomendado
   N) No

   > Responde S o N.

EMPIEZA AHORA con la Pregunta 1.
