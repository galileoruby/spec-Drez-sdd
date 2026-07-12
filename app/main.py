"""Punto de entrada HTTP de la aplicación."""

import logging
import re
import time
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import ChoiceLoader, FileSystemLoader
from markupsafe import Markup, escape
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.modules.dashboard.routes import router as dashboard_router
from app.modules.propiedades.routes import router as propiedades_router

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.loader = ChoiceLoader(
    [
        FileSystemLoader(str(BASE_DIR / "templates")),
        FileSystemLoader(str(BASE_DIR / "modules" / "propiedades" / "templates")),
    ]
)
logger = logging.getLogger(__name__)
settings = get_settings()

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO))


def icon_svg(nombre: str, size: int = 20, class_name: str = "") -> Markup:
    """Retorna un SVG inline de la carpeta de iconos vendoreados."""
    icon_path = BASE_DIR / "static" / "icons" / f"{nombre}.svg"
    classes = "icon"
    if class_name:
        classes = f"{classes} {escape(class_name)}"

    if not icon_path.exists():
        return Markup(
            f'<span class="{classes}" aria-hidden="true" '
            f'style="width:{size}px;height:{size}px"></span>'
        )

    svg_text = icon_path.read_text(encoding="utf-8")
    svg_text = re.sub(r'\s(?:width|height|class)="[^"]*"', "", svg_text)
    svg_text = svg_text.replace(
        "<svg",
        (
            f'<svg class="{classes}" width="{size}" height="{size}" '
            f'aria-hidden="true" focusable="false"'
        ),
        1,
    )
    return Markup(svg_text)


async def _check_db(session: AsyncSession) -> bool:
    """Verifica conectividad de base de datos con una consulta liviana."""
    await session.execute(text("SELECT 1"))
    return True


def create_app() -> FastAPI:
    """Crea y configura la instancia principal de FastAPI."""
    app = FastAPI(title="Realtor")
    app.state.templates = templates
    templates.env.globals["icon_svg"] = icon_svg
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="static",
    )
    app.include_router(dashboard_router)
    app.include_router(propiedades_router)

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
    async def health(
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> dict[str, str]:
        try:
            await _check_db(session)
        except Exception:
            return {"status": "degraded", "db": "error"}
        return {"status": "ok", "db": "ok"}

    return app


app = create_app()
