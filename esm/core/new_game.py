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
from esm.core.esports.manager import Manager
from esm.core.esports.moba.generator import ChampionGenerator
from esm.core.esports.moba.generator import MobaPlayerGenerator
from esm.core.esports.moba.generator import TeamGenerator
from esm.core.esports.moba.team import Team


class CreateGameSession:
    def __init__(self):
        self.filename = None
        self.game_name = None
        self.manager_name = None
        self.date_of_birth = None
        self.season = None
        self.esport = None
        self.manager = None
        self.team = None
        self.teams = TeamGenerator()
        self.players = MobaPlayerGenerator()
        self.champions = ChampionGenerator()

    def get_names(
            self,
            filename: str,
            game_name: str,
            manager_name: str,
            date_of_birth: str,
            season: str,
            esport: str,
    ):
        self.filename = filename
        self.game_name = game_name
        self.manager_name = manager_name
        self.date_of_birth = date_of_birth
        self.season = season
        self.esport = esport

    def start_new_game(self):
        self.manager = Manager(
            self.manager_name, self.date_of_birth, self.team, True, 50
        )

    def generate_new_database(self):
        self.teams.generate_teams()
        self.players.generate_players()
        self.champions.generate_champions()
        self.write_files()

    def write_files(self):
        self.teams.generate_file()
        self.players.generate_file()
        self.champions.generate_file()

    def get_team(self, team: Team):
        self.team = team
