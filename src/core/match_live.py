import os
import json

from .match import Match
from .team import Team
from .player import Player


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def get_from_file(file_name):
    with open(file_name, "r") as fp:
        dictionary = json.load(fp)

    return dictionary


def get_team_list():
    teams_file = os.path.join(THIS_FOLDER, "../resources/db/teams.json")
    team_list = get_from_file(teams_file)

    return team_list


def get_player_list():
    players_file = os.path.join(THIS_FOLDER, "../resources/db/players.json")
    player_list = get_from_file(players_file)

    return player_list


def get_team(team_id, list_teams):
    obtained_team = None

    for team in list_teams:
        if team["id"] == team_id:
            obtained_team = team
            return obtained_team

    if obtained_team is None:
        raise Exception("Team was not found!")


def get_teams_dictionaries(team1_id, team2_id):
    # Get teams list
    list_of_teams = get_team_list()

    # search for team id
    team1 = get_team(team1_id, list_of_teams)
    team2 = get_team(team2_id, list_of_teams)

    return team1, team2


def create_team_object(team_dict):
    team_id = team_dict["id"]
    name = team_dict["name"]
    list_of_players = team_dict["roster"]

    team = Team(team_id, name, list_of_players)

    return team


def create_player_object(player_dict):
    player_id = player_dict["id"]
    first_name = player_dict["first_name"]
    last_name = player_dict["last_name"]
    nationality = player_dict["nationality"]
    nick_name = player_dict["nick_name"]
    skill = player_dict["skill"]
    player = Player(player_id, nationality, first_name, last_name, nick_name, skill)

    return player


def get_roster(list_of_players):
    all_players = get_player_list()
    roster = list()

    for player_id in list_of_players:
        for player in all_players:
            if player["id"] == player_id:
                roster.append(player)
                break

    return roster


def initialize():
    pass


def picks_and_bans(team1, team2):
    pass


def start_match(team1, team2):
    pass
