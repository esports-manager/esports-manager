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
import math
import random
import uuid

from esm.core.esports.moba.match import Match
from esm.core.esports.moba.match_live import MatchLive
from esm.core.utils import find_file
from esm.core.generator.generate_champions import ChampionGenerator
from esm.core.generator.generate_players import MobaPlayerGenerator
from esm.core.generator.generate_teams import TeamGenerator


class MobaModel:
    """
    The Core module corresponds to a Model on a traditional MVC model.
    """

    def __init__(self, amount_players=50):
        self._amount_players = amount_players
        self._amount_teams = math.floor(self.amount_players / 5)
        self.champions = ChampionGenerator()
        self.players = MobaPlayerGenerator()
        self.teams = TeamGenerator()

        self.match = None
        self.matches = []

        self.match_live = None

        self.championship = None

    @property
    def amount_players(self):
        return self._amount_players

    @amount_players.setter
    def amount_players(self, amount):
        self._amount_players = amount

    @property
    def amount_teams(self):
        self._amount_teams = math.floor(self.amount_players / 5)
        return self._amount_teams

    def reset_generators(self):
        self.champions = ChampionGenerator()
        self.players = MobaPlayerGenerator()
        self.teams = TeamGenerator()

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

    def check_player_amount(self):
        if self.amount_players > 300 or self.amount_players < 50:
            raise ValueError('Number of players is not supported! Ranges from 50 to 300 players! Defaulting to 50.')

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

    @staticmethod
    def initialize_match(championship_id, team1, team2) -> Match:
        return Match(uuid.uuid4(), championship_id=championship_id, team1=team1, team2=team2)

    @staticmethod
    def initialize_match_live(
            match, show_commentary=True, match_speed=1, simulate=True, queue=None, picks_bans_queue=None,
    ) -> MatchLive:
        return MatchLive(
            match,
            show_commentary=show_commentary,
            match_speed=match_speed,
            simulate=simulate,
            queue=queue,
            picks_bans_queue=picks_bans_queue
        )

    def initialize_random_debug_match(self, queue=None, picksbans=True, picks_bans_queue=None) -> MatchLive:
        self.players.get_players_objects()

        self.teams.player_list = self.players.players
        self.teams.get_teams_objects()

        team1 = random.choice(self.teams.teams)
        self.teams.teams.remove(team1)
        team2 = random.choice(self.teams.teams)
        self.teams.teams.remove(team2)

        self.match = self.initialize_match(uuid.uuid4(), team1, team2)
        self.match_live = self.initialize_match_live(
            self.match,
            queue=queue,
            picks_bans_queue=picks_bans_queue
        )

        self.reset_generators()

        self.get_player_default_lanes()

        if picksbans:
            self.match_live.picks_and_bans()

        return self.match_live

    def get_player_default_lanes(self) -> None:
        for team in self.match.teams:
            team.get_players_default_lanes()

    @staticmethod
    def reset_team_values(match) -> None:
        match.reset_teams()

    @staticmethod
    def reset_match(match, queue=None, picks_bans_queue=None) -> None:
        match.reset_match(queue, picks_bans_queue)
