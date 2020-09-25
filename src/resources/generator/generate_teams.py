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
from .generate_players import generate_player, get_nick_team_names, get_players_nationalities
from ..utils import write_to_json, load_list_from_json


def get_num_teams() -> int:
    return 700


def generate_roster(players: list, team_id: int) -> list:
    roster = []
    roster_length = random.randrange(5, 10)
    names = load_list_from_json('names.json')
    nicknames = get_nick_team_names('nicknames.txt')
    nationalities = get_players_nationalities(names)
    champions = load_list_from_json('champions.json')

    for i in range(roster_length):
        nationality = random.choice(nationalities)
        player = generate_player(
            names,
            nationality,
            nicknames,
            len(players),
            team_id,
            i,
            champions
        )
        roster.append(player['id'])
        players.append(player)

    return roster


def generate_each_team(players: list, team_names: list, team_id: int) -> dict:
    team_name = gen_team_name(team_names)
    roster = generate_roster(players, team_id)

    return {
        "id": team_id,
        "name": team_name,
        "roster_id": roster
    }


def generate_teams(players: list) -> list:
    num_teams = get_num_teams()
    team_names = get_nick_team_names('team_names.txt')

    # Handling number of teams being higher than the number of available team names
    if num_teams > len(team_names):
        num_teams = len(team_names)

    teams = []

    for i in range(num_teams):
        team = generate_each_team(players, team_names, i)
        teams.append(team)

    return teams


def generate_team_file(players) -> None:
    teams = generate_teams(players)
    write_to_json(teams, 'teams.json')
