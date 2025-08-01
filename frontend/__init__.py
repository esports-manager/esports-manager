# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

root_dir = Path(__file__).parent
static_dir = root_dir / "static"
templates_dir = root_dir / "templates"


sidebar = {
    "home": {
        "name": "Home",
        "icon": "bi bi-house-door-fill",
        "url": "home",
    },
    "inbox": {
        "name": "Inbox",
        "icon": "bi bi-inbox-fill",
        "url": "inbox",
    },
    "news": {
        "name": "News",
        "icon": "bi bi-newspaper",
        "url": "news",
    },
    "practice": {
        "name": "Practice",
        "icon": "bi bi-cone-striped",
        "url": "practice",
    },
    "roster": {
        "name": "Roster",
        "icon": "bi bi-people",
        "url": "roster",
    },
    "staff": {
        "name": "Staff",
        "icon": "bi bi-briefcase-fill",
        "url": "staff",
    },
    "scout": {
        "name": "Scout",
        "icon": "bi bi-binoculars-fill",
        "url": "scout",
    },
    "champions": {
        "name": "Champions",
        "icon": "bi bi-star-fill",
        "url": "champions",
    },
    "players": {
        "name": "Players",
        "icon": "bi bi-person-fill",
        "url": "players",
    },
    "teams": {
        "name": "Teams",
        "icon": "bi bi-shield-fill",
        "url": "teams",
    },
    "championships": {
        "name": "Championships",
        "icon": "bi bi-trophy-fill",
        "url": "championships",
    },
}

current_page = "home"


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
        contentview = f"pages/{page}.html"
        return templates.TemplateResponse(
            "layout.html",
            {
                "request": request,
                "content": contentview,
                "sidebar": sidebar,
                "current_page": current_page,
            },
        )

    return app
