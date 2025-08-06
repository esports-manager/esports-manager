# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from esm.db import get_session
from fastapi import Request, Depends, APIRouter, HTTPException, status
from sqlmodel import Session
from fastapi.templating import Jinja2Templates
from esm.models.moba.player import MobaPlayer, MobaPlayerPublic
from esm.models.moba.team import MobaTeamPublic, MobaTeam
from typing import Optional
from esm.config import FRONTEND_DIR
from frontend.sidebar import sidebar

player_routes = APIRouter(
    tags=["players"],
    responses={404: {"description": "Player not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


class MobaPlayerWithTeam(MobaPlayerPublic):
    team: Optional["MobaTeamPublic"] = None


@player_routes.get("/players")
async def players(request: Request):
    global current_page
    global sidebar
    current_page = "players"
    contentview = "components/players_list.html"

    return templates.TemplateResponse(
        "layout.html",
        {
            "request": request,
            "content": contentview,
            "sidebar": sidebar,
            "current_page": current_page,
        },
    )


@player_routes.get("/players/{player_id}")
async def player(request: Request, session: Session = Depends(get_session)):
    global current_page
    global sidebar
    current_page = "players"
    contentview = "components/player_info.html"

    id = int(request.path_params.get("player_id"))
    player = session.get(MobaPlayer, id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )

    player_data = player.model_dump()
    team_data = None
    if player.current_contract and player.current_contract.team_id:
        team_data = session.get(MobaTeam, player.current_contract.team_id)
        player_data["team"] = MobaTeamPublic.model_validate(team_data.model_dump())
    player_with_team = MobaPlayerWithTeam.model_validate(player_data)

    return templates.TemplateResponse(
        "layout.html",
        {
            "request": request,
            "player": player_with_team,
            "content": contentview,
            "sidebar": sidebar,
            "current_page": current_page,
        },
    )
