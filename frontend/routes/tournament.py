# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    *, request: Request, session: AsyncSession = Depends(get_session), id: int
):
    global sidebar  # used by layout
    current_page = "tournaments"
    contentview = "components/tournaments/tournament_info.html"
    session_id = request.query_params.get("session_id")

    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tournament not found"
        )

    tournament_public = MobaTournamentPublic.model_validate(tournament.model_dump())

    # Fetch participating teams via association table
    participant_result = await session.execute(
        select(MobaTournamentParticipant).where(
            MobaTournamentParticipant.tournament_id == id
        )
    )
    team_ids = [tp.team_id for tp in participant_result.scalars().all()]
    teams = []
    if team_ids:
        team_result = await session.execute(
            select(MobaTeam).where(MobaTeam.id.in_(team_ids))
        )
        teams = team_result.scalars().all()
    participating_teams: List[MobaTeamPublic] = [
        MobaTeamPublic.model_validate(t.model_dump()) for t in teams
    ]

    return templates.TemplateResponse(
        request,
        "layout.html",
        {
            "request": request,
            "content": contentview,
            "sidebar": sidebar,
            "current_page": current_page,
            "tournament": tournament_public,
            "teams": participating_teams,
            "session_id": session_id,
        },
    )
