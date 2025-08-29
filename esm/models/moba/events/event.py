from sqlmodel import SQLModel, Field
import enum
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any


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
    team1: Optional[Any] = None
    team2: Optional[Any] = None
    state: Optional[Any] = None
    duration: int = 0
    follow_up: Optional[Tuple[MobaEventType, Optional[MobaJungleType]]] = None
    commentary: list[str] = Field(default_factory=list)

    @abstractmethod
    def calculate(self) -> Any:
        raise NotImplementedError
