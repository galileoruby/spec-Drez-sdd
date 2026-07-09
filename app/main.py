"""Punto de entrada HTTP de la aplicación."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def create_app() -> FastAPI:
    """Crea y configura la instancia principal de FastAPI."""
    app = FastAPI(title="Realtor")
    app.state.templates = templates
    app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "static")),
        name="static",
    )
    return app


app = create_app()
