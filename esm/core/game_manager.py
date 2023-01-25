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
import re
from pathlib import Path
from typing import Union
from unicodedata import normalize

from esm.core.esports.manager import Manager
from esm.core.gamestate import GameState
from esm.core.esports.moba.generator import ChampionGenerator
from esm.core.esports.moba.generator import MobaPlayerGenerator
from esm.core.esports.moba.generator import TeamGenerator
from esm.core.save_load.load_game import LoadGame
from esm.core.save_load.save_game import SaveGame
from esm.core.settings import Settings


class GameManager:
    """
    Manages the state of the current game session.
    """

    def __init__(
            self,
            manager: Manager,
            filename: str,
            esport: str,
            season: str,
            game_name: str,
            settings: Settings,
            auto_save_enabled: bool = True
    ):
        self.manager = manager
        self.esport = esport
        self.season = season
        self.filename = self.normalize_filename(filename)
        self.game_name = game_name
        self.teams = TeamGenerator()
        self.players = MobaPlayerGenerator()
        self.champions = ChampionGenerator()
        self.gamestate = self.get_gamestate()
        self.settings = settings
        self.auto_save_enabled = auto_save_enabled
        self.load = None
        self.save = None

    @classmethod
    def get_game_manager(cls, gamestate: GameState, settings: Settings, auto_save_enabled: bool = True):
        return cls(
            Manager(
                gamestate.manager["name"],
                gamestate.manager["birthday"],
                gamestate.manager["team"],
                True,
                gamestate.manager["quality"],
            ),
            gamestate.filename,
            gamestate.esport,
            gamestate.season,
            gamestate.gamename,
            settings,
            auto_save_enabled,
        )

    def get_gamestate(self):
        self.teams.get_teams_objects()
        self.players.get_players_objects()
        self.champions.get_champions()
        gamestate = GameState(
            self.game_name,
            self.filename,
            self.manager.get_dict(),
            self.season,
            self.esport,
            self.teams.teams_dict.copy(),
            self.players.players_dict.copy(),
            self.champions.champions_list.copy(),
        )
        self.reset_generators()
        return gamestate

    def normalize_filename(self, filename, delim=u'_'):
        """
        Normalizes the save game filename. This will prevent unsupported filenames from being saved.

        Solution from: https://stackoverflow.com/questions/9042515/normalizing-unicode-text-to-filenames-etc-in-python
        """
        _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.:]+')
        result = []
        for word in _punct_re.split(filename.lower()):
            word = normalize('NFKD', word).encode('ascii', 'ignore')
            if word := word.decode('utf-8'):
                result.append(word)

        filename = delim.join(result)
        filename = ''.join(filename)
        filename = f'{filename}.cbor'
        return filename

    def reset_generators(self):
        """
        Resets generators to avoid keeping them in memory.
        """
        self.teams = TeamGenerator()
        self.players = MobaPlayerGenerator()
        self.champions = ChampionGenerator()

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
        self.reset_generators()
        self.create_save_game()
        self.save.save_game()

    def get_gamestate_for_generators(self):
        self.teams.get_from_data_file(self.gamestate.teams)
        self.players.get_from_data_file(self.gamestate.players)
        self.champions.get_from_data_file(self.gamestate.champions)

    def write_generator_files(self):
        self.teams.generate_file()
        self.players.generate_file()
        self.champions.generate_file()

    def auto_save(self):
        """
        Calls the SaveGame module to save an autosave file.
        """
        self.reset_generators()
        self.create_save_game()
        self.save.save_autosave()
        self.get_gamestate_for_generators()
        self.write_generator_files()

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
        self.get_gamestate_for_generators()
        self.write_generator_files()

    def get_temporary_file(self):
        self.reset_generators()
        self.create_save_game()
        self.save.save_temporary_file()
        self.get_gamestate_for_generators()
        self.write_generator_files()
        return self.save.temporary_file

    def delete_temporary_file(self):
        self.save.delete_temporary_file()
