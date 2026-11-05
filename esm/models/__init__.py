# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later

from .game import (
    BGMI_SLUG,
    DEFAULT_GAMES,
    GAME_TOURNAMENT_SYSTEM,
    LEAGUE_OF_LEGENDS_SLUG,
    Game,
    GameBase,
    GameCreate,
    GameGenre,
    GamePublic,
    GameUpdate,
    TournamentSystem,
    normalize_slug,
)
from .tournament import (
    TournamentFormat,
    TournamentSummary,
    TournamentTier,
    TournamentType,
)

__all__ = [
    "BGMI_SLUG",
    "DEFAULT_GAMES",
    "GAME_TOURNAMENT_SYSTEM",
    "LEAGUE_OF_LEGENDS_SLUG",
    "Game",
    "GameBase",
    "GameCreate",
    "GameGenre",
    "GamePublic",
    "GameUpdate",
    "TournamentSystem",
    "normalize_slug",
    "TournamentType",
    "TournamentFormat",
    "TournamentTier",
    "TournamentSummary",
]
