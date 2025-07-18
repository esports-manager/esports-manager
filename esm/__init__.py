#      eSports Manager - A free and open source eSports management simulation game
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine, Session
from contextlib import asynccontextmanager
from typing import Optional, Callable
from .config import Config

# Global engine variable
engine = None


def get_session():
    """Get a database session"""
    with Session(engine) as session:
        yield session


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

    # Register the API Routes here
    from .apis.players import player_routes
    from .apis.teams import team_routes
    from .apis.matches import match_routes
    from .apis.staff import staff_routes
    from .apis.tournaments import tournament_routes

    app.include_router(player_routes)
    app.include_router(team_routes)
    app.include_router(match_routes)
    app.include_router(staff_routes)
    app.include_router(tournament_routes)

    return app
