import os
import json

from src.definitions import ROOT_DIR


def find_file(filename) -> str:
    """
    This function is used to find files used by the project. It receives the
    ROOT_DIR (src) and searches from there. It removes the need to hard-code
    certain files.

    It was added because tests were failing outside of PyCharm, so running tests
    from terminal or VS Code was producing tons of Errors. So I had to refactor
    everything, come up with ways that tests would work in all platforms, and that's
    what I ended up with.

    I hope this won't affect performance that much, and maybe in the future more
    elegant solutions will come out.

    :param filename:
    :return:
    """
    for root, _, files in os.walk(ROOT_DIR):
        if filename in files:
            return os.path.join(root, filename)
    else:
        raise FileNotFoundError("File couldn't be found!")


def get_from_file(file_name: str) -> list:
    """
    General function used to read a JSON file, extracting its data to a dictionary/list
    :param file_name:
    :return:
    """
    with open(file_name, "r") as fp:
        dictionary = json.load(fp)

    return dictionary


def get_dict_list(filepath: str) -> list:
    """
    Reads a specified file (champions, player or team json) and
    returns the list from that file
    :param filepath:
    :return:
    """
    file = find_file(filepath)
    return get_from_file(file)


def get_list_of_team_names() -> list:
    return [team["name"] for team in get_dict_list('teams.json')]
