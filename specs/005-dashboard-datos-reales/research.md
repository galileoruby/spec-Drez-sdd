# Research: 005-dashboard-datos-reales

## Decisión 1: Orquestación de home en servicio de dashboard

- **Decision**: Crear un servicio del módulo `dashboard` para componer el contexto de la home server-rendered.
- **Rationale**: Centraliza lógica de negocio de métricas y preserva `routes.py` delgado, facilitando pruebas unitarias del cálculo.
- **Alternatives considered**:
  - Calcular métricas directamente en `app/main.py`.
    - Rechazada por mezclar composición de negocio con configuración/ruteo global.
  - Calcular métricas en el template Jinja.
    - Rechazada por romper separación de responsabilidades y testabilidad.

## Decisión 2: Fuente de datos real para disponibles y rentadas

- **Decision**: Obtener conteos por estado (`disponible`, `rentada`) desde repositorio de `propiedades` mediante consulta agregada.
- **Rationale**: Reutiliza dominio existente, evita duplicación y minimiza round-trips a base de datos.
- **Alternatives considered**:
  - Ejecutar dos consultas independientes (`COUNT`) por estado.
    - Rechazada por menor eficiencia y mayor complejidad operativa.
  - Cargar listado completo de propiedades y contar en memoria.
    - Rechazada por costo innecesario y peor escalabilidad.

## Decisión 3: Contrato de contexto estable de la home

- **Decision**: Mantener estructura y orden actual de métricas/accesos; solo cambia la procedencia de valores para disponibles/rentadas.
- **Rationale**: Reduce riesgo de regresiones en render y componentes ya integrados.
- **Alternatives considered**:
  - Rediseñar contrato para semántica nueva de métricas.
    - Rechazada por abrir alcance no autorizado y riesgo de ruptura.

## Decisión 4: Endpoint adicional

- **Decision**: No agregar endpoint nuevo en esta spec.
- **Rationale**: El objetivo funcional se cumple con render server-side de `/` y no existe necesidad imprescindible de refresh parcial.
- **Alternatives considered**:
  - Endpoint HTMX para refresco parcial de métricas.
    - Rechazada por aportar complejidad sin valor funcional requerido en esta iteración.

## Decisión 5: Estado de ingresos y vencidos

- **Decision**: Mantener ambos indicadores en modo no operativo explícito.
- **Rationale**: No existe modelo de datos completo en esta feature para cálculo real; evita cifras inventadas.
- **Alternatives considered**:
  - Simular valores derivados de propiedades.
    - Rechazada por generar resultados engañosos y deuda funcional.

## Resultado de clarificaciones

No quedan decisiones críticas abiertas para pasar a diseño e implementación de tareas.
