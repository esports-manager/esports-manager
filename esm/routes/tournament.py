# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Game agnostic tournament listing across every supported eSport."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.config import FRONTEND_DIR
from esm.db import get_session
from esm.models.game import Game
from esm.models.tournament import TournamentSummary
from esm.services.games import get_game_by_slug
from esm.services.tournaments import (
    InvalidFilterError,
    filters_from_query,
    list_tournament_summaries,
    pagination_from_query,
    pagination_meta,
    sort_from_query,
)

tournament_routes = APIRouter(
    prefix="/tournaments",
    tags=["tournaments"],
    responses={404: {"description": "Tournament not found"}},
)

templates = Jinja2Templates(directory=FRONTEND_DIR / "templates")


async def _active_games(session: AsyncSession) -> list[Game]:
    query = (
        select(Game)
        .where(Game.is_active == True)  # noqa: E712
        .order_by(Game.name)
    )
    return list((await session.execute(query)).scalars().all())


@tournament_routes.get("/", response_model=list[TournamentSummary])
async def get_tournaments(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """List tournaments of every game, optionally filtered by game slug."""
    try:
        filters = filters_from_query(request.query_params)
    except InvalidFilterError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    sort_by, direction = sort_from_query(request.query_params)
    page, per_page = pagination_from_query(
        request.query_params.get("page"), request.query_params.get("per_page")
    )
    game_slug = (request.query_params.get("game") or "").strip().lower()

    if game_slug:
        game = await get_game_by_slug(session, game_slug)
        system = game.tournament_system if game else None
        if system is None:
            tournaments: list[TournamentSummary] = []
            pagination = pagination_meta(0, page, per_page)
        else:
            tournaments, pagination = await list_tournament_summaries(
                session,
                system=system,
                sort_by=sort_by,
                direction=direction,
                page=page,
                per_page=per_page,
                **filters,
            )
    else:
        tournaments, pagination = await list_tournament_summaries(
            session,
            sort_by=sort_by,
            direction=direction,
            page=page,
            per_page=per_page,
            **filters,
        )

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/tournaments/tournaments_list.html",
            {
                "request": request,
                "tournaments": tournaments,
                "pagination": pagination,
                "games": await _active_games(session),
                "current_filters": {
                    "game": game_slug,
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
