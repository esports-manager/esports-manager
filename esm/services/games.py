# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Game registry helpers shared by the API and the server rendered frontend."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.models.game import (
    DEFAULT_GAMES,
    Game,
    GameCreate,
    TournamentSystem,
)


class GameError(Exception):
    """Base class for game registry errors."""

    status_code = 400


class GameAlreadyExistsError(GameError):
    status_code = 409


class GameNotFoundError(GameError):
    status_code = 404


class InvalidTournamentGameError(GameError):
    status_code = 400


async def get_game_by_slug(session: AsyncSession, slug: str) -> Game | None:
    result = await session.execute(select(Game).where(Game.slug == slug))
    return result.scalars().first()


async def ensure_default_games(session: AsyncSession) -> list[Game]:
    """Register the built-in games (League of Legends, BGMI) if missing.

    Safe to call on every startup: existing games are left untouched, so a
    user that renamed or disabled a default game keeps their changes.
    """
    created: list[Game] = []
    for spec in DEFAULT_GAMES:
        if await get_game_by_slug(session, spec["slug"]) is None:
            game = Game(**spec)
            session.add(game)
            created.append(game)

    if created:
        await session.commit()
        for game in created:
            await session.refresh(game)
    return created


async def create_game(session: AsyncSession, payload: GameCreate) -> Game:
    if await get_game_by_slug(session, payload.slug) is not None:
        raise GameAlreadyExistsError(
            f"A game with the slug '{payload.slug}' already exists"
        )

    existing_name = await session.execute(
        select(Game).where(Game.name.ilike(payload.name))
    )
    if existing_name.scalars().first() is not None:
        raise GameAlreadyExistsError(f"A game named '{payload.name}' already exists")

    game = Game.model_validate(payload)
    session.add(game)
    await session.commit()
    await session.refresh(game)
    return game


async def default_tournament_game(
    session: AsyncSession, system: TournamentSystem
) -> Game | None:
    """Oldest active game that runs tournaments with ``system``."""
    result = await session.execute(select(Game).where(Game.is_active == True))  # noqa: E712
    for game in result.scalars().all():
        if game.tournament_system is system:
            return game
    return None


async def resolve_tournament_game(
    session: AsyncSession,
    game_id: int | None,
    system: TournamentSystem,
) -> Game:
    """Return the game a tournament belongs to.

    When ``game_id`` is omitted the oldest active game using the requested
    tournament system is used, which is how a fresh install gets BGMI
    tournaments without the client having to know the registry ids.
    """
    if game_id is not None:
        game = await session.get(Game, game_id)
        if game is None:
            raise GameNotFoundError(f"Game {game_id} was not found")
    else:
        game = await default_tournament_game(session, system)
        if game is None:
            raise GameNotFoundError(
                "No game with the "
                f"'{system.value}' tournament system is registered. "
                "Add a game first (see /api/games)."
            )

    if not game.is_active:
        raise InvalidTournamentGameError(f"Game '{game.name}' is not active")
    if game.tournament_system is not system:
        raise InvalidTournamentGameError(
            f"Game '{game.name}' does not use the '{system.value}' tournament system"
        )
    return game


async def resolve_optional_tournament_game(
    session: AsyncSession,
    game_id: int | None,
    system: TournamentSystem,
) -> Game | None:
    """Like :func:`resolve_tournament_game` but tolerant of an empty registry.

    Legacy MOBA tournaments were created before the game registry existed;
    when no game of the requested system is registered they keep a ``None``
    game and are displayed as League of Legends tournaments.
    """
    if game_id is None:
        return await default_tournament_game(session, system)
    return await resolve_tournament_game(session, game_id, system)
