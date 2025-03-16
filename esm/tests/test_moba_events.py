#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
import pytest

from esm.core.esports.moba.champion import Champion
from esm.core.esports.moba.mobateam import MobaPlayerSimulation, MobaTeamSimulation
from esm.core.esports.moba.simulation import moba_sim_match
from esm.core.esports.moba.simulation.events import (
    MobaEvent,
    MobaEventFactory,
    MobaEventFight,
    MobaEventInhibAssault,
    MobaEventJungle,
    MobaEventNexusAssault,
    MobaEventNothing,
    MobaEventTowerAssault,
)
from esm.core.esports.moba.simulation.moba_event_type import MobaEventOutcome
from esm.core.esports.moba.simulation.moba_sim_engine import MobaSimEngine
from esm.core.esports.moba.simulation.moba_sim_match import MobaMatch, MobaSimMatch
from esm.core.esports.moba.simulation.moba_sim_state import MobaSimState
from esm.core.esports.moba.simulation.picksbans import PicksBans


@pytest.fixture
def moba_match_sim(
    moba_match_simulation: MobaSimMatch, mock_champions: list[Champion]
) -> MobaSimMatch:
    team1 = moba_match_simulation.team1
    team2 = moba_match_simulation.team2
    pickbans = PicksBans(mock_champions, team1, team2)
    pickbans.run()
    return moba_match_simulation


def test_moba_event_nothing(moba_match_sim: MobaSimMatch):
    team1 = moba_match_sim.team1
    team2 = moba_match_sim.team2

    event = MobaEventNothing(team1, team2, 0.0)
    state = MobaSimState()
    event.calculate_event(state)
    assert event.outcome == MobaEventOutcome.NOTHING
