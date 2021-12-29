#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
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
from esm.definitions import SAVE_FILE_DIR
from esm.core.generator.generate_champions import ChampionGenerator
from esm.core.generator.generate_teams import TeamGenerator


class LoadGameError(Exception):
    pass


class LoadGame:
    def __init__(self, folder=SAVE_FILE_DIR):
        self.folder = folder

    def check_game_file(self, filename) -> bool:
        """
        Checks the integrity of the game file. If there are missing keywords, it's a corrupted savefile,
        and the game cannot be loaded.
        Returns True if the file is okay, or False otherwise.
        """
        pass

    def load_game_file(self, filename):
        """
        Load data from the game file.
        """
        if self.check_game_file(filename):
            with open(filename, 'r') as fp:
                return cbor2.load(fp)
        else:
            raise LoadGameError("The save file is corrupted!")

    def __get_game_data(self, filename):
        """
        Deserialize data from the load file.
        """
        data = self.load_game_file(filename)
        t = TeamGenerator()
        t.teams_dict = data["teams"]
        t.player_list = data["players"]
        t.get_teams_objects()
        teams = t.teams
        players = t.player_list
        c = ChampionGenerator()
        c.champions_list = data["champions"]
        c.get_champions()
        champions = c.champions_obj
        return data, teams, players, champions

    def load_game_state(self, filename) -> GameState:
        """
        Turns load game data into GameState data.
        """
        data, teams, players, champions = self.__get_game_data(filename)
        return GameState(
            data["game_name"],
            data["filename"],
            Manager(
                data["manager"]["name"],
                data["manager"]["birthday"],
                data["manager"]["team"],
                True,
                data["manager"]["quality"],
            ),
            data["season"],
            data["esport"],
            teams,
            players,
            champions
        )

    def get_load_game_files(self) -> list:
        """
        Returns a list of available load game files
        """
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        load_game_files = []
        for root, _, files in os.walk(self.folder):
            for file in files:
                if file.endswith(".cbor") and self.check_game_file(file):
                    load_game_files.append(file)

        return load_game_files
