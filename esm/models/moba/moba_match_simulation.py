from sqlmodel import SQLModel, Field
from typing import TYPE_CHECKING
import enum
from datetime import datetime


if TYPE_CHECKING:
    from esm.models.moba.team_simulation import MobaTeamSimulation
    from esm.models.moba.events.event import MobaEventBase, MobaEventType


class MobaJungleObjective(SQLModel):
    name: str
    enabled: bool = True  # If the objective is available on this patch
    available: bool = False  # If the objective is available to be taken


class MobaMatchStatus(str, enum.Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    ENDED = "ended"


class MobaMatchState(SQLModel):
    team1_towers_taken: int = 0
    team2_towers_taken: int = 0
    team1_inhibitors_taken: int = 0
    team2_inhibitors_taken: int = 0
    team1_nexus_exposed: bool = False
    team2_nexus_exposed: bool = False
    jungle_objectives: list[MobaJungleObjective] = Field(default_factory=list)
    first_blood: bool = False
    first_tower: bool = False
    winner: int | None = None
    time: int = 0
    status: MobaMatchStatus = Field(default=MobaMatchStatus.NOT_STARTED)

    def update_jungle_objectives(self) -> None:
        default_objectives = [
            MobaJungleObjective(name="Dragon"),
            MobaJungleObjective(name="Baron"),
            MobaJungleObjective(name="Grub"),
            MobaJungleObjective(name="Rift Herald"),
            MobaJungleObjective(name="Atakhan"),
        ]
        self.jungle_objectives = default_objectives

    def reset(self) -> None:
        self.team1_towers_taken = 0
        self.team2_towers_taken = 0
        self.team1_inhibitors_taken = 0
        self.team2_inhibitors_taken = 0
        self.team1_nexus_exposed = False
        self.team2_nexus_exposed = False
        self.first_blood = False
        self.first_tower = False
        self.winner = None
        self.time = 0
        self.status = MobaMatchStatus.NOT_STARTED
        self.update_jungle_objectives()

    @property
    def minutes_played(self) -> int:
        return self.time // 60

    @property
    def seconds_played(self) -> int:
        return self.time % 60


class MobaMatchSimulation(SQLModel):
    team1: "MobaTeamSimulation"
    team2: "MobaTeamSimulation"
    state: MobaMatchState = Field(default_factory=MobaMatchState)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    events: list["MobaEventBase"] = Field(default_factory=list)
    enabled_events: list[type["MobaEventBase"]] = Field(default_factory=list)

    def add_event(self, event: "MobaEventBase") -> None:
        self.events.append(event)

    def get_enabled_events(self) -> list[type["MobaEventType"]]:
        # Here the simulation engine should look at the Match State and then decide which events are possible
        pass

    def get_event(self) -> "MobaEventBase":
        # Here the simulation engine should choose one event from the list of possible events
        pass
