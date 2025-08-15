# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import enum
from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, Enum


class TournamentType(enum.Enum):
    INTERNATIONAL = "international"
    REGIONAL = "regional"
    NATIONAL = "national"
    SHOWMATCH = "showmatch"


class TournamentFormat(enum.Enum):
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"
    LEAGUE = "league"
    GSL = "gsl"
    BO1_SERIES = "bo1_series"
    BO2_SERIES = "bo2_series"
    BO3_SERIES = "bo3_series"
    BO5_SERIES = "bo5_series"
    BO7_SERIES = "bo7_series"
    BO9_SERIES = "bo9_series"


class TournamentTier(enum.Enum):
    PREMIER = "premier"
    MAJOR = "major"
    LEAGUE = "league"
    MINOR = "minor"
    ACADEMY = "academy"
    SEMIPRO = "semipro"
    AMATEUR = "amateur"


class TournamentStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUSPENDED = "suspended"
    ENDED = "ended"
    CANCELLED = "cancelled"


class TournamentBase(SQLModel):
    name: str = Field(index=True)
    abbreviation: Optional[str] = Field(default=None)
    type: TournamentType = Field(sa_column=Column(Enum(TournamentType)))
    format: TournamentFormat = Field(sa_column=Column(Enum(TournamentFormat)))
    tier: TournamentTier = Field(
        sa_column=Column(Enum(TournamentTier)), default=TournamentTier.LEAGUE
    )
    status: TournamentStatus = Field(
        sa_column=Column(Enum(TournamentStatus)), default=TournamentStatus.NOT_STARTED
    )
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    location: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    banner_path: Optional[str] = Field(default=None)
    default_color: Optional[str] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)


class TournamentPublic(TournamentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class TournamentCreate(TournamentBase):
    pass


class TournamentUpdate(SQLModel):
    name: Optional[str] = None
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
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    location: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    banner_path: Optional[str] = Field(default=None)
    default_color: Optional[str] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
