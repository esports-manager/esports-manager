import os
import json
from src import THIS_FOLDER

def get_from_file(file_name):
    """
    General function used to read a JSON file, extracting its data to a dictionary/list
    :param file_name:
    :return:
    """
    with open(file_name, "r") as fp:
        dictionary = json.load(fp)

    return dictionary


def get_dict_list(filepath):
    """
    Reads a specified file (champions, player or team json) and
    returns the list from that file
    :param filepath:
    :return:
    """
    file = os.path.join(THIS_FOLDER, filepath)
    dict_list = get_from_file(file)

    return dict_list


def get_list_of_team_names():
    dict_list = get_dict_list('./resources/db/teams.json')

    team_list = list()

    for team in dict_list:
        team_list.append(team["name"])

    return team_list
