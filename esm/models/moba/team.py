# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlmodel import SQLModel, Field, DateTime, Column
from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship
from datetime import datetime

from esm.models.moba.player_contract import MobaPlayerContract

if TYPE_CHECKING:
    from esm.models.moba.player import MobaPlayer


class MobaTeamBase(SQLModel):
    name: str
    nationality: Optional[str]
    region: Optional[str]
    description: Optional[str]
    logo_path: Optional[str]


class MobaTeam(MobaTeamBase, table=True):
    __tablename__ = "moba_teams"

    id: Optional[int] = Field(default=None, primary_key=True)

    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(DateTime)
    )
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))

    contracts: list["MobaPlayerContract"] = Relationship(back_populates="team")

    @property
    def current_players(self) -> list["MobaPlayer"]:
        return [contract.player for contract in self.contracts if contract.is_active]

    def add_player(self, player: "MobaPlayer", contract: "MobaPlayerContract") -> None:
        if contract.team_id != self.id:
            raise ValueError("Contract is not for this team")
        player.add_contract(contract)
        self.contracts.append(contract)

    def remove_player(self, player: "MobaPlayer") -> None:
        contract = player.current_contract
        if not contract:
            raise ValueError("Player has no active contract")
        if contract.team_id != self.id:
            raise ValueError("Contract is not for this team")
        player.remove_contract(contract)


class MobaTeamCreate(MobaTeamBase):
    pass


class MobaTeamPublic(MobaTeamBase):
    id: int


class MobaTeamUpdate(SQLModel):
    name: Optional[str] = None
    nationality: Optional[str] = None
    region: Optional[str] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
