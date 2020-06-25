import os
import json


def get_current_folder():
    return os.path.dirname(os.path.abspath(os.path.basename(__file__)))


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
    file = os.path.join(get_current_folder(), filepath)
    return get_from_file(file)


def get_list_of_team_names():
    dict_list = get_dict_list('../resources/db/teams.json')

    team_list = []

    for team in dict_list:
        team_list.append(team["name"])

    return team_list
