from esm.models.moba.events.event import MobaEventBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaJungleEvent(MobaEventBase):
    def get_duration(self) -> int:
        pass

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()
        state.time += self.duration
        return state
