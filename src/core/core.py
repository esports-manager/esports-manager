#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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
import math
import threading

from src.resources.generator.generate_players import MobaPlayerGenerator
from src.resources.generator.generate_teams import TeamGenerator
from src.resources.generator.generate_champions import ChampionGenerator
from src.resources.utils import find_file
from src.core.esports.moba.championship import Championship
from src.core.esports.moba.match import Match
from src.core.esports.moba.match_live import MatchLive


class Core:
    def __init__(self, amount_players=400):
        self.amount_players = amount_players
        self.amount_teams = math.floor(self.amount_players / 5)
        self.champions = ChampionGenerator()
        self.champions.get_champion_names()
        self.players = MobaPlayerGenerator()
        self.teams = TeamGenerator()

        self.match = None
        self.matches = []

        self.match_simulation = None

        self.championship = None

    def generate_all(self):
        self.champions.get_champion_names()
        self.players.champions_list = self.champions.create_champions_list()

        self.players.lane = 0
        self.players.generate_players(amount=self.amount_players)

        self.teams.amount = self.amount_teams
        self.teams.generate_teams()

        self.teams.generate_file()
        self.champions.generate_file()
        self.players.generate_file()

    def check_files(self):
        try:
            find_file(self.champions.file_name)
            find_file(self.players.file_name)
            find_file(self.teams.file_name)
        except FileNotFoundError:
            self.generate_all()

    def get_players(self):
        self.players.get_players_objects()
        return self.players.players

    def get_teams(self):
        self.teams.get_teams_objects()
        return self.teams.teams

    def get_champions(self):
        self.champions.get_champions()
        return self.champions.champions_obj

    def initialize_match(self, championship_id, team1, team2):
        self.match = Match(championship_id=championship_id, team1=team1, team2=team2)

    def initialize_match_simulation(self, match, show_commentary, match_speed, sim):
        self.match_simulation = MatchLive(match, show_commentary=show_commentary, match_speed=match_speed, simulate=sim)

    def get_championship(self):
        pass
