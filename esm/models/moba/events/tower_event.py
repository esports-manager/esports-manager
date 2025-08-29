import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase, MobaEventType

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaTowerEvent(MobaEventBase):
    def get_duration(self) -> int:
        # Sieges are longer than fights
        return random.randint(25, 75)

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()

        # Decide which team secures the tower (biased by win_probability)
        p_team1 = self.team1.state.win_probability
        acting_team = self.team1 if random.random() < p_team1 else self.team2
        target_team = self.team2 if acting_team is self.team1 else self.team1

        # Destroy a tower on the target side: prioritize lane towers, then base
        destroyed = False
        destroyed_lane = None
        for lane in ["top", "mid", "bot"]:
            count = getattr(target_team.state.towers, lane)
            if count > 0:
                setattr(target_team.state.towers, lane, count - 1)
                destroyed = True
                destroyed_lane = lane
                break
        if not destroyed and target_team.state.towers.base > 0:
            target_team.state.towers.base -= 1
            destroyed = True
            destroyed_lane = "base"

        # Track first tower and totals
        if destroyed:
            if not state.first_tower:
                state.first_tower = True
                acting_team.state.first_tower = True
            if acting_team is self.team1:
                state.team1_towers_taken += 1
            else:
                state.team2_towers_taken += 1
            lane_txt = (
                f" {destroyed_lane}"
                if destroyed_lane and destroyed_lane != "base"
                else ""
            )
            self.commentary.append(
                f"{acting_team.team.name} destroyed a{lane_txt} tower."
            )

        # Advance clock
        state.time += self.duration

        # Chance to trigger a follow-up fight after tower
        if random.random() < 0.25:
            self.follow_up = (MobaEventType.FIGHT_EVENT, None)

        return state
