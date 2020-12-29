#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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

from src.core.esports.moba.match import Match
from src.core.esports.moba.mobaevent import MobaEventHandler
from src.resources.generator.generate_champions import ChampionGenerator


class MatchLive:
    def __init__(self, match: Match, show_commentary, match_speed, simulate=True):
        self.match = match
        self.game_time = 0.0
        self.first_blood = False
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False
        self.simulate = simulate
        self.event_handler = MobaEventHandler()
        self.champions = ChampionGenerator()

    def picks_and_bans(self) -> None:
        """
        Dummy picks and bans implementation. Will be changed in the future.

        Probably picks and bans should be handled differently in the UI. But I need to come up
        with a general implementation that can be used regardless of the UI.
        """
        self.champions.get_champions()
        for team in self.match.teams:
            for player in team.list_players:
                player.get_default_lane()
                champion = random.choice(self.champions.champions_obj)
                self.champions.champions_obj.remove(champion)
                player.champion = champion

    def calculate_both_teams_win_prob(self) -> None:
        total_prob = sum(
            team.total_skill for team in self.match.teams
        )

        for team in self.match.teams:
            team.win_prob = (team.total_skill / total_prob) * 100

    def increment_game_time(self, quantity):
        self.game_time += quantity

    def get_tower_number(self):
        return sum(sum(team.towers.values()) for team in self.match.teams)

    def which_team_nexus_exposed(self):
        if self.match.team1.is_nexus_exposed():
            if self.match.team2.is_nexus_exposed():
                return self.match.team1, self.match.team2
            return self.match.team1
        elif self.match.team2.is_nexus_exposed():
            return self.match.team2
        else:
            return None

    def is_any_inhib_open(self) -> bool:
        for team in self.match.teams:
            if team.is_inhib_exposed():
                return True
        else:
            return False

    def simulation(self):
        while not self.is_match_over:
            self.calculate_both_teams_win_prob()
            self.event_handler.get_game_state(self.game_time,
                                              self.which_team_nexus_exposed(),
                                              self.is_any_inhib_open(),
                                              self.get_tower_number())
            self.event_handler.generate_event(self.game_time)
            self.event_handler.event.calculate_event(self.match.team1,
                                                     self.match.team2,
                                                     self.which_team_nexus_exposed(),
                                                     self.is_any_inhib_open())
            self.increment_game_time(1)
            # TODO: match sim could be played without generating comments, so players can get instant results
            # probably this implementation without a sleep should do the trick, because it is going to generate stats
            if self.game_time == 50:
                self.is_match_over = True
            # time.sleep(self.match_speed)


def initialize_match(team1,
                     team2,
                     ch_id):
    """
    Instantiate each object that is going to be used by the match, returning
    the match object.
    :param team1_id:
    :param team2_id:
    :param match_id:
    :param ch_id:+
    :return:
    """

    match = Match(ch_id, team1, team2)
    return MatchLive(match, True, 1)
