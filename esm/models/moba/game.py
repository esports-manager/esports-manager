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


class MobaGameStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MobaGameFormat(enum.Enum):
    BO1 = "bo1"
    BO2 = "bo2"
    BO3 = "bo3"
    BO5 = "bo5"


class MobaGameResult(enum.Enum):
    BLUE_WIN = "blue_win"
    RED_WIN = "red_win"
    DRAW = "draw"


class MobaGameBase(SQLModel):
    status: MobaGameStatus = Field(
        sa_column=Column(Enum(MobaGameStatus)), default=MobaGameStatus.NOT_STARTED
    )
    format: MobaGameFormat = Field(
        sa_column=Column(Enum(MobaGameFormat)), default=MobaGameFormat.BO1
    )
    result: Optional[MobaGameResult] = Field(
        sa_column=Column(Enum(MobaGameResult)), default=None
    )
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)


class MobaGame(MobaGameBase, table=True):
    __tablename__ = "moba_games"

    id: int | None = Field(default=None, primary_key=True)
    blue_team_id: int = Field(foreign_key="moba_teams.id")
    red_team_id: int = Field(foreign_key="moba_teams.id")

    # Relationships
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    blue_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "MobaGame.blue_team_id"}
    )
    red_team: "MobaTeam" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "MobaGame.red_team_id"}
    )


class MobaGamePublic(MobaGameBase):
    id: int


class MobaGameCreate(MobaGameBase):
    pass


class MobaGameUpdate(SQLModel):
    blue_team_id: Optional[int] = Field(default=None, foreign_key="moba_teams.id")
    red_team_id: Optional[int] = Field(default=None, foreign_key="moba_teams.id")
    status: Optional[MobaGameStatus] = Field(
        default=None, sa_column=Column(Enum(MobaGameStatus))
    )
    format: Optional[MobaGameFormat] = Field(
        default=None, sa_column=Column(Enum(MobaGameFormat))
    )
    result: Optional[MobaGameResult] = Field(
        default=None, sa_column=Column(Enum(MobaGameResult))
    )
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
