import os
from pathlib import Path
from typing import Union

from esm.core.save_load import LoadGame, SaveGame
from esm.core.settings import Settings
from esm.core.gamestate import GameState


def check_if_save_file_exists(filename: Union[str, Path]) -> bool:
    return os.path.exists(filename)


def get_load_game_files(settings: Settings) -> list:
    load = LoadGame(folder=settings.save_file_dir)
    return load.get_load_game_files('.cbor')


def get_autosave_files(settings: Settings) -> list:
    load = LoadGame(folder=settings.save_file_dir)
    return load.get_load_game_files('.autosav')


def create_save_game(gamestate: GameState, filename: str, settings: Settings, auto_save_enabled: bool) -> SaveGame:
    return SaveGame(gamestate, filename, save_directory=settings.save_file_dir, autosave_enabled=auto_save_enabled,)


def auto_save(save: SaveGame) -> None:
    save.autosave()


def load_game(filename: Union[Path, str], settings: Settings) -> GameState:
    load = LoadGame(folder=settings.save_file_dir)
    return load.load_game_state(filename)


def get_temporary_file(save: SaveGame):
    return save.temporary_file


def delete_temporary_file(save: SaveGame):
    save.delete_temporary_file()
