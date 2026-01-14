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

        team1_towers = self.team1.towers_remaining
        team2_towers = self.team2.towers_remaining

        if team1_towers == 0 and team2_towers == 0:
            raise ValueError("No towers remaining")
        elif team1_towers == 0:
            acting_team = self.team2
        elif team2_towers == 0:
            acting_team = self.team1
        else:
            acting_team = random.choices(
                [self.team1, self.team2],
                [self.team1.state.win_probability, self.team2.state.win_probability],
            )[0]

        defending_team = self.team1 if acting_team is self.team2 else self.team2

        taken = random.random() < acting_team.state.win_probability
        if taken:
            tower = random.choice(defending_team.get_remaining_towers())
            defending_team.take_tower(tower)
            self.commentary.append(f"{acting_team.team.name} took {tower} tower!")
        else:
            self.commentary.append(
                f"{defending_team.team.name} is defending {defending_team.get_remaining_towers()} tower!"
            )

        # Advance clock
        state.time += self.duration

        # Chance to trigger a follow-up fight after tower
        if random.random() < 0.25:
            self.follow_up = (MobaEventType.FIGHT_EVENT, None)

        return state
