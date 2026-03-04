# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter
from .player import player_routes
from .team import team_routes
from .champion import champion_routes
from .search import search_routes
from .tournament import tournament_routes
from .inbox import inbox_routes
from .simulation import simulation_routes
from .staff import staff_routes
from .lineup import lineup_routes
from .draft import draft_routes
from .match import match_routes
from .session import session_routes

moba_router = APIRouter(
    prefix="/moba",
    tags=["moba"],
    responses={404: {"description": "Resource not found"}},
)

moba_router.include_router(player_routes)
moba_router.include_router(team_routes)
moba_router.include_router(champion_routes)
moba_router.include_router(search_routes)
moba_router.include_router(tournament_routes)
moba_router.include_router(inbox_routes)
moba_router.include_router(staff_routes)
moba_router.include_router(simulation_routes)
moba_router.include_router(lineup_routes)
moba_router.include_router(draft_routes)
moba_router.include_router(match_routes)
moba_router.include_router(session_routes)
