"""Rutas HTTP del dashboard principal."""

from __future__ import annotations

import logging
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.dashboard import service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> HTMLResponse:
    """Renderiza la home con métricas reales de propiedades."""

    logger.info("dashboard.home.request_start")
    contexto = await service.construir_contexto_home(session)
    logger.info(
        "dashboard.home.request_end",
        extra={
            "disponibles": contexto.metricas[0].valor,
            "rentadas": contexto.metricas[1].valor,
            "mostrar_estado_vacio": contexto.mostrar_estado_vacio,
        },
    )

    templates = cast(Jinja2Templates, request.app.state.templates)
    return templates.TemplateResponse(
        request=request,
        name="pages/dashboard.html",
        context=contexto.model_dump(),
    )
