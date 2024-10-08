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
from datetime import timedelta
from typing import Optional

from ..mobateam import MobaTeamSimulation
from .events import MobaEventFactory
from .moba_event_type import MobaEventOutcome


class MobaSimEngine:
    def __init__(self, team1: MobaTeamSimulation, team2: MobaTeamSimulation):
        self.team1 = team1
        self.team2 = team2
        self.events = []
        self.event_history = []
        self.event_factory = MobaEventFactory()
        self.match_time: timedelta = timedelta(0)

    def get_events(self, outcome: Optional[MobaEventOutcome]):
        self.events.clear()

        if outcome:
            self.event_factory.get_event_from_outcome(
                self.team1, self.team2, self.match_time, outcome
            )

    def run(self):
        outcome = None
        if self.event_history:
            outcome = self.event_history[-1].outcome

        self.get_events(outcome)
