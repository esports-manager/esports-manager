from typing import Tuple

from .champion import Champion
from .player import MobaPlayer
from .team import Team


def get_team(team_id, list_teams) -> dict:
    """
    Extracts the desired team from the list of teams, returning the team's
    dictionary
    :param team_id:
    :param list_teams:
    :return: team dictionary
    """

    for team in list_teams:
        if team["id"] == team_id:
            return team

    else:
        raise ValueError("Team was not found!")


def get_teams_dictionaries(team1_id, team2_id, list_of_teams) -> Tuple[dict, dict]:
    """
    Used to return both teams dictionaries, based on their team IDs
    :param team1_id:
    :param team2_id:
    :param list_of_teams:
    :return:
    """
    team1 = get_team(team1_id, list_of_teams)
    team2 = get_team(team2_id, list_of_teams)

    return team1, team2


def create_team_object(team_dict: dict, all_players: list) -> Team:
    """
    Creates the team object based on the Team class. It also gets the roster
    and uses the get_roster() function to create the players list
    :param team_dict:
    :param all_players:
    :return:
    """
    team_id = team_dict["id"]
    name = team_dict["name"]
    list_of_players = team_dict["roster_id"]
    roster = get_roster(list_of_players, all_players)

    return Team(team_id, name, roster)


def create_player_object(player_dict: dict) -> MobaPlayer:
    """
    Creates the player object
    :param player_dict:
    :return:
    """
    player_id = player_dict["id"]
    first_name = player_dict["first_name"]
    last_name = player_dict["last_name"]
    nationality = player_dict["nationality"]
    nick_name = player_dict["nick_name"]
    skill = player_dict["skill"]

    return MobaPlayer(
        player_id, nationality, first_name, last_name, nick_name, skill
    )


def create_champion_object(champion_dict: dict) -> Champion:
    """
    Creates the champion object to insert it on the player choice
    :param champion_dict: champion dictionary obtained from json file
    :return: champion object
    """
    champion_id = champion_dict["id"]
    name = champion_dict["name"]
    skill = champion_dict["skill"]

    return Champion(champion_id, name, skill)


def get_roster(list_of_players: list, all_players: list) -> list:
    """
    Searches for each player ID on the player's list, creates the player
    object based on the player dictionary, returning this object
    :param list_of_players: list of players from the roster
    :param all_players: entire player list database
    :return: list of players
    """
    roster = []

    # Is there a more pythonic way to do this?
    for player_id in list_of_players:
        for player_dict in all_players:
            if player_dict["id"] == player_id:
                player = create_player_object(player_dict)
                roster.append(player)
                break

    return roster
