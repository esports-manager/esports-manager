import json
import os
import random

import src.core.match_live
import src.core.match
import src.core.team
import src.core.player

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def read_file(file):
    with open(file, 'r') as fp:
        content = json.load(fp)

    return content


def get_teams_from_db():
    team_file = os.path.join(THIS_FOLDER, 'resources/db/teams.json')
    teams = read_file(team_file)

    return teams


def get_team(team_id, teams):
    for team in teams:
        if team["id"] == team_id:
            return team


def get_players_from_db():
    player_file = os.path.join(THIS_FOLDER, 'resources/db/players.json')
    players = read_file(player_file)

    return players


def get_players(team, players):
    team_players = []

    for player_id in team["roster"]:
        for player in players:
            if player_id == player["id"]:
                team_players.append(player)
                break

    return team_players


if __name__ == '__main__':
    teams_list = get_teams_from_db()
    team1 = get_team(5, teams_list)
    team2 = get_team(7, teams_list)
    players_list = get_players_from_db()
    for player in players_list:
        print(player["first_name"] + " " + player["last_name"] + ": " + player["nick_name"])
