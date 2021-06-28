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

from esm.core.esports.moba.match_live import MatchLive


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
        self.amount_team_wins = [0, 0]
        self.avg_team_kills = [0, 0]
        self.avg_team_deaths = [0, 0]
        self.avg_team_assists = [0, 0]
        self.match.simulate = False
        self.match.show_commentary = False
        self.running_test = False

    def reset_values(self):
        self.amount_team_kills = [[], []]
        self.amount_team_deaths = [[], []]
        self.amount_team_assists = [[], []]
        self.amount_team_wins = [0, 0]
        self.avg_team_kills = [0, 0]
        self.avg_team_deaths = [0, 0]
        self.avg_team_assists = [0, 0]
        self.match.simulate = False
        self.match.show_commentary = False
        self.running_test = False

    def _get_team_stats(self, i):
        team = self.match.match.teams[i]
        self.amount_team_kills[i].append(team.kills)
        self.amount_team_deaths[i].append(team.deaths)
        self.amount_team_assists[i].append(team.assists)

        self.avg_team_kills[i] += team.kills
        self.avg_team_deaths[i] += team.deaths
        self.avg_team_assists[i] += team.assists

    def _get_amount_wins(self):
        if self.match.victorious_team == self.match.match.team1:
            self.amount_team_wins[0] += 1
        else:
            self.amount_team_wins[1] += 1

    def get_avg(self, avg):
        for i, value in enumerate(avg):
            avg[i] = value / self.amount_test

    def get_team_stats(self):
        for i in range(2):
            self._get_team_stats(i)
        self._get_amount_wins()

    def run_match_test(self):
        i = 0
        print('Starting tests!')
        while self.running_test and i <= self.amount_test:
            self.match.simulation()
            self.get_team_stats()
            self.match.reset_match()
            i += 1

        self.get_avg(self.avg_team_kills)
        self.get_avg(self.avg_team_deaths)
        self.get_avg(self.avg_team_assists)

        print(self.avg_team_kills)
        print(self.avg_team_deaths)
        print(self.avg_team_assists)
        print(self.amount_team_wins)
        print(self.match.match.team1.name, 'won', self.amount_team_wins[0], 'times')
        percentage = (self.amount_team_wins[0] / self.amount_test) * 100
        print('Won about ', percentage, '% of the games')
        self.running_test = False


if __name__ == '__main__':
    from esm.core.core import Core

    core = Core()
    core.check_files()
    core.get_champions()
    core.get_players()
    core.get_teams()
    core.initialize_random_debug_match()
    core.match_live.picks_and_bans()
    match_tester = MatchTester(500, core.match_live)
    match_tester.run_match_test()
