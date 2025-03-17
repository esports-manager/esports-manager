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
from esm.core.esports.moba.simulation.moba_event_type import (
    MobaEventOutcome,
    MobaEventType,
)
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


def test_moba_event_tower_assault_get_towers(moba_match_sim: MobaSimMatch):
    team1 = moba_match_sim.team1
    team2 = moba_match_sim.team2
    event = MobaEventTowerAssault(team1, team2, 0.0, 0.0)
    towers = event.get_towers()
    assert len(towers) == 6


def test_moba_event_tower_assault_get_attacking_team(moba_match_sim: MobaSimMatch):
    team1 = moba_match_sim.team1
    team2 = moba_match_sim.team2
    event = MobaEventTowerAssault(team1, team2, 0.0, 0.0)
    team = event.get_attacking_team()
    assert isinstance(team, MobaTeamSimulation)


def test_moba_event_tower_assault_get_outcome(moba_match_sim: MobaSimMatch):
    team1 = moba_match_sim.team1
    team2 = moba_match_sim.team2
    event = MobaEventTowerAssault(team1, team2, 0.0, 0.0)
    team = event.get_attacking_team()
    outcome = event.get_outcome(team)
    assert outcome in [MobaEventOutcome.DEFEND_TOWER, MobaEventOutcome.TAKE_TOWER]


def test_moba_event_tower_assault_get_tower(moba_match_sim: MobaSimMatch):
    team1 = moba_match_sim.team1
    team2 = moba_match_sim.team2
    event = MobaEventTowerAssault(team1, team2, 0.0, 0.0)
    attacking_team = event.get_attacking_team()
    tower = event.get_tower(attacking_team, event.get_towers())
    assert tower is not None
    assert tower != ""


def test_moba_event_tower_assault(moba_match_sim: MobaSimMatch):
    team1 = moba_match_sim.team1
    team2 = moba_match_sim.team2
    event = MobaEventTowerAssault(team1, team2, 0.0, 0.0)

    state = MobaSimState()
    event.calculate_event(state)
    assert event.outcome in [MobaEventOutcome.DEFEND_TOWER, MobaEventOutcome.TAKE_TOWER]


def test_moba_event_jungle_grubs(moba_match_sim: MobaSimMatch):
    team1 = moba_match_sim.team1
    team2 = moba_match_sim.team2
    event = MobaEventJungle(MobaEventType.JUNGLE_GRUBS, team1, team2, 0.0, 0.0)

    state = MobaSimState()
    state.void_grubs.alive = True
    assert state.void_grubs.alive is True
    event.calculate_event(state)
    assert event.outcome in [MobaEventOutcome.TAKE_GRUBS, MobaEventOutcome.STEAL_GRUBS]
    assert state.void_grubs.alive is False
    assert state.void_grubs.respawn_timer > 0


def test_moba_event_jungle_herald():
    pass
