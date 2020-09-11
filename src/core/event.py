import random


class Event:
    def __init__(self,
                 event_id: int,
                 name: str,
                 priority: int,
                 # commentaries: list,
                 points: int,
                 #  conditions: str = None
                 ):
        self.event_id = event_id
        self.name = name
        self._priority = priority
        # self.commentaries = commentaries
        self._points = points
        # self.conditions = conditions

    @property
    def priority(self):
        return self._priority

    @property
    def points(self):
        return self._points

    @priority.setter
    def priority(self, value):
        self._priority += value

    @points.setter
    def points(self, value):
        self._points = value


class EventHandler:
    def __init__(self):
        self.events = []
        self.eventlog = []
        self.possible = [(0, 'invade'),
                         (1, 'gank'),
                         (1, 'solo_kill'),
                         (1, 'team_fight'),
                         (2, 'tower_assault'),
                         (3, 'jungle_major'),
                         (4, 'inhibitor_assault'),
                         (5, 'nexus_assault'),
                         (5, 'backdoor')
                         ]

    def possible_events(self, number: int):
        for event in self.possible:
            if number in event:
                self.events.append(event)

    def get_events(self, game_time, inhib=False, nexus=0):
        if game_time == 0.0:
            self.possible_events(0)
        elif 0.0 < game_time <= 15.0:
            for event in self.events:
                if 0 in event:
                    self.events.remove(event)

            if not self.events:
                self.possible_events(1)
        elif 15.0 < game_time <= 20.0:
            self.possible_events(2)
        else:
            self.possible_events(3)

        if inhib is not False:
            self.possible_events(4)

        if nexus != 0:
            self.possible_events(5)

    def create_event(self, ev_id, name, priority, points):
        self.eventlog.append(Event(ev_id, name, priority, points))

    def choose_event(self):
        weights = [i[0] for i in self.events]
        return random.choices(self.events, weights=weights, k=1)

    def calculate_event(self):
        pass
