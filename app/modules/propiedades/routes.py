"""Rutas HTTP del modulo propiedades."""

from __future__ import annotations

import logging
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.propiedades import service

router = APIRouter(prefix="/propiedades", tags=["propiedades"])
logger = logging.getLogger(__name__)


@router.get("", response_class=HTMLResponse)
async def listar_propiedades(
	request: Request,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> HTMLResponse:
	"""Renderiza el listado de propiedades en formato cards."""

	logger.info("propiedades.listado.request_start")
	contexto = await service.construir_contexto_listado(session)
	logger.info(
		"propiedades.listado.request_end",
		extra={
			"total_propiedades": contexto.total_propiedades,
			"mostrar_estado_vacio": contexto.mostrar_estado_vacio,
		},
	)
	templates = cast(Jinja2Templates, request.app.state.templates)
	return templates.TemplateResponse(
		request=request,
		name="pages/propiedades.html",
		context=contexto.model_dump(),
	)
