#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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

import cbor2

from esm.core.esports.manager import Manager
from esm.core.gamestate import GameState
from esm.core.hashfile import HashFile
from esm.definitions import SAVE_FILE_DIR


class LoadGameError(Exception):
    pass


class LoadGame:
    def __init__(self, folder=SAVE_FILE_DIR):
        self.folder = folder
        self.hash_file = HashFile()

    def check_game_file(self, filename: str) -> bool:
        """
        Checks the integrity of the game file. If there are missing keywords, it's a corrupted savefile,
        and the game cannot be loaded.
        Returns True if the file is okay, or False otherwise.
        """
        self.hash_file.read_hash_file()
        hash_data = self.hash_file.hash_file(filename)
        try:
            return self.hash_file.hash_data[os.path.normpath(filename)] == hash_data
        except KeyError:
            raise LoadGameError("File is not registered in the hash file!")

    @staticmethod
    def check_for_autosaves(filename: str, list_files: list):
        """
        Checks if a file contains autosaves. This will prompt the user that an autosave file has been identified
        and will ask them if they want to load the autosave file instead of the save file.
        """
        autosave = str(filename.split('.')[0]) + '.autosav'
        return autosave in list_files

    def load_game_file(self, filename: str):
        """
        Load data from the game file.
        """
        filename = os.path.join(self.folder, filename)
        if self.check_game_file(filename):
            with open(filename, 'rb') as fp:
                return cbor2.load(fp)
        else:
            raise LoadGameError("The save file is corrupted!")

    def __check_key_integrity(self, data: dict):
        expected_keys = [
            "gamename",
            "filename",
            "manager",
            "season",
            "esport",
            "teams",
            "players",
            "champions",
            "save_date"
        ]
        obtained_keys = [k for k in data]
        return expected_keys == obtained_keys

    def __get_game_data(self, filename: str):
        """
        Deserialize data from the load file.
        """
        data = self.load_game_file(filename)
        if self.__check_key_integrity(data):
            teams = data["teams"]
            players = data["players"]
            champions = data["champions"]
            return data, teams, players, champions
        else:
            raise LoadGameError("The save file does not contain the expected keys")

    def load_game_state(self, filename: str) -> GameState:
        """
        Turns load game data into GameState data.
        """
        data, teams, players, champions = self.__get_game_data(filename)
        return GameState(
            data["gamename"],
            data["filename"],
            Manager(
                data["manager"]["name"],
                data["manager"]["birthday"],
                data["manager"]["team"],
                True,
                data["manager"]["quality"],
            ).get_dict(),
            data["season"],
            data["esport"],
            teams,
            players,
            champions
        )

    def get_load_game_files(self, extension: str) -> list:
        """
        Returns a list of available load game files
        """
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        load_game_files = []
        for root, _, files in os.walk(self.folder):
            for file in files:
                if file.endswith(extension) and self.check_game_file(os.path.join(root, file)):
                    load_game_files.append(file)

        return load_game_files
