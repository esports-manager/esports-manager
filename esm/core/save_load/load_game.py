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
import os
from pathlib import Path

import cbor2

from esm.core.gamestate import GameState


class LoadGameError(Exception):
    pass


class LoadGame:
    """
    The LoadGame module deals with loading game files and turning them into GameState data.

    When loading a save file, the module checks the integrity of the save file by looking at the keys contained
    in a GameState module and comparing to the save file. If a key is missing or does not correspond to what
    is in the save game file, the module throws an error that the file is corrupted.
    """

    def __init__(self, folder: Path):
        self.folder = folder

    @staticmethod
    def check_for_autosaves(filename: str, list_files: list):
        """
        Checks if a file contains autosaves. This will prompt the user that an autosave file has been identified
        and will ask them if they want to load the autosave file instead of the save file.
        """
        autosave = str(filename.split(".")[0]) + ".autosav"
        return autosave in list_files

    def load_game_file(self, filename: str):
        """
        Load data from the game file.
        """
        filename = os.path.join(self.folder, filename)
        with open(filename, "rb") as fp:
            return cbor2.load(fp)

    @staticmethod
    def __check_key_integrity(data: dict):
        expected_keys = [
            "gamename",
            "filename",
            "manager",
            "season",
            "esport",
            "regions",
            "teams",
            "players",
            "champions",
            "save_date",
        ]
        obtained_keys = list(data)
        return expected_keys == obtained_keys

    def __get_game_data(self, filename: str):
        """
        Deserialize data from the load file.
        """
        data = self.load_game_file(filename)
        if self.__check_key_integrity(data):
            regions = data["regions"]
            teams = data["teams"]
            players = data["players"]
            champions = data["champions"]
            return data, teams, regions, players, champions
        else:
            raise LoadGameError("The save file does not contain the expected keys")

    def load_game_state(self, filename: str) -> GameState:
        """
        Turns load game data into GameState data.
        """
        data, teams, regions, players, champions = self.__get_game_data(filename)
        return GameState(
            data["gamename"],
            filename,
            data["manager"],
            data["season"],
            data["esport"],
            regions,
            teams,
            players,
            champions,
        )

    def get_load_game_files(self, extension: str) -> list:
        """
        Returns a list of available load game files
        """
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        load_game_files = []
        for root, _, files in os.walk(self.folder):
            load_game_files.extend(file for file in files if file.endswith(extension))

        return load_game_files
