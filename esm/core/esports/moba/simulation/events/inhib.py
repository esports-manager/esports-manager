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
import logging
import random
from typing import Union

from esm.core.esports.moba.mobateam import MobaTeamSimulation

from .general import MobaEvent

logger = logging.getLogger(__name__)


class InhibEvent(MobaEvent):
    def calculate_event(
        self,
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
        which_nexus: Union[MobaTeamSimulation, None],
    ):
        if team1.get_exposed_inhibs():
            attack_team = team2
            def_team = team1
        elif team2.get_exposed_inhibs():
            attack_team = team1
            def_team = team2
        else:
            attack_team, def_team = self._get_probable_team(team1, team2)

        exposed = random.choice(def_team.get_exposed_inhibs())

        prevailing = random.choices(
            [attack_team, def_team], [attack_team.win_prob, def_team.win_prob]
        )[0]

        for player in prevailing.roster:
            player.points += self.points / 5

        if prevailing == attack_team:
            def_team.inhibitors[exposed] -= 1
            self.get_commentary(atk_team_name=prevailing.name, lane=exposed)
        else:
            self.get_commentary(
                def_team_name=prevailing.name, defended=True, lane=exposed
            )

        logger.debug("Inhib event calculated")
