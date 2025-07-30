from sqlmodel import (
    CheckConstraint,
    SQLModel,
    Field,
    Relationship,
)
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime

if TYPE_CHECKING:
    from esm.models.moba.team import MobaTeam
    from esm.models.moba.player import MobaPlayer


class MobaPlayerContractBase(SQLModel):
    start_date: date
    end_date: date
    salary: int = Field(default=0)
    is_active: bool = Field(default=True, index=True)


class MobaPlayerContract(MobaPlayerContractBase, table=True):
    __tablename__ = "moba_player_contracts"
    __table_args__ = (
        CheckConstraint("start_date < end_date", name="start_date_before_end_date"),
        CheckConstraint("salary >= 0", name="salary_non_negative"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="moba_teams.id")
    player_id: int = Field(foreign_key="moba_players.id")
    player: "MobaPlayer" = Relationship(back_populates="contracts")
    team: "MobaTeam" = Relationship(back_populates="contracts")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class MobaPlayerContractPublic(MobaPlayerContractBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]


class MobaPlayerContractCreate(MobaPlayerContractBase):
    team_id: int
    player_id: int


class MobaPlayerContractUpdate(SQLModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    salary: Optional[int] = None
    is_active: Optional[bool] = None
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
