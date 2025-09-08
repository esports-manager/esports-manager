from sqlmodel import SQLModel, Field
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from esm.models.moba.team_simulation import MobaTeamSimulation
from esm.models.moba.events.event_types import MobaEventType, MobaJungleType
from esm.models.moba.moba_match_state import MobaMatchState


class MobaEventBase(SQLModel, ABC):
    name: str = ""
    event_type: Optional[MobaEventType] = None
    jungle_type: Optional[MobaJungleType] = None
    team1: Optional[MobaTeamSimulation] = None
    team2: Optional[MobaTeamSimulation] = None
    state: Optional[MobaMatchState] = None
    duration: int = 0
    follow_up: Optional[Tuple[MobaEventType, Optional[MobaJungleType]]] = None
    commentary: list[str] = Field(default_factory=list)
    points: int = 0

    @abstractmethod
    def calculate(self) -> MobaMatchState:
        raise NotImplementedError
