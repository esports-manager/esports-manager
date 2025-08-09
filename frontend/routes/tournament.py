# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from esm.config import FRONTEND_DIR
from esm.db import get_session
from esm.models.moba.team import MobaTeam, MobaTeamPublic
from esm.models.moba.tournament import MobaTournament, MobaTournamentPublic
from esm.models.moba.tournament_participant import MobaTournamentParticipant
from frontend.sidebar import sidebar


tournament_routes = APIRouter(tags=["moba_tournaments_frontend"])

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


@tournament_routes.get("/tournaments/{id}")
async def get_tournament_page(
    *, request: Request, session: Session = Depends(get_session), id: int
):
    global sidebar  # used by layout
    current_page = "tournaments"
    contentview = "components/tournament_info.html"

    tournament = session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    tournament_public = MobaTournamentPublic.model_validate(tournament.model_dump())

    # Fetch participating teams via association table
    team_ids = [
        tp.team_id
        for tp in session.exec(
            select(MobaTournamentParticipant).where(
                MobaTournamentParticipant.tournament_id == id
            )
        ).all()
    ]
    teams = []
    if team_ids:
        teams = session.exec(select(MobaTeam).where(MobaTeam.id.in_(team_ids))).all()
    participating_teams: List[MobaTeamPublic] = [
        MobaTeamPublic.model_validate(t.model_dump()) for t in teams
    ]

    return templates.TemplateResponse(
        "layout.html",
        {
            "request": request,
            "content": contentview,
            "sidebar": sidebar,
            "current_page": current_page,
            "tournament": tournament_public,
            "teams": participating_teams,
        },
    )
