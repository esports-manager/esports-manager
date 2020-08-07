class Event:
    def __init__(self,
                 event_id: int,
                 name: str,
                 priority: int,
                 commentaries: list,
                 points: int,
                 conditions: str = None):
        self.event_id = event_id
        self.name = name
        self._priority = priority
        self.commentaries = commentaries
        self._points = points
        self.conditions = conditions

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
