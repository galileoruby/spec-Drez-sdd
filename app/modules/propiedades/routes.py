"""Rutas HTTP del modulo propiedades."""

from __future__ import annotations

import logging
from typing import Annotated, cast

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.propiedades import service
from app.modules.propiedades.schemas import PropiedadCrearFormulario

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
	mostrar_exito = request.query_params.get("creada") == "1"
	contexto = contexto.model_copy(
		update={
			"mostrar_exito": mostrar_exito,
			"mensaje_exito": "Propiedad creada correctamente." if mostrar_exito else None,
		},
	)
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


@router.get("/crear", response_class=HTMLResponse)
async def formulario_crear_propiedad(request: Request) -> HTMLResponse:
	"""Renderiza la pantalla de alta de una nueva propiedad."""

	logger.info("propiedades.crear.formulario.request_start")
	contexto = service.construir_contexto_creacion()
	logger.info("propiedades.crear.formulario.request_end")
	templates = cast(Jinja2Templates, request.app.state.templates)
	return templates.TemplateResponse(
		request=request,
		name="crear_propiedad.html",
		context=contexto.model_dump(),
	)


@router.post("/crear", response_class=HTMLResponse)
async def crear_propiedad(
	request: Request,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
	"""Procesa el alta de una nueva propiedad."""

	logger.info("propiedades.crear.request_start")
	formulario_crudo = dict(await request.form())
	formulario = PropiedadCrearFormulario.model_validate(formulario_crudo)
	try:
		resultado = await service.crear_propiedad(session, formulario)
	except service.ErrorValidacionCreacionPropiedad as error_validacion:
		logger.info(
			"propiedades.crear.request_error",
			extra={
				"tiene_errores": True,
			},
		)
		templates = cast(Jinja2Templates, request.app.state.templates)
		return templates.TemplateResponse(
			request=request,
			name="crear_propiedad.html",
			context=error_validacion.contexto.model_dump(),
			status_code=422,
		)

	logger.info(
		"propiedades.crear.request_end",
		extra={"propiedad_id": str(resultado.propiedad_id)},
	)
	return RedirectResponse(url=resultado.redireccion, status_code=303)
