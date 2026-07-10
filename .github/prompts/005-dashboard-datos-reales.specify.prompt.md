---
name: 005-dashboard-datos-reales-spec
agent: speckit.specify
---

Crear una nueva spec llamada 005-dashboard-datos-reales en specs/005-dashboard-datos-reales/spec.md.

Objetivo de la spec:
Reemplazar el mock actual del dashboard principal por datos reales de base de datos para las métricas de propiedades, manteniendo la arquitectura vertical slice y el contrato de contexto de la home.

Instrucciones de redacción (muy importante):
1. No repetir reglas globales ya definidas en la constitución ni en las instrucciones de GitHub.
2. Enfocar el contenido solo en decisiones y requisitos específicos de esta feature.
3. Si una regla ya existe a nivel global, solo referenciar que “aplica la gobernanza vigente” sin reescribirla.
4. Escribir todo en español.
5. Mantener alcance acotado y verificable.

Contexto funcional actual:
- La home ya existe y se renderiza con datos hardcodeados.
- Ya existe base de propiedades (spec previa) con estados que permiten calcular conteos reales.
- Las métricas ingresos y vencidos aún no tienen modelo de datos completo para cálculo real.

Alcance incluido:
1. Obtener desde base de datos las métricas:
   - propiedades disponibles
   - propiedades rentadas
2. Reemplazar en la home los valores hardcodeados de esas métricas.
3. Conservar el contrato de contexto de la vista (orden y estructura de métricas/accesos).
4. Mantener ingresos y vencidos en modo no operativo explícito (sin inventar cálculo).

Alcance excluido:
1. No crear en esta spec módulos de rentas/pagos nuevos.
2. No rediseñar UI, tokens visuales ni estilos.
3. No introducir nuevas dependencias.
4. No implementar reporting ni analítica histórica.

Decisión arquitectónica esperada:
- La página principal server-rendered debe resolver datos vía servicio de dashboard.
- Solo definir endpoint adicional si aporta valor funcional concreto para refresh parcial; si no, documentar que no se requiere endpoint nuevo en esta spec.

Criterios de aceptación mínimos:
1. La home deja de usar datos hardcodeados para disponibles y rentadas.
2. Los valores renderizados reflejan datos reales persistidos.
3. El banner de estado vacío responde al estado real de datos.
4. Tests cubren al menos:
   - cálculo de métricas desde repositorio/servicio
   - render de home con valores reales
5. Se define claramente qué queda pendiente para una spec futura (ingresos/vencidos reales).

Entregable esperado:
Generar spec.md completo, con secciones claras de objetivo, alcance, no alcance, historias de usuario, criterios de aceptación, riesgos/dependencias y preguntas abiertas (solo si faltan decisiones).

Si falta información, hacer preguntas de clarificación en modo interactivo antes de cerrar la spec.