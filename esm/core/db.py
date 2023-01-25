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
from .settings import Settings
from .esports.moba.generator import TeamGenerator, ChampionGenerator, MobaPlayerGenerator


class DB:
    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def teams_file(self):
        return self.settings.teams_file

    @property
    def players_file(self):
        return self.settings.players_file

    @property
    def champions_file(self):
        return self.settings.champions_file

    def get_moba_generators(self):
        players = MobaPlayerGenerator(file_name=self.players_file)
        teams = TeamGenerator(file_name=self.teams_file)
        champions = ChampionGenerator(file_name=self.champions_file)
        return players, teams, champions

    def generate_all(self):
        players_gen, teams_gen, champions_gen = self.get_moba_generators()
        champions_gen.generate_champions()
        players_gen.champions_list = champions_gen.champions_obj

        players_gen.lane = 0
        players_gen.generate_players(amount=self.settings.amount_players)

        amount_teams = self.settings.amount_players / 5

        teams_gen.amount = amount_teams
        teams_gen.player_list = players_gen.players
        teams_gen.generate_teams()

        teams_gen.generate_file()
        champions_gen.generate_file()
        players_gen.generate_file()

    def load_moba_teams(self):
        players_gen, teams_gen, champions_gen = self.get_moba_generators()


