# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, Column, Enum
from typing import Optional
from datetime import datetime
import enum


class LineupStatus(enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"


class MobaMatchLineupSlot(SQLModel, table=True):
    __tablename__ = "moba_match_lineup_slots"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="moba_games.id")
    team_id: int = Field(foreign_key="moba_teams.id")
    player_id: Optional[int] = Field(default=None, foreign_key="moba_players.id")
    slot_role: str = Field(index=True)
    assigned_role: Optional[str] = Field(default=None)
    slot_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaMatchLineup(SQLModel, table=True):
    __tablename__ = "moba_match_lineups"

    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="moba_games.id", unique=True)
    blue_team_status: LineupStatus = Field(
        sa_column=Column(Enum(LineupStatus)), default=LineupStatus.DRAFT
    )
    red_team_status: LineupStatus = Field(
        sa_column=Column(Enum(LineupStatus)), default=LineupStatus.DRAFT
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaMatchLineupPublic(SQLModel):
    id: int
    match_id: int
    blue_team_status: LineupStatus
    red_team_status: LineupStatus


class MobaMatchLineupSlotPublic(SQLModel):
    id: int
    match_id: int
    team_id: int
    player_id: Optional[int]
    slot_role: str
    assigned_role: Optional[str]
    slot_order: int
