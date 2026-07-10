"""Servicios de negocio para la home del dashboard."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard import repository
from app.modules.dashboard.schemas import (
    AccesoRapidoHome,
    ContextoHomeDashboard,
    MetricaHome,
)

ConteosOperativosProvider = Callable[[AsyncSession], Awaitable[tuple[int, int]]]


async def construir_contexto_home(
    session: AsyncSession,
    conteos_provider: ConteosOperativosProvider = repository.obtener_conteos_operativos,
) -> ContextoHomeDashboard:
    """Construye el contexto de la home usando datos reales persistidos."""

    disponibles, rentadas = await conteos_provider(session)
    mostrar_estado_vacio = disponibles == 0 and rentadas == 0

    metricas = [
        MetricaHome(
            titulo="Propiedades disponibles",
            valor=str(disponibles),
            icono="building-2",
            tendencia="",
            operativa=True,
        ),
        MetricaHome(
            titulo="Propiedades rentadas",
            valor=str(rentadas),
            icono="file-text",
            tendencia="",
            operativa=True,
        ),
        MetricaHome(
            titulo="Ingresos del mes",
            valor="No operativo",
            icono="wallet",
            tendencia="Pendiente de modelado en spec futura",
            operativa=False,
        ),
        MetricaHome(
            titulo="Pagos vencidos",
            valor="No operativo",
            icono="alert-triangle",
            tendencia="Pendiente de modelado en spec futura",
            operativa=False,
        ),
    ]

    accesos_rapidos = [
        AccesoRapidoHome(titulo="Nuevo inquilino", href="#", icono="users"),
        AccesoRapidoHome(titulo="Generar contrato", href="#", icono="file-text"),
        AccesoRapidoHome(titulo="Crear ticket", href="#", icono="wrench"),
    ]

    return ContextoHomeDashboard(
        metricas=metricas,
        accesos_rapidos=accesos_rapidos,
        mostrar_estado_vacio=mostrar_estado_vacio,
    )
