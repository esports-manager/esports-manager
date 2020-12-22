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

from src.core.esports.moba.moba import Moba
from src.resources.utils import load_list_from_json


class MobaEvent:
    def __init__(self,
                 event_id: int = uuid.uuid4(),
                 event_name: str = None,
                 priority: int = 0,
                 points: int = 0,
                 event_time: float = 0.0,
                 commentary=None
                 ):
        if commentary is None:
            self.commentary = []
        self.event_name = event_name
        self.event_id = event_id
        self.priority = priority
        self.commentary = self.load_commentary(commentary)
        self.event_time = event_time
        self.factor = random.gauss(0, 1)
        self.points = points

    def calculate_kill(self, team1, team2):
        pass

    def calculate_baron(self, team1, team2):
        pass

    def calculate_dragon(self, team1, team2):
        pass

    def calculate_tower(self, team1, team2, tower_number):
        pass

    def calculate_inhib(self, team1, team2, which_inhib):
        pass

    def calculate_nexus(self, team1, team2, which_nexus):
        pass

    def calculate_event(self,
                        team1,
                        team2,
                        which_nexus,
                        which_inhib,
                        tower_number
                        ):
        if self.event_name == 'KILL':
            self.calculate_kill(team1, team2)
        if self.event_name == 'BARON':
            self.calculate_baron(team1, team2)
        if self.event_name == 'DRAGON':
            self.calculate_dragon(team1, team2)
        if self.event_name == 'TOWER ASSAULT':
            self.calculate_tower(team1, team2, tower_number)
        if self.event_name == 'INHIB ASSAULT':
            self.calculate_inhib(team1, team2, which_inhib)
        if self.event_name == 'NEXUS ASSAULT':
            self.calculate_nexus(team1, team2, which_nexus)
        print(str(self.event_time) + ' ' + self.event_name)

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
        self.events = load_list_from_json('mobaevents.json')
        self.commentaries = None
        self.event = MobaEvent()
        self.enabled_events = []
        self.event_history = []

    def get_game_state(self, game_time, which_nexus_exposed, inhib_down, towers_number):
        if game_time == 0.0:
            self.get_enabled_events(['NOTHING', 'KILL'])

        if game_time == 15.0:
            self.get_enabled_events(['TOWER ASSAULT'])
        if towers_number == 0:
            self.remove_enabled_event('TOWER ASSAULT')

        self.check_jungle(game_time, 'BARON')
        self.check_jungle(game_time, 'DRAGON')

        if inhib_down:
            self.get_enabled_events(['INHIB ASSAULT'])
        else:
            self.remove_enabled_event('INHIB ASSAULT')

        if which_nexus_exposed is not None:
            self.get_enabled_events(['NEXUS ASSAULT'])
        pass

    def check_jungle(self, game_time, jungle):
        for event in self.events:
            if event['name'] == jungle:
                if self.event.event_name == jungle:
                    if event in self.enabled_events:
                        self.enabled_events.remove(event)
                    event['spawn_time'] += event['cooldown']
                else:
                    if game_time >= event['spawn_time']:
                        if event not in self.enabled_events:
                            self.get_enabled_events([event['name']])

    def remove_enabled_event(self, name):
        for event in self.enabled_events:
            if event['name'] == name:
                self.enabled_events.remove(event)

    def get_enabled_events(self, names):
        for event in self.events:
            for name in names:
                if event['name'] == name:
                    self.enabled_events.append(event)

    def load_commentaries_file(self):
        """
        Load commentaries file
        """
        pass

    def get_event_priorities(self):
        priorities = []
        for event in self.enabled_events:
            priorities.append(event['priority'])

        return priorities

    def generate_event(self, game_time):
        priorities = self.get_event_priorities()
        ev_chosen = random.choices(self.enabled_events, priorities)[0]
        self.event = MobaEvent(event_name=ev_chosen['name'],
                               priority=ev_chosen['priority'],
                               points=ev_chosen['points'],
                               event_time=game_time)
        self.event_history.append(self.event)
