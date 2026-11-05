# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Game registry API: list, register and maintain the supported eSports."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.db import get_session
from esm.models.bgmi.tournament import BgmiTournament
from esm.models.game import (
    Game,
    GameCreate,
    GameGenre,
    GamePublic,
    GameUpdate,
    TournamentSystem,
)
from esm.models.moba.tournament import MobaTournament
from esm.services.games import (
    GameAlreadyExistsError,
    create_game,
    get_game_by_slug,
)
from esm.services.tournaments import InvalidFilterError, parse_enum

game_routes = APIRouter(
    prefix="/games",
    tags=["games"],
    responses={404: {"description": "Game not found"}},
)


@game_routes.get("/", response_model=list[GamePublic])
async def get_games(
    request: Request,
    session: AsyncSession = Depends(get_session),
    genre: str | None = Query(default=None),
    tournament_system: str | None = Query(default=None),
    active: bool | None = Query(default=None),
    search: str | None = Query(default=None),
):
    query = select(Game)

    try:
        if genre:
            query = query.where(Game.genre == parse_enum(GameGenre, genre, "genre"))
        system = (
            parse_enum(TournamentSystem, tournament_system, "tournament_system")
            if tournament_system
            else None
        )
    except InvalidFilterError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if active is not None:
        query = query.where(Game.is_active == active)
    if search:
        query = query.where(Game.name.icontains(search))

    query = query.order_by(Game.name)
    games = list((await session.execute(query)).scalars().all())

    if system is not None:
        games = [game for game in games if game.tournament_system is system]
    return games


@game_routes.post("/", response_model=GamePublic, status_code=status.HTTP_201_CREATED)
async def register_game(
    *,
    session: AsyncSession = Depends(get_session),
    game: GameCreate,
):
    try:
        return await create_game(session, game)
    except GameAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@game_routes.get("/{id}", response_model=GamePublic)
async def get_game(*, session: AsyncSession = Depends(get_session), id: int):
    game = await session.get(Game, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@game_routes.get("/by-slug/{slug}", response_model=GamePublic)
async def get_game_by_slug_endpoint(
    *, session: AsyncSession = Depends(get_session), slug: str
):
    game = await get_game_by_slug(session, slug)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@game_routes.patch("/{id}", response_model=GamePublic)
async def update_game(
    *,
    session: AsyncSession = Depends(get_session),
    id: int,
    game: GameUpdate,
):
    db_game = await session.get(Game, id)
    if not db_game:
        raise HTTPException(status_code=404, detail="Game not found")

    data = game.model_dump(exclude_unset=True)
    new_slug = data.get("slug")
    if new_slug and new_slug != db_game.slug:
        if await get_game_by_slug(session, new_slug) is not None:
            raise HTTPException(
                status_code=409,
                detail=f"A game with the slug '{new_slug}' already exists",
            )

    db_game.sqlmodel_update(data)
    session.add(db_game)
    await session.commit()
    await session.refresh(db_game)
    return db_game


@game_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(*, session: AsyncSession = Depends(get_session), id: int):
    game = await session.get(Game, id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    moba_result = await session.execute(
        select(MobaTournament).where(MobaTournament.game_id == id)
    )
    bgmi_result = await session.execute(
        select(BgmiTournament).where(BgmiTournament.game_id == id)
    )
    if moba_result.scalars().first() or bgmi_result.scalars().first():
        raise HTTPException(
            status_code=409,
            detail="Game still has tournaments. Delete them before removing the game",
        )

    await session.delete(game)
    await session.commit()
    return None
