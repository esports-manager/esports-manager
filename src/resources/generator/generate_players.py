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


def generate_player(file: list, nationality: str, nicknames: list) -> dict:
    """
    Generates player dictionary
    :param file: list
    :param nationality: string
    :return player: dictionary
    """
    first_name, last_name = generate_player_name(file, nationality)
    nick_name = gen_nick_name(nicknames)

    skill = get_players_skills(nationality)
    skill = int(skill)

    return {
        "first_name": first_name,
        "last_name": last_name,
        "nick_name": nick_name,
        "nationality": nationality,
        "skill": skill
    }


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
    if skill > 93:
        skill = 90
    elif skill < 30:
        skill = 30
    
    return skill


def generate_player_list() -> list:
    """
    Generates each player and adds to a list
    :return player_list:
    """
    players_list = []

    file = load_list_from_json('names.json')
    nicknames = get_nick_team_names('nicknames.txt')

    nationalities = get_players_nationalities(file)

    for i in range(get_num_players()):
        nationality = random.choice(nationalities)
        player = generate_player(file, nationality, nicknames)
        player["id"] = i
        players_list.append(player)
    
    return players_list


def get_num_players() -> int:
    """
    Defines the number of players here. Could be replaced by a file.
    :return:
    """
    return 500


def generate_player_file() -> None:
    """
    Runs the entire thing
    """
    players = generate_player_list()
    write_to_json(players, 'players.json')
