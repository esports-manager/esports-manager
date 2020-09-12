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

import json
import random
from math import floor

from .get_names import gen_team_name, get_nick_team_names
from ..utils import write_to_json, load_list_from_json


def get_num_teams(players: list) -> int:
    return int(floor(len(players) / 5))


# TODO: let teams have a bigger roster than 5 players
def choose_five_players(players: list) -> list:
    chosen_players_id = []

    while len(chosen_players_id) != 5:
        player = random.choice(players)
        players.remove(player)
        chosen_players_id.append(player["id"])

    return chosen_players_id


def generate_each_team(players: list, team_names: list) -> dict:
    team_name = gen_team_name(team_names)
    roster_id = choose_five_players(players)

    return {"name": team_name, "roster_id": roster_id}


def generate_teams(players: list) -> list:
    num_teams = get_num_teams(players)
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
