# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter
from .player import player_routes
from .team import team_routes
from .champion import champion_routes

moba_router = APIRouter(
    prefix="/moba",
    tags=["moba"],
    responses={404: {"description": "Resource not found"}},
)

moba_router.include_router(player_routes)
moba_router.include_router(team_routes)
moba_router.include_router(champion_routes)
