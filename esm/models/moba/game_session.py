# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Column, DateTime, Relationship

if TYPE_CHECKING:
    from esm.models.moba.team import MobaTeam


class MobaGameSessionBase(SQLModel):
    name: str
    manager_name: str
    team_id: int = Field(foreign_key="moba_teams.id")
    base_database_url: str
    session_database_url: Optional[str] = Field(default=None)
    current_day: int = Field(default=1, ge=1)
    seed: int = Field(default=0, ge=0)


class MobaGameSession(MobaGameSessionBase, table=True):
    __tablename__ = "moba_game_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)

    team: Optional["MobaTeam"] = Relationship()

    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(DateTime)
    )
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))


class MobaGameSessionCreate(SQLModel):
    manager_name: str
    team_id: int
    name: Optional[str] = None
    seed: Optional[int] = Field(default=None, ge=0)
    base_database_url: Optional[str] = None


class MobaGameSessionPublic(MobaGameSessionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class MobaGameSessionUpdate(SQLModel):
    name: Optional[str] = None
    manager_name: Optional[str] = None
    team_id: Optional[int] = None
    current_day: Optional[int] = Field(default=None, ge=1)
    seed: Optional[int] = Field(default=None, ge=0)
    session_database_url: Optional[str] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
