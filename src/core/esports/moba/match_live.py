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
from src.resources.utils import load_list_from_json
from src.core.esports.moba.event import EventHandler


class MatchLive:
    def __init__(self, match: Match, show_commentary, match_speed):
        self.match = match
        self.game_time = 0.0
        self.first_blood = False
        self.victorious_team = None
        self.show_commentary = show_commentary
        self.match_speed = match_speed
        self.is_match_over = False
        self.event_handler = EventHandler()

    def picks_and_bans(self, champions) -> None:
        """
        Dummy picks and bans implementation. Will be changed in the future.
        """
        pass

    def calculate_both_teams_win_prob(self) -> None:
        total_prob = sum(
            (team.player_overall + team.champion_overall)/2 + team.points for team in self.match.teams
        )

        for team in self.match.teams:
            team.win_prob = (team.player_overall + team.champion_overall + team.points) / total_prob

    def increment_game_time(self, quantity):
        self.game_time += quantity

    def which_team_nexus_exposed(self):
        if self.match.team1.is_nexus_exposed():
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
            self.event_handler.get_events(self.game_time, self.is_any_inhib_open(), self.which_team_nexus_exposed())
            print(self.game_time, self.event_handler.choose_event().name)
            self.increment_game_time(1)
            # TODO: match sim could be played without generating comments, so players can get instant results
            # probably this implementation without a sleep should do the trick, because it is going to generate stats
            if self.game_time == 50:
                self.is_match_over = True
            # time.sleep(self.match_speed)


def initialize_match(team1,
                     team2,
                     match_id,
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
    return MatchLive(match, True, )
