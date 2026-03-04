# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from typing import Callable, Optional
from .config import Config
from .db import DatabaseManager
from . import db
from .logging_config import configure_logging, request_id_var

logger = logging.getLogger("esm.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config()
    config.load_config()
    configure_logging(
        level=config.log_level or None,
        log_file=config.log_file or None,
        force=True,
    )
    logger.info(
        "Loaded config port=%s database_url=%s",
        config.port,
        config.database_url,
    )
    db.db_manager = DatabaseManager(config.database_url)
    await db.db_manager.create_db_and_tables()
    logger.info("Database initialized")
    yield


def create_api(lifespan: Optional[Callable] = lifespan):
    configure_logging()
    app = FastAPI(
        title="eSports Manager API",
        description="A free and open source eSports manager game API",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = (
            request.headers.get("X-Request-ID")
            or request.headers.get("X-Correlation-ID")
            or uuid4().hex
        )
        token = request_id_var.set(request_id)
        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)
        response.headers.setdefault("X-Request-ID", request_id)
        return response

    from .routes.moba import moba_router

    app.include_router(moba_router, prefix="/api")

    return app
