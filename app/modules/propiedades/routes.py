"""Rutas HTTP del modulo propiedades."""

from __future__ import annotations

import logging
from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.modules.propiedades import service
from app.modules.propiedades.schemas import (
	PropiedadCrearFormulario,
	PropiedadEditarFormulario,
)

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
	mostrar_exito = request.query_params.get("editada") == "1" or request.query_params.get("creada") == "1"
	mensaje_exito = None
	if request.query_params.get("editada") == "1":
		mensaje_exito = "Propiedad editada correctamente."
	elif request.query_params.get("creada") == "1":
		mensaje_exito = "Propiedad creada correctamente."
	contexto = contexto.model_copy(
		update={
			"mostrar_exito": mostrar_exito,
			"mensaje_exito": mensaje_exito,
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


@router.get("/editar/{propiedad_id}", response_class=HTMLResponse)
async def formulario_editar_propiedad(
	request: Request,
	propiedad_id: UUID,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> HTMLResponse:
	"""Renderiza la pantalla de edición de una propiedad existente."""

	logger.info("propiedades.editar.formulario.request_start")
	propiedad = await service.obtener_propiedad_por_id(session, propiedad_id)
	if propiedad is None:
		raise HTTPException(status_code=404, detail="La propiedad solicitada no existe.")

	contexto = service.construir_contexto_edicion(propiedad)
	logger.info(
		"propiedades.editar.formulario.request_end",
		extra={"propiedad_id": str(propiedad_id)},
	)
	templates = cast(Jinja2Templates, request.app.state.templates)
	return templates.TemplateResponse(
		request=request,
		name="editar_propiedad.html",
		context=contexto.model_dump(),
	)


@router.post("/editar/{propiedad_id}", response_class=HTMLResponse)
async def editar_propiedad(
	request: Request,
	propiedad_id: UUID,
	session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
	"""Procesa la actualización de una propiedad existente."""

	logger.info("propiedades.editar.request_start")
	formulario_crudo = dict(await request.form())
	formulario = PropiedadEditarFormulario.model_validate(formulario_crudo)
	try:
		resultado = await service.editar_propiedad(session, propiedad_id, formulario)
	except service.PropiedadNoEncontradaError:
		raise HTTPException(status_code=404, detail="La propiedad solicitada no existe.")
	except service.ErrorConflictoOptimistaEdicionPropiedad as error_conflicto:
		logger.info(
			"propiedades.editar.request_conflict",
			extra={"propiedad_id": str(propiedad_id)},
		)
		templates = cast(Jinja2Templates, request.app.state.templates)
		return templates.TemplateResponse(
			request=request,
			name="editar_propiedad.html",
			context=error_conflicto.contexto.model_dump(),
			status_code=409,
		)
	except service.ErrorValidacionEdicionPropiedad as error_validacion:
		logger.info(
			"propiedades.editar.request_error",
			extra={"propiedad_id": str(propiedad_id), "tiene_errores": True},
		)
		templates = cast(Jinja2Templates, request.app.state.templates)
		return templates.TemplateResponse(
			request=request,
			name="editar_propiedad.html",
			context=error_validacion.contexto.model_dump(),
			status_code=422,
		)

	logger.info(
		"propiedades.editar.request_end",
		extra={"propiedad_id": str(resultado.propiedad_id)},
	)
	return RedirectResponse(url=resultado.redireccion, status_code=303)


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
