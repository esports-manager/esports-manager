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
from dataclasses import asdict, dataclass

from .serializable import Serializable


@dataclass
class GameState(Serializable):
    gamename: str
    filename: str
    manager: dict
    season: str
    esport: str
    regions: dict
    teams: dict
    players: dict
    champions: dict

    @classmethod
    def get_from_dict(cls, data: dict):
        return cls(**data)

    def serialize(self) -> dict[str, str | dict | list]:
        return asdict(self)
