# Contrato de contexto: pagina de propiedades

## Ruta

- Endpoint: GET /propiedades
- Tipo de respuesta: text/html

## Contexto esperado por template

## Clave propiedades

- Tipo: list[dict]
- Orden: created_at descendente
- Campos por item:

```json
{
  "imagen_url": "string",
  "titulo": "string",
  "direccion": "string",
  "habitaciones": 0,
  "banos": "string",
  "area_m2": "string",
  "precio_renta": "string",
  "estado": "string"
}
```

## Clave mostrar_estado_vacio

- Tipo: bool
- Regla: true cuando no hay propiedades.

## Clave total_propiedades

- Tipo: int
- Regla: total de cards a renderizar.

## Reglas de presentacion obligatorias

1. Si imagen_url no es utilizable, usar fallback local fijo del proyecto.
2. Titulo con truncado visual maximo de 2 lineas.
3. Direccion con truncado visual maximo de 2 lineas.
4. Renderizar una card por propiedad sin filtros ni paginacion.

## Navegacion lateral

- El enlace Propiedades de sidebar debe usar href="/propiedades".
