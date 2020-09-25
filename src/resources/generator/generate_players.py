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

import random

from src.resources.generator.get_names import generate_player_name, gen_nick_name, get_nick_team_names
from src.resources.utils import find_file, load_list_from_json

from ..utils import write_to_json


def get_players_nationalities(file: list) -> list:
    """
    Defines nationalities
    :param file: list
    :return nationality: list
    """

    return ['Brazil', 'Korea', 'United States']

    # This function will get all nationalities, but I'm not ready to implement all nationalities into the game
    # return [element['region'] for element in file]


def generate_player(file: list,
                    nationality: str,
                    nicknames: list,
                    player_id: int,
                    team_id: int,
                    lane: int,
                    champions: list) -> dict:
    """
    Generates player dictionary
    """
    first_name, last_name = generate_player_name(file, nationality)
    nick_name = gen_nick_name(nicknames)

    multipliers = get_player_role_multiplier(lane)
    skill = int(get_players_skills(nationality))

    return {
        "id": player_id,
        "team_id": team_id,
        "first_name": first_name,
        "last_name": last_name,
        "nick_name": nick_name,
        "nationality": nationality,
        "multipliers": multipliers,
        "skill": skill
    }


def get_player_role_multiplier(lane: int) -> list:
    roles = []
    for i in range(5):
        if i == lane:
            roles.append(1)
        else:
            mult = random.randrange(3, 10) / 10
            roles.append(mult)

    return roles


def get_players_skills(nationality: str) -> int:
    """
    Randomly generates players skills according to their nationality
    :param nationality: string
    :return skill: int
    """
    if nationality == "Brazil":
        mu = 50
        sigma = 20
    elif nationality == "Korea":
        mu = 80
        sigma = 10
    elif nationality == "United States":
        mu = 65
        sigma = 20
    else:
        mu = 50
        sigma = 10
        
    skill = random.gauss(mu, sigma)

    # Players' skill will follow the 30 < skill < 90 interval
    if skill >= 90:
        skill = 90
    elif skill < 30:
        skill = 30
    
    return skill


def get_num_players() -> int:
    """
    Defines the number of players here. Could be replaced by a file.
    :return:
    """
    return 200


def generate_player_file(players) -> None:
    """
    Runs the entire thing
    """
    write_to_json(players, 'players.json')
