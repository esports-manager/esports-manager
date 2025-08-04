# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, Column, Enum
from esm.models.person import Person
from typing import TYPE_CHECKING, Optional
import enum
from datetime import datetime, date
from sqlmodel import Relationship
from esm.services import get_country_code

if TYPE_CHECKING:
    from esm.models.moba.player_contract import MobaPlayerContract


class MobaPlayerRole(enum.Enum):
    TOP = "top"
    JUNGLE = "jungle"
    MID = "mid"
    ADC = "adc"
    SUPPORT = "support"


class MobaPlayerBase(Person):
    role: MobaPlayerRole = Field(sa_column=Column(Enum(MobaPlayerRole), index=True))
    is_active: bool = Field(default=True)

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

    value: int = Field(default=1000000)

    @property
    def overall(self) -> int:
        return (
            sum(
                [
                    self.mechanics,
                    self.knowledge,
                    self.agility,
                    self.reflexes,
                    self.accuracy,
                    self.aggressiveness,
                    self.vision,
                    self.farming,
                    self.communication,
                ]
            )
            // 9
        )

    def get_country_code(self) -> str:
        if self.nationality:
            return get_country_code(self.nationality)
        else:
            return ""


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
    id: Optional[int] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)


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
    is_active: Optional[bool] = None
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
    value: Optional[int] = Field(default=None, gt=0)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
