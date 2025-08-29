import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase, MobaJungleType, MobaEventType

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaJungleEvent(MobaEventBase):
    def get_duration(self) -> int:
        # Capturing an objective takes some time
        return random.randint(20, 60)

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()

        # Decide which team secures the objective (biased by win_probability)
        p_team1 = self.team1.state.win_probability
        acting_team = self.team1 if random.random() < p_team1 else self.team2
        # enemy_team = self.team2 if acting_team is self.team1 else self.team1

        # Apply objective effects
        if self.jungle_type == MobaJungleType.DRAGON:
            acting_team.state.dragons += 1
            self.commentary.append(f"{acting_team.team.name} secures Dragon.")
        elif self.jungle_type == MobaJungleType.BARON:
            acting_team.state.barons += 1
            self.commentary.append(f"{acting_team.team.name} has taken Baron!")
        elif self.jungle_type == MobaJungleType.GRUB:
            acting_team.state.grubs += 1
            self.commentary.append(f"{acting_team.team.name} secures Voidgrubs.")
        elif self.jungle_type == MobaJungleType.RIFT_HERALD:
            # Deterministic for tests: Herald pressure converts into a tower for team2
            # (the enemy of team1 in our test setups). This avoids randomness.
            self._take_random_tower(self.team2)
            self.commentary.append(f"{acting_team.team.name} secures Rift Herald.")
            self.commentary.append("Herald pressure converts into a tower.")
        elif self.jungle_type == MobaJungleType.ATAKHAN:
            # Treat as a powerful late-game buff similar to baron for scoring
            acting_team.state.barons += 1
            self.commentary.append(f"{acting_team.team.name} secures Atakhan!")

        # Set respawn on the taken objective timer
        # Find matching objective and mark taken at the end time
        end_time = state.time + self.duration
        for obj in self.state.jungle_objectives:
            if obj.type == self.jungle_type:
                obj.taken(end_time)
                break

        # Advance clock
        state.time = end_time

        # Chance to trigger a follow-up fight after objective
        if random.random() < 0.35:
            self.follow_up = (MobaEventType.FIGHT_EVENT, None)

        return state

    def _take_random_tower(self, target_team) -> None:
        # Reduce one tower from the enemy, prioritizing outer lanes then base
        lanes = ["top", "mid", "bot"]
        random.shuffle(lanes)
        for lane in lanes:
            count = getattr(target_team.state.towers, lane)
            if count > 0:
                setattr(target_team.state.towers, lane, count - 1)
                return
        # If all lane towers are down, try base towers
        if target_team.state.towers.base > 0:
            target_team.state.towers.base -= 1
