---
description: "Lista de tareas para blindar tokens visuales"
---

# Tareas: 002-blindar-tokens-visuales

**Entrada**: Documentos de diseño de `specs/002-blindar-tokens-visuales/`

**Prerrequisitos**: `plan.md` (requerido), `spec.md` (requerido), `checklists/requirements.md`

**Pruebas**: No se solicitaron pruebas automatizadas; la validación es documental y de consistencia de gobernanza.

**Organización**: Las tareas están agrupadas por historia de usuario para permitir implementación y revisión independiente.

## Formato: `[ID] [P?] [US] Descripción`

- **[P]**: Puede ejecutarse en paralelo si no depende de otra tarea abierta
- **[US]**: Historia de usuario a la que pertenece la tarea
- Incluir rutas exactas en las descripciones

## Fase 1: Preparación

**Propósito**: Confirmar alcance y artefactos base antes de tocar la gobernanza

- [X] T001 [P] Revisar el alcance de la spec y confirmar los artefactos base en `specs/002-blindar-tokens-visuales/spec.md` y `specs/002-blindar-tokens-visuales/checklists/requirements.md`

---

## Fase 2: Fundacional

**Propósito**: Establecer la base compartida de gobernanza que bloquea todas las historias de usuario

**Checkpoint**: La gobernanza de tokens visuales queda definida y puede referenciarse de forma consistente en el resto de artefactos

- [X] T002 [P] Consolidar la regla global de autorización explícita y trazabilidad de tokens visuales en `.specify/memory/constitution.md`
- [X] T003 [P] Declarar `.github/instructions/frontend.instructions.md` como fuente operativa para tokens visuales y fijar la regla de uso en `.github/instructions/frontend.instructions.md`

---

## Fase 3: Historia de usuario 1 - Proteger la consistencia visual base (Prioridad: P1)

**Objetivo**: Evitar cambios no autorizados en colores, sombras, radios y espaciados canónicos

**Prueba independiente**: Se puede revisar una propuesta de cambio visual y confirmar que, sin autorización explícita, no cumple la norma de esta spec

- [X] T004 [US1] Formalizar en `.specify/memory/constitution.md` que cualquier cambio en tokens visuales canónicos requiere autorización explícita y trazabilidad en `tasks.md`

**Checkpoint**: La consistencia visual base queda protegida por la constitución global

---

## Fase 4: Historia de usuario 2 - Hacer explícita la fuente operativa de tokens (Prioridad: P2)

**Objetivo**: Reducir ambigüedad sobre dónde leer la norma operativa de tokens visuales

**Prueba independiente**: Se puede inspeccionar la documentación y verificar que existe una única fuente operativa declarada para los tokens visuales

- [X] T005 [US2] Declarar explícitamente en `.github/instructions/frontend.instructions.md` que este archivo es la fuente operativa para tokens visuales

**Checkpoint**: La referencia operativa queda inequívoca para cualquier trabajo de frontend

---

## Fase 5: Historia de usuario 3 - Exigir trazabilidad de cambios en tokens (Prioridad: P3)

**Objetivo**: Garantizar que cualquier cambio de tokens visuales quede rastreado en tareas aprobadas

**Prueba independiente**: Se puede revisar una spec futura y comprobar que la trazabilidad del cambio visual aparece en `tasks.md`

- [X] T006 [US3] Añadir en `.specify/templates/spec-template.md` la sección obligatoria de tokens visuales y reglas de gobernanza
- [X] T007 [US3] Incluir en `.specify/templates/spec-template.md` la exigencia de rastrear cada cambio de token visual a tareas concretas en `tasks.md`

**Checkpoint**: La trazabilidad queda incorporada al flujo estándar de creación de specs

---

## Fase final: Pulido y coherencia transversal

**Propósito**: Sincronizar referencias cruzadas y dejar el conjunto listo para uso repetido

- [X] T008 [P] Actualizar el historial de versión y referencias cruzadas de gobernanza en `.specify/memory/constitution.md` y `.specify/templates/spec-template.md`

---

## Dependencias y orden de ejecución

### Dependencias de fase

- **Preparación (Fase 1)**: Sin dependencias previas
- **Fundacional (Fase 2)**: Depende de la preparación y bloquea las historias de usuario
- **Historias de usuario (Fases 3+)**: Dependen de la fase fundacional
- **Pulido (Fase final)**: Depende de todas las historias de usuario que se quieran cerrar

### Dependencias de historias de usuario

- **Historia de usuario 1 (P1)**: Puede comenzar tras la fase fundacional; no depende de otras historias
- **Historia de usuario 2 (P2)**: Puede comenzar tras la fase fundacional; no depende de otras historias
- **Historia de usuario 3 (P3)**: Puede comenzar tras la fase fundacional; no depende de otras historias

### Dentro de cada historia de usuario

- La tarea debe dejar el artefacto coherente y autónomo
- Las modificaciones de gobernanza deben mantenerse en español
- Las referencias a `tasks.md` deben ser explícitas y verificables

### Oportunidades en paralelo

- `T002` y `T003` pueden ejecutarse en paralelo porque tocan artefactos distintos
- `T005` y `T006` pueden ejecutarse en paralelo después de la fase fundacional si el equipo separa la edición de artefactos
- `T008` puede ejecutarse al final una vez consolidadas las tres historias

---

## Ejemplo paralelo: Historia de usuario 1

```bash
Task: "Consolidar la regla global de autorización explícita y trazabilidad de tokens visuales en .specify/memory/constitution.md"
Task: "Declarar .github/instructions/frontend.instructions.md como fuente operativa para tokens visuales y fijar la regla de uso en .github/instructions/frontend.instructions.md"
```

---

## Estrategia de implementación

### MVP primero (Historia de usuario 1)

1. Completar la Fase 1: Preparación
2. Completar la Fase 2: Fundacional
3. Completar la Fase 3: Historia de usuario 1
4. Validar que la regla global de tokens visuales ya no permite cambios no autorizados

### Entrega incremental

1. Preparación + fundación -> base de gobernanza
2. Historia de usuario 1 -> protección de consistencia visual
3. Historia de usuario 2 -> fuente operativa explícita
4. Historia de usuario 3 -> trazabilidad obligatoria en el flujo de specs

### Estrategia paralela

1. Un agente puede cerrar la constitution mientras otro ajusta la instrucción de frontend
2. Una vez asentada la base, otro agente puede extender la plantilla de spec con la gobernanza de tokens
3. El pulido final se puede realizar después de consolidar los tres cambios