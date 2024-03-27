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
from dataclasses import dataclass

from esm.core.esports.moba.mobateam import MobaTeam

from ...serializable import Serializable


@dataclass
class MobaRegion(Serializable):
    region_id: str
    name: str
    short_name: str
    teams: list[MobaTeam]

    def serialize(self) -> dict:
        return {
            "region_id": self.region_id,
            "name": self.name,
            "short_name": self.short_name,
            "teams": [team.team_id.int for team in self.teams],
        }

    @classmethod
    def get_from_dict(cls, dictionary: dict, teams: list[MobaTeam]):
        return cls(
            region_id=dictionary["region_id"],
            name=dictionary["name"],
            short_name=dictionary["short_name"],
            teams=teams,
        )
