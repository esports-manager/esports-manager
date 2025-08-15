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
    yield


def create_api(lifespan: Optional[Callable] = lifespan):
    app = FastAPI(
        title="eSports Manager API",
        description="A free and open source eSports manager game API",
        version="0.1.0",
        lifespan=lifespan,
    )

    from .routes.moba import moba_router

    app.include_router(moba_router, prefix="/api")

    return app
