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


class MobaEventJungle(MobaEvent):
    def __init__(
        self,
        event_type: MobaEventType,
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
        event_time: float,
        points: float,
    ):
        super().__init__(
            event_type,
            team1,
            team2,
            MobaEventPriority.LOW,
            event_time,
            points,
        )

    def get_attacking_team(self) -> MobaTeamSimulation:
        team1_overall = self.team1.get_team_overall()
        team2_overall = self.team2.get_team_overall()

        return random.choices(
            [self.team1, self.team2], [team1_overall, team2_overall], k=1
        )[0]

    def get_outcome(self, attacking_team: MobaTeamSimulation) -> MobaEventOutcome:
        team1_attributes = 0
        team2_attributes = 0

        for player in self.team1.players:
            team1_attributes += (
                player.player.attributes.utility.map_control
                + player.player.attributes.utility.vision_control
                + player.player.attributes.utility.objective_control
                + player.player.attributes.knowledge.map_awareness
                + player.player.attributes.communication.team_work
                + player.player.attributes.communication.decisioning
                + player.player.attributes.communication.shot_calling
                + player.player.attributes.knowledge.timing
            )

        for player in self.team2.players:
            team2_attributes = (
                player.player.attributes.utility.map_control
                + player.player.attributes.utility.vision_control
                + player.player.attributes.utility.objective_control
                + player.player.attributes.knowledge.map_awareness
                + player.player.attributes.communication.team_work
                + player.player.attributes.communication.decisioning
                + player.player.attributes.communication.shot_calling
                + player.player.attributes.knowledge.timing
            )

        team = random.choices(
            [self.team1, self.team2], [team1_attributes, team2_attributes], k=1
        )[0]

        if team == attacking_team:
            if self.event_type == MobaEventType.JUNGLE_GRUBS:
                return MobaEventOutcome.TAKE_GRUBS
        else:
            if self.event_type == MobaEventType.JUNGLE_GRUBS:
                return MobaEventOutcome.STEAL_GRUBS

        return MobaEventOutcome.NOTHING

    def calculate_event(self, sim_state: MobaSimState):
        attacking_team = self.get_attacking_team()
        self.outcome = self.get_outcome(attacking_team)
        defending_team = self.team1 if attacking_team == self.team2 else self.team2

        if self.outcome == MobaEventOutcome.TAKE_GRUBS:
            attacking_team.stats.grubs += 3
            sim_state.take_void_grubs()
            for player in attacking_team.players:
                player.points += self.points
        elif self.outcome == MobaEventOutcome.STEAL_GRUBS:
            defending_team.stats.grubs += 3
            sim_state.take_void_grubs()
            for player in defending_team.players:
                player.points += self.points
