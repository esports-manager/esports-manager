# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import Callable, Optional
from .config import Config
from .db import DatabaseManager
from . import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config()
    config.load_config()
    db.db_manager = DatabaseManager(config.database_url)
    await db.db_manager.create_db_and_tables()

    # Register the built-in games (League of Legends, BGMI) on first run.
    from .services.games import ensure_default_games

    async with db.db_manager.async_session_maker() as session:
        await ensure_default_games(session)
    yield


def create_api(lifespan: Optional[Callable] = lifespan):
    app = FastAPI(
        title="eSports Manager API",
        description="A free and open source eSports manager game API",
        version="0.1.0",
        lifespan=lifespan,
    )

    from .routes.bgmi import bgmi_router
    from .routes.game import game_routes
    from .routes.moba import moba_router
    from .routes.tournament import tournament_routes

    app.include_router(moba_router, prefix="/api")
    app.include_router(bgmi_router, prefix="/api")
    app.include_router(game_routes, prefix="/api")
    app.include_router(tournament_routes, prefix="/api")

    return app
