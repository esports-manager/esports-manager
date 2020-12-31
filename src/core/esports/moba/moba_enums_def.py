#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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


class MobaEventType(Enum):
    """
    Defines the types of events that can occur during a match
    """
    NOTHING = 0
    KILL = auto()
    TOWER_ASSAULT = auto()
    JG_DRAGON = auto()
    JG_BARON = auto()
    INHIB_ASSAULT = auto()
    NEXUS_ASSAULT = auto()


class Lanes(Enum):
    """
    Defines lanes that can be played during a MOBA match
    """
    TOP = 0
    JG = auto()
    MID = auto()
    ADC = auto()
    SUP = auto()


class JungleMonsters(Enum):
    DRAGON = auto()
    BARON = auto()


class Towers(Enum):
    BLUE_FIRST_TOP_TOWER = auto()
    BLUE_SECOND_TOP_TOWER = auto()
    BLUE_THIRD_TOP_TOWER = auto()
    BLUE_FIRST_MID_TOWER = auto()
    BLUE_SECOND_MID_TOWER = auto()
    BLUE_THIRD_MID_TOWER = auto()
    BLUE_FIRST_BOT_TOWER = auto()
    BLUE_SECOND_BOT_TOWER = auto()
    BLUE_THIRD_BOT_TOWER = auto()
    BLUE_FIRST_NEXUS_TOWER = auto()
    BLUE_SECOND_NEXUS_TOWER = auto()
    RED_FIRST_TOP_TOWER = auto()
    RED_SECOND_TOP_TOWER = auto()
    RED_THIRD_TOP_TOWER = auto()
    RED_FIRST_MID_TOWER = auto()
    RED_SECOND_MID_TOWER = auto()
    RED_THIRD_MID_TOWER = auto()
    RED_FIRST_BOT_TOWER = auto()
    RED_SECOND_BOT_TOWER = auto()
    RED_THIRD_BOT_TOWER = auto()
    RED_FIRST_NEXUS_TOWER = auto()
    RED_SECOND_NEXUS_TOWER = auto()
