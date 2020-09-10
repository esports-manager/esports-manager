import random
import asyncio

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

    def simulation(self):
        while not self.is_match_over:

            self.event_handler.get_events(self.game_time)


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

    for team in live.match.teams:
        print(team.list_players)
