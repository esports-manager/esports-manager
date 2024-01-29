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
from queue import Queue
from typing import Union

from esm.core.esports.moba.team import TeamSimulation

from .general import EventCreator, MobaEvent

logger = logging.getLogger(__name__)


class TowerEventEventCreator(EventCreator):
    def factory_method(
        self, event_chosen: dict, game_time: float, show_commentary: bool, queue: Queue
    ):
        return TowerEvent(
            event_name=event_chosen["name"],
            priority=event_chosen["priority"],
            points=event_chosen["points"],
            event_time=game_time,
            show_commentary=show_commentary,
            queue=queue,
        )


class TowerEvent(MobaEvent):
    def _get_tower_attributes(self, team1: TeamSimulation, team2: TeamSimulation):
        """
        Checks which towers are up, and if they can be attacked. If it is a Base tower,
        there is a higher chance to focus on it
        """
        if team1.are_all_towers_down():
            attack_team = team1
            def_team = team2
        elif team2.are_all_towers_down():
            attack_team = team2
            def_team = team1
        else:
            attack_team, def_team = self._get_probable_team(team1, team2)

        lanes = [lanes for lanes, value in def_team.towers.items() if value != 0]

        # You cannot attack a base tower unless it is exposed
        if not def_team.are_base_towers_exposed():
            lanes.remove("base")

        if lanes:
            probs = []
            for lane, value in def_team.towers.items():
                if lane in lanes:
                    if value == 1:
                        probs.append(0.5)
                    elif value == 2:
                        probs.append(0.3)
                    else:
                        probs.append(0.2)

            chosen_lane = random.choices(lanes, weights=probs)[0]
        else:
            chosen_lane = None

        return attack_team, def_team, chosen_lane

    def _destroy_tower(self, prevailing, attack_team, def_team, lane):
        # Decides the player that destroys the tower
        skills = [player.get_player_total_skill() for player in prevailing.roster]
        player = random.choices(attack_team.roster, skills)[0]

        # player gets full points for destroying the tower
        player.points += self.points

        # Other players are awarded points as well, but reduced number of points
        for other_player in prevailing.roster:
            if other_player != player:
                other_player.points += self.points / 4

        def_team.towers[lane] -= 1
        self.get_commentary(atk_team_name=prevailing.name, lane=lane)

        logger.debug("Team {0} destroyed the {1} tower".format(prevailing.name, lane))

    def calculate_event(
        self,
        team1: TeamSimulation,
        team2: TeamSimulation,
        which_nexus: Union[TeamSimulation, None],
    ):
        """
        This method calculates the tower assault outcome
        """
        attack_team, def_team, lane = self._get_tower_attributes(team1, team2)

        if lane is not None:
            # Chooses which team prevails over the tower assault
            prevailing = random.choices(
                [attack_team, def_team], [attack_team.win_prob, def_team.win_prob]
            )[0]
            # If the prevailing team destroys the tower
            if prevailing == attack_team:
                self._destroy_tower(prevailing, attack_team, def_team, lane)

            else:
                self.get_commentary(
                    def_team_name=def_team.name, defended=True, lane=lane
                )

                for player in def_team.list_players:
                    player.points += self.points / 5
        else:
            self.event_name = "NOTHING"

        logger.debug("Calculate tower method done!")
