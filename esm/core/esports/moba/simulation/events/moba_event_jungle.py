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


class MobaEventJungleError(Exception):
    pass


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
        team1_attributes = sum(
            (
                player.player.attributes.utility.map_control
                + player.player.attributes.utility.vision_control
                + player.player.attributes.utility.objective_control
                + player.player.attributes.knowledge.map_awareness
                + player.player.attributes.communication.team_work
                + player.player.attributes.communication.decisioning
                + player.player.attributes.communication.shot_calling
                + player.player.attributes.knowledge.timing
            )
            for player in self.team1.players
        )
        team2_attributes = sum(
            (
                player.player.attributes.utility.map_control
                + player.player.attributes.utility.vision_control
                + player.player.attributes.utility.objective_control
                + player.player.attributes.knowledge.map_awareness
                + player.player.attributes.communication.team_work
                + player.player.attributes.communication.decisioning
                + player.player.attributes.communication.shot_calling
                + player.player.attributes.knowledge.timing
            )
            for player in self.team2.players
        )

        team = random.choices(
            [self.team1, self.team2], [team1_attributes, team2_attributes], k=1
        )[0]

        if team == attacking_team:
            if self.event_type == MobaEventType.JUNGLE_GRUBS:
                return MobaEventOutcome.TAKE_GRUBS
            elif self.event_type == MobaEventType.JUNGLE_HERALD:
                return MobaEventOutcome.TAKE_HERALD
            elif self.event_type == MobaEventType.JUNGLE_DRAKE:
                return MobaEventOutcome.TAKE_DRAKE
            elif self.event_type == MobaEventType.JUNGLE_BARON:
                return MobaEventOutcome.TAKE_BARON
        else:
            if self.event_type == MobaEventType.JUNGLE_GRUBS:
                return MobaEventOutcome.STEAL_GRUBS
            elif self.event_type == MobaEventType.JUNGLE_HERALD:
                return MobaEventOutcome.STEAL_HERALD
            elif self.event_type == MobaEventType.JUNGLE_DRAKE:
                return MobaEventOutcome.STEAL_DRAKE
            elif self.event_type == MobaEventType.JUNGLE_BARON:
                return MobaEventOutcome.STEAL_BARON

        return MobaEventOutcome.NOTHING

    def is_elder_drake(self) -> bool:
        return self.team1.stats.dragons == 4 or self.team2.stats.dragons == 4

    def award_points(self, team: MobaTeamSimulation):
        if self.is_elder_drake():
            self.points += 10

        for player in team.players:
            player.points += self.points

    def check_state(self, sim_state: MobaSimState):
        if self.event_type == MobaEventType.JUNGLE_GRUBS:
            if not sim_state.void_grubs.alive:
                raise MobaEventJungleError("Void Grubs cannot be generated")
        elif self.event_type == MobaEventType.JUNGLE_HERALD:
            if not sim_state.herald.alive:
                raise MobaEventJungleError("Herald cannot be generated")
        elif self.event_type == MobaEventType.JUNGLE_DRAKE:
            if not sim_state.dragon.alive:
                raise MobaEventJungleError("Drake cannot be generated")
        elif self.event_type == MobaEventType.JUNGLE_BARON:
            if not sim_state.baron.alive:
                raise MobaEventJungleError("Baron cannot be generated")

    def calculate_event(self, sim_state: MobaSimState):
        self.check_state(sim_state)
        attacking_team = self.get_attacking_team()
        self.outcome = self.get_outcome(attacking_team)
        defending_team = self.team1 if attacking_team == self.team2 else self.team2

        if self.outcome == MobaEventOutcome.TAKE_GRUBS:
            attacking_team.stats.grubs += 3
            sim_state.take_void_grubs()
            self.award_points(attacking_team)
        elif self.outcome == MobaEventOutcome.STEAL_GRUBS:
            defending_team.stats.grubs += 3
            sim_state.take_void_grubs()
            self.award_points(defending_team)
        elif self.outcome == MobaEventOutcome.TAKE_HERALD:
            sim_state.take_herald()
            self.award_points(attacking_team)
        elif self.outcome == MobaEventOutcome.STEAL_HERALD:
            sim_state.take_herald()
            self.award_points(defending_team)
        elif self.outcome == MobaEventOutcome.TAKE_DRAKE:
            sim_state.take_drake()
            if not self.is_elder_drake():
                attacking_team.stats.dragons += 1
            self.award_points(attacking_team)
        elif self.outcome == MobaEventOutcome.STEAL_DRAKE:
            sim_state.take_drake()
            if not self.is_elder_drake():
                defending_team.stats.dragons += 1
            self.award_points(defending_team)
        elif self.outcome == MobaEventOutcome.TAKE_BARON:
            sim_state.take_baron()
            self.award_points(attacking_team)
        elif self.outcome == MobaEventOutcome.STEAL_BARON:
            sim_state.take_baron()
            self.award_points(defending_team)
