# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, Column, Enum, Relationship
from typing import TYPE_CHECKING, Optional
import enum
from datetime import datetime

if TYPE_CHECKING:
    from esm.models.moba.player_contract import MobaPlayer
    from esm.models.moba.champion import MobaChampion


class MobaChampionMasteryTier(enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    CHALLENGER = "challenger"


class MobaChampionMastery(SQLModel, table=True):
    __tablename__ = "moba_champion_masteries"
    id: int = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="moba_players.id", nullable=False)
    champion_id: int = Field(foreign_key="moba_champions.id", nullable=False)
    tier: MobaChampionMasteryTier = Field(
        sa_column=Column(Enum(MobaChampionMasteryTier))
    )
    points: int = Field(ge=0, default=0)

    player: "MobaPlayer" = Relationship(back_populates="champion_pool")
    champion: "MobaChampion" = Relationship(back_populates="champion_masteries")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaChampionMasteryCreate(SQLModel):
    player_id: int
    champion_id: int
    tier: MobaChampionMasteryTier
    points: int


class MobaChampionMasteryUpdate(SQLModel):
    tier: Optional[MobaChampionMasteryTier] = Field(default=None)
    points: Optional[int] = Field(default=None)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)


class MobaChampionMasteryPublic(SQLModel):
    player_id: int
    champion_id: int
    tier: MobaChampionMasteryTier
    points: int
