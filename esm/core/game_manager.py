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

    def load_game(self, filename: Union[str, os.PathLike]):
        load = LoadGame(self.settings.save_file_dir)
        self.gamestate = load.load_game_state(filename)

    def save_game(self, filename: Union[str, os.PathLike]):
        save = SaveGame(self.gamestate, filename, self.settings.save_file_dir, self.auto_save_enabled)
        save.save_game()
