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

from esm.core.esports.moba.simulation.moba_sim_state import MobaSimState

from ...mobateam import MobaTeamSimulation
from ..moba_event_base import MobaEvent, MobaEventPriority
from ..moba_event_type import MobaEventOutcome, MobaEventType


class MobaEventTowerAssault(MobaEvent):
    def __init__(
        self,
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
        event_time: float,
        points: float,
    ):
        super().__init__(
            MobaEventType.TOWER_ASSAULT,
            team1,
            team2,
            MobaEventPriority.LOW,
            event_time,
            points,
        )

    def get_towers(self) -> list[str]:
        towers = []
        team1_towers = [f"team1_{tower}" for tower in self.team1.get_exposed_towers()]
        team2_towers = [f"team2_{tower}" for tower in self.team2.get_exposed_towers()]
        towers.extend(team1_towers)
        towers.extend(team2_towers)
        return towers

    def get_outcome(self, attacking_team: MobaTeamSimulation) -> MobaEventOutcome:
        team1_attributes = 0
        team2_attributes = 0

        for player in self.team1.players:
            team1_attributes += (
                player.player.attributes.utility.map_control
                + player.player.attributes.offensive.lane_pressure
                + player.player.attributes.knowledge.map_awareness
                + player.player.attributes.communication.team_work
                + player.player.attributes.communication.decisioning
            )

        for player in self.team2.players:
            team2_attributes += (
                player.player.attributes.utility.map_control
                + player.player.attributes.offensive.lane_pressure
                + player.player.attributes.knowledge.map_awareness
                + player.player.attributes.communication.team_work
                + player.player.attributes.communication.decisioning
            )

        team = random.choices(
            [self.team1, self.team2], [team1_attributes, team2_attributes], k=1
        )[0]

        if team == attacking_team:
            return MobaEventOutcome.TAKE_TOWER
        else:
            return MobaEventOutcome.DEFEND_TOWER

    def get_attacking_team(self) -> MobaTeamSimulation:
        if not self.team1.get_exposed_towers():
            return self.team2
        if not self.team2.get_exposed_towers():
            return self.team1

        team1_overall = self.team1.get_team_overall()
        team2_overall = self.team2.get_team_overall()

        team = random.choices(
            [self.team1, self.team2], [team1_overall, team2_overall], k=1
        )[0]
        return team

    def get_tower(self, attacking_team, towers) -> str:
        twers = []
        if attacking_team == self.team1:
            for tower in towers:
                if "team2" in tower:
                    twers.append(tower)
        else:
            for tower in towers:
                if "team1" in tower:
                    twers.append(tower)

        return random.choice(twers)

    def calculate_event(self, sim_state: MobaSimState):
        towers = self.get_towers()
        attacking_team = self.get_attacking_team()
        self.outcome = self.get_outcome(attacking_team)
        tower = self.get_tower(attacking_team, towers)

        defending_team = self.team1 if attacking_team == self.team2 else self.team2

        if self.outcome == MobaEventOutcome.TAKE_TOWER:
            defending_team.remove_tower(tower)
            for player in attacking_team.players:
                player.points += self.points
