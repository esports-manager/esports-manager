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

from esm.core.esports.moba.simulation.match_live import MatchLive


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
        self.game_times = []
        self.match.simulation_delay = False
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
        self.game_times = []
        self.match.simulation_delay = False
        self.match.show_commentary = False
        self.running_test = False

    def _get_team_stats(self, i):
        team = self.match.game.teams[i]
        self.amount_team_kills[i].append(team.kills)
        self.amount_team_deaths[i].append(team.deaths)
        self.amount_team_assists[i].append(team.assists)

        self.game_times.append(self.match.game_time)

        self.avg_team_kills[i] += team.kills
        self.avg_team_deaths[i] += team.deaths
        self.avg_team_assists[i] += team.assists

    def _get_amount_wins(self):
        if self.match.victorious_team == self.match.game.team1:
            self.amount_team_wins[0] += 1
        else:
            self.amount_team_wins[1] += 1

    def get_max_game_time(self):
        max_game_time = 0
        for game_time in self.game_times:
            max_game_time = max(max_game_time, game_time)

        return max_game_time

    def get_avg_game_time(self):
        return sum(self.game_times) / len(self.game_times)

    def get_avg(self, avg):
        for i, value in enumerate(avg):
            avg[i] = value / self.amount_test

    def get_team_stats(self):
        for i in range(2):
            self._get_team_stats(i)
        self._get_amount_wins()

    def run_match_test(self):
        i = 0
        print("Starting tests!")
        while self.running_test and i <= self.amount_test:
            self.match.simulation()
            self.get_team_stats()
            self.match.reset_match()
            i += 1

        self.get_avg(self.avg_team_kills)
        self.get_avg(self.avg_team_deaths)
        self.get_avg(self.avg_team_assists)

        print("Average team kills:")
        print(f"{self.match.game.team1.team.name}: {self.amount_team_kills[0]}")
        print(f"{self.match.game.team2.team.name}: {self.amount_team_kills[1]}")
        print("Average team deaths:")
        print(f"{self.match.game.team1.team.name}: {self.amount_team_deaths[0]}")
        print(f"{self.match.game.team2.team.name}: {self.amount_team_deaths[1]}")
        print("Average team assists:")
        print(f"{self.match.game.team1.team.name}: {self.amount_team_assists[0]}")
        print(f"{self.match.game.team2.team.name}: {self.amount_team_assists[1]}")
        print("Amount team wins:")
        print(f"{self.match.game.team1.team.name}: {self.amount_team_wins[0]}")
        print(f"{self.match.game.team2.team.name}: {self.amount_team_wins[1]}")

        print("Average game time was", self.get_avg_game_time())
        print("Max game time was", self.get_max_game_time())
        self.running_test = False
