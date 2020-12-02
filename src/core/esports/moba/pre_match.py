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

from src.core.esports.moba.champion import Champion
from .player import MobaPlayer
from .team import Team
from src.resources.utils import load_list_from_json


def get_all_team_objects():
    return [create_team_object(team, load_list_from_json('players.json')) for team in load_list_from_json('teams.json')]


def get_data():
    players = load_list_from_json('players.json')
    teams = load_list_from_json('teams.json')

    team_list = []
    for team in teams:
        team_list.append(create_team_object(team, players))

    data = []
    for team in team_list:
        data.append([team.team_id, team.name, team.player_overall])

    data.sort(key=lambda team: team[2], reverse=False)

    return data


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


def get_teams_dictionaries(team_ids: list, list_of_teams: list) -> list:
    """
    Used to return a list of teams dictionaries, based on their team IDs
    :param team_ids:
    :param list_of_teams:
    :return:
    """
    return [get_team(team_id, list_of_teams) for team_id in team_ids]


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
    mult = player_dict["multipliers"]
    skill = player_dict["skill"]

    return MobaPlayer(
        player_id, nationality, first_name, last_name, nick_name, mult, skill
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
