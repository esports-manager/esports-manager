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
import time

from src.core.esports.moba.match import Match


class MatchTester:
    """
    MatchTester receives a match and tests it to print statistics of the match results
    """

    def __init__(self, amount_test: int, match: Match):
        self.amount_test = amount_test
        self.match = match
        self.amount_team_kills = [0, 0]
        self.amount_team_deaths = [0, 0]
        self.amount_team_assists = [0, 0]
        self.avg_team_kills = [0, 0]
        self.avg_team_deaths = [0, 0]
        self.avg_team_assists = [0, 0]

    def get_team_stats(self):
        for team, stat in zip(self.match.match.teams, self.amount_team_kills):
            stat = team.kills

        for team, stat in zip(self.match.match.teams, self.amount_team_deaths):
            stat = team.deaths

        for team, stat in zip(self.match.match.teams, self.amount_team_assists):
            stat = team.assists

    def run_match_test(self):
        for i in range(self.amount_test):
            self.match.simulation()
