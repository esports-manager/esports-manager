#  eSports Manager - free and open source eSports Management game
#  Copyright (C) 2020-2024  Pedrenrique G. Guimarães
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
from enum import Enum, auto


class MobaEventType(Enum):
    NOTHING = auto()
    FIGHT = auto()
    JUNGLE_GRUBS = auto()
    JUNGLE_HERALD = auto()
    JUNGLE_DRAKE = auto()
    JUNGLE_BARON = auto()
    INHIB_ASSAULT = auto()
    TOWER_ASSAULT = auto()
    NEXUS_ASSAULT = auto()


class MobaEventOutcome(Enum):
    NOTHING = auto()
    KILL = auto()
    DEFEND_INHIB = auto()
    DEFEND_TOWER = auto()
    DEFEND_NEXUS = auto()
    TAKE_INHIB = auto()
    TAKE_TOWER = auto()
    TAKE_NEXUS = auto()
