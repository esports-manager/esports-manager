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
import uuid
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

from ...serializable import Serializable
from .moba_definitions import LaneMultipliers, Lanes


class ChampionLoadError(Exception):
    pass


class ChampionDifficulty(Enum):
    EASY = 0
    MEDIUM = auto()
    HARD = auto()
    PRO = auto()
    GOD = auto()


class ChampionType(Enum):
    TANK = 0
    FIGHTER = auto()
    ASSASSIN = auto()
    MAGE = auto()
    MARKSMAN = auto()
    UTILITY = auto()
    HEALER = auto()


@dataclass(eq=False)
class Champion(Serializable):
    champion_id: uuid.UUID
    name: str
    skill: int
    scaling_factor: float
    scaling_peak: int
    lanes: LaneMultipliers
    champion_difficulty: ChampionDifficulty
    champion_type1: ChampionType
    champion_type2: Optional[ChampionType] = None

    def __post_init__(self):
        if self.champion_type2 == self.champion_type1:
            self.champion_type2 = None

    @classmethod
    def get_from_dict(cls, dictionary: dict):
        champion_id = uuid.UUID(hex=dictionary["id"])
        name = dictionary["name"]
        skill = dictionary["skill"]
        scaling_factor = dictionary["scaling_factor"]
        scaling_peak = dictionary["scaling_peak"]
        difficulty = ChampionDifficulty(dictionary["difficulty"])
        champion_type1 = ChampionType(dictionary["type1"])
        if dictionary["type2"] is None:
            champion_type2 = None
        else:
            champion_type2 = ChampionType(dictionary["type2"])

        if skill > 100 or skill < 0:
            raise ChampionLoadError(
                f"Skill value is not supported for champion with ID {champion_id.hex}!"
            )

        lanes = LaneMultipliers.get_from_dict(dictionary["lanes"])

        return cls(
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

    def serialize(self) -> dict:
        return {
            "id": self.champion_id.hex,
            "name": self.name,
            "skill": self.skill,
            "scaling_factor": self.scaling_factor,
            "scaling_peak": self.scaling_peak,
            "lanes": self.lanes.serialize(),
            "difficulty": self.champion_difficulty.value,
            "type1": self.champion_type1.value,
            "type2": (
                self.champion_type2.value if self.champion_type2 is not None else None
            ),
        }

    def get_current_skill(self, lane: Lanes) -> int:
        return self.lanes[lane] * self.skill

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other: Any):
        if isinstance(other, Champion):
            return self.champion_id == other.champion_id
        return NotImplemented
