import json
import random
from math import floor

from .get_names import gen_team_name, get_nick_team_names
from ..utils import write_to_json, load_list_from_json


# TODO: let teams have a bigger roster than 5 players
def choose_five_players(players: list) -> list:
    chosen_players_id = []

    for _ in range(5):
        player = random.choice(players)
        players.remove(player)
        chosen_players_id.append(player["id"])

    return chosen_players_id


def generate_each_team(players: list, team_names: list) -> dict:
    team_name = gen_team_name(team_names)
    roster_id = choose_five_players(players)

    return {"name": team_name, "roster_id": roster_id}


def generate_teams(players: list) -> list:
    num_teams = floor(int(len(players) / 5))
    team_names = get_nick_team_names('team_names.txt')

    # Handling number of teams being higher than the number of available team names
    if num_teams > len(team_names):
        num_teams = len(team_names)

    teams = []

    for i in range(num_teams):
        team = generate_each_team(players, team_names)
        team["id"] = i
        teams.append(team)

    return teams


def generate_team_file() -> None:
    players = load_list_from_json('players.json')
    teams = generate_teams(players)
    write_to_json(teams, 'teams.json')
