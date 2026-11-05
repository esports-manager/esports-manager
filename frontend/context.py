# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Shared template context for the server rendered pages."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.models.bgmi.tournament import BGMI_MAPS, DEFAULT_MAP_POOL, BgmiGameMode
from esm.models.game import Game, GameGenre
from esm.models.tournament import (
    TournamentFormat,
    TournamentStatus,
    TournamentTier,
    TournamentType,
)
from frontend.sidebar import sidebar

TOURNAMENT_TYPE_LABELS = {
    "international": "International",
    "regional": "Regional",
    "national": "National",
    "showmatch": "Showmatch",
}

TOURNAMENT_FORMAT_LABELS = {
    "single_elimination": "Single elimination",
    "double_elimination": "Double elimination",
    "round_robin": "Round robin",
    "swiss": "Swiss",
    "league": "League",
    "gsl": "GSL",
    "bo1_series": "Best of 1",
    "bo2_series": "Best of 2",
    "bo3_series": "Best of 3",
    "bo5_series": "Best of 5",
    "bo7_series": "Best of 7",
    "bo9_series": "Best of 9",
}

TOURNAMENT_TIER_LABELS = {
    "premier": "Premier",
    "major": "Major",
    "league": "League",
    "minor": "Minor",
    "academy": "Academy",
    "semipro": "Semi-pro",
    "amateur": "Amateur",
}

TOURNAMENT_STATUS_LABELS = {
    "not_started": "Not started",
    "in_progress": "In progress",
    "suspended": "Suspended",
    "ended": "Ended",
    "cancelled": "Cancelled",
}


def _options(enum_class: Any, labels: dict[str, str]) -> list[dict[str, str]]:
    return [
        {
            "value": member.value,
            "label": labels.get(member.value, member.value.replace("_", " ").title()),
        }
        for member in enum_class
    ]


def game_systems_map(games: list[Game]) -> dict[str, str | None]:
    return {
        game.slug: game.tournament_system.value if game.tournament_system else None
        for game in games
    }


async def load_games(session: AsyncSession) -> list[Game]:
    result = await session.execute(select(Game).order_by(Game.name))
    return list(result.scalars().all())


async def page_context(session: AsyncSession) -> dict[str, Any]:
    """Everything the page shell and the games/tournaments modals need."""
    games = await load_games(session)
    return {
        "sidebar": sidebar,
        "games": games,
        "game_systems": game_systems_map(games),
        "default_game_slug": next(
            (game.slug for game in games if game.supports_tournaments), ""
        ),
        "genre_options": _options(GameGenre, {}),
        "game_mode_options": _options(BgmiGameMode, {}),
        "tournament_types": _options(TournamentType, TOURNAMENT_TYPE_LABELS),
        "tournament_formats": _options(TournamentFormat, TOURNAMENT_FORMAT_LABELS),
        "tournament_tiers": _options(TournamentTier, TOURNAMENT_TIER_LABELS),
        "tournament_statuses": _options(TournamentStatus, TOURNAMENT_STATUS_LABELS),
        "bgmi_maps": list(BGMI_MAPS),
        "bgmi_default_maps": list(DEFAULT_MAP_POOL),
    }
