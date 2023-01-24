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
from dataclasses import dataclass
from .moba_enums_def import Lanes, get_lanes_from_dict
import uuid


@dataclass
class Champion:
    champion_id: uuid.UUID
    name: str
    skill: int
    lanes: dict[Lanes, float]

    @classmethod
    def get_from_dict(cls, dictionary: dict):
        champion_id = uuid.UUID(hex=dictionary['id'])
        name = dictionary['name']
        skill = dictionary['skill']
        lanes = dictionary['lanes']
        return cls(champion_id, name, skill, get_lanes_from_dict(lanes))

    def serialize_lanes(self) -> dict[int, float]:
        _lanes = {}
        for lane, mult in self.lanes.items():
            _lanes.update({lane.value: mult})

        return _lanes

    def serialize(self) -> dict:
        return {
            "id": self.champion_id.hex,
            "name": self.name,
            "skill": self.skill,
            "lanes": self.serialize_lanes()
        }

    def __str__(self):
        return f"{self.name}"
