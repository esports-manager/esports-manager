import json
import os
import random

from .get_names import get_br_first_names, get_kr_first_names, get_usa_first_names
from .get_names import get_br_last_names, get_kr_last_names, get_usa_last_names


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

JSON_FILE = os.path.join(THIS_FOLDER, '../db/players.json')

NUM_PLAYERS = 100


def get_players_nationalities():
    """
    Defines nationalities
    :return nationality: string
    """
    nationalities = [
        "br",
        "kr",
        "usa"
    ]

    return nationalities


def generate_nickname():
    min_length = 6
    max_length = 10

    en_vowels = ('a', 'e', 'i', 'o', 'u', 'y')
    en_consonants = ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'z',
                     'sh', 'zh', 'ch', 'kh', 'th')

    is_vowels_first = bool(random.randint(0, 1))
    result = ''

    for i in range(0, random.randint(min_length, max_length)):
        is_even = i % 2 == 0
        if (is_vowels_first and is_even) or (not is_vowels_first and not is_even):
            result += random.choice(en_vowels)
        else:
            result += random.choice(en_consonants)

    return result.title()


def generate_player(nationality):
    """
    Generates player dictionary
    :param nationality: string
    :return player: dictionary
    """
    if nationality == "br":
        first_names = get_br_first_names()
        last_names = get_br_last_names()
    elif nationality == "usa":
        first_names = get_usa_first_names()
        last_names = get_usa_last_names()
    else:
        first_names = get_kr_first_names()
        last_names = get_kr_last_names()

    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    nick_name = generate_nickname()

    skill = get_players_skills(nationality)
    skill = int(skill)

    player = {
        "first_name": first_name,
        "last_name": last_name,
        "nick_name": nick_name,
        "nationality": nationality,
        "skill": skill
    }

    return player


def get_players_skills(nationality):
    """
    Randomly generates players skills according to their nationality
    :param nationality: string
    :return skill: int
    """
    if nationality == "br":
        mu = 45
        sigma = 20
    elif nationality == "kr":
        mu = 75
        sigma = 5
    elif nationality == "usa":
        mu = 65
        sigma = 10
    else:
        mu = 50
        sigma = 10
        
    skill = random.gauss(mu, sigma)

    if skill > 99:
        skill = 99    
    
    return skill


def generate_player_list():
    """
    Generates each player and adds to a list
    :return player_list:
    """
    players_list = []
    nationalities = get_players_nationalities()
    
    for i in range(NUM_PLAYERS):
        nationality = random.choice(nationalities)
        player = generate_player(nationality)
        player["id"] = i
        players_list.append(player)
    
    return players_list


def generate_file(list_objects, file):
    """
    Writes list to a json file
    :param list_objects: player list
    """
    with open(file, "w") as fp:
        json.dump(list_objects, fp, sort_keys=True, indent=4)


def generate(file):
    """
    Runs the entire thing
    """
    players = generate_player_list()
    generate_file(players, file)
