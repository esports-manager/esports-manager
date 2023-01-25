#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2023  Pedrenrique G. Guimarães
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
import logging
import random
from queue import Queue
from typing import Union

from esm.core.esports.moba.team import Team
from .general import MobaEvent, EventCreator

logger = logging.getLogger(__name__)


class NexusEventEventCreator(EventCreator):
    def factory_method(
            self,
            event_chosen: dict,
            game_time: float,
            show_commentary: bool,
            queue: Queue
    ):
        return NexusEvent(
            event_name=event_chosen["name"],
            priority=event_chosen["priority"],
            points=event_chosen["points"],
            event_time=game_time,
            show_commentary=show_commentary,
            queue=queue
        )


class NexusEvent(MobaEvent):
    def calculate_event(self, team1: Team, team2: Team, which_nexus: Union[Team, None]):
        if which_nexus is not None:
            if which_nexus == team1:
                atk_team = team2
                def_team = team1
            elif which_nexus == team2:
                atk_team = team1
                def_team = team2
            else:
                # gets which team is more likely to attack due to the skill lvl
                atk_team, def_team = self._get_probable_team(team1, team2)

            prevailing = random.choices(
                [atk_team, def_team], [atk_team.total_skill, def_team.total_skill]
            )[0]

            if prevailing == atk_team:
                def_team.nexus = 0
                self.get_commentary(atk_team_name=prevailing.name)
