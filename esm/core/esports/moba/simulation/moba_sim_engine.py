#  eSports Manager - free and open source eSports Management game
#  Copyright (C) 2020-2024  Pedrenrique G. Guimarães
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import random

from ..mobateam import MobaTeamSimulation
from .events import MobaEventFactory
from .moba_event_def import MOBA_EVENT_DEF
from .moba_event_type import MobaEventOutcome, MobaEventType
from .moba_sim_state import MobaSimState


class MobaSimEngine:
    def __init__(self, team1: MobaTeamSimulation, team2: MobaTeamSimulation):
        self.team1 = team1
        self.team2 = team2
        self.event_history = []
        self.event_factory = MobaEventFactory()
        self.sim_state = MobaSimState()

    def get_events(self) -> list[MobaEventType]:
        events = [MobaEventType.NOTHING, MobaEventType.FIGHT]

        if ev := self.sim_state.get_event_types():
            events.extend(ev)

        if (
            self.team1.get_exposed_towers() or self.team2.get_exposed_towers()
        ) and self.sim_state.match_time >= MOBA_EVENT_DEF[MobaEventType.TOWER_ASSAULT][
            "start_time"
        ]:
            events.append(MobaEventType.TOWER_ASSAULT)

        if self.team1.get_exposed_inhibs() or self.team2.get_exposed_inhibs():
            events.append(MobaEventType.INHIB_ASSAULT)

        if self.team1.is_nexus_exposed() or self.team2.is_nexus_exposed():
            events.append(MobaEventType.NEXUS_ASSAULT)

        return events

    def get_event_probability(self, events: list[MobaEventType]) -> list[int]:
        return [MOBA_EVENT_DEF[event]["probability"] for event in events]

    def run(self):
        events = self.get_events()
        probabilities = self.get_event_probability(events)
        event_type = random.choices(events, probabilities, k=1)[0]
        event = self.event_factory.create_event(
            event_type, self.team1, self.team2, self.sim_state.match_time
        )
        event.calculate_event(self.sim_state)
