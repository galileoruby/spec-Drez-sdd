# Contratos HTTP — 001-bootstrap-proyecto

## Alcance
Contratos de los endpoints iniciales definidos en la spec fundacional.

## 1) GET /health

### Objetivo
Exponer estado operativo de la aplicación y conectividad con base de datos.

### Request
- Método: `GET`
- Body: no aplica
- Auth: no aplica

### Response (estado saludable)
- Status: `200 OK`
- Body JSON:

```json
{
  "status": "ok",
  "db": "ok"
}
```

### Response (falla de DB)
- Status: `200 OK`
- Body JSON:

```json
{
  "status": "degraded",
  "db": "error"
}
```

### Reglas de logging
- Nivel `INFO` por request
- Eventos mínimos: inicio, fin
- Campos mínimos: ruta, status, duración
- Prohibido incluir payload sensible

## 2) GET /

### Objetivo
Renderizar dashboard demo inicial con layout base y tres métricas fijas.

### Request
- Método: `GET`
- Body: no aplica
- Auth: no aplica

### Response
- Status: `200 OK`
- Content-Type: `text/html`
- Render esperado:
  - Sidebar visible en desktop
  - Sidebar colapsable para viewport `< 1024px`
  - Navbar
  - Tres tarjetas de métrica:
    - Propiedades activas — `12` — `building-2`
    - Contratos vigentes — `9` — `file-text`
    - Ingresos estimados — `$8,750` — `wallet`

### Reglas de logging
- Nivel `INFO` por request
- Eventos mínimos: inicio, fin
- Campos mínimos: ruta, status, duración
- Prohibido incluir payload sensible
