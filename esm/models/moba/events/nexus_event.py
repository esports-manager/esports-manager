from esm.models.moba.events.event import MobaEventBase
from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaNexusEvent(MobaEventBase):
    def get_duration(self) -> int:
        pass

    def calculate(self) -> MobaMatchState:
        state = self.state.model_copy()
        self.duration = self.get_duration()
        state.time += self.duration
        return state
