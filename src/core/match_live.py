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
import time

from src.core.match import Match
from src.resources.utils import load_list_from_json
from src.core.pre_match import get_teams_dictionaries, create_team_object, create_champion_object
from src.core.event import EventHandler


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

    def picks_and_bans(self) -> None:
        """
        Dummy picks and bans implementation. Will be changed in the future.
        """
        champion_list = load_list_from_json('champions.json')

        # TODO: implement proper picks an bans

        # Testing, picking random champions for each player
        for i in range(2):
            for player in self.match.teams[i].list_players:
                champion_dict = random.choice(champion_list)
                champion_list.remove(champion_dict)
                champion = create_champion_object(champion_dict)
                player.champion = champion

    def calculate_both_teams_win_prob(self) -> None:
        total_prob = sum(
            team.player_overall + team.champion_overall + team.points for team in self.match.teams
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
            return 0

    def is_any_inhib_open(self):
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
            # TODO: match sim could be player without generating comments, so players can get instant results
            # probably this implementation without a sleep should do the trick, because it is going to generate stats
            if self.game_time == 50:
                self.is_match_over = True
            # time.sleep(self.match_speed)


def initialize_match(team1_id: int,
                     team2_id: int,
                     match_id: int,
                     ch_id: int) -> Match:
    """
    Instantiate each object that is going to be used by the match, returning
    the match object.
    :param team1_id:
    :param team2_id:
    :param match_id:
    :param ch_id:+
    :return:
    """
    # Gets both lists to use it on the appropriate functions
    team_list = load_list_from_json('teams.json')
    player_list = load_list_from_json('players.json')

    # Creates both teams dictionaries to create their objects
    team1_dict, team2_dict = get_teams_dictionaries(team1_id, team2_id, team_list)

    # Instantiate team objects, creating players' objects as well
    team1 = create_team_object(team1_dict, player_list)
    team2 = create_team_object(team2_dict, player_list)

    return Match(match_id, ch_id, team1, team2)


def get_live_obj_test() -> MatchLive:
    """
    This function is used to get random teams from the db, and then get matchlive obj.
    In the future this might be trashed.
    :return:
    """
    list_ids = [i for i in range(20)]

    # Guarantees that team1 ID is not the same from team2 ID
    team1_id = random.choice(list_ids)
    list_ids.remove(team1_id)
    team2_id = random.choice(list_ids)

    live = MatchLive(initialize_match(team1_id, team2_id, 1, 1), True, 1)
    live.picks_and_bans()

    return live


def start_match(team1_id: int,
                team2_id: int,
                match_id: int,
                show_commentary: bool,
                match_speed: int,
                ch_id: int) -> Match:

    match = initialize_match(team1_id, team2_id, match_id, ch_id)

    live = MatchLive(match, show_commentary, match_speed)
    live.picks_and_bans()

    # asyncio.run(live.match_loop())

    return match


def debug_match():
    live = get_live_obj_test()

    print(live.match.teams)

    players = [None, None]
    champions = [None, None]
    for i, team in enumerate(live.match.teams):
        players[i] = [player for player in team.list_players]
        champions[i] = [player.champion for player in players[i]]

    print(players)
    print(champions)
    live.simulation()


if __name__ == '__main__':
    debug_match()
