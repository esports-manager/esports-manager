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
import uuid
from dataclasses import dataclass
from typing import Any
from .moba_definitions import Lanes, LaneMultipliers
from ...serializable import Serializable


class ChampionLoadError(Exception):
    pass


@dataclass(eq=False)
class Champion(Serializable):
    champion_id: uuid.UUID
    name: str
    skill: int
    scaling_factor: float
    scaling_peak: int
    lanes: LaneMultipliers

    @classmethod
    def get_from_dict(cls, dictionary: dict):
        champion_id = uuid.UUID(hex=dictionary['id'])
        name = dictionary['name']
        skill = dictionary['skill']
        scaling_factor = dictionary['scaling_factor']
        scaling_peak = dictionary['scaling_peak']

        if skill > 100 or skill < 0:
            raise ChampionLoadError(f"Skill value is not supported for champion with ID {champion_id.hex}!")

        lanes = LaneMultipliers.get_from_dict(dictionary["lanes"])

        return cls(champion_id, name, skill, scaling_factor, scaling_peak, lanes)

    def serialize(self) -> dict:
        return {
            "id": self.champion_id.hex,
            "name": self.name,
            "skill": self.skill,
            "scaling_factor": self.scaling_factor,
            "scaling_peak": self.scaling_peak,
            "lanes": self.lanes.serialize()
        }

    def get_current_skill(self, lane: Lanes) -> int:
        return self.lanes[lane] * self.skill

    def __str__(self):
        return f"{self.name}"

    def __eq__(self, other: Any):
        if isinstance(other, Champion):
            return self.champion_id == other.champion_id
        return NotImplemented
