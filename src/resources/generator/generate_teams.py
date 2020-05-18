import json
import os
import random

from .generate_players import NUM_PLAYERS, generate_nickname, JSON_FILE, THIS_FOLDER, generate_file


def get_players():
    with open(JSON_FILE, "r") as fp:
        players = json.load(fp)

    return players


def choose_five_players(players):
    chosen_players_id = []

    for i in range(5):
        player = random.choice(players)
        players.remove(player)
        chosen_players_id.append(player["id"])

    return chosen_players_id


def generate_each_team(players):
    team_name = generate_nickname()
    roster_id = choose_five_players(players)
    team = {"name": team_name,
            "roster_id": roster_id
            }

    return team


def generate_teams(players):
    num_teams = int(NUM_PLAYERS / 5)

    teams = []
    for i in range(num_teams):
        team = generate_each_team(players)
        team["id"] = i
        teams.append(team)

    return teams


def run_generation():
    team_file = os.path.join(THIS_FOLDER, '../db/teams.json')
    players = get_players()
    teams = generate_teams(players)
    generate_file(teams, team_file)
