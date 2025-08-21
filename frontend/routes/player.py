# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import date
from esm.db import get_session
from fastapi import Request, Depends, APIRouter, HTTPException, status
from sqlmodel import Session
from fastapi.templating import Jinja2Templates
from esm.models.moba.player import MobaPlayer, MobaPlayerPublic
from esm.models.moba.team import MobaTeamPublic, MobaTeam
from esm.models.moba.champion import MobaChampion
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
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    champion_pool: Optional[list[dict]] = None


@player_routes.get("/players")
async def players(request: Request):
    global current_page
    global sidebar
    current_page = "players"
    contentview = "components/players/players_list.html"

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
async def player(
    request: Request, player_id: int, session: Session = Depends(get_session)
):
    global current_page
    global sidebar
    current_page = "players"
    contentview = "components/players/player_info.html"

    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )

    player_data = player.model_dump()
    team_data = None
    if player.current_contract and player.current_contract.team_id:
        team_data = session.get(MobaTeam, player.current_contract.team_id)
        player_data["team"] = MobaTeamPublic.model_validate(team_data.model_dump())

    if player.current_contract:
        player_data["contract_start_date"] = player.current_contract.start_date
        player_data["contract_end_date"] = player.current_contract.end_date
    if player.champion_pool:
        champions = []
        for champion_mastery in player.champion_pool:
            champion = session.get(MobaChampion, champion_mastery.champion_id)
            champion_data = champion.model_dump()
            champion_data["tier"] = champion_mastery.tier
            champion_data["points"] = champion_mastery.points
            champions.append(champion_data)
        player_data["champion_pool"] = champions
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
