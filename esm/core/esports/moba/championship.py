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
import random
import uuid

from esm.core.esports.moba.mobamatch import MobaMatch
from esm.core.esports.moba.simulation.match_live import MatchLive


class Championship:
    def __init__(
        self, name: str, championship_id: uuid.UUID, country: str, teams: list
    ):
        self.name = name
        self.championship_id = championship_id
        self.country = country
        self.teams = teams
        self.matches = []
        self.points_per_win = 3

    def schedule_matches(self):
        """
        Very naive implementation of match scheduling. This will make teams face off twice
        in the championship. This should work for now.
        """
        self.matches.clear()
        for team in self.teams:
            opp_teams = self.teams.copy()
            opp_teams.remove(team)
            random.shuffle(opp_teams)
            for opp_team in opp_teams:
                self.matches.append(
                    MatchLive(
                        MobaMatch(uuid.uuid4(), self.championship_id, team, opp_team),
                        show_commentary=False,
                        simulation_delay=False,
                    )
                )

        random.shuffle(self.matches)

    def reset_championship(self):
        for match in self.matches:
            match.reset_match()

    def count_matches_per_team(self):
        matches_per_team = []

        for team in self.teams:
            count = sum(team in match.game.teams for match in self.matches)
            matches_per_team.append([team, count])

        return matches_per_team

    def __repr__(self):
        return "{0}".format(self.__class__.__name__)

    def __str__(self):
        return "{0}".format(self.__class__.__name__)
