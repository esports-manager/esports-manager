#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
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

from esm.core.esports.moba.match import Match


class Championship:
    def __init__(self, name: str, championship_id: int, country: str, teams: list):
        self.name = name
        self.championship_id = championship_id
        self.country = country
        self.teams = teams
        self.matches = []

    def schedule_matches(self):
        """
        Very naive implementation of match scheduling. This will make teams face off twice
        in the championship. This should work for now.
        """
        for team in self.teams:
            opp_teams = self.teams.copy()
            opp_teams.remove(team)
            random.shuffle(opp_teams)
            for opp_team in opp_teams:
                self.matches.append(Match(self.championship_id, team, opp_team))
                opp_teams.remove(opp_team)

            random.shuffle(self.matches)

    def __repr__(self):
        return "{0}".format(self.__class__.__name__)

    def __str__(self):
        return "{0}".format(self.__class__.__name__)
