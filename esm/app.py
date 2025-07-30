# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from contextlib import asynccontextmanager
from typing import Callable, Optional
from .config import Config

from .routes.moba.player import player_routes
from .routes.moba.team import team_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global engine
    config = Config()
    database_url = getattr(config, "DATABASE_URL", "sqlite:///main.db")
    engine = create_engine(database_url, echo=True)
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown - cleanup if needed
    pass


def create_api(lifespan: Optional[Callable] = lifespan):
    app = FastAPI(
        title="eSports Manager API",
        description="A free and open source eSports manager game API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(player_routes, prefix="/api/moba")
    app.include_router(team_routes, prefix="/api/moba")

    return app
