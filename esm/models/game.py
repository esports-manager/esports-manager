# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Game registry.

A game is an eSport title (League of Legends, BGMI, ...). Tournaments are
always attached to a game, and the game decides which tournament ruleset a
competition uses (MOBA brackets or BGMI battle royale scoring).
"""

import enum
import re
from datetime import datetime
from typing import Optional

from pydantic import model_validator
from sqlmodel import Column, DateTime, Enum, Field, SQLModel


class GameGenre(enum.Enum):
    MOBA = "moba"
    BATTLE_ROYALE = "battle_royale"
    FPS = "fps"
    RTS = "rts"
    SPORTS = "sports"
    FIGHTING = "fighting"
    OTHER = "other"

    @property
    def label(self) -> str:
        return {
            GameGenre.MOBA: "MOBA",
            GameGenre.BATTLE_ROYALE: "Battle Royale",
            GameGenre.FPS: "FPS",
            GameGenre.RTS: "RTS",
            GameGenre.SPORTS: "Sports",
            GameGenre.FIGHTING: "Fighting",
            GameGenre.OTHER: "Other",
        }[self]


class TournamentSystem(enum.Enum):
    """Tournament ruleset used by a game."""

    MOBA = "moba"
    BGMI = "bgmi"

    @property
    def label(self) -> str:
        return {
            TournamentSystem.MOBA: "MOBA series",
            TournamentSystem.BGMI: "BGMI battle royale",
        }[self]


GAME_TOURNAMENT_SYSTEM: dict[GameGenre, TournamentSystem] = {
    GameGenre.MOBA: TournamentSystem.MOBA,
    GameGenre.BATTLE_ROYALE: TournamentSystem.BGMI,
}

LEAGUE_OF_LEGENDS_SLUG = "league-of-legends"
BGMI_SLUG = "bgmi"

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Games registered when the application starts for the first time.
DEFAULT_GAMES: tuple[dict, ...] = (
    {
        "name": "League of Legends",
        "slug": LEAGUE_OF_LEGENDS_SLUG,
        "abbreviation": "LoL",
        "genre": GameGenre.MOBA,
        "publisher": "Riot Games",
        "platform": "PC",
        "team_size": 5,
        "description": (
            "Five-versus-five MOBA played on Summoner's Rift. The default "
            "title of the MOBA tournament circuit."
        ),
    },
    {
        "name": "BGMI",
        "slug": BGMI_SLUG,
        "abbreviation": "BGMI",
        "genre": GameGenre.BATTLE_ROYALE,
        "publisher": "Krafton",
        "platform": "Android / iOS",
        "team_size": 4,
        "description": (
            "Battlegrounds Mobile India: squad battle royale where teams earn "
            "placement and elimination points across a series of matches."
        ),
    },
)


def normalize_slug(value: str) -> str:
    """Turn a human readable name into a URL friendly slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not SLUG_PATTERN.match(slug):
        raise ValueError(
            "Slug must contain only lowercase letters, numbers and hyphens"
        )
    return slug


def validate_slug(value: str) -> str:
    if not SLUG_PATTERN.match(value):
        raise ValueError(
            "Slug must contain only lowercase letters, numbers and hyphens"
        )
    return value


class GameBase(SQLModel):
    name: str = Field(index=True, unique=True)
    abbreviation: Optional[str] = Field(default=None, max_length=16)
    genre: GameGenre = Field(sa_column=Column(Enum(GameGenre)))
    publisher: Optional[str] = Field(default=None)
    platform: Optional[str] = Field(default=None)
    team_size: int = Field(default=5, ge=1, le=10)
    description: Optional[str] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)

    @property
    def tournament_system(self) -> Optional[TournamentSystem]:
        return GAME_TOURNAMENT_SYSTEM.get(self.genre)

    @property
    def supports_tournaments(self) -> bool:
        return self.tournament_system is not None


class Game(GameBase, table=True):
    __tablename__ = "games"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)

    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(DateTime)
    )
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))


class GamePublic(GameBase):
    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class GameCreate(GameBase):
    slug: Optional[str] = Field(
        default=None,
        description="URL friendly identifier. Derived from the name when omitted.",
    )

    @model_validator(mode="after")
    def _fill_slug(self):
        self.slug = (
            normalize_slug(self.slug) if self.slug else normalize_slug(self.name)
        )
        return self


class GameUpdate(SQLModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    abbreviation: Optional[str] = Field(default=None, max_length=16)
    genre: Optional[GameGenre] = Field(default=None, sa_column=Column(Enum(GameGenre)))
    publisher: Optional[str] = None
    platform: Optional[str] = None
    team_size: Optional[int] = Field(default=None, ge=1, le=10)
    description: Optional[str] = None
    logo_path: Optional[str] = None
    is_active: Optional[bool] = None
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))

    @model_validator(mode="after")
    def _validate_slug(self):
        if self.slug:
            self.slug = validate_slug(self.slug)
        return self
