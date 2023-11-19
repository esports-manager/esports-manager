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

from esm.core.gamestate import GameState
from esm.core.settings import Settings
from .load_game import LoadGame, LoadGameError
from .save_game import SaveGame


def check_if_save_file_exists(filename: Union[str, Path]) -> bool:
    return os.path.exists(filename)


def get_load_game_files(settings: Settings) -> list:
    load = LoadGame(folder=settings.save_file_dir)
    return load.get_load_game_files('.cbor')


def get_autosave_files(settings: Settings) -> list:
    load = LoadGame(folder=settings.save_file_dir)
    return load.get_load_game_files('.autosav')


def create_save_game(gamestate: GameState, filename: str, settings: Settings, auto_save_enabled: bool) -> SaveGame:
    return SaveGame(gamestate, filename, save_directory=settings.save_file_dir, autosave_enabled=auto_save_enabled, )


def auto_save(save: SaveGame) -> None:
    save.autosave()


def load_game(filename: Union[Path, str], settings: Settings) -> GameState:
    load = LoadGame(folder=settings.save_file_dir)
    return load.load_game_state(filename)


def get_temporary_file(save: SaveGame):
    return save.temporary_file


def delete_temporary_file(save: SaveGame):
    save.delete_temporary_file()
