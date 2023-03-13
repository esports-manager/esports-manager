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
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum, auto

from ...serializable import Serializable


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


class LaneMultiplierError(Exception):
    pass


@dataclass
class LaneMultipliers(Serializable):
    top: float
    jng: float
    mid: float
    adc: float
    sup: float

    @staticmethod
    def _check_multiplier(value: float) -> bool:
        return 0.0 <= value <= 1.0

    def __post_init__(self):
        if not (
                self._check_multiplier(self.top) and self._check_multiplier(self.jng) and self._check_multiplier(
                self.mid) and self._check_multiplier(self.adc) and self._check_multiplier(self.sup)
        ):
            raise LaneMultiplierError("Lane value cannot be negative or greater than 1.0!")

    def __getitem__(self, key: Lanes):
        if key == Lanes.TOP:
            return self.top
        elif key == Lanes.JNG:
            return self.jng
        elif key == Lanes.MID:
            return self.mid
        elif key == Lanes.ADC:
            return self.adc
        elif key == Lanes.SUP:
            return self.sup
        else:
            raise KeyError(key)

    def __setitem__(self, key: Lanes, value: float):
        if key == Lanes.TOP:
            self.top = value
        elif key == Lanes.JNG:
            self.jng = value
        elif key == Lanes.MID:
            self.mid = value
        elif key == Lanes.ADC:
            self.adc = value
        elif key == Lanes.SUP:
            self.sup = value
        else:
            raise KeyError(key)

    def get_best_attribute(self) -> Lanes:
        lanes = self.serialize()
        max_attr = max(list(lanes.values()))

        if self.top == max_attr:
            return Lanes.TOP
        if self.jng == max_attr:
            return Lanes.JNG
        if self.mid == max_attr:
            return Lanes.MID
        if self.adc == max_attr:
            return Lanes.ADC
        if self.sup == max_attr:
            return Lanes.SUP

    @classmethod
    def get_from_dict(cls, dictionary: dict):
        return cls(
            dictionary[Lanes.TOP.value],
            dictionary[Lanes.JNG.value],
            dictionary[Lanes.MID.value],
            dictionary[Lanes.ADC.value],
            dictionary[Lanes.SUP.value],
        )

    def serialize(self) -> dict[int, float]:
        return {
            Lanes.TOP.value: self.top,
            Lanes.JNG.value: self.jng,
            Lanes.MID.value: self.mid,
            Lanes.ADC.value: self.adc,
            Lanes.SUP.value: self.sup
        }


def get_lanes_from_dict(lanes: dict[int, float]) -> dict[Lanes, float]:
    return {Lanes(lane): mult for lane, mult in lanes.items()}
