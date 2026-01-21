# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, Column, Enum
from typing import Optional
from datetime import datetime
import enum


class DraftPhase(enum.Enum):
    BAN_1 = "ban_1"
    PICK_1 = "pick_1"
    BAN_2 = "ban_2"
    PICK_2 = "pick_2"
    COMPLETED = "completed"


class DraftTeamSide(enum.Enum):
    BLUE = "blue"
    RED = "red"


class DraftActionType(enum.Enum):
    BAN = "ban"
    PICK = "pick"


class MobaMatchDraftSession(SQLModel, table=True):
    __tablename__ = "moba_match_draft_sessions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: int = Field(foreign_key="moba_games.id", unique=True)
    current_phase: DraftPhase = Field(
        sa_column=Column(Enum(DraftPhase)), default=DraftPhase.BAN_1
    )
    current_turn: DraftTeamSide = Field(
        sa_column=Column(Enum(DraftTeamSide)), default=DraftTeamSide.BLUE
    )
    turn_number: int = Field(default=0)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaMatchDraftAction(SQLModel, table=True):
    __tablename__ = "moba_match_draft_actions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    draft_session_id: int = Field(foreign_key="moba_match_draft_sessions.id")
    action_type: DraftActionType = Field(sa_column=Column(Enum(DraftActionType)))
    team_side: DraftTeamSide = Field(sa_column=Column(Enum(DraftTeamSide)))
    champion_id: int = Field(foreign_key="moba_champions.id")
    player_slot: Optional[str] = Field(default=None)
    order_index: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)


class MobaMatchDraftSessionPublic(SQLModel):
    id: int
    match_id: int
    current_phase: DraftPhase
    current_turn: DraftTeamSide
    turn_number: int
    is_completed: bool


class MobaMatchDraftActionPublic(SQLModel):
    id: int
    draft_session_id: int
    action_type: DraftActionType
    team_side: DraftTeamSide
    champion_id: int
    player_slot: Optional[str]
    order_index: int
