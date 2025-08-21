# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import enum
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship, Column, Enum
from esm.models.person import Person

if TYPE_CHECKING:
    from esm.models.moba.team import MobaTeam


class MobaStaffRole(enum.Enum):
    HEAD_COACH = "head_coach"
    ASSISTANT_COACH = "assistant_coach"
    STRATEGIC_COACH = "strategic_coach"
    ANALYST = "analyst"
    SCOUT = "scout"
    DIRECTOR = "director"  # CEO / Director
    MEDIA_MANAGER = "media_manager"


class MobaStaffBase(Person):
    role: MobaStaffRole = Field(sa_column=Column(Enum(MobaStaffRole)))

    years_experience: Optional[int] = Field(default=None, ge=0)

    def display_name(self) -> str:
        return self.nick_name or f"{self.first_name} {self.last_name}"


class MobaStaff(MobaStaffBase, table=True):
    __tablename__ = "moba_staff"

    id: Optional[int] = Field(default=None, primary_key=True)

    team_id: Optional[int] = Field(default=None, foreign_key="moba_teams.id")
    team: "MobaTeam" = Relationship(back_populates="staff")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaStaffCreate(MobaStaffBase):
    team_id: Optional[int] = None


class MobaStaffUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nick_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    bio: Optional[str] = None
    image_path: Optional[str] = None
    role: Optional[MobaStaffRole] = None
    years_experience: Optional[int] = Field(default=None, ge=0)
    team_id: Optional[int] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)


class MobaStaffPublic(MobaStaffBase):
    id: int
    team_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
