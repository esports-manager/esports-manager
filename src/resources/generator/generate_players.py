import json
import os
import random

from src.resources.generator.get_names import get_br_first_names, get_kr_first_names, get_usa_first_names, \
    get_br_last_names, get_kr_last_names, get_usa_last_names, gen_nick_or_team_name


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

JSON_FILE = os.path.join(THIS_FOLDER, '../db/players.json')

NUM_PLAYERS = 200


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
    nick_name = gen_nick_or_team_name("nicknames.txt")

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
        mu = 50
        sigma = 20
    elif nationality == "kr":
        mu = 80
        sigma = 10
    elif nationality == "usa":
        mu = 65
        sigma = 20
    else:
        mu = 50
        sigma = 10
        
    skill = random.gauss(mu, sigma)

    if skill > 93:
        skill = 90
    elif skill < 30:
        skill = 30
    
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


def generate():
    """
    Runs the entire thing
    """
    players = generate_player_list()
    generate_file(players, JSON_FILE)