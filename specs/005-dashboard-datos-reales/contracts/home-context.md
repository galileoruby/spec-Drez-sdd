# Contrato de contexto de home: 005-dashboard-datos-reales

## Objetivo

Documentar el contrato de datos que consume `app/templates/pages/dashboard.html` para evitar regresiones durante el cambio de mock a datos reales.

## Ruta afectada

- Endpoint existente: `GET /`
- Tipo de respuesta: `text/html`

## Contrato de contexto (render)

## Clave `metricas`

- **Tipo**: `list[dict]`
- **Orden**: Se conserva el orden vigente en la home.
- **Estructura por elemento**:

```json
{
  "titulo": "string",
  "valor": "string",
  "icono": "string",
  "tendencia": "string"
}
```

## Reglas de negocio del contrato

1. Las métricas de **disponibles** y **rentadas** deben reflejar conteos reales persistidos.
2. Las métricas de **ingresos** y **vencidos** se mantienen en modo no operativo explícito (sin cálculo real).
3. Se preservan claves, orden y estructura para compatibilidad con componentes actuales.

## Clave `mostrar_estado_vacio`

- **Tipo**: `bool`
- **Regla**:
  - `true` cuando no existan datos para métricas operativas.
  - `false` cuando exista al menos un registro que alimente disponibles/rentadas.

## Endpoint adicional

No se agrega endpoint adicional en esta spec. El contrato se resuelve con server-rendering del `GET /`.

## Ejemplo de contexto efectivo

```json
{
  "metricas": [
    {
      "titulo": "Propiedades disponibles",
      "valor": "24",
      "icono": "building-2",
      "tendencia": ""
    },
    {
      "titulo": "Propiedades rentadas",
      "valor": "18",
      "icono": "file-text",
      "tendencia": ""
    },
    {
      "titulo": "Ingresos del mes",
      "valor": "No operativo",
      "icono": "wallet",
      "tendencia": "Pendiente de modelado en spec futura"
    },
    {
      "titulo": "Pagos vencidos",
      "valor": "No operativo",
      "icono": "alert-triangle",
      "tendencia": "Pendiente de modelado en spec futura"
    }
  ],
  "mostrar_estado_vacio": false
}
```
