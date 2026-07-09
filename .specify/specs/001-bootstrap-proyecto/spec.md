# Especificación de funcionalidad: 001-bootstrap-proyecto

**Rama de funcionalidad**: `001-bootstrap-proyecto`

**Creado**: 2026-07-08

**Estado**: Aprobada

**Entrada**: Descripción del usuario: "Dejar el esqueleto técnico y visual del sistema Realtor en pie, listo para recibir el primer módulo de dominio en la spec 002. Es la spec fundacional: sin ella las siguientes no se sostienen."

## Escenarios de usuario y pruebas

### Historia de usuario 1 - Esqueleto técnico base del sistema (Prioridad: P1)

El equipo de desarrollo debe poder levantar una aplicación FastAPI con configuración, base de datos y endpoints base listos para futuras funcionalidades de dominio.

**Por qué esta prioridad**: esta historia entrega la base necesaria para que las siguientes specs puedan construir sobre una infraestructura estable y consistente.

**Prueba independiente**: se puede iniciar el servidor, consultar la ruta de salud y verificar que el dashboard base se renderiza correctamente.

**Escenarios de aceptación**:

1. **Dado** que la aplicación está configurada con variables de entorno adecuadas, **cuando** se inicia el servidor, **entonces** el endpoint de salud responde con estado operativo y la conexión a base de datos queda verificada.
2. **Dado** que el sistema está ejecutándose, **cuando** se solicita la ruta raíz, **entonces** se renderiza un dashboard demo con una barra lateral, una barra de navegación y tres tarjetas de métrica.

---

### Historia de usuario 2 - Base visual reutilizable para futuras vistas (Prioridad: P2)

El equipo debe poder reutilizar una estructura visual consistente con sidebar, navbar, componentes de UI y sistema de iconos vendoreados para futuras pantallas del producto.

**Por qué esta prioridad**: esta historia asegura que la interfaz tenga una base sólida, coherente y preparada para crecer sin introducir inconsistencias visuales.

**Prueba independiente**: se puede abrir la ruta raíz y verificar que el layout responsive, los componentes y los iconos se renderizan correctamente.

**Escenarios de aceptación**:

1. **Dado** que el layout base está implementado, **cuando** se carga la ruta raíz en un navegador, **entonces** la interfaz muestra una sidebar visible y un área principal con componentes estructurales.
2. **Dado** que la aplicación está en un ancho menor a 1024px, **cuando** se visualiza la interfaz, **entonces** la sidebar se colapsa mediante un menú toggleable.

---

### Historia de usuario 3 - Preparación para calidad y despliegue inicial (Prioridad: P3)

El equipo debe poder ejecutar validaciones estáticas, migraciones de base de datos y comprobaciones de calidad sin reconfigurar el proyecto desde cero.

**Por qué esta prioridad**: esta historia reduce el riesgo técnico inicial y facilita el avance del proyecto con estándares de calidad desde el comienzo.

**Prueba independiente**: se pueden ejecutar las tareas de lint, formato, tipado y migraciones sobre la base del proyecto.

**Escenarios de aceptación**:

1. **Dado** que la configuración de herramientas está lista, **cuando** se ejecutan las verificaciones de Ruff, MyPy y las migraciones de Alembic, **entonces** estas operaciones finalizan sin errores críticos.
2. **Dado** que la infraestructura de base de datos está disponible, **cuando** se aplica la migración baseline, **entonces** la migración queda registrada correctamente en Supabase.

---

## Casos límite

- Qué ocurre si las variables de entorno de base de datos no están definidas correctamente.
- Cómo responde la aplicación si la conexión a la base de datos no está disponible en el momento de consultar la ruta de salud.
	- Decisión: responder con `HTTP 200` y JSON `{"status":"degraded","db":"error"}`.
- Qué ocurre si un icono solicitado no existe en la carpeta de iconos vendoreados.
- Qué sucede si la aplicación se carga en un dispositivo móvil con pantallas pequeñas.

## Requisitos

### Requisitos funcionales

- **FR-001**: El sistema DEBE exponer una estructura base de proyecto con los módulos y archivos requeridos en la ruta esperada.
- **FR-002**: El sistema DEBE incluir un módulo de configuración basado en Pydantic Settings que lea variables desde el archivo de entorno y exponga los valores de base de datos, entorno de aplicación y nivel de logging.
- **FR-003**: El sistema DEBE definir una conexión asíncrona a PostgreSQL con la configuración requerida para Supabase y un proveedor de sesión de base de datos por request.
- **FR-004**: El sistema DEBE inicializar Alembic en modo asíncrono y preparar una migración baseline aplicable contra Supabase.
	- La baseline DEBE incluir `CREATE EXTENSION IF NOT EXISTS pgcrypto;` para habilitar `gen_random_uuid()`.
- **FR-005**: El sistema DEBE exponer el endpoint GET /health que devuelva un estado JSON con el resultado de la aplicación y la base de datos.
	- Cuando la base de datos falle, DEBE responder `HTTP 200` con `{"status":"degraded","db":"error"}`.
- **FR-006**: El sistema DEBE exponer el endpoint GET / que renderice un dashboard demo con sidebar, navbar y tres tarjetas de métrica con datos hardcoded.
	- El dashboard demo DEBE incluir exactamente estas métricas hardcoded:
	- Propiedades activas: `12` con icono `building-2`.
	- Contratos vigentes: `9` con icono `file-text`.
	- Ingresos del mes: `$8,750` con icono `wallet`.
- **FR-007**: El sistema DEBE incluir un sistema visual base con tokens de diseño, layout responsive, componentes reutilizables y estilos organizados por secciones.
	- La sidebar DEBE colapsarse en viewport menor a `1024px`.
- **FR-008**: El sistema DEBE incluir iconografía SVG outline vendoreada en la ruta indicada y un macro Jinja2 para inyectar los iconos de forma inline.
	- Los 13 SVG DEBEN vendorearse desde archivos oficiales de Lucide, uno por archivo, sin edición estructural.
- **FR-009**: El sistema DEBE incluir los componentes estructurales base en la carpeta de templates correspondiente.
	- Los componentes estructurales base en esta spec DEBEN entregarse con HTML completo, clases CSS base y estados visuales mínimos (hover/focus/empty).
- **FR-010**: El sistema DEBE configurar Ruff, MyPy y pytest-asyncio con las reglas y opciones requeridas en el archivo de configuración del proyecto.
- **FR-011**: El sistema DEBE permitir que las verificaciones estáticas y las migraciones se ejecuten sin errores críticos en el entorno definido.
- **FR-012**: El sistema DEBE mantener todo el contenido de documentación en español, sin mezclar idiomas en archivos Markdown.
- **FR-013**: El endpoint GET /health y la ruta GET / DEBEN emitir logging estructurado en nivel INFO por request (inicio/fin, ruta, código de estado y duración), sin payload sensible.

### Entidades clave

- **Configuración de aplicación**: representa los valores de entorno que determinan el comportamiento del sistema en ejecución.
- **Conexión de base de datos**: representa la sesión asíncrona y la configuración de acceso a PostgreSQL mediante Supabase.
- **Dashboard base**: representa la vista inicial del sistema con componentes estructurales y métricas demo.

## Criterios de éxito

### Resultados medibles

- **CS-001**: La aplicación puede iniciarse con uvicorn sin errores y la ruta /health responde:
	- Estado saludable: `HTTP 200` con `{"status":"ok","db":"ok"}`.
	- Falla de DB: `HTTP 200` con `{"status":"degraded","db":"error"}`.
- **CS-002**: La ruta / renderiza un dashboard demo con una sidebar visible y tres tarjetas de métrica.
- **CS-003**: El layout responde correctamente al reducir el ancho de la pantalla por debajo de 1024px.
- **CS-004**: Las verificaciones de Ruff, formato, MyPy y migración de Alembic se ejecutan sin errores críticos.
- **CS-005**: Todo el contenido narrativo de los archivos .md del repo está en español. Se aceptan como excepciones: nombres de tecnologías (FastAPI, SQLAlchemy, HTMX, Jinja2, etc.), rutas de archivos (app/main.py, .specify/, etc.), comandos de terminal (uv sync, alembic upgrade head, etc.) e identificadores técnicos (DATABASE_URL, get_session, etc.). No se aceptan párrafos, descripciones ni comentarios en inglés.

## Clarificaciones

### Session 2026-07-08

- Q: ¿Qué contrato exacto tendrá GET /health cuando la DB falle? → A: `HTTP 200` con `{"status":"degraded","db":"error"}`.
- Q: ¿Cuál es el breakpoint exacto para colapsar la sidebar? → A: colapsa en viewport menor a `1024px`.
- Q: ¿Qué valores exactos tendrán las tres tarjetas de métrica? → A: Propiedades activas `12` (`building-2`), Contratos vigentes `9` (`file-text`), Ingresos del mes `$8,750` (`wallet`).
- Q: ¿Cuál es el alcance de implementación de componentes estructurales en la 001? → A: HTML completo + clases CSS base + estados mínimos (hover/focus/empty).
- Q: ¿Cómo se incorporan los 13 SVG de Lucide? → A: vendoreados desde archivos oficiales, uno por archivo, sin edición estructural.
- Q: ¿Cómo debe ser la migración baseline? → A: incluir `CREATE EXTENSION IF NOT EXISTS pgcrypto;` para `gen_random_uuid()`.
- Q: ¿Qué política de logging aplica a GET /health y GET /? → A: logging estructurado INFO por request (inicio/fin, ruta, status, duración), sin payload sensible.

## Supuestos

- El entorno de desarrollo usa Python 3.13 y el gestor uv.
- La base de datos PostgreSQL de Supabase estará disponible para las migraciones y validaciones iniciales.
- No se implementará autenticación de usuarios ni módulos de negocio en esta especificación.
- La interfaz inicial prioriza una base visual estable y reutilizable sobre funcionalidades complejas.
- La baseline incluirá `pgcrypto` para estandarizar `gen_random_uuid()` desde el arranque.

## Notas de cierre (Fase 6)

- Se verificó la consistencia entre `spec.md`, `plan.md` y `tasks.md`.
- El contrato final de `GET /health` queda consolidado con `HTTP 200` tanto en estado `ok` como en estado `degraded`.
- Se completaron todas las fases de implementación definidas en `tasks.md` (T001 a T036).
- La evidencia operativa de validación técnica quedó registrada en `quickstart.md`.
