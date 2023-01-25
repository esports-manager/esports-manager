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

from enum import Enum, auto


class LaneError(Exception):
    pass


class Lanes(Enum):
    """
    Defines lanes that can be played during a MOBA match
    """

    TOP = 0
    JNG = auto()
    MID = auto()
    ADC = auto()
    SUP = auto()


def get_lanes_from_dict(lanes: dict[int, float]) -> dict[Lanes, float]:
    _lanes = {}
    for lane, mult in lanes.items():
        _lanes.update({Lanes(lane): mult})

    return _lanes
