import random

from .match import Match
from ..resources.utils import get_dict_list
from .pre_match import get_teams_dictionaries, create_team_object, create_champion_object


def initialize_match(team1_id: int,
                     team2_id: int,
                     match_id: int,
                     show_commentary: bool,
                     match_speed: int,
                     ch_id: int) -> Match:
    """
    Instantiate each object that is going to be used by the match, returning
    the match object.
    :param team1_id:
    :param team2_id:
    :param match_id:
    :param show_commentary:
    :param match_speed:
    :param ch_id:
    :return:
    """
    # Gets both lists to use it on the appropriate functions
    team_list = get_dict_list('teams.json')
    player_list = get_dict_list('players.json')

    # Creates both teams dictionaries to create their objects
    team1_dict, team2_dict = get_teams_dictionaries(team1_id, team2_id, team_list)

    # Instantiate team objects, creating players' objects as well
    team1 = create_team_object(team1_dict, player_list)
    team2 = create_team_object(team2_dict, player_list)

    return Match(match_id, ch_id, team1, team2, show_commentary, match_speed)


def picks_and_bans(match: Match) -> None:
    """
    Dummy picks and bans implementation. Will be changed in the future.
    :param match:
    :return:
    """
    champion_list = get_dict_list('champions.json')

    # TODO: implement proper picks an bans

    # Testing, picking random champions for each player
    for i in range(2):
        for player in match.teams[i].list_players:
            champion_dict = random.choice(champion_list)
            champion_list.remove(champion_dict)
            champion = create_champion_object(champion_dict)
            player.champion = champion


def get_match_obj_test() -> Match:
    """
    This function is used to get random teams from the db, and then get match obj.
    In the future this might be trashed.
    :return:
    """
    list_ids = [i for i in range(20)]

    # Guarantees that team1 ID is not the same from team2 ID
    team1_id = random.choice(list_ids)
    list_ids.remove(team1_id)
    team2_id = random.choice(list_ids)

    match = initialize_match(team1_id, team2_id, 1, True, 1, 6)
    picks_and_bans(match)

    return match


def start_match(team1_id: int,
                team2_id: int,
                match_id: int,
                show_commentary: bool,
                match_speed: int,
                ch_id: int) -> Match:

    match = initialize_match(team1_id, team2_id, match_id, show_commentary, match_speed, ch_id)
    picks_and_bans(match)

    # TODO: implement match loop

    return match
