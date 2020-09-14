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


class Event:
    def __init__(self,
                 event_id: int,
                 name: str,
                 priority: int,
                 points: int,
                 ):
        self.event_id = event_id
        self.name = name
        self._priority = priority
        self.commentaries = None
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


class EventHandler:
    def __init__(self):
        self.events = []
        self.eventlog = []
        self.possible = [(0, 'invade', 1, 10),
                         (0, 'nothing', 1, 0),
                         (1, 'lane_farm', 2, 10),
                         (1, 'gank', 1, 10),
                         (1, 'lane_fight', 1, 10),
                         (1, 'team_fight', 1, 15),
                         (2, 'tower_assault', 2, 20),
                         (3, 'jungle_major', 2, 20),
                         (4, 'inhibitor_assault', 3, 25),
                         (5, 'nexus_assault', 4, 50),
                         (5, 'backdoor', 4, 50)
                         ]

    def possible_events(self, number: int):
        for event in self.possible:
            if event[0] == number:
                ev = self.create_event(event[1], event[2], event[3])
                self.events.append(ev)

    def get_events(self, game_time, inhib=False, nexus=0):
        if game_time == 0.0:
            self.possible_events(0)
        elif 0.0 < game_time <= 15.0:
            self.events.clear()
            self.possible_events(1)
        elif 15.0 < game_time <= 20.0:
            self.possible_events(2)
        else:
            self.possible_events(3)

        if inhib is not False:
            self.possible_events(4)

        if nexus != 0:
            self.possible_events(5)

    def create_event(self, name, priority, points):
        ev_id = len(self.eventlog) + 1
        return Event(ev_id, name, priority, points)

    def choose_event(self):
        weights = [event.priority for event in self.events]
        ev = random.choices(self.events, weights=weights, k=1)[0]
        self.eventlog.append(ev)
        return ev

    def calculate_event(self):
        pass
