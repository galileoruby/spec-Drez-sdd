# Data Model: 006-pagina-propiedades-cards

## Alcance

La feature no crea tablas ni migraciones nuevas. Define contratos de lectura y render para listar propiedades existentes.

## Entidad logica: PropiedadCardView

- Tipo: DTO de presentacion para card.
- Campos visibles obligatorios:
  - imagen_url: str
  - titulo: str
  - direccion: str
  - habitaciones: int
  - banos: str
  - area_m2: str
  - precio_renta: str
  - estado: str
- Reglas:
  - imagen_url debe usar fallback local cuando no sea utilizable.
  - titulo y direccion se presentan con truncado multilinea (2 lineas cada uno).

## Entidad logica: ListadoPropiedadesContexto

- Tipo: contexto server-rendered para template.
- Campos:
  - propiedades: list[PropiedadCardView]
  - mostrar_estado_vacio: bool
  - total_propiedades: int
- Reglas:
  - mostrar_estado_vacio = true cuando total_propiedades == 0.
  - propiedades llega ordenada por created_at descendente.

## Relacion con dominio persistente

- Fuente: app.modules.propiedades.models.Propiedad.
- Campos de origen usados:
  - titulo
  - direccion
  - habitaciones
  - banos
  - area_m2
  - precio_mensual
  - estado
  - imagen_url
  - created_at (solo para orden)

## Casos de datos incompletos

- imagen_url faltante o vacia: se reemplaza con fallback local.
- textos largos: se mantienen en contenido, con truncado visual CSS.
- estado distinto de disponible/rentada: se muestra el estado real proveniente del dominio.

## Validaciones funcionales

- Una card por propiedad retornada.
- Campos visibles completos por card.
- Estado vacio consistente cuando no hay registros.
