import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase
from esm.models.moba.events.event_types import MobaEventType
from esm.services.narration import narrate_inhibitor

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaInhibitorEvent(MobaEventBase):
    def get_duration(self) -> int:
        # Taking an exposed inhibitor takes a bit
        return random.randint(30, 75)

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()

        team1_exposed_inhibitors = self.team1.get_exposed_inhibitors()
        team2_exposed_inhibitors = self.team2.get_exposed_inhibitors()

        if (team1_exposed_inhibitors) == 0 and len(team2_exposed_inhibitors) == 0:
            raise ValueError("No exposed inhibitors")

        elif len(team1_exposed_inhibitors) == 0:
            acting_team = self.team1
        elif len(team2_exposed_inhibitors) == 0:
            acting_team = self.team2
        else:
            acting_team = random.choices(
                [self.team1, self.team2],
                [self.team1.state.win_probability, self.team2.state.win_probability],
            )[0]

        defending_team = self.team1 if acting_team is self.team2 else self.team2

        taken = random.random() < acting_team.state.win_probability
        if taken:
            inhibitor = random.choice(defending_team.get_exposed_inhibitors())
            defending_team.take_inhibitor(inhibitor)
            text, severity = narrate_inhibitor(acting_team, inhibitor)
            self.commentary.append(text)
        else:
            self.commentary.append(
                f"{defending_team.team.name} defends their inhibitor!"
            )

        state.time += self.duration

        if random.random() < 0.25:
            self.follow_up = (MobaEventType.FIGHT_EVENT, None)

        return state
