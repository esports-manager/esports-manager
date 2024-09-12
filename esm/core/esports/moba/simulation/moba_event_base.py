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
from abc import ABC, abstractmethod
from datetime import timedelta
from enum import Enum, auto

from ..mobateam import MobaTeamSimulation
from .moba_event_type import MobaEventType


class MobaEventPriority(Enum):
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()


class MobaEvent(ABC):
    @abstractmethod
    def calculate_event(self):
        pass


class MobaEventBase:
    def __init__(
        self,
        event_type: MobaEventType,
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
        priority: MobaEventPriority,
        event_time: timedelta,
        points: float,
    ):
        self.event_type = event_type
        self.team1 = team1
        self.team2 = team2
        self.priority = priority
        self.event_time = event_time
        self.points = points
