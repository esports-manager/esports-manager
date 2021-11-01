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
from esm.core.esports.manager import Manager
from esm.core.load_game import LoadGame
from esm.core.save_game import SaveGame
from esm.core.gamestate import GameState
from esm.resources.generator.generate_teams import TeamGenerator
from esm.resources.generator.generate_players import MobaPlayerGenerator
from esm.resources.generator.generate_champions import ChampionGenerator


class GameManager:
    """
    Manages the state of the current game session.
    """
    def __init__(self, manager: Manager, filename, esport, season, game_name):
        self.manager = manager
        self.esport = esport
        self.season = season
        self.game_name = game_name
        self.teams = TeamGenerator()
        self.players = MobaPlayerGenerator()
        self.champions = ChampionGenerator()
        self.teams.get_teams_objects()
        self.players.get_players_objects()
        self.champions.get_champions()
        self.gamestate = GameState(
            game_name,
            filename,
            manager,
            season,
            esport,
            self.teams.teams,
            self.players.players,
            self.champions.champions_obj
        )
        self.load = LoadGame(filename)
        self.save = SaveGame(self.gamestate, filename)
        self.temporary_file = None
    
    def save_game(self):
        self.save.save_game()

    def get_temporary_file(self):
        self.gamestate.create_temporary_file()
        self.gamestate.write_to_temporary_file()
        return self.gamestate.temporary_file
