# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, Column, Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship
from datetime import datetime
import enum


if TYPE_CHECKING:
    from esm.models.moba.team import MobaTeam


class MobaMatchStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MobaMatchFormat(enum.Enum):
    BO1 = "bo1"
    BO2 = "bo2"
    BO3 = "bo3"
    BO5 = "bo5"


class MobaMatchResult(enum.Enum):
    BLUE_WIN = "blue_win"
    RED_WIN = "red_win"
    DRAW = "draw"


class MobaMatchBase(SQLModel):
    status: MobaMatchStatus = Field(
        sa_column=Column(Enum(MobaMatchStatus)), default=MobaMatchStatus.NOT_STARTED
    )
    format: MobaMatchFormat = Field(
        sa_column=Column(Enum(MobaMatchFormat)), default=MobaMatchFormat.BO1
    )
    result: Optional[MobaMatchResult] = Field(
        sa_column=Column(Enum(MobaMatchResult)), default=None
    )
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)


class MobaMatch(MobaMatchBase, table=True):
    __tablename__ = "moba_games"

    id: int | None = Field(default=None, primary_key=True)
    blue_team_id: int = Field(foreign_key="moba_teams.id")
    red_team_id: int = Field(foreign_key="moba_teams.id")

    # Relationships
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    blue_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "MobaMatch.blue_team_id"}
    )
    red_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "MobaMatch.red_team_id"}
    )


class MobaMatchPublic(MobaMatchBase):
    id: int


class MobaMatchCreate(MobaMatchBase):
    pass


class MobaMatchUpdate(SQLModel):
    blue_team_id: Optional[int] = Field(default=None, foreign_key="moba_teams.id")
    red_team_id: Optional[int] = Field(default=None, foreign_key="moba_teams.id")
    status: Optional[MobaMatchStatus] = Field(
        default=None, sa_column=Column(Enum(MobaMatchStatus))
    )
    format: Optional[MobaMatchFormat] = Field(
        default=None, sa_column=Column(Enum(MobaMatchFormat))
    )
    result: Optional[MobaMatchResult] = Field(
        default=None, sa_column=Column(Enum(MobaMatchResult))
    )
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
