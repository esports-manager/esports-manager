import os
import random
import json

from .match import Match
from .team import Team
from .player import Player
from .champion import Champion


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def get_from_file(file_name):
    """
    General function used to read a JSON file, extracting its data to a dictionary/list
    :param file_name:
    :return:
    """
    with open(file_name, "r") as fp:
        dictionary = json.load(fp)

    return dictionary


def get_dict_list(filepath):
    """
    Reads a specified file (champions, player or team json) and
    returns the list from that file
    :param filepath:
    :return:
    """
    file = os.path.join(THIS_FOLDER, filepath)
    dict_list = get_from_file(file)

    return dict_list


def get_team(team_id, list_teams):
    """
    Extracts the desired team from the list of teams, returning the team's
    dictionary
    :param team_id:
    :param list_teams:
    :return:
    """
    obtained_team = None

    for team in list_teams:
        if team["id"] == team_id:
            obtained_team = team
            return obtained_team

    if obtained_team is None:
        raise Exception("Team was not found!")


def get_teams_dictionaries(team1_id, team2_id, list_of_teams):
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


def create_team_object(team_dict, all_players):
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

    team = Team(team_id, name, roster)

    return team


def create_player_object(player_dict):
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

    player = Player(player_id, nationality, first_name, last_name, nick_name, skill)

    return player


def create_champion_object(champion_dict):
    champion_id = champion_dict["id"]
    name = champion_dict["name"]
    skill = champion_dict["skill"]

    champion = Champion(champion_id, name, skill)

    return champion


def get_roster(list_of_players, all_players):
    """
    Searches for each player ID on the player's list, creates the player
    object based on the player dictionary, returning this object
    :param list_of_players: list of players from the roster
    :param all_players: entire player list database
    :return:
    """
    roster = list()

    for player_id in list_of_players:
        for player_dict in all_players:
            if player_dict["id"] == player_id:
                player = create_player_object(player_dict)
                roster.append(player)
                break

    return roster


def initialize_match(team1_id, team2_id, match_id, show_commentary, match_speed, ch_id):
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
    team_list = get_dict_list("../resources/db/teams.json")
    player_list = get_dict_list("../resources/db/players.json")

    # Creates both teams dictionaries to create their objects
    team1_dict, team2_dict = get_teams_dictionaries(team1_id, team2_id, team_list)

    # Instantiate team objects, creating players' objects as well
    team1 = create_team_object(team1_dict, player_list)
    team2 = create_team_object(team2_dict, player_list)

    # Instantiate a match
    match = Match(match_id, ch_id, team1, team2, show_commentary, match_speed)

    return match


def picks_and_bans(match):
    champion_list = get_dict_list("../resources/db/champions.json")

    # TODO: implement proper picks an bans

    # Testing, picking random champions for each player
    for i in range(2):
        for player in match.teams[i].list_players:
            champion_dict = random.choice(champion_list)
            champion_list.remove(champion_dict)
            champion = create_champion_object(champion_dict)
            player.champion = champion


def start_match(team1_id, team2_id, match_id, show_commentary, match_speed, ch_id):
    match = initialize_match(team1_id, team2_id, match_id, show_commentary, match_speed, ch_id)
    picks_and_bans(match)

    return match
