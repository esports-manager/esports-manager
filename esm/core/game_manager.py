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
import os

from pathlib import Path
from typing import Union

from .gamestate import GameState
from .db import DB
from .save_load import LoadGame, SaveGame
from .settings import Settings


class GameManager:
    """
    Manages the state of the current game session.
    """

    def __init__(
            self,
            settings: Settings,
            db: DB,
            auto_save_enabled: bool = True
    ):
        self.settings = settings
        self.auto_save_enabled = auto_save_enabled
        self.db = db
        self.gamestate = None
        self.current_matches = None
        self.load = None
        self.save = None

    def get_gamestate(self):
        return GameState(
            self.game_name,
            self.filename,
            self.manager.get_dict(),
            self.season,
            self.esport,
            self.teams.teams_dict.copy(),
            self.players.players_dict.copy(),
            self.champions.champions_list.copy(),
        )

    def create_save_game(self):
        self.save = SaveGame(
            self.get_gamestate(),
            self.filename,
            save_directory=self.settings.save_file_dir,
            autosave_enabled=self.auto_save_enabled,
        )

    def save_game(self):
        """
        Calls the SaveGame module to save the game file.
        """
        self.create_save_game()
        self.save.save_game()

    def auto_save(self):
        """
        Calls the SaveGame module to save an autosave file.
        """
        self.create_save_game()
        self.save.save_autosave()

    def get_load_game_files(self):
        self.load = LoadGame(folder=self.settings.save_file_dir)
        self.load.get_load_game_files('.cbor')

    def check_if_save_file_exists(self, filename: Union[str, Path]):
        return os.path.exists(filename)

    def get_autosave_files(self):
        self.load = LoadGame(folder=self.settings.save_file_dir)
        self.load.get_load_game_files('.autosav')

    def load_game(self, filename: Union[Path, str]):
        self.filename = filename
        self.load = LoadGame(folder=self.settings.save_file_dir)
        self.gamestate = self.load.load_game_state(filename)
        self.save = SaveGame(self.gamestate, filename)

    def get_temporary_file(self):
        self.create_save_game()
        self.save.save_temporary_file()
        return self.save.temporary_file

    def delete_temporary_file(self):
        self.save.delete_temporary_file()
