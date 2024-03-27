#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
import re
from pathlib import Path
from typing import Union
from unicodedata import normalize

import cbor2

from ...definitions import ROOT_DIR


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


def get_from_file(file_name: Path) -> list[dict]:
    """
    General function used to read a JSON/CBOR file, extracting its data to a dictionary/list
    :param file_name:
    :return:
    """
    if file_name.suffix == ".json":
        with file_name.open("r", encoding="utf-8") as fp:
            dictionary = json.load(fp)
    else:
        with file_name.open("rb") as fp:
            dictionary = cbor2.load(fp)

    return dictionary


def load_list_from_file(filepath: Union[str, Path]) -> list[dict]:
    """
    Reads a specified file (champions, player or team json) and
    returns the list from that file
    :param filepath:
    :return:
    """
    if os.path.exists(filepath):
        return get_from_file(filepath)
    else:
        raise FileNotFoundError("File was not found")


def get_files_from_extension(directory: Union[str, Path], extension: str) -> list[str]:
    return [
        str(file) for file in Path(directory).glob(f"*{extension}") if file.is_file()
    ]


def normalize_filename(filename, delim="_") -> str:
    """
    Normalizes the save game filename. This will prevent unsupported filenames from being saved.

    Solution from: https://stackoverflow.com/questions/9042515/normalizing-unicode-text-to-filenames-etc-in-python
    """
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')
    result = []
    for word in _punct_re.split(filename.lower()):
        word = normalize("NFKD", word).encode("ascii", "ignore")
        if word := word.decode("utf-8"):
            result.append(word)

    filename = delim.join(result)
    filename = "".join(filename)
    return f"{filename}.cbor"


def get_nations(names: list[dict[str, str | float]]) -> list[dict]:
    return [nat["region"] for nat in names]


def get_default_names_file() -> Path:
    return ROOT_DIR / "res" / "definitions" / "names.json"
