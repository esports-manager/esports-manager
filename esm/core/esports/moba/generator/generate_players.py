#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
from typing import Optional, Tuple

from ....utils import get_nations
from ..champion import Champion
from ..player import (
    ChampionMastery,
    CommunicationAttributes,
    KnowledgeAttributes,
    LaneMultipliers,
    Lanes,
    MechanicsAttributes,
    MobaPlayer,
    MobaPlayerAttributes,
    MobaPlayerChampion,
    OffensiveAttributes,
    UtilityAttributes,
)
from .default_player_nick_names import get_default_player_nick_names
from .generator import GeneratorInterface


def generate_attribute_value(mu, sigma) -> int:
    return abs(int(random.gauss(mu, sigma)))


class MobaPlayerGeneratorError(Exception):
    pass


class MobaPlayerAttributesGeneratorError(Exception):
    pass


class MobaPlayerAttributesGenerator(GeneratorInterface):
    def generate_offensive_attributes(
        self, mu: int = 40, sigma: int = 10
    ) -> OffensiveAttributes:
        return OffensiveAttributes(
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
        )

    def generate_communication_attributes(
        self, mu: int = 40, sigma: int = 10
    ) -> CommunicationAttributes:
        return CommunicationAttributes(
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
        )

    def generate_knowledge_attributes(
        self, mu: int = 40, sigma: int = 10
    ) -> KnowledgeAttributes:
        return KnowledgeAttributes(
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
        )

    def generate_mechanics_attributes(
        self, mu: int = 40, sigma: int = 10
    ) -> MechanicsAttributes:
        return MechanicsAttributes(
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
        )

    def generate_utility_attributes(
        self, mu: int = 40, sigma: int = 10
    ) -> UtilityAttributes:
        return UtilityAttributes(
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
            generate_attribute_value(mu, sigma),
        )

    def generate(self, mu: int, sigma: int, lane: Lanes) -> MobaPlayerAttributes:
        if lane in [Lanes.JNG, Lanes.SUP]:
            offensive = self.generate_offensive_attributes()
            mechanics = self.generate_mechanics_attributes()
            communication = self.generate_communication_attributes(mu, sigma)
            knowledge = self.generate_knowledge_attributes(mu, sigma)
            utility = self.generate_utility_attributes()
        elif lane in [Lanes.MID, Lanes.TOP]:
            offensive = self.generate_offensive_attributes(mu, sigma)
            mechanics = self.generate_mechanics_attributes(mu, sigma)
            communication = self.generate_communication_attributes(mu, sigma)
            knowledge = self.generate_knowledge_attributes(mu, sigma)
            utility = self.generate_utility_attributes()
        else:
            offensive = self.generate_offensive_attributes(mu, sigma)
            mechanics = self.generate_mechanics_attributes(mu, sigma)
            communication = self.generate_communication_attributes(mu, sigma)
            knowledge = self.generate_knowledge_attributes()
            utility = self.generate_utility_attributes()

        return MobaPlayerAttributes(
            offensive, communication, mechanics, knowledge, utility
        )


class MobaPlayerGenerator(GeneratorInterface):
    """
    Generates all MobaPlayer data
    """

    def __init__(
        self,
        champions_list: list[Champion],
        names: list[dict[str, float | str | int]],
        today: date = date.today(),
        min_age: int = 16,
        max_age: int = 25,
    ):
        self.nationalities = get_nations(names)
        self.nick_names = get_default_player_nick_names()

        if min_age > max_age:
            raise MobaPlayerGeneratorError(
                "Minimum age cannot be higher than maximum age!"
            )

        self.attribute_gen = MobaPlayerAttributesGenerator()
        self.min_age = min_age
        self.max_age = max_age
        self.td = today  # used to calculate the date of birth. Varies according to the current season calendar
        self.champions_list = champions_list
        self.names = names

    @staticmethod
    def generate_id() -> uuid.UUID:
        return uuid.uuid4()

    def get_nationality(self) -> str:
        """
        Defines players nationalities
        """
        return random.choice(self.nationalities)

    def generate_dob(self) -> date:
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
        return min_year + timedelta(days=rand_date)  # assigns date of birth

    def generate_champions(
        self, lane: Lanes, amount: int = 0
    ) -> list[MobaPlayerChampion]:
        """
        Generates champion skill level for each player.
        Chooses a random amount of champions to generate.
        """
        champs = []
        for champion in self.champions_list:
            best_lane = champion.lanes.get_best_attribute().value
            if lane == best_lane:
                champs.append(champion)

        if not champs:
            return []

        player_champions = []
        if amount == 0:
            amount = random.randrange(1, len(champs))

        for _ in range(amount):
            ch = random.choice(champs)
            champs.remove(ch)
            champion_mastery = random.choices(
                list(ChampionMastery), [0.0, 0.5, 0.2, 0.01, 0.005, 0.0005, 0.0005]
            )[0]
            moba_player_champ = MobaPlayerChampion(
                ch.champion_id, champion_mastery, 0.0
            )
            player_champions.append(moba_player_champ)

        return player_champions

    def get_nationality_skill(self, nationality: str) -> Tuple[int, int]:
        for nat in self.names:
            if nat["region"] == nationality:
                mu = nat["mu"]
                sigma = nat["sigma"]

                return mu, sigma

    def generate_attributes(
        self, mu: int, sigma: int, lane: Lanes
    ) -> MobaPlayerAttributes:
        """
        Randomly generates players skills according to their nationality
        """
        return self.attribute_gen.generate(mu, sigma, lane)

    def generate_first_name(self, nationality: str) -> str:
        """
        Generates the player's real name
        """
        for name_dict in self.names:
            if name_dict["region"] == nationality:
                return random.choice(name_dict["male"])

        raise ValueError("Invalid region!")

    def generate_last_name(self, nationality: str) -> str:
        """
        Generates the player's real name
        """
        for name_dict in self.names:
            if name_dict["region"] == nationality:
                return random.choice(name_dict["surnames"])

        raise ValueError("Invalid region!")

    def generate_nick(self) -> str:
        """
        Generates the player's nickname
        """
        return random.choice(self.nick_names)

    def generate_multipliers(self, main_lane: Lanes) -> LaneMultipliers:
        """
        Generates players multipliers.
        Multipliers are used to define the player's experience on a lane.
        It ranges from 0.55 to 1.

        It goes like this:
        player_skill * multiplier = player_actual_skill_in_game

        Essentially this should discourage the users from making players play off-lane
        """
        mult = {}
        for lane in range(5):
            multiplier = random.randrange(55, 100) / 100 if lane != main_lane else 1
            mult[lane] = multiplier

        return LaneMultipliers.get_from_dict(mult)

    def generate(
        self,
        lane: Lanes,
        nationality: Optional[str] = None,
        mu: Optional[int] = None,
        sigma: Optional[int] = None,
        amount_champions: int = 0,
    ) -> MobaPlayer:
        """
        Runs the player generation routine
        """
        if not nationality:
            nationality = self.get_nationality()

        if mu is None or sigma is None:
            mu, sigma = self.get_nationality_skill(nationality)

        return MobaPlayer(
            self.generate_id(),
            nationality,
            self.generate_first_name(nationality),
            self.generate_last_name(nationality),
            self.generate_dob(),
            self.generate_nick(),
            self.generate_multipliers(lane),
            self.generate_attributes(mu, sigma, lane),
            self.generate_champions(lane, amount_champions),
        )
