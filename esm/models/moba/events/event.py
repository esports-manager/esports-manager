from sqlmodel import SQLModel, Field
import enum
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any, TYPE_CHECKING
from esm.models.moba.team_simulation import MobaTeamSimulation


if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaEventType(str, enum.Enum):
    NOTHING_EVENT: str = "nothing"
    FIGHT_EVENT: str = "fight"
    JUNGLE_EVENT: str = "jungle event"
    TOWER_EVENT: str = "tower event"
    INHIBITOR_EVENT: str = "inhibitor event"
    NEXUS_EVENT: str = "nexus event"


class MobaJungleType(str, enum.Enum):
    DRAGON: str = "dragon"
    BARON: str = "baron"
    GRUB: str = "grub"
    RIFT_HERALD: str = "rift herald"
    ATAKHAN: str = "atakhan"


class MobaEventBase(SQLModel, ABC):
    name: str = ""
    event_type: Optional[MobaEventType] = None
    jungle_type: Optional[MobaJungleType] = None
    team1: Optional[MobaTeamSimulation] = None
    team2: Optional[MobaTeamSimulation] = None
    state: Optional["MobaMatchState"] = None
    duration: int = 0
    follow_up: Optional[Tuple[MobaEventType, Optional[MobaJungleType]]] = None
    commentary: list[str] = Field(default_factory=list)
    points: int = 0

    @abstractmethod
    def calculate(self) -> Any:
        raise NotImplementedError
