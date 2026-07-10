"""Carga inicial idempotente de propiedades en Miami."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_seed_propiedades_miami"
down_revision: str | None = "0002_create_propiedades"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

PROPIEDADES_MIAMI: tuple[dict[str, object], ...] = (
    {
        "id": "70f8dcb8-7f07-4a37-a8f3-599e55d7be01",
        "titulo": "Loft Brickell Bay",
        "direccion": "1200 Brickell Bay Dr Apt 1801",
        "ciudad": "Miami",
        "precio_mensual": "4200.00",
        "habitaciones": 2,
        "banos": "2.0",
        "area_m2": "118.00",
        "estado": "disponible",
    },
    {
        "id": "ef47479a-4c7e-4b59-afd1-12f56ddf4b02",
        "titulo": "Condo Ocean Drive 9B",
        "direccion": "801 Ocean Dr Unit 9B",
        "ciudad": "Miami",
        "precio_mensual": "5100.00",
        "habitaciones": 3,
        "banos": "2.5",
        "area_m2": "152.40",
        "estado": "rentada",
    },
    {
        "id": "cb00fe26-8cfc-4fbf-86c1-9a7f2dd71603",
        "titulo": "Casa Coral Gables Norte",
        "direccion": "3400 Ponce de Leon Blvd",
        "ciudad": "Miami",
        "precio_mensual": "6800.00",
        "habitaciones": 4,
        "banos": "3.0",
        "area_m2": "244.00",
        "estado": "disponible",
    },
    {
        "id": "53ae8ccd-7971-47ef-8db8-f1ec343ca604",
        "titulo": "Townhouse Wynwood Central",
        "direccion": "75 NW 29th St",
        "ciudad": "Miami",
        "precio_mensual": "3900.00",
        "habitaciones": 2,
        "banos": "2.0",
        "area_m2": "129.70",
        "estado": "mantenimiento",
    },
    {
        "id": "5dcfefef-0417-46eb-97e4-2869fd6ab705",
        "titulo": "Residencia Coconut Grove Park",
        "direccion": "3125 Commodore Plaza",
        "ciudad": "Miami",
        "precio_mensual": "7200.00",
        "habitaciones": 4,
        "banos": "3.5",
        "area_m2": "261.30",
        "estado": "rentada",
    },
    {
        "id": "8ae5072e-73a4-4812-8b35-3bf4f5274506",
        "titulo": "Apartamento Midtown Vista",
        "direccion": "3250 NE 1st Ave",
        "ciudad": "Miami",
        "precio_mensual": "3350.00",
        "habitaciones": 1,
        "banos": "1.5",
        "area_m2": "87.20",
        "estado": "disponible",
    },
    {
        "id": "8a95bfba-6ef2-4817-89db-5ffc3dc44d07",
        "titulo": "Penthouse Edgewater 21",
        "direccion": "2900 NE 7th Ave PH21",
        "ciudad": "Miami",
        "precio_mensual": "9800.00",
        "habitaciones": 3,
        "banos": "3.5",
        "area_m2": "288.90",
        "estado": "inactiva",
    },
    {
        "id": "5838fb7d-6ae4-4b69-b1b6-5779771fe008",
        "titulo": "Studio Little Havana Sol",
        "direccion": "1400 SW 8th St Unit 4",
        "ciudad": "Miami",
        "precio_mensual": "2100.00",
        "habitaciones": 1,
        "banos": "1.0",
        "area_m2": "54.00",
        "estado": "disponible",
    },
    {
        "id": "c9138ec7-e3d8-4bd8-a43f-f9f39500cf09",
        "titulo": "Villa Key Biscayne Azul",
        "direccion": "450 Ocean Dr",
        "ciudad": "Miami",
        "precio_mensual": "12400.00",
        "habitaciones": 5,
        "banos": "4.0",
        "area_m2": "336.50",
        "estado": "rentada",
    },
    {
        "id": "c596241d-eb02-4f19-bff0-ab775f6f3d10",
        "titulo": "Condo Downtown River 12",
        "direccion": "200 Biscayne Blvd Way Unit 12",
        "ciudad": "Miami",
        "precio_mensual": "4600.00",
        "habitaciones": 2,
        "banos": "2.0",
        "area_m2": "132.80",
        "estado": "mantenimiento",
    },
)


def _imagen_url(propiedad_id: str) -> str:
    """Genera la URL de imagen determinista para cada propiedad."""

    return f"https://picsum.photos/seed/{propiedad_id}/800/500"


def upgrade() -> None:
    """Siembra 10 propiedades de Miami de forma idempotente."""

    bind = op.get_bind()
    upsert_sql = sa.text(
        """
        INSERT INTO propiedades (
            id,
            titulo,
            direccion,
            ciudad,
            precio_mensual,
            habitaciones,
            banos,
            area_m2,
            estado,
            imagen_url
        ) VALUES (
            CAST(:id AS uuid),
            :titulo,
            :direccion,
            :ciudad,
            :precio_mensual,
            :habitaciones,
            :banos,
            :area_m2,
            CAST(:estado AS estado_propiedad),
            :imagen_url
        )
        ON CONFLICT (titulo, direccion, ciudad) DO UPDATE SET
            precio_mensual = EXCLUDED.precio_mensual,
            habitaciones = EXCLUDED.habitaciones,
            banos = EXCLUDED.banos,
            area_m2 = EXCLUDED.area_m2,
            estado = EXCLUDED.estado,
            imagen_url = EXCLUDED.imagen_url,
            updated_at = now()
        """
    )

    for propiedad in PROPIEDADES_MIAMI:
        bind.execute(
            upsert_sql,
            {
                **propiedad,
                "imagen_url": _imagen_url(str(propiedad["id"])),
            },
        )


def downgrade() -> None:
    """Elimina los registros sembrados por id fijo."""

    bind = op.get_bind()
    delete_sql = sa.text(
        """
        DELETE FROM propiedades
        WHERE id = ANY(CAST(:ids AS uuid[]))
        """
    )
    bind.execute(delete_sql, {"ids": [row["id"] for row in PROPIEDADES_MIAMI]})
