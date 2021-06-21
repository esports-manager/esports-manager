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
import math
import random
import uuid

from esm.core.esports.moba.championship import Championship
from esm.core.esports.moba.match import Match
from esm.core.esports.moba.match_live import MatchLive
from esm.resources.generator.generate_players import MobaPlayerGenerator
from esm.resources.generator.generate_teams import TeamGenerator
from esm.resources.generator.generate_champions import ChampionGenerator
from esm.resources.utils import find_file


class Core:
    def __init__(self, amount_players=400):
        self.amount_players = amount_players
        self.amount_teams = math.floor(self.amount_players / 5)
        self.champions = ChampionGenerator()
        self.players = MobaPlayerGenerator()
        self.teams = TeamGenerator()

        self.match = None
        self.matches = []

        self.match_simulation = None

        self.championship = None

    def generate_all(self) -> None:
        self.champions.create_champions_list()
        self.players.champions_list = self.champions.champions_obj

        self.players.lane = 0
        self.players.generate_players(amount=self.amount_players)

        self.teams.amount = self.amount_teams
        self.teams.player_list = self.players.players
        self.teams.generate_teams()

        self.teams.generate_file()
        self.champions.generate_file()
        self.players.generate_file()

    def check_files(self) -> None:
        find_file(self.champions.file_name)
        find_file(self.players.file_name)
        find_file(self.teams.file_name)

    def get_players(self) -> list:
        self.players.get_players_objects()
        return self.players.players

    def get_teams(self) -> list:
        self.teams.get_teams_objects()
        return self.teams.teams

    def get_champions(self) -> list:
        self.champions.get_champions()
        return self.champions.champions_obj

    def initialize_match(self, championship_id, team1, team2) -> None:
        self.match = Match(championship_id=championship_id, team1=team1, team2=team2)

    def initialize_match_simulation(
        self, match, show_commentary=True, match_speed=1, simulate=True
    ) -> None:
        self.match_simulation = MatchLive(
            match,
            show_commentary=show_commentary,
            match_speed=match_speed,
            simulate=simulate,
        )

    def initialize_random_debug_match(self) -> None:
        self.players.get_players_objects()

        self.teams.player_list = self.players.players
        self.teams.get_teams_objects()

        team1 = random.choice(self.teams.teams)
        self.teams.teams.remove(team1)
        team2 = random.choice(self.teams.teams)
        self.teams.teams.remove(team2)

        self.initialize_match(uuid.uuid4(), team1, team2)
        self.initialize_match_simulation(self.match)

    def get_championship(self) -> Championship:
        pass

    @staticmethod
    def reset_team_values(match) -> None:
        match.reset_teams()
