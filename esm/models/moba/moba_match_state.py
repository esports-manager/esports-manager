from sqlmodel import SQLModel, Field
from typing import Optional
from esm.models.moba.events.event_types import MobaJungleType
from esm.models.moba.moba_match import MobaMatchStatus


JUNGLE_OBJECTIVES = {
    MobaJungleType.DRAGON: {
        "name": "dragon",
        "first_spawn_at": 5 * 60,
        "respawn_seconds": 5 * 60,
        "despawn_at": None,
    },
    MobaJungleType.RIFT_HERALD: {
        "name": "rift herald",
        "first_spawn_at": 8 * 60,
        "respawn_seconds": 6 * 60,
        "despawn_at": 20 * 60,
    },
    MobaJungleType.GRUB: {
        "name": "void grubs",
        "first_spawn_at": 5 * 60,
        "respawn_seconds": 3 * 60,
        "despawn_at": 14 * 60,
    },
    MobaJungleType.BARON: {
        "name": "baron nashor",
        "first_spawn_at": 20 * 60,
        "respawn_seconds": 6 * 60,
        "despawn_at": None,
    },
    MobaJungleType.ATAKHAN: {
        "name": "atakhan",
        "first_spawn_at": 25 * 60,
        "respawn_seconds": 6 * 60,
        "despawn_at": None,
    },
}


class MobaJungleObjective(SQLModel):
    name: str
    type: MobaJungleType
    enabled: bool = True  # If the objective is on this patch
    available: bool = False  # Spawning window says it can be taken now
    first_spawn_at: int = 0
    respawn_seconds: int = 0
    next_spawn_at: int = 0
    despawn_at: Optional[int] = None

    def refresh(self, current_time: int) -> None:
        if not self.enabled:
            return

        if self.despawn_at is not None and current_time >= self.despawn_at:
            self.available = False
            return

        self.available = current_time >= self.next_spawn_at

    def taken(self, current_time: int) -> None:
        self.available = False
        self.next_spawn_at = current_time + self.respawn_seconds


class MobaMatchState(SQLModel):
    jungle_objectives: list[MobaJungleObjective] = Field(default_factory=list)
    first_blood: bool = False
    first_tower: bool = False
    winner: int | None = None
    time: int = 0
    status: MobaMatchStatus = Field(default=MobaMatchStatus.NOT_STARTED)

    def update_jungle_objectives(self) -> None:
        self.jungle_objectives = [
            MobaJungleObjective(
                name=JUNGLE_OBJECTIVES[obj]["name"],
                type=obj,
                first_spawn_at=JUNGLE_OBJECTIVES[obj]["first_spawn_at"],
                respawn_seconds=JUNGLE_OBJECTIVES[obj]["respawn_seconds"],
                despawn_at=JUNGLE_OBJECTIVES[obj]["despawn_at"],
            )
            for obj in list(MobaJungleType)
        ]

    def reset(self) -> None:
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
