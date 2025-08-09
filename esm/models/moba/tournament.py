# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field, Column, Enum
from esm.models.tournament import (
    TournamentType,
    TournamentFormat,
    TournamentTier,
)


class MobaTournamentBase(SQLModel):
    name: str = Field(index=True)
    abbreviation: Optional[str] = Field(default=None)
    type: TournamentType = Field(sa_column=Column(Enum(TournamentType)))
    format: TournamentFormat = Field(sa_column=Column(Enum(TournamentFormat)))
    tier: TournamentTier = Field(
        sa_column=Column(Enum(TournamentTier)), default=TournamentTier.LEAGUE
    )
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    location: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    banner_path: Optional[str] = Field(default=None)
    default_color: Optional[str] = Field(default=None)
    logo_path: Optional[str] = Field(default=None)


class MobaTournament(MobaTournamentBase, table=True):
    __tablename__ = "moba_tournaments"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaTournamentPublic(MobaTournamentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class MobaTournamentCreate(MobaTournamentBase):
    pass


class MobaTournamentUpdate(SQLModel):
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
