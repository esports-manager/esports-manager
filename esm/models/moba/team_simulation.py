from sqlmodel import SQLModel, Field
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
    team: MobaTeam
    players: list[MobaPlayerSimulation] = Field(default_factory=list)
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

    @property
    def towers_remaining(self) -> int:
        return (
            self.state.towers.top
            + self.state.towers.mid
            + self.state.towers.bot
            + self.state.towers.base
        )

    @property
    def are_inhibitors_exposed(self) -> bool:
        return len(self.get_exposed_inhibitors()) > 0

    def get_exposed_inhibitors(self) -> list[str]:
        exposed = []
        if self.state.towers.top == 0 and self.state.inhibitors.top == 1:
            exposed.append("top")
        if self.state.towers.mid == 0 and self.state.inhibitors.mid == 1:
            exposed.append("mid")
        if self.state.towers.bot == 0 and self.state.inhibitors.bot == 1:
            exposed.append("bot")
        return exposed

    def are_base_towers_exposed(self) -> bool:
        towers = [self.state.towers.top, self.state.towers.mid, self.state.towers.bot]
        inhibitors = [
            self.state.inhibitors.top,
            self.state.inhibitors.mid,
            self.state.inhibitors.bot,
        ]
        return (
            any(t == 0 and i == 1 for t, i in zip(towers, inhibitors))
            and self.state.towers.base > 0
        )

    def get_remaining_towers(self) -> list[str]:
        remaining = []
        if self.state.towers.top > 0:
            remaining.append("top")
        if self.state.towers.mid > 0:
            remaining.append("mid")
        if self.state.towers.bot > 0:
            remaining.append("bot")

        if self.are_base_towers_exposed():
            remaining.append("base")
        return remaining

    def is_nexus_exposed(self) -> bool:
        inhibitors = [
            self.state.inhibitors.top,
            self.state.inhibitors.mid,
            self.state.inhibitors.bot,
        ]
        return any(i == 0 for i in inhibitors) and self.state.towers.base == 0

    def score(self) -> int:
        return sum(player.get_score() for player in self.players)
