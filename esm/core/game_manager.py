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
from pathlib import Path
from typing import Union

from esm.core.esports.manager import Manager
from esm.core.gamestate import GameState
from esm.core.load_game import LoadGame
from esm.core.save_game import SaveGame
from esm.core.generator.generate_champions import ChampionGenerator
from esm.core.generator.generate_players import MobaPlayerGenerator
from esm.core.generator.generate_teams import TeamGenerator


class GameManager:
    """
    Manages the state of the current game session.
    """

    def __init__(self, manager: Manager, filename: str, esport: str, season: str, game_name: str):
        self.manager = manager
        self.esport = esport
        self.season = season
        self.filename = filename
        self.game_name = game_name
        self.teams = TeamGenerator()
        self.players = MobaPlayerGenerator()
        self.champions = ChampionGenerator()
        self.teams.get_teams_objects()
        self.players.get_players_objects()
        self.champions.get_champions()
        self.gamestate = self.get_gamestate()
        self.load = LoadGame()
        self.save = SaveGame(self.gamestate, filename)

    def get_gamestate(self):
        return GameState(
            self.game_name,
            self.filename,
            self.manager,
            self.season,
            self.esport,
            self.teams,
            self.players,
            self.champions
        )

    def save_game(self):
        self.save.save_game()

    def get_load_game_files(self):
        self.load.get_load_game_files()

    def load_game(self, filename: Union[Path, str]):
        self.filename = filename
        self.gamestate = self.load.load_game_state(filename)
        self.save = SaveGame(self.gamestate, filename)

    def get_temporary_file(self):
        self.gamestate.create_temporary_file()
        return self.gamestate.temporary_file
