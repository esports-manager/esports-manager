# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, Column, Enum
from esm.models.person import Person
from typing import Optional
import enum
from datetime import datetime, date
from sqlmodel import Relationship


from esm.models.moba.player_contract import MobaPlayerContract


class MobaPlayerRole(enum.Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    ADC = "adc"
    SUPPORT = "support"


class MobaPlayerBase(Person):
    role: MobaPlayerRole = Field(sa_column=Column(Enum(MobaPlayerRole), index=True))

    # Attributes
    mechanics: int = Field(gt=0, lt=100, default=50)
    knowledge: int = Field(gt=0, lt=100, default=50)
    agility: int = Field(gt=0, lt=100, default=50)
    reflexes: int = Field(gt=0, lt=100, default=50)
    accuracy: int = Field(gt=0, lt=100, default=50)
    aggressiveness: int = Field(gt=0, lt=100, default=50)
    vision: int = Field(gt=0, lt=100, default=50)
    farming: int = Field(gt=0, lt=100, default=50)
    communication: int = Field(gt=0, lt=100, default=50)

    # Player's individual stats
    morale: int = Field(gt=0, lt=100, default=50)
    form: int = Field(gt=0, lt=100, default=50)


class MobaPlayer(MobaPlayerBase, table=True):
    __tablename__ = "moba_players"

    id: Optional[int] = Field(default=None, primary_key=True)

    contracts: list["MobaPlayerContract"] = Relationship(back_populates="player")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)

    @property
    def current_contract(self) -> Optional["MobaPlayerContract"]:
        return next(
            (contract for contract in self.contracts if contract.is_active), None
        )

    def add_contract(self, contract: "MobaPlayerContract") -> None:
        for c in self.contracts:
            c.is_active = False
        contract.is_active = True
        self.contracts.append(contract)

    def remove_contract(self, contract: "MobaPlayerContract") -> None:
        for c in self.contracts:
            if c.id == contract.id:
                c.is_active = False


class MobaPlayerPublic(MobaPlayerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class MobaPlayerCreate(MobaPlayerBase):
    pass


class MobaPlayerUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nick_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    bio: Optional[str] = None
    image_path: Optional[str] = None
    role: Optional[MobaPlayerRole] = Field(
        default=None, sa_column=Column(Enum(MobaPlayerRole), index=True)
    )
    mechanics: Optional[int] = Field(default=None, gt=0, lt=100)
    knowledge: Optional[int] = Field(default=None, gt=0, lt=100)
    agility: Optional[int] = Field(default=None, gt=0, lt=100)
    reflexes: Optional[int] = Field(default=None, gt=0, lt=100)
    accuracy: Optional[int] = Field(default=None, gt=0, lt=100)
    aggressiveness: Optional[int] = Field(default=None, gt=0, lt=100)
    vision: Optional[int] = Field(default=None, gt=0, lt=100)
    farming: Optional[int] = Field(default=None, gt=0, lt=100)
    communication: Optional[int] = Field(default=None, gt=0, lt=100)
    morale: Optional[int] = Field(default=None, gt=0, lt=100)
    form: Optional[int] = Field(default=None, gt=0, lt=100)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
