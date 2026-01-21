import random
from typing import TYPE_CHECKING
from esm.models.moba.events.event import MobaEventBase
from esm.services.narration import narrate_nexus

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaNexusEvent(MobaEventBase):
    def get_duration(self) -> int:
        # Ending push takes a bit
        return random.randint(30, 90)

    def calculate(self) -> "MobaMatchState":
        # Import here to avoid circular import at module level
        from esm.models.moba.moba_match_simulation import MobaMatchStatus

        state = self.state.model_copy()
        self.duration = self.get_duration()

        # Pick winner by current win probability
        p_team1 = self.team1.state.win_probability
        winner_idx = 1 if random.random() < p_team1 else 2
        state.winner = winner_idx

        # Advance time and end
        state.time += self.duration
        state.status = MobaMatchStatus.COMPLETED
        
        winner_team = self.team1 if winner_idx == 1 else self.team2
        text, severity = narrate_nexus(winner_team)
        self.commentary.append(text)
        
        return state
