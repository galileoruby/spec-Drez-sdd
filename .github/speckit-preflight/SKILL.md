---
name: speckit-preflight
description: >
  Verifica que el entorno esté listo antes de ejecutar cualquier comando
  Speckit. USE WHEN: el usuario va a ejecutar speckit.specify,
  speckit.clarify, speckit.plan, speckit.tasks o speckit.implement.
---

# Preflight Speckit

Antes de continuar con cualquier comando Speckit, verifica lo siguiente
en orden y reporta el resultado de cada punto:

1. Lee `.specify/feature.json` y confirma que existe y tiene
   `feature_directory` apuntando a una carpeta bajo `specs/`.

2. Verifica que esa carpeta existe en el filesystem del repo.

3. Lee `.specify/extensions.yml` y lista los hooks `before_<comando>`
   que tienen `optional: false`. Informa cuáles requieren ejecución
   obligatoria antes de continuar.

4. Lee `.specify/memory/constitution.md` y confirma que fue cargado.

5. Si algún punto falla, detente y reporta exactamente qué falta antes
   de continuar.

6. Si todo está en orden, responde: "Preflight completado. Listo para
   ejecutar `<comando>`."