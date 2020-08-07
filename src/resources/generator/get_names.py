import os
import random

from ..utils import find_file


def generate_player_name(names: list, nationality: str):
    for name_dict in names:
        if name_dict['region'] == nationality:
            first_name = random.choice(name_dict['male'])
            last_name = random.choice(name_dict['surnames'])

            return first_name, last_name
    else:
        raise ValueError('Nationality not found!')


def gen_team_name(team_names: list) -> str:
    team_name = random.choice(team_names)
    team_names.remove(team_name)
    return team_name


def gen_nick_name(names: list) -> str:
    return random.choice(names)


def get_nick_team_names(filename: str) -> list:
    file = find_file(filename)

    with open(file, "r", encoding='utf-8') as fp:
        names = fp.read().splitlines()

    return names
