# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import Request, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from esm.config import FRONTEND_DIR
from frontend.sidebar import sidebar


static_dir = FRONTEND_DIR / "static"
templates_dir = FRONTEND_DIR / "templates"


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
        global current_page
        global sidebar
        current_page = "home"
        contentview = "pages/home.html"
        return templates.TemplateResponse(
            "layout.html",
            {
                "request": request,
                "content": contentview,
                "sidebar": sidebar,
                "current_page": current_page,
            },
        )

    @app.get("/page/{page}")
    async def page(request: Request, page: str):
        global current_page
        global sidebar
        current_page = page
        contentview = f"pages/{current_page}.html"
        return templates.TemplateResponse(
            "layout.html",
            {
                "request": request,
                "content": contentview,
                "sidebar": sidebar,
                "current_page": current_page,
            },
        )

    from frontend.routes.player import player_routes
    from frontend.routes.team import team_routes

    app.include_router(player_routes)
    app.include_router(team_routes)

    return app
