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

from src.core.esports.moba.match_live import MatchLive


class MatchTester:
    """
    MatchTester receives a match and tests it to print statistics of the match results
    """

    def __init__(self, amount_test: int, match: MatchLive):
        self.amount_test = amount_test
        self.match = match
        self.amount_team_kills = [[], []]
        self.amount_team_deaths = [[], []]
        self.amount_team_assists = [[], []]
        self.avg_team_kills = [0, 0]
        self.avg_team_deaths = [0, 0]
        self.avg_team_assists = [0, 0]
        self.match.simulate = False
        self.match.show_commentary = False

    def _get_team_stats(self, i):
        team = self.match.match.teams[i]
        self.amount_team_kills[i].append(team.kills)
        self.amount_team_deaths[i].append(team.deaths)
        self.amount_team_assists[i].append(team.assists)

        self.avg_team_kills[i] += team.kills
        self.avg_team_deaths[i] += team.deaths
        self.avg_team_assists[i] += team.assists

    def get_avg(self, avg):
        for i, value in enumerate(avg):
            avg[i] = value / self.amount_test

    def get_team_stats(self):
        for i in range(2):
            self._get_team_stats(i)

    def run_match_test(self):
        for _ in range(self.amount_test):
            self.match.simulation()
            self.get_team_stats()
            self.match.reset_match()

        self.get_avg(self.avg_team_kills)
        self.get_avg(self.avg_team_deaths)
        self.get_avg(self.avg_team_assists)

        print(self.amount_team_kills)
        print(self.amount_team_deaths)
        print(self.amount_team_assists)
        print(self.avg_team_kills)
        print(self.avg_team_deaths)
        print(self.avg_team_assists)


if __name__ == '__main__':
    from src.core.core import Core

    core = Core()
    core.check_files()
    core.get_champions()
    core.get_players()
    core.get_teams()
    core.initialize_random_debug_match()
    core.match_simulation.picks_and_bans()
    match_tester = MatchTester(500, core.match_simulation)
    match_tester.run_match_test()
