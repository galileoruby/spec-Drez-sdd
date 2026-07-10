"""Pruebas unitarias del servicio de dashboard."""

from __future__ import annotations

from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard.service import construir_contexto_home


async def _conteos_con_datos(_session: AsyncSession) -> tuple[int, int]:
    return (7, 3)


async def _conteos_sin_datos(_session: AsyncSession) -> tuple[int, int]:
    return (0, 0)


async def _conteos_solo_inactivos(_session: AsyncSession) -> tuple[int, int]:
    return (0, 0)


@pytest.mark.asyncio
async def test_construir_contexto_home_conteos_reales_y_orden_contractual() -> None:
    """Valida cálculo real y orden estable del contrato de métricas."""

    contexto = await construir_contexto_home(
        cast(AsyncSession, object()),
        conteos_provider=_conteos_con_datos,
    )

    assert [metrica.titulo for metrica in contexto.metricas] == [
        "Propiedades disponibles",
        "Propiedades rentadas",
        "Ingresos del mes",
        "Pagos vencidos",
    ]
    assert contexto.metricas[0].valor == "7"
    assert contexto.metricas[1].valor == "3"


@pytest.mark.asyncio
async def test_ingresos_y_vencidos_permanecen_no_operativos() -> None:
    """Garantiza que las métricas no modeladas se mantengan explícitas."""

    contexto = await construir_contexto_home(
        cast(AsyncSession, object()),
        conteos_provider=_conteos_con_datos,
    )

    assert contexto.metricas[2].operativa is False
    assert contexto.metricas[2].valor == "No operativo"
    assert contexto.metricas[3].operativa is False
    assert contexto.metricas[3].valor == "No operativo"


@pytest.mark.asyncio
async def test_estado_vacio_true_sin_datos_operativos() -> None:
    """Verifica que el estado vacío responda a ausencia real de datos."""

    contexto = await construir_contexto_home(
        cast(AsyncSession, object()),
        conteos_provider=_conteos_sin_datos,
    )

    assert contexto.mostrar_estado_vacio is True


@pytest.mark.asyncio
async def test_estado_vacio_true_si_no_hay_disponibles_ni_rentadas() -> None:
    """Cubre edge case con propiedades fuera de estados objetivo."""

    contexto = await construir_contexto_home(
        cast(AsyncSession, object()),
        conteos_provider=_conteos_solo_inactivos,
    )

    assert contexto.mostrar_estado_vacio is True
