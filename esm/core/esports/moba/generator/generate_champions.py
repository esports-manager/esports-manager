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
from typing import Optional

from ..champion import Champion, ChampionDifficulty, ChampionType
from ..mobaplayer import LaneMultipliers, Lanes
from .default_champion_defs import get_default_champion_names
from .generator import GeneratorInterface


class ChampionGeneratorError(Exception):
    pass


class ChampionGenerator(GeneratorInterface):
    def __init__(self):
        self.random = False
        self.random_names: Optional[list[str]] = None

    def generate_champion_id(self) -> uuid.UUID:
        return uuid.uuid4()

    def _get_random_champion_name(self) -> str:
        if self.random_names is None:
            self.random_names = get_default_champion_names()
        name = random.choice(self.random_names)
        self.random_names.remove(name)
        return name

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
                    lanes[lane] = round(random.randrange(1, 75) / 100, 2)
        else:
            main_lane = random.choice(list(Lanes))
            for lane in Lanes:
                if lane == main_lane:
                    lanes[lane] = 1.0
                else:
                    lanes[lane] = round(random.randrange(1, 75) / 100, 2)

        return LaneMultipliers.get_from_dict(lanes)

    def generate_scaling_peak(self) -> int:
        """
        Generates the time when the scaling reaches its peak and the champion stops growing.
        """
        return random.randrange(15, 30)

    def generate_champion_skill(self) -> int:
        return random.randrange(1, 100)

    def generate_champion_difficulty(
        self, difficulty: Optional[dict] = None
    ) -> ChampionDifficulty:
        if difficulty is not None:
            try:
                return ChampionDifficulty(difficulty["difficulty"])
            except KeyError:
                pass

        return random.choice(list(ChampionDifficulty))

    def generate_champion_type(
        self, ch_type: Optional[dict] = None, used_type: ChampionType = None
    ) -> Optional[ChampionType]:
        if ch_type is not None:
            if used_type:
                try:
                    if ch_type["type2"]:
                        return ChampionType(ch_type["type2"])
                    else:
                        return None
                except KeyError:
                    pass
            else:
                try:
                    if ch_type["type1"] is None:
                        raise ChampionGeneratorError("Champion type 1 is None")
                    return ChampionType(ch_type["type1"])
                except KeyError:
                    pass

        ch_types = list(ChampionType)
        if used_type:
            is_there_second_type = random.randint(0, 1)
            if is_there_second_type == 0:
                return None
            ch_types.remove(used_type)
        return random.choice(ch_types)

    def generate(self, champion_def: Optional[dict] = None) -> Champion:
        if champion_def is None:
            self.random = True
        champion_id = self.generate_champion_id()
        name = self.generate_champion_name(champion_def)
        scaling_factor = self.generate_champion_scaling()
        scaling_peak = self.generate_scaling_peak()
        skill = self.generate_champion_skill()
        lanes = self.generate_champion_lanes(champion_def)
        difficulty = self.generate_champion_difficulty(champion_def)
        champion_type1 = self.generate_champion_type(champion_def)
        champion_type2 = self.generate_champion_type(champion_def, champion_type1)

        return Champion(
            champion_id,
            name,
            skill,
            scaling_factor,
            scaling_peak,
            lanes,
            difficulty,
            champion_type1,
            champion_type2,
        )
