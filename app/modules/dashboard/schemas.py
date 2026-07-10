"""Schemas de salida para el dashboard principal."""

from pydantic import BaseModel, ConfigDict


class MetricaHome(BaseModel):
    """Representa una tarjeta de métrica del dashboard."""

    model_config = ConfigDict(frozen=True)

    titulo: str
    valor: str
    icono: str
    tendencia: str
    operativa: bool


class AccesoRapidoHome(BaseModel):
    """Representa un acceso rápido visible en la home."""

    model_config = ConfigDict(frozen=True)

    titulo: str
    href: str
    icono: str


class ContextoHomeDashboard(BaseModel):
    """Contexto completo que consume la vista principal."""

    model_config = ConfigDict(frozen=True)

    metricas: list[MetricaHome]
    accesos_rapidos: list[AccesoRapidoHome]
    mostrar_estado_vacio: bool
