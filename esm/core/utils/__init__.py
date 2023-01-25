#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2023  Pedrenrique G. Guimarães
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
import os
from pathlib import Path
from typing import Union

import cbor2

from esm.definitions import TEAMS_FILE


def write_to_file(
        contents: list,
        filename: Union[str, Path],
) -> None:
    file = filename
    if not os.path.exists(filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    filename = str(filename)
    if filename.endswith(".json"):
        with open(file, "w") as fp:
            json.dump(contents, fp, sort_keys=True)
    elif filename.endswith(".cbor"):
        with open(file, "wb") as fp:
            cbor2.dump(contents, fp)


def get_from_file(file_name: Union[str, Path]) -> list:
    """
    General function used to read a JSON/CBOR file, extracting its data to a dictionary/list
    :param file_name:
    :return:
    """
    if file_name.endswith(".json"):
        with open(file_name, "r", encoding="utf-8") as fp:
            dictionary = json.load(fp)
    else:
        with open(file_name, "rb") as fp:
            dictionary = cbor2.load(fp)

    return dictionary


def load_list_from_file(filepath: Union[str, Path]) -> list:
    """
    Reads a specified file (champions, player or team json) and
    returns the list from that file
    :param filepath:
    :return:
    """
    if os.path.exists(filepath):
        return get_from_file(filepath)
    else:
        raise FileNotFoundError('File was not found')


def get_key_from_json(key: str = "name", file: Union[str, Path] = TEAMS_FILE) -> list:
    """
    Gets a key from a json file. By default it is used by the GUI to get
    names from the file teams.json, but we can repurpose that for other
    files too, such as get player names, champion names, etc...
    :param key:
    :param file:
    :return:
    """
    return [obj[key] for obj in load_list_from_file(file)]
