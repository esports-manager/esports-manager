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

from esm.core.esports.moba.simulation.moba_event_base import MobaEventOutcome
from esm.core.esports.moba.simulation.moba_sim_state import MobaSimState

from ...mobateam import MobaTeamSimulation
from ..moba_event_base import MobaEvent, MobaEventPriority, MobaEventType


class MobaEventNothing(MobaEvent):
    def __init__(
        self,
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
        event_time: float,
    ):
        super().__init__(
            MobaEventType.NOTHING, team1, team2, MobaEventPriority.LOW, event_time, 0.0
        )

    def calculate_event(self, sim_state: MobaSimState):
        self.outcome = MobaEventOutcome.NOTHING
        self.event_time = random.randint(30, 60)
