# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""BGMI tournament API."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.config import ESM_DIR, FRONTEND_DIR
from esm.db import get_session
from esm.models.bgmi.tournament import (
    BgmiTournament,
    BgmiTournamentCreate,
    BgmiTournamentPublic,
    BgmiTournamentUpdate,
)
from esm.models.bgmi.tournament_participant import BgmiTournamentParticipant
from esm.models.game import Game, TournamentSystem
from esm.models.moba.team import MobaTeam, MobaTeamPublic
from esm.models.tournament import TournamentSummary
from esm.services import serve_image
from esm.services.games import GameError, resolve_tournament_game
from esm.services.tournaments import (
    InvalidFilterError,
    filters_from_query,
    list_tournament_summaries,
    pagination_from_query,
    sort_from_query,
)

bgmi_tournament_routes = APIRouter(
    prefix="/tournaments",
    tags=["bgmi_tournaments"],
    responses={404: {"description": "Tournament not found"}},
)

templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")


@bgmi_tournament_routes.get("/", response_model=list[TournamentSummary])
async def get_bgmi_tournaments(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        filters = filters_from_query(request.query_params)
    except InvalidFilterError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    sort_by, direction = sort_from_query(request.query_params)
    page, per_page = pagination_from_query(
        request.query_params.get("page"), request.query_params.get("per_page")
    )

    tournaments, pagination = await list_tournament_summaries(
        session,
        system=TournamentSystem.BGMI,
        sort_by=sort_by,
        direction=direction,
        page=page,
        per_page=per_page,
        **filters,
    )

    if request.headers.get("HX-Request"):
        games = (
            (
                await session.execute(
                    select(Game)
                    .where(Game.is_active == True)  # noqa: E712
                    .order_by(Game.name)
                )
            )
            .scalars()
            .all()
        )
        return templates.TemplateResponse(
            request,
            "components/tournaments/tournaments_list.html",
            {
                "request": request,
                "tournaments": tournaments,
                "pagination": pagination,
                "games": games,
                "current_filters": {
                    "game": "bgmi",
                    "tier": request.query_params.get("tier", ""),
                    "type": request.query_params.get("type", ""),
                    "format": request.query_params.get("format", ""),
                    "location": request.query_params.get("location", ""),
                    "search": request.query_params.get("search", ""),
                    "sort": sort_by,
                    "direction": direction,
                },
            },
        )

    return tournaments


@bgmi_tournament_routes.post(
    "/", response_model=BgmiTournamentPublic, status_code=status.HTTP_201_CREATED
)
async def create_bgmi_tournament(
    *,
    session: AsyncSession = Depends(get_session),
    tournament: BgmiTournamentCreate,
):
    try:
        game = await resolve_tournament_game(
            session, tournament.game_id, TournamentSystem.BGMI
        )
    except GameError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    db_tournament = BgmiTournament.model_validate(tournament)
    db_tournament.game_id = game.id
    session.add(db_tournament)
    await session.commit()
    await session.refresh(db_tournament)
    return db_tournament


@bgmi_tournament_routes.get("/{id}", response_model=BgmiTournamentPublic)
async def get_bgmi_tournament(*, session: AsyncSession = Depends(get_session), id: int):
    tournament = await session.get(BgmiTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


class TournamentTeamLink(BaseModel):
    team_id: int


@bgmi_tournament_routes.get("/{id}/teams", response_model=list[MobaTeamPublic])
async def get_tournament_teams(
    *, session: AsyncSession = Depends(get_session), id: int
):
    tournament = await session.get(BgmiTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    result = await session.execute(
        select(BgmiTournamentParticipant).where(
            BgmiTournamentParticipant.tournament_id == id
        )
    )
    team_ids = [participant.team_id for participant in result.scalars().all()]
    if not team_ids:
        return []
    teams_result = await session.execute(
        select(MobaTeam).where(MobaTeam.id.in_(team_ids))
    )
    return [
        MobaTeamPublic.model_validate(team.model_dump())
        for team in teams_result.scalars().all()
    ]


@bgmi_tournament_routes.post("/{id}/teams", status_code=status.HTTP_204_NO_CONTENT)
async def add_tournament_team(
    *, session: AsyncSession = Depends(get_session), id: int, link: TournamentTeamLink
):
    tournament = await session.get(BgmiTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    team = await session.get(MobaTeam, link.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    result = await session.execute(
        select(BgmiTournamentParticipant).where(
            (BgmiTournamentParticipant.tournament_id == id)
            & (BgmiTournamentParticipant.team_id == link.team_id)
        )
    )
    if result.scalars().first():
        return None

    session.add(BgmiTournamentParticipant(tournament_id=id, team_id=link.team_id))
    await session.commit()
    return None


@bgmi_tournament_routes.delete(
    "/{id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_tournament_team(
    *, session: AsyncSession = Depends(get_session), id: int, team_id: int
):
    result = await session.execute(
        select(BgmiTournamentParticipant).where(
            (BgmiTournamentParticipant.tournament_id == id)
            & (BgmiTournamentParticipant.team_id == team_id)
        )
    )
    association = result.scalars().first()
    if not association:
        return None
    await session.delete(association)
    await session.commit()
    return None


@bgmi_tournament_routes.patch("/{id}", response_model=BgmiTournamentPublic)
async def update_bgmi_tournament(
    *,
    session: AsyncSession = Depends(get_session),
    id: int,
    tournament: BgmiTournamentUpdate,
):
    db_tournament = await session.get(BgmiTournament, id)
    if not db_tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    data = tournament.model_dump(exclude_unset=True)
    if "game_id" in data and data["game_id"] is not None:
        try:
            game = await resolve_tournament_game(
                session, data["game_id"], TournamentSystem.BGMI
            )
        except GameError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc))
        data["game_id"] = game.id

    db_tournament.sqlmodel_update(data)
    session.add(db_tournament)
    await session.commit()
    await session.refresh(db_tournament)
    return db_tournament


@bgmi_tournament_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bgmi_tournament(
    *, session: AsyncSession = Depends(get_session), id: int
):
    tournament = await session.get(BgmiTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    participants = await session.execute(
        select(BgmiTournamentParticipant).where(
            BgmiTournamentParticipant.tournament_id == id
        )
    )
    for participant in participants.scalars().all():
        await session.delete(participant)

    await session.delete(tournament)
    await session.commit()
    return None


@bgmi_tournament_routes.get("/images/{filename}")
async def get_tournament_image(filename: str):
    image_path = Path(ESM_DIR) / "res" / "img" / "tournaments" / filename
    return serve_image(
        image_path,
        Path(ESM_DIR) / "res" / "img" / "tournaments" / "default_tournament.webp",
    )
