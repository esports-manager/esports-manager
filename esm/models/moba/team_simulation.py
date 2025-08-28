from sqlmodel import SQLModel, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from esm.models.moba.team import MobaTeam
    from esm.models.moba.player_simulation import MobaPlayerSimulation


class MobaTowers(SQLModel):
    top: int = 3
    mid: int = 3
    bot: int = 3
    base: int = 2


class MobaInhibitors(SQLModel):
    top: int = 1
    mid: int = 1
    bot: int = 1


class MobaTeamState(SQLModel):
    towers: MobaTowers = Field(default_factory=MobaTowers)
    inhibitors: MobaInhibitors = Field(default_factory=MobaInhibitors)
    dragons: int = 0
    barons: int = 0
    grubs: int = 0
    first_blood: bool = False
    first_tower: bool = False
    win_probability: float = 0.5


class MobaTeamSimulation(SQLModel):
    team: "MobaTeam"
    players: list["MobaPlayerSimulation"] = Field(default_factory=list)
    state: MobaTeamState = Field(default_factory=MobaTeamState)

    @property
    def kills(self) -> int:
        return sum(player.kills for player in self.players)

    @property
    def deaths(self) -> int:
        return sum(player.deaths for player in self.players)

    @property
    def assists(self) -> int:
        return sum(player.assists for player in self.players)

    @property
    def kda(self) -> float:
        if self.deaths == 0:
            return self.kills + self.assists
        return (self.kills + self.assists) / self.deaths

    @property
    def points(self) -> int:
        return sum(player.points for player in self.players)
