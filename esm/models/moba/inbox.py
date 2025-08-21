# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, Column, Enum
from typing import TYPE_CHECKING, Optional
import enum
from datetime import datetime
from sqlmodel import Relationship


if TYPE_CHECKING:
    from esm.models.moba.player import MobaPlayer
    from esm.models.moba.team import MobaTeam
    from esm.models.moba.staff import MobaStaff


class MobaInboxCategory(enum.Enum):
    GENERAL = "general"
    TRANSFER = "transfer"
    CONTRACT = "contract"
    MATCH = "match"
    TRAINING = "training"
    SCOUTING = "scouting"
    TOURNAMENT = "tournament"
    MARKET = "market"
    ADMIN = "admin"


class MobaInboxStatus(enum.Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class MobaInboxPriority(enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MobaInboxBase(SQLModel):
    subject: str = Field(index=True)
    body: str
    category: MobaInboxCategory = Field(sa_column=Column(Enum(MobaInboxCategory)))
    status: MobaInboxStatus = Field(
        default=MobaInboxStatus.UNREAD,
        sa_column=Column(Enum(MobaInboxStatus)),
    )
    priority: MobaInboxPriority = Field(
        default=MobaInboxPriority.NORMAL,
        sa_column=Column(Enum(MobaInboxPriority)),
    )

    # Optional linkage to known senders
    sender_team_id: Optional[int] = Field(default=None, foreign_key="moba_teams.id")
    sender_player_id: Optional[int] = Field(default=None, foreign_key="moba_players.id")
    # Optional staff sender
    sender_staff_id: Optional[int] = Field(default=None, foreign_key="moba_staff.id")

    # Fallback sender display
    sender_name: Optional[str] = Field(default=None)
    sender_title: Optional[str] = Field(default=None)
    sender_avatar_path: Optional[str] = Field(default=None)

    # UX helpers
    is_starred: bool = Field(default=False)
    labels: Optional[str] = Field(
        default=None, description="Comma-separated labels for filtering"
    )
    action_url: Optional[str] = Field(default=None)


class MobaInbox(MobaInboxBase, table=True):
    __tablename__ = "moba_inbox"

    id: Optional[int] = Field(default=None, primary_key=True)

    sender_team: Optional["MobaTeam"] = Relationship()
    sender_player: Optional["MobaPlayer"] = Relationship()
    sender_staff: Optional["MobaStaff"] = Relationship()

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
    read_at: Optional[datetime] = Field(default=None)
    archived_at: Optional[datetime] = Field(default=None)


class MobaInboxCreate(MobaInboxBase):
    pass


class MobaInboxUpdate(SQLModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    category: Optional[MobaInboxCategory] = Field(default=None)
    status: Optional[MobaInboxStatus] = Field(default=None)
    priority: Optional[MobaInboxPriority] = Field(default=None)

    sender_team_id: Optional[int] = Field(default=None)
    sender_player_id: Optional[int] = Field(default=None)
    sender_staff_id: Optional[int] = Field(default=None)

    sender_name: Optional[str] = None
    sender_title: Optional[str] = None
    sender_avatar_path: Optional[str] = None

    is_starred: Optional[bool] = None
    labels: Optional[str] = None
    action_url: Optional[str] = None

    read_at: Optional[datetime] = Field(default=None)
    archived_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)


class MobaInboxPublic(MobaInboxBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
