# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from esm.config import ESM_DIR, FRONTEND_DIR
from esm.db import get_session
from esm.services import serve_image
from esm.models.moba.tournament import (
    MobaTournament,
    MobaTournamentCreate,
    MobaTournamentUpdate,
    MobaTournamentPublic,
)
from esm.models.moba.tournament_participant import MobaTournamentParticipant
from esm.models.moba.team import MobaTeam, MobaTeamPublic
from esm.models.game import LEAGUE_OF_LEGENDS_SLUG, Game, TournamentSystem
from esm.models.tournament import TournamentSummary
from esm.services.games import (
    GameError,
    resolve_optional_tournament_game,
    resolve_tournament_game,
)
from esm.services.tournaments import (
    InvalidFilterError,
    filters_from_query,
    list_tournament_summaries,
    pagination_from_query,
    sort_from_query,
)


tournament_routes = APIRouter(
    prefix="/tournaments",
    tags=["moba_tournaments"],
    responses={404: {"description": "Tournament not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


@tournament_routes.get("/", response_model=list[TournamentSummary])
async def get_tournaments(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """List MOBA tournaments.

    Filtering, sorting and pagination are shared with the game agnostic
    listing so every eSport behaves the same way.
    """
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
        system=TournamentSystem.MOBA,
        sort_by=sort_by,
        direction=direction,
        page=page,
        per_page=per_page,
        **filters,
    )

    # HTMX partial rendering support
    if request.headers.get("HX-Request"):
        games = (
            await session.execute(
                select(Game)
                .where(Game.is_active == True)  # noqa: E712
                .order_by(Game.name)
            )
        ).scalars().all()
        return templates.TemplateResponse(
            request,
            "components/tournaments/tournaments_list.html",
            {
                "request": request,
                "tournaments": tournaments,
                "pagination": pagination,
                "games": games,
                "current_filters": {
                    "game": LEAGUE_OF_LEGENDS_SLUG,
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


@tournament_routes.post(
    "/", response_model=MobaTournament, status_code=status.HTTP_201_CREATED
)
async def create_tournament(
    *,
    session: AsyncSession = Depends(get_session),
    tournament: MobaTournamentCreate,
):
    try:
        game = await resolve_optional_tournament_game(
            session, tournament.game_id, TournamentSystem.MOBA
        )
    except GameError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))

    db_tournament = MobaTournament.model_validate(tournament)
    if game is not None:
        db_tournament.game_id = game.id
    session.add(db_tournament)
    await session.commit()
    await session.refresh(db_tournament)
    return db_tournament


@tournament_routes.get("/{id}", response_model=MobaTournamentPublic)
async def get_tournament(*, session: AsyncSession = Depends(get_session), id: int):
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament = MobaTournamentPublic.model_validate(tournament.model_dump())
    return tournament


@tournament_routes.get("/{id}/teams", response_model=list[MobaTeamPublic])
async def get_tournament_teams(*, session: AsyncSession = Depends(get_session), id: int):
    # Ensure tournament exists
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    result = await session.execute(
        select(MobaTournamentParticipant).where(
            MobaTournamentParticipant.tournament_id == id
        )
    )
    team_ids = [tp.team_id for tp in result.scalars().all()]
    if not team_ids:
        return []
    teams_result = await session.execute(select(MobaTeam).where(MobaTeam.id.in_(team_ids)))
    teams = teams_result.scalars().all()
    return [MobaTeamPublic.model_validate(t.model_dump()) for t in teams]


class TournamentTeamLink(BaseModel):
    team_id: int


@tournament_routes.post("/{id}/teams", status_code=status.HTTP_204_NO_CONTENT)
async def add_tournament_team(
    *, session: AsyncSession = Depends(get_session), id: int, link: TournamentTeamLink
):
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    team = await session.get(MobaTeam, link.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # avoid duplicates
    result = await session.execute(
        select(MobaTournamentParticipant).where(
            (MobaTournamentParticipant.tournament_id == id)
            & (MobaTournamentParticipant.team_id == link.team_id)
        )
    )
    existing = result.scalars().first()
    if existing:
        return None
    assoc = MobaTournamentParticipant(tournament_id=id, team_id=link.team_id)
    session.add(assoc)
    await session.commit()
    return None


@tournament_routes.delete(
    "/{id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_tournament_team(
    *, session: AsyncSession = Depends(get_session), id: int, team_id: int
):
    result = await session.execute(
        select(MobaTournamentParticipant).where(
            (MobaTournamentParticipant.tournament_id == id)
            & (MobaTournamentParticipant.team_id == team_id)
        )
    )
    assoc = result.scalars().first()
    if not assoc:
        return None
    await session.delete(assoc)
    await session.commit()
    return None


@tournament_routes.patch("/{id}", response_model=MobaTournament)
async def update_tournament(
    *,
    session: AsyncSession = Depends(get_session),
    id: int,
    tournament: MobaTournamentUpdate,
):
    db_tournament = await session.get(MobaTournament, id)
    if not db_tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament_data = tournament.model_dump(exclude_unset=True)
    if tournament_data.get("game_id") is not None:
        try:
            game = await resolve_tournament_game(
                session, tournament_data["game_id"], TournamentSystem.MOBA
            )
        except GameError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc))
        tournament_data["game_id"] = game.id
    db_tournament.sqlmodel_update(tournament_data)
    session.add(db_tournament)
    await session.commit()
    await session.refresh(db_tournament)
    return db_tournament


@tournament_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(*, session: AsyncSession = Depends(get_session), id: int):
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    await session.delete(tournament)
    await session.commit()
    return None


@tournament_routes.get("/images/{filename}")
async def get_tournament_image(filename: str):
    image_path = Path(ESM_DIR) / "res" / "img" / "tournaments" / filename
    return serve_image(
        image_path,
        Path(ESM_DIR) / "res" / "img" / "tournaments" / "default_tournament.webp",
    )
