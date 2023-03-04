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

import random
import uuid
from datetime import date, timedelta
from typing import Tuple

from esm.core.esports.moba.generator.default_player_nick_names import get_default_player_nick_names
from esm.core.esports.moba.generator.generate_champions import ChampionGenerator
from esm.core.esports.moba.player import MobaPlayer
from esm.core.utils import load_list_from_file, write_to_file, get_nations
from esm.definitions import PLAYERS_FILE, NAMES_FILE


class MobaPlayerGeneratorError(Exception):
    pass


class MobaPlayerGenerator:
    """
    Generates all MobaPlayer data
    """

    def __init__(
            self,
            today: date = date.today(),
            min_age: int = 16,
            max_age: int = 25,
            lane: int = 0,
            champions_list: list = None,
            file_name: str = PLAYERS_FILE,
    ):
        if champions_list is None:
            champions_list = []
        self.player_id = None
        self.first_name = None
        self.last_name = None
        self.nick_name = None
        self.dob = None
        self.skill = None
        self.skill_gain = None
        self.exp = None
        self.nationalities = None
        self.nationality = None
        self.player_obj = None

        if min_age > max_age:
            raise MobaPlayerGeneratorError(
                "Minimum age cannot be higher than maximum age!"
            )

        self.min_age = min_age
        self.max_age = max_age
        self.lane = lane
        self.td = today  # used to calculate the date of birth. Varies according to the current season calendar
        self.multipliers = []
        self.champions = []
        self.champions_list = champions_list
        self.players = []
        self.file_name = file_name
        self.names = None
        self.nick_names = None

    def get_names(self) -> None:
        self.names = load_list_from_file(NAMES_FILE)

    def get_nick_names(self) -> None:
        self.nick_names = get_default_player_nick_names()

    def generate_id(self) -> None:
        self.player_id = uuid.uuid4()

    def get_nationalities(self) -> None:
        self.nationalities = get_nations()

    def get_nationality(self) -> None:
        """
        Defines players nationalities
        """
        self.nationality = random.choice(self.nationalities)

    def generate_dob(self) -> None:
        """
        Generates the player's date of birth
        """
        year = timedelta(seconds=31556952)  # definition of a Gregorian calendar date

        max_age = (
                self.max_age * year
        )  # players should be a max of self.max_age years old
        min_age = (
                self.min_age * year
        )  # players can't be less than self.min_age years old
        min_year = self.td - max_age  # minimum date for birthday
        max_year = self.td - min_age  # max date for birthday

        days_interval = max_year - min_year
        rand_date = random.randrange(
            days_interval.days
        )  # chooses a random date from the max days interval
        self.dob = min_year + timedelta(days=rand_date)  # assigns date of birth

    def generate_champions(self, amount: int = 0) -> None:
        """
        Generates champion skill level for each player.
        Chooses a random amount of champions to generate.
        """
        self.champions.clear()
        if not self.champions_list:
            self.champions_list = ChampionGenerator()
            self.champions_list.get_champions()
            self.champions_list = self.champions_list.champions

        champs = self.champions_list.copy()
        if amount == 0:
            amount = random.randrange(3, 15)

        for _ in range(amount):
            ch = random.choice(champs)
            champs.remove(ch)
            mult = random.randrange(60, 100) / 100

            champion_dict = {
                "id": ch.champion_id.int,
                "mult": mult,
            }

            self.champions.append(champion_dict)

    def get_nationality_skill(self) -> Tuple[int, int]:
        for nat in self.names:
            if nat["region"] == self.nationality:
                mu = nat["mu"]
                sigma = nat["sigma"]

                return mu, sigma

    def generate_skill(self) -> None:
        """
        Randomly generates players skills according to their nationality
        """
        mu, sigma = self.get_nationality_skill()
        self.skill = int(random.gauss(mu, sigma))

        # Players' skill will follow the 30 < skill < 90 interval
        if self.skill >= 90:
            self.skill = 90
        elif self.skill < 30:
            self.skill = 30

        sk_g = list(MobaSkillGain)
        self.skill_gain = random.choice(sk_g)
        self.exp = 0.0

    def generate_name(self) -> None:
        """
        Generates the player's real name
        """
        for name_dict in self.names:
            if name_dict["region"] == self.nationality:
                self.first_name = random.choice(name_dict["male"])
                self.last_name = random.choice(name_dict["surnames"])
                break
        # else:
        #    raise ValueError('Nationality not found!')

    def generate_nick(self) -> None:
        """
        Generates the player's nickname
        """
        self.nick_name = random.choice(self.nick_names)

    def get_dictionary(self) -> None:
        """
        Generates the dictionary based on the class' attributes
        """
        return self.player_obj.get_dict()

    def get_object(self) -> None:
        """
        Generates a player object
        """
        self.player_obj = MobaPlayer(
            self.player_id,
            self.nationality,
            self.first_name,
            self.last_name,
            self.dob,
            self.nick_name,
            self.multipliers,
            self.skill,
            self.skill_gain,
            self.champions,
            self.exp,
        )

    def generate_multipliers(self) -> None:
        """
        Generates players multipliers.
        Multipliers are used to define the player's experience on a lane.
        It ranges from 0.55 to 1.

        It goes like this:
        player_skill * multiplier = player_actual_skill_in_game

        Essentially this should discourage the users from making players play off-lane
        """
        mult = []
        for _ in range(5):
            multiplier = random.randrange(55, 100) / 100
            mult.append(multiplier)

        if self.lane == -1:
            mult[mult.index(max(mult))] = 1
        else:
            mult[self.lane] = 1

        self.multipliers = mult

    def generate_player(self) -> None:
        """
        Runs the player generation routine
        """
        if self.names is None:
            self.get_names()
        if self.nationalities is None:
            self.get_nationalities()
        if self.nick_names is None:
            self.get_nick_names()
        self.generate_id()
        self.get_nationality()
        self.generate_name()
        self.generate_nick()
        self.generate_skill()
        self.generate_dob()
        self.generate_champions()
        self.generate_multipliers()
        self.get_dictionary()
        self.get_object()
        self.players.append(self.player_obj)

    def generate_players(self, amount: int = 5) -> None:
        """
        Generates an "amount" of players.
        If the self.lane attribute is set to -1, then it randomly generates players with variable lanes.
        Otherwise, it generates an "amount/5" players that play on the same lane, doing that for every lane.
        """
        if self.lane == -1:
            for _ in range(amount):
                self.generate_player()
        else:
            self.lane = 0
            for _ in range(5):
                for __ in range(amount // 5):
                    self.generate_player()
                self.lane += 1

    def get_data_from_obj(self, player=None) -> None:
        """
        Gets an object and enters data to the MobaPlayerGenerator attributes
        """
        if player is None:
            player = self.player_obj

        self.player_id = player.player_id
        self.first_name = player.first_name
        self.last_name = player.last_name
        self.dob = player.birthday
        self.nationality = player.nationality
        self.nick_name = player.nick_name
        self.skill = player.skill
        self.skill = player.skill_lvl.skill_gain
        self.exp = player.skill_lvl.exp
        self.multipliers = player.mult
        self.champions = player.champions

    def get_players_objects(self) -> None:
        """
        Creates players objects based on the player dictionary
        """
        self.players = []
        if not self.players_dict:
            self.get_players_dict()
        self.players = [MobaPlayer.get_from_dict(player) for player in self.players_dict]

    def get_from_data_file(self, data: list):
        players_dict = data.copy()
        self.players = [MobaPlayer.get_from_dict(player) for player in players_dict]