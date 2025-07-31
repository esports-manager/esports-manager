# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import enum
from sqlmodel import SQLModel, Field, Column, Enum
from typing import Optional, TYPE_CHECKING
from datetime import datetime, date

if TYPE_CHECKING:
    pass


class MobaChampionRole(enum.Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    ADC = "adc"
    SUPPORT = "support"


class MobaChampionType(enum.Enum):
    ASSASSIN = "assassin"
    HEALER = "healer"
    TANK = "tank"
    MAGE = "mage"
    FIGHTER = "fighter"
    MARKSMAN = "marksman"


class MobaChampionDifficulty(enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MobaChampionTier(enum.Enum):
    SP = "s+"
    S = "s"
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    F = "f"


class MobaChampionBase(SQLModel):
    name: str = Field(index=True)
    release_date: date
    primary_role: MobaChampionRole = Field(sa_column=Column(Enum(MobaChampionRole)))
    secondary_role: Optional[MobaChampionRole] = Field(
        default=None, sa_column=Column(Enum(MobaChampionRole))
    )
    champion_type1: MobaChampionType = Field(sa_column=Column(Enum(MobaChampionType)))
    champion_type2: Optional[MobaChampionType] = Field(
        default=None, sa_column=Column(Enum(MobaChampionType))
    )
    difficulty: MobaChampionDifficulty = Field(
        sa_column=Column(Enum(MobaChampionDifficulty))
    )
    strength: int = Field(gt=0, lt=100, default=50)
    image_path: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    def get_champion_tier(self) -> MobaChampionTier:
        if self.strength >= 95:
            return MobaChampionTier.SP
        elif self.strength >= 90:
            return MobaChampionTier.S
        elif self.strength >= 85:
            return MobaChampionTier.A
        elif self.strength >= 80:
            return MobaChampionTier.B
        elif self.strength >= 75:
            return MobaChampionTier.C
        elif self.strength >= 70:
            return MobaChampionTier.D
        else:
            return MobaChampionTier.F


class MobaChampion(MobaChampionBase, table=True):
    __tablename__ = "moba_champions"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaChampionPublic(MobaChampionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class MobaChampionCreate(MobaChampionBase):
    pass


class MobaChampionUpdate(SQLModel):
    name: Optional[str] = None
    release_date: Optional[date] = None
    primary_role: Optional[MobaChampionRole] = Field(
        default=None, sa_column=Column(Enum(MobaChampionRole))
    )
    secondary_role: Optional[MobaChampionRole] = Field(
        default=None, sa_column=Column(Enum(MobaChampionRole))
    )
    champion_type1: Optional[MobaChampionType] = Field(
        default=None, sa_column=Column(Enum(MobaChampionType))
    )
    champion_type2: Optional[MobaChampionType] = Field(
        default=None, sa_column=Column(Enum(MobaChampionType))
    )
    difficulty: Optional[MobaChampionDifficulty] = Field(
        default=None, sa_column=Column(Enum(MobaChampionDifficulty))
    )
    strength: Optional[int] = Field(gt=0, lt=100, default=None)
    image_path: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
