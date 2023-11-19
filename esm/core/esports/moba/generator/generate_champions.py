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
from typing import Optional

from .default_champion_defs import get_default_champion_names
from .generator import GeneratorInterface
from ..champion import Champion, ChampionType, ChampionDifficulty
from ..player import Lanes, LaneMultipliers


class ChampionGenerator(GeneratorInterface):
    def __init__(self, champion_def: list[dict]):
        self.champion_def = champion_def
        self.random = False
        self.random_names: list[str] = []

    def generate_champion_id(self) -> uuid.UUID:
        return uuid.uuid4()

    def _get_random_champion_name(self) -> str:
        if not self.random_names:
            self.random_names = get_default_champion_names()
        return random.choice(self.random_names)

    def generate_champion_name(self, champion_def: Optional[dict]) -> str:
        return self._get_random_champion_name() if self.random else champion_def["name"]

    def generate_champion_scaling(self) -> float:
        return round(random.random(), 2)

    def generate_champion_lanes(self, champion_def: Optional[dict]) -> LaneMultipliers:
        lanes = {}
        if not self.random:
            for lane in Lanes:
                if lane.name in champion_def["lanes"]:
                    lanes[lane] = 1.0
                else:
                    lanes[lane] = round(random.randrange(1, 95) / 100, 2)
        else:
            main_lane = random.choice(list(Lanes))
            for lane in Lanes:
                if lane == main_lane:
                    lanes[lane] = 1.0
                else:
                    lanes[lane] = round(random.randrange(1, 95) / 100, 2)

        return LaneMultipliers.get_from_dict(lanes)

    def generate_scaling_peak(self) -> int:
        """
        Generates the time when the scaling reaches its peak and the champion stops growing.
        """
        return random.randrange(15, 30)

    def generate_champion_skill(self) -> int:
        return random.randrange(1, 100)

    def generate_champion_difficulty(self, difficulty: Optional[str] = None):
        if difficulty:
            return ChampionDifficulty(difficulty)
        return random.choice(list(ChampionDifficulty))

    def generate_champion_type(self, ch_type: Optional[str] = None, used_type: ChampionType = None) -> ChampionType:
        if ch_type:
            return ChampionType(ch_type)

        ch_types = list(ChampionType)
        if used_type:
            ch_types.remove(used_type)
        return random.choice(ch_types)

    def generate_champion(
            self, champion_def: Optional[dict] = None, rand: bool = False
    ) -> Champion:
        if rand:
            self.random = True
        champion_id = self.generate_champion_id()
        name = self.generate_champion_name(champion_def)
        scaling_factor = self.generate_champion_scaling()
        scaling_peak = self.generate_scaling_peak()
        skill = self.generate_champion_skill()
        lanes = self.generate_champion_lanes(champion_def)
        difficulty = self.generate_champion_difficulty(champion_def["champion_difficulty"])
        champion_type1 = self.generate_champion_type(champion_def["champion_type1"])
        champion_type2 = self.generate_champion_type(champion_def["champion_type2"], champion_type1)

        return Champion(
            champion_id,
            name,
            skill,
            scaling_factor,
            scaling_peak,
            lanes,
            difficulty,
            champion_type1,
            champion_type2
        )

    def generate(self, amount: int = 0, rand: bool = False) -> list[Champion]:
        if amount == 0:
            amount = len(self.champion_def)
        elif amount < 20:
            amount = 20
            random.shuffle(self.champion_def)

        return [
            self.generate_champion(ch_def, rand)
            for ch_def in self.champion_def[:amount]
        ]
