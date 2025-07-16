from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

root_dir = Path(__file__).parent
static_dir = root_dir / "static"
templates_dir = root_dir / "templates"


def create_frontend(app: FastAPI) -> FastAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    templates = Jinja2Templates(directory=templates_dir)

    @app.get("/")
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/home")
    async def home(request: Request):
        return templates.TemplateResponse("layout.html", {"request": request})

    @app.get("/page/{page}")
    async def page(request: Request, page: str):
        return templates.TemplateResponse(f"pages/{page}.html", {"request": request})

    return app
