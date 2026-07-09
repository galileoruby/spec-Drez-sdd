"""Punto de entrada HTTP de la aplicación."""

import logging
import time
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
logger = logging.getLogger(__name__)
settings = get_settings()

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))


METRICAS_DASHBOARD = [
    {"titulo": "Propiedades activas", "valor": "12", "icono": "building-2"},
    {"titulo": "Contratos vigentes", "valor": "9", "icono": "file-text"},
    {"titulo": "Ingresos del mes", "valor": "$8,750", "icono": "wallet"},
]


async def _check_db(session: AsyncSession) -> bool:
    """Verifica conectividad de base de datos con una consulta liviana."""
    await session.execute(text("SELECT 1"))
    return True


def create_app() -> FastAPI:
    """Crea y configura la instancia principal de FastAPI."""
    app = FastAPI(title="Realtor")
    app.state.templates = templates
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="static",
    )

    @app.middleware("http")
    async def request_logger(request: Request, call_next):
        if request.url.path in {"/health", "/"}:
            logger.info(
                "event=request_start path=%s method=%s",
                request.url.path,
                request.method,
            )
            started_at = time.perf_counter()
            response = await call_next(request)
            duration_ms = (time.perf_counter() - started_at) * 1000
            logger.info(
                "event=request_end path=%s status=%s duration_ms=%.2f",
                request.url.path,
                response.status_code,
                duration_ms,
            )
            return response

        return await call_next(request)

    @app.get("/health")
    async def health(session: AsyncSession = Depends(get_session)) -> dict[str, str]:
        try:
            await _check_db(session)
        except Exception:
            return {"status": "degraded", "db": "error"}
        return {"status": "ok", "db": "ok"}

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request=request,
            name="pages/dashboard.html",
            context={"metricas": METRICAS_DASHBOARD},
        )

    return app


app = create_app()
