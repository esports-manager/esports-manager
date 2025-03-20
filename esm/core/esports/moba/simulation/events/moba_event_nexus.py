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

from ...mobateam import MobaTeam, MobaTeamSimulation
from ..moba_event_base import MobaEvent, MobaEventPriority
from ..moba_event_type import MobaEventOutcome, MobaEventType


class MobaEventNexusAssaultError(Exception):
    pass


class MobaEventNexusAssault(MobaEvent):
    def __init__(
        self,
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
        event_time: float,
        points: float,
    ):
        super().__init__(
            MobaEventType.NEXUS_ASSAULT,
            team1,
            team2,
            MobaEventPriority.LOW,
            event_time,
            points,
        )

    def get_defending_team(self) -> MobaTeamSimulation:
        teams = []
        if self.team1.is_nexus_exposed():
            teams.append(self.team1)

        if self.team2.is_nexus_exposed():
            teams.append(self.team2)

        if len(teams) == 1:
            return teams[0]

        probabilities = [team.get_team_overall() for team in teams]

        return random.choices(teams, probabilities, k=1)[0]

    def get_outcome(
        self, attacking_team: MobaTeamSimulation, defending_team: MobaTeamSimulation
    ) -> MobaEventOutcome:
        attacking_team_attributes = sum(
            (
                player.player.attributes.mechanics.positioning
                + player.player.attributes.communication.shot_calling
                + player.player.attributes.communication.decisioning
                + player.player.attributes.communication.team_work
            )
            for player in attacking_team.players
        )

        defending_team_attributes = sum(
            (
                player.player.attributes.mechanics.positioning
                + player.player.attributes.communication.shot_calling
                + player.player.attributes.communication.decisioning
                + player.player.attributes.communication.team_work
            )
            for player in defending_team.players
        )

        team = random.choices(
            [attacking_team, defending_team],
            [attacking_team_attributes, defending_team_attributes],
        )[0]

        if team == attacking_team:
            return MobaEventOutcome.TAKE_NEXUS
        else:
            return MobaEventOutcome.DEFEND_NEXUS

    def calculate_event(self, sim_state: MobaSimState):
        if not self.team1.nexus or not self.team2.nexus:
            raise MobaEventNexusAssaultError(
                "Game is over, should not be generating events"
            )

        defending_team = self.get_defending_team()
        attacking_team = self.team1 if defending_team == self.team2 else self.team2

        if not defending_team.is_nexus_exposed():
            raise MobaEventNexusAssaultError(
                "If nexus is not exposed, you cannot take the nexus"
            )

        self.outcome = self.get_outcome(attacking_team, defending_team)

        if self.outcome == MobaEventOutcome.TAKE_NEXUS:
            defending_team.nexus = False
