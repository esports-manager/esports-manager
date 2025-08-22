# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Dict, Any

from esm.db import get_session
from esm.config import FRONTEND_DIR
from esm.models.moba.player import MobaPlayer, MobaPlayerPublic
from esm.models.moba.team import MobaTeam, MobaTeamPublic
from esm.models.moba.champion import MobaChampion, MobaChampionPublic

search_routes = APIRouter(
    prefix="/search",
    tags=["moba_search"],
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


@search_routes.get("/")
async def omni_search(
    request: Request,
    session: Session = Depends(get_session),
):
    q = (request.query_params.get("q") or "").strip()
    results: Dict[str, Any] = {
        "players": [],
        "teams": [],
        "champions": [],
        "query": q,
    }

    if q:
        # Players by nick_name
        player_query = (
            select(MobaPlayer)
            .where(MobaPlayer.nick_name.icontains(q))
            .order_by(MobaPlayer.nick_name.asc(), MobaPlayer.id.asc())
            .limit(5)
        )
        players = session.exec(player_query).all()
        results["players"] = [
            MobaPlayerPublic.model_validate(p.model_dump()) for p in players
        ]

        # Teams by name
        team_query = (
            select(MobaTeam)
            .where(MobaTeam.name.icontains(q))
            .order_by(MobaTeam.name.asc(), MobaTeam.id.asc())
            .limit(5)
        )
        teams = session.exec(team_query).all()
        results["teams"] = [
            MobaTeamPublic.model_validate(t.model_dump()) for t in teams
        ]

        # Champions by name
        champ_query = (
            select(MobaChampion)
            .where(MobaChampion.name.icontains(q))
            .order_by(MobaChampion.name.asc(), MobaChampion.id.asc())
            .limit(5)
        )
        champions = session.exec(champ_query).all()
        results["champions"] = [
            MobaChampionPublic.model_validate(c.model_dump()) for c in champions
        ]

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/search_results.html",
            {"request": request, "results": results},
        )

    return results
