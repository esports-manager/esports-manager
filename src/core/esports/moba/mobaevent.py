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

from src.core.esports.moba.moba_enums_def import MobaEventType
from src.core.esports.moba.moba import Moba


class MobaEvent:
    def __init__(self,
                 ev_type: MobaEventType = MobaEventType.NOTHING,
                 event_id: int = uuid.uuid4(),
                 priority: int = 0,
                 points: int = 0,
                 event_time: float = 0.0,
                 commentary: list = []
                 ):
        self.moba = Moba()
        self.event_id = event_id
        self.ev_type = ev_type
        self._priority = priority
        self.commentary = self.load_commentary(commentary)
        self.event_time = event_time
        self._points = points

    @property
    def priority(self):
        if self.ev_type == MobaEventType.NOTHING:
            self._priority = 1
        elif self.ev_type == MobaEventType.JG_DRAGON:
            for jg in self.moba.major_jg:
                if jg['name'] == 'Dragon':
                    self._priority = jg['priority']
        elif self.ev_type == MobaEventType.JG_BARON:
            for jg in self.moba.major_jg:
                if jg['name'] == 'Baron':
                    self._priority = jg['priority']
        elif self.ev_type == MobaEventType.TOWER_ASSAULT:
            self._priority = 7
        elif self.ev_type == MobaEventType.GANK:
            self._priority = 3
        elif self.ev_type == MobaEventType.LANE_FIGHT:
            self._priority = 3
        elif self.ev_type == MobaEventType.TEAM_FIGHT:
            self._priority = 4
        elif self.ev_type == MobaEventType.INHIB_ASSAULT:
            self._priority = 9
        elif self.ev_type == MobaEventType.LANE_FARM:
            self._priority = 4
        elif self.ev_type == MobaEventType.NEXUS_ASSAULT:
            self._priority = 10

        return self._priority

    @property
    def points(self):
        if self.ev_type == MobaEventType.NOTHING:
            self._points = 0
        elif self.ev_type == MobaEventType.JG_DRAGON:
            self._points = 50
        elif self.ev_type == MobaEventType.JG_BARON:
            self._points = 100
        elif self.ev_type == MobaEventType.TOWER_ASSAULT:
            self._points = 10
        elif self.ev_type == MobaEventType.GANK:
            self._points = 5
        elif self.ev_type == MobaEventType.LANE_FIGHT:
            self._points = 8
        elif self.ev_type == MobaEventType.TEAM_FIGHT:
            self._points = 10
        elif self.ev_type == MobaEventType.INHIB_ASSAULT:
            self._points = 20
        elif self.ev_type == MobaEventType.LANE_FARM:
            self._points = 4

        return self._points

    @priority.setter
    def priority(self, value):
        self._priority = value

    @points.setter
    def points(self, value):
        self._points = value

    def calculate_event(self
                        # players_atk,
                        # players_def,
                        # which_nexus,
                        # which_inhib,
                        # which_jg,
                        # which_tower
                        ):
        # atk_n = len(players_atk)
        # def_n = len(players_def)
        # random_factor = random.random()
        #
        # if atk_n > 1:
        #     atk_n = random.randrange(1, atk_n)
        #
        # if def_n > 1:
        #     def_n = random.randrange(1, def_n)

        if self.ev_type == MobaEventType.NEXUS_ASSAULT:
            pass
        elif self.ev_type == MobaEventType.INHIB_ASSAULT:
            pass
        elif self.ev_type == MobaEventType.TOWER_ASSAULT:
            pass
        elif self.ev_type == MobaEventType.JG_BARON:
            pass
        elif self.ev_type == MobaEventType.JG_DRAGON:
            pass
        elif self.ev_type == MobaEventType.LANE_FARM:
            pass
        elif self.ev_type == MobaEventType.TEAM_FIGHT:
            pass
        elif self.ev_type == MobaEventType.GANK:
            pass
        elif self.ev_type == MobaEventType.LANE_FIGHT:
            pass

        print(self.ev_type.name)

    def load_commentary(self, commentaries):
        """
        Chooses commentary based on a list of commentaries.

        For now this is a dummy implementation that does nothing, but it will load commentaries depending
        on the locale.
        """
        return 'Nothing to see here'


class MobaEventHandler:
    def __init__(self):
        """
        Initializes the event handler.
        """
        self.moba = Moba()
        self.events = []
        self.commentaries = None
        self.event = MobaEvent()
        self.enabled_events = [MobaEventType.NOTHING]
        self.event_history = []

    def check_major_jg(self, jg_name):
        """
        Checks if a jungle monster is up
        """
        if self.event.ev_type == MobaEventType.JG_BARON:
            for jg in self.moba.major_jg:
                if jg['name'] == jg_name:
                    jg['spawn_time'] += jg['cooldown']
                    break
        else:
            for jg in self.moba.major_jg:
                if jg['name'] == jg_name:
                    if self.event.event_time >= jg['spawn_time']:
                        return True

        return False

    def get_game_state(self, game_time, which_nexus_exposed, inhib_down, towers_number):
        # Check if towers can already be assaulted
        if game_time >= self.moba.tower_time:
            self.enabled_events.append(MobaEventType.TOWER_ASSAULT)

        # Check if there is any tower up
        if towers_number == 0:
            self.enabled_events.remove(MobaEventType.TOWER_ASSAULT)

        # Check if Baron is up
        if self.check_major_jg('Baron'):
            self.enabled_events.append(MobaEventType.JG_BARON)
        else:
            if MobaEventType.JG_BARON in self.enabled_events:
                self.enabled_events.remove(MobaEventType.JG_BARON)

        # Check if Dragon is up
        if self.check_major_jg('Dragon'):
            self.enabled_events.append(MobaEventType.JG_DRAGON)
        else:
            if MobaEventType.JG_BARON in self.enabled_events:
                self.enabled_events.remove(MobaEventType.JG_DRAGON)

        # Check if an inhib is down
        if inhib_down:
            self.enabled_events.append(MobaEventType.INHIB_ASSAULT)
        else:
            if MobaEventType.INHIB_ASSAULT in self.enabled_events:
                self.enabled_events.remove(MobaEventType.INHIB_ASSAULT)

        # Check if a nexus is exposed
        if which_nexus_exposed is not None:
            self.enabled_events.append(MobaEventType.NEXUS_ASSAULT)

    def load_commentaries_file(self):
        """
        Load commentaries file
        """
        pass

    def generate_event(self, game_time):
        self.events = [MobaEvent(ev_type=ev_type, event_time=game_time) for ev_type in self.enabled_events]
        priorities = [event.priority for event in self.events]
        self.event = random.choices(self.events, priorities)[0]
        self.event_history.append(self.event)
