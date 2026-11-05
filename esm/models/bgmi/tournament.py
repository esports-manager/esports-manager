# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""BGMI (Battlegrounds Mobile India) tournament models.

BGMI competitions are battle royale tournaments: teams play a series of
matches and score placement points plus one point per elimination. That is
different enough from MOBA brackets to deserve its own table, but it reuses
the shared tournament enums (type, format, tier, status) and the team
registry.
"""

import enum
from datetime import date, datetime
from typing import Optional

from sqlalchemy import JSON
from sqlmodel import Column, DateTime, Enum, Field, SQLModel

from esm.models.tournament import (
    TournamentFormat,
    TournamentStatus,
    TournamentTier,
    TournamentType,
)


class BgmiGameMode(enum.Enum):
    SOLO = "solo"
    DUO = "duo"
    SQUAD = "squad"

    @property
    def label(self) -> str:
        return self.value.title()


BGMI_MAPS: tuple[str, ...] = (
    "erangel",
    "miramar",
    "sanhok",
    "vikendi",
    "livik",
    "karakin",
    "nusa",
)

DEFAULT_MAP_POOL: tuple[str, ...] = ("erangel", "miramar", "sanhok", "vikendi")

# Points awarded for finishing a match in a given position.
DEFAULT_PLACEMENT_POINTS: dict[str, int] = {
    "1": 10,
    "2": 6,
    "3": 5,
    "4": 4,
    "5": 3,
    "6": 2,
    "7": 1,
    "8": 1,
}


class BgmiTournamentBase(SQLModel):
    name: str = Field(index=True)
    game_id: Optional[int] = Field(default=None, foreign_key="games.id", index=True)
    abbreviation: Optional[str] = Field(default=None)
    type: TournamentType = Field(sa_column=Column(Enum(TournamentType)))
    format: TournamentFormat = Field(sa_column=Column(Enum(TournamentFormat)))
    tier: TournamentTier = Field(
        sa_column=Column(Enum(TournamentTier)), default=TournamentTier.LEAGUE
    )
    status: TournamentStatus = Field(
        sa_column=Column(Enum(TournamentStatus)), default=TournamentStatus.NOT_STARTED
    )
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    location: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    banner_path: Optional[str] = Field(default=None)
    default_color: Optional[str] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)

    # BGMI specific rules
    game_mode: BgmiGameMode = Field(
        default=BgmiGameMode.SQUAD, sa_column=Column(Enum(BgmiGameMode))
    )
    map_pool: list[str] = Field(
        default_factory=lambda: list(DEFAULT_MAP_POOL), sa_column=Column(JSON)
    )
    points_per_kill: int = Field(default=1, ge=0, le=10)
    placement_points: dict[str, int] = Field(
        default_factory=lambda: dict(DEFAULT_PLACEMENT_POINTS),
        sa_column=Column(JSON),
    )
    teams_per_lobby: int = Field(default=16, ge=2, le=32)
    match_count: int = Field(default=6, ge=1, le=30)


class BgmiTournament(BgmiTournamentBase, table=True):
    __tablename__ = "bgmi_tournaments"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(DateTime)
    )
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))

    @property
    def map_pool_label(self) -> str:
        return ", ".join(m.title() for m in self.map_pool)

    @property
    def placements(self) -> list[tuple[int, int]]:
        """Placement points as a sorted ``(placement, points)`` list."""
        return sorted(
            ((int(pos), points) for pos, points in self.placement_points.items()),
            key=lambda item: item[0],
        )


class BgmiTournamentPublic(BgmiTournamentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class BgmiTournamentCreate(BgmiTournamentBase):
    pass


class BgmiTournamentUpdate(SQLModel):
    name: Optional[str] = None
    game_id: Optional[int] = Field(default=None, foreign_key="games.id")
    abbreviation: Optional[str] = None
    type: Optional[TournamentType] = Field(
        default=None, sa_column=Column(Enum(TournamentType))
    )
    format: Optional[TournamentFormat] = Field(
        default=None, sa_column=Column(Enum(TournamentFormat))
    )
    tier: Optional[TournamentTier] = Field(
        default=None, sa_column=Column(Enum(TournamentTier))
    )
    status: Optional[TournamentStatus] = Field(
        default=None, sa_column=Column(Enum(TournamentStatus))
    )
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    location: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    banner_path: Optional[str] = Field(default=None)
    default_color: Optional[str] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)
    game_mode: Optional[BgmiGameMode] = Field(
        default=None, sa_column=Column(Enum(BgmiGameMode))
    )
    map_pool: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    points_per_kill: Optional[int] = Field(default=None, ge=0, le=10)
    placement_points: Optional[dict[str, int]] = Field(
        default=None, sa_column=Column(JSON)
    )
    teams_per_lobby: Optional[int] = Field(default=None, ge=2, le=32)
    match_count: Optional[int] = Field(default=None, ge=1, le=30)
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
