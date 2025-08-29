import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaNothingEvent(MobaEventBase):
    def get_duration(self) -> int:
        return random.randint(30, 90)

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()
        state.time += self.duration
        return state
