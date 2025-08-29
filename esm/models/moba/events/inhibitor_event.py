import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase, MobaEventType

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaInhibitorEvent(MobaEventBase):
    def get_duration(self) -> int:
        # Taking an exposed inhibitor takes a bit
        return random.randint(30, 75)

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()

        # Choose team that takes inhibitor
        p_team1 = self.team1.state.win_probability
        acting_team = self.team1 if random.random() < p_team1 else self.team2
        target_team = self.team2 if acting_team is self.team1 else self.team1

        # Only possible if a lane is exposed: lane towers down for that lane
        taken = False
        taken_lane = None
        for lane in ["top", "mid", "bot"]:
            lane_towers = getattr(target_team.state.towers, lane)
            lane_inhib = getattr(target_team.state.inhibitors, lane)
            if lane_towers == 0 and lane_inhib > 0:
                setattr(target_team.state.inhibitors, lane, lane_inhib - 1)
                taken = True
                taken_lane = lane
                break

        if taken:
            if acting_team is self.team1:
                state.team1_inhibitors_taken += 1
            else:
                state.team2_inhibitors_taken += 1
            if taken_lane:
                self.commentary.append(
                    f"{acting_team.team.name} destroyed the {taken_lane} inhibitor!"
                )

        # Nexus exposure flags on the side that lost inhibitor
        def update_exposure(team_idx: int, team):
            exposed = team.state.towers.base == 0 and (
                team.state.inhibitors.top == 0
                or team.state.inhibitors.mid == 0
                or team.state.inhibitors.bot == 0
            )
            if team_idx == 1:
                state.team1_nexus_exposed = exposed
            else:
                state.team2_nexus_exposed = exposed

        update_exposure(1, self.team1)
        update_exposure(2, self.team2)

        # Advance time
        state.time += self.duration

        # Optional follow-up fight
        if random.random() < 0.25:
            self.follow_up = (MobaEventType.FIGHT_EVENT, None)

        return state
