---
name: 006-pagina-propiedades-cards-spec
agent: speckit.specify
---

Crear una nueva spec llamada 006-pagina-propiedades-cards en specs/006-pagina-propiedades-cards/spec.md.

Objetivo de la spec:
Crear una página server-rendered de propiedades que liste todas las propiedades persistidas en la base de datos en formato de cards, similar al diseño adjunto, incorporando primero un endpoint dedicado que consulte los datos reales y luego una vista responsive que renderice esas propiedades. La navegación lateral debe redirigir correctamente a esta nueva página desde el link de “Propiedades”.

Instrucciones de redacción (muy importante):
1. No repetir reglas globales ya definidas en la constitución ni en las instrucciones del repositorio.
2. Enfocar el contenido solo en decisiones y requisitos específicos de esta feature.
3. Si una regla ya existe a nivel global, solo referenciar que aplica la gobernanza vigente.
4. Escribir todo en español.
5. Mantener alcance acotado, implementable y verificable.
6. No introducir alcance no solicitado.
7. Si falta una decisión crítica para cerrar la spec, hacer preguntas de clarificación en modo interactivo antes de terminar.

Contexto funcional actual:
- Ya existe el layout base con sidebar, navbar y render server-side reutilizable en base.html.
- El link “Propiedades” del sidebar actualmente no navega a una página real y está hardcodeado como placeholder en _sidebar.html.
- Ya existe el dominio base de propiedades y la persistencia en base de datos.
- Ya existe un patrón de router server-rendered para páginas en routes.py.
- Ya existe un componente base de card de propiedad en el repositorio, pero esta spec debe definir con claridad si se reutiliza o se ajusta el markup para cumplir el diseño solicitado.

Alcance incluido:
1. Crear un endpoint GET dedicado para listar propiedades.
2. El endpoint debe consultar desde base de datos todas las propiedades necesarias para la pantalla.
3. Crear la página de propiedades con grid responsive de cards.
4. Mostrar en cada card:
   - imagen
   - título
   - dirección
   - número de habitaciones
   - número de baños
   - área en metros cuadrados
   - precio de renta
   - estado
5. Definir comportamiento responsive:
   - desktop: 3 cards por fila
   - tablet: 2 cards por fila
   - phone: 1 card por fila
6. Conectar el link “Propiedades” del menú lateral para que navegue a la nueva página.
7. Mantener la página dentro del layout visual existente del sistema.
8. Definir contratos de contexto y pruebas mínimas para endpoint + render.

Alcance excluido:
1. No crear dominio nuevo de rentas, pagos, inquilinos o contratos.
2. No crear filtros avanzados, búsqueda, paginación ni ordenamiento, salvo que se decida explícitamente en clarificación.
3. No introducir nuevas dependencias.
4. No rediseñar el layout global, navbar o sidebar más allá del enlace necesario.
5. No cambiar tokens visuales globales ni paleta.
6. No crear edición inline ni acciones CRUD adicionales desde esta pantalla, salvo navegación futura claramente fuera de alcance.

Secuencia funcional esperada:
1. Primero definir el endpoint que obtendrá las propiedades desde la base de datos.
2. Luego definir la vista/página server-rendered que consumirá ese resultado.
3. Finalmente conectar la navegación lateral para que el enlace de propiedades redirija a la nueva página.

Decisiones arquitectónicas esperadas:
1. La feature debe vivir en su propio vertical slice de propiedades o extender el slice existente de propiedades, sin mezclar lógica de negocio en templates.
2. El endpoint debe ser async y usar servicio + repositorio para obtener datos reales.
3. La vista debe ser server-rendered.
4. La página debe reutilizar el layout existente del sistema.
5. La responsividad debe resolverse con CSS propio del proyecto y sin frameworks externos.
6. El contrato de datos enviado al template debe quedar explícitamente definido para evitar acoplamiento implícito.

Requisitos funcionales mínimos que la spec debe cubrir:
1. El sistema debe exponer una ruta navegable para la página de propiedades.
2. El sistema debe consultar propiedades reales persistidas desde base de datos.
3. El sistema debe renderizar una card por propiedad.
4. Cada card debe contener exactamente los datos visibles solicitados.
5. El sistema debe mostrar 3, 2 o 1 card por fila según breakpoint desktop, tablet o phone.
6. El enlace “Propiedades” del sidebar debe apuntar a la nueva ruta real.
7. La vista debe seguir funcionando cuando no existan propiedades.
8. La spec debe definir qué sucede con imágenes faltantes o datos incompletos visibles.

Casos límite a considerar:
1. No existen propiedades en base de datos.
2. Existe una propiedad sin imagen utilizable.
3. Existen textos largos en título o dirección.
4. Existen propiedades con estados distintos de disponible/rentada.
5. Existen muchas propiedades y el usuario navega en pantalla pequeña.
6. La dirección o el área exceden el espacio visual esperado de la card.

Criterios de aceptación mínimos:
1. Existe un endpoint GET para propiedades que obtiene los datos requeridos desde base de datos.
2. La página de propiedades renderiza cards con datos reales persistidos.
3. Cada card muestra imagen, título, dirección, habitaciones, baños, área, precio y estado.
4. El layout responsive cumple:
   - 3 columnas en desktop
   - 2 columnas en tablet
   - 1 columna en phone
5. El link “Propiedades” del menú lateral navega a la nueva página.
6. Se preserva el layout general de la app sin rediseño global.
7. Existen pruebas para:
   - obtención de propiedades desde repositorio/servicio
   - render HTML de la página
   - navegación al endpoint correcto
   - comportamiento del estado vacío
8. Queda explícitamente definido qué no entra en esta spec para evitar scope creep.

Entregables esperados:
1. spec.md completo.
2. Historias de usuario priorizadas.
3. Requisitos funcionales verificables.
4. Casos límite.
5. Criterios de aceptación medibles.
6. Riesgos y dependencias.
7. Preguntas abiertas solo si son realmente bloqueantes.

Notas específicas que debe reflejar la spec:
1. La página debe inspirarse visualmente en el diseño adjunto: cards con imagen dominante arriba y bloque de información resumida debajo.
2. La navegación lateral ya existe y debe ser actualizada desde el componente de sidebar actual en _sidebar.html.
3. La nueva pantalla debe convivir con el layout base actual en base.html.
4. La implementación debe apoyarse en datos reales del dominio de propiedades ya existente.

Si falta información importante, hacer preguntas de clarificación en modo interactivo antes de cerrar la spec.