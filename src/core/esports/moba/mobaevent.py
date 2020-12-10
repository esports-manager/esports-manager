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

import random
import uuid
from enum import Enum, auto

from src.core.esports.moba.moba_enums_def import MobaEventType, JungleMonsters


class MobaEvent:
    def __init__(self,
                 event_id: int = uuid.uuid4().int,
                 ev_type: MobaEventType = MobaEventType.NOTHING,
                 priority: int = 0,
                 points: int = 0,
                 commentary: list = []
                 ):
        self.event_id = event_id
        self.ev_type = ev_type
        self._priority = priority
        self.commentary = self.load_commentary(commentary)
        self._points = points

    @property
    def priority(self):
        return self._priority

    @property
    def points(self):
        return self._points

    @priority.setter
    def priority(self, value):
        self._priority = value

    @points.setter
    def points(self, value):
        self._points = value

    def calculate_event(self,
                        players_atk,
                        players_def,
                        which_nexus,
                        which_inhib,
                        which_jg,
                        which_tower):
        atk_n = len(players_atk)
        def_n = len(players_def)

        if atk_n > 1:
            atk_n = random.randrange(1, atk_n)

        if def_n > 1:
            def_n = random.randrange(1, def_n)

        if self.ev_type == MobaEventType.NEXUS_ASSAULT:
            pass
        elif self.ev_type == MobaEventType.INHIB_ASSAULT:
            pass
        elif self.ev_type == MobaEventType.TOWER_ASSAULT:
            pass
        elif self.ev_type == MobaEventType.JG_MAJOR:
            pass
        else:
            pass

    def load_commentary(self, commentaries):
        """
        Chooses commentary based on a list of commentaries.

        For now this is a dummy implementation that does nothing, but it will load commentaries depending
        on the locale.
        """
        pass


class MobaEventHandler:
    def __init__(self):
        """
        Initializes the event handler.
        """
        self.events = []
        self.commentaries = None
        self.event = None
        self.event_history = []

    def get_game_state(self, game_time, which_nexus_exposed, inhib_down, major_jungle_av):
        if game_time <= 15.0:
            pass
        pass

    def load_commentaries_file(self):
        """
        Load commentaries file
        """
        pass

    def set_event(self, ev_type, priority, points):
        """
        Creates the event, adding it to the Event Log.

        :param ev_type:
        :param priority:
        :param points:
        :return:
        """
        self.event = MobaEvent(ev_type=ev_type, priority=priority, points=points)

    def generate_event(self):
        # weights = [event.priority for event in self.events]
        # ev = random.choices(self.events, weights=weights, k=1)[0]
        # self.eventlog.append(ev)
        # return ev
        pass