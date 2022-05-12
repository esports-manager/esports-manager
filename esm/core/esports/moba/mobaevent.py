#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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

import logging
import random
from queue import Queue

from esm.core.esports.moba.moba_events_details import get_moba_events
from esm.core.esports.moba.events import *


logger = logging.getLogger(__name__)


class EventFactory:
    def generate_event(self, event_chosen: dict, game_time: float, show_commentary: bool, queue: Queue) -> MobaEvent:
        name = event_chosen["name"]
        if name == "NOTHING":
            return NothingEvent.get_from_dict(event_chosen, game_time, show_commentary, queue)
        elif name in ["BARON", "DRAGON", "HERALD"]:
            return JungleEvent.get_from_dict(event_chosen, game_time, show_commentary, queue)
        elif name == "INHIB ASSAULT":
            return InhibEvent.get_from_dict(event_chosen, game_time, show_commentary, queue)
        elif name == "TOWER ASSAULT":
            return TowerEvent.get_from_dict(event_chosen, game_time, show_commentary, queue)
        elif name == "KILL":
            return KillEvent.get_from_dict(event_chosen, game_time, show_commentary, queue)
        elif name == "NEXUS ASSAULT":
            return NexusEvent.get_from_dict(event_chosen, game_time, show_commentary, queue)


class MobaEventHandler:
    def __init__(self, show_commentary: bool = False, queue: Queue = None):
        """
        Initializes the event handler.
        """
        self.events = get_moba_events()
        self.commentaries = None
        self.event = None
        self.event_factory = EventFactory()
        self.enabled_events = []
        self.event_history = []
        self.show_commentary = show_commentary
        self.queue = queue if self.show_commentary else None

    def get_game_state(
            self, game_time, which_nexus_exposed, is_any_inhib_open, towers_number
    ) -> None:
        if game_time == 0.0:
            self.get_enabled_events(["NOTHING", "KILL"])

        if game_time >= 10.0:
            self.get_enabled_events(["TOWER ASSAULT"])
        if towers_number == 0:
            self.remove_enabled_event("TOWER ASSAULT")

        if self.event is not None:
            self.check_jungle(game_time)

        # TODO: We need to add a Inhibitor Spawn time
        if is_any_inhib_open:
            self.get_enabled_events(["INHIB ASSAULT"])
        else:
            self.remove_enabled_event("INHIB ASSAULT")

        if which_nexus_exposed is not None:
            self.get_enabled_events(["NEXUS ASSAULT"])

    def check_jungle(self, game_time: float) -> None:
        """
        Checks if the jungle event is available
        """
        jungle_events = ["BARON", "DRAGON", "HERALD"]
        jungle_names = [event for event in self.events if event["name"] in jungle_events]

        for event in jungle_names:
            if self.event.event_name == event["name"]:
                if event in self.enabled_events:
                    self.enabled_events.remove(event)
                event["spawn_time"] += event["cooldown"]
            elif (
                    game_time >= event["spawn_time"]
                    and event not in self.enabled_events
            ):
                self.enabled_events.append(event)
            if 0.0 < event["end_time"] <= game_time and event in self.enabled_events:
                self.enabled_events.remove(event)

    def remove_enabled_event(self, name):
        """
        Removes no longer available event from the list of enabled events
        """
        for event in self.enabled_events:
            if event["name"] == name:
                self.enabled_events.remove(event)

    def get_enabled_events(self, names):
        """
        Adds events to the list of enabled events
        """
        for event in self.events:
            for name in names:
                if event["name"] == name and event not in self.enabled_events:
                    self.enabled_events.append(event)

    def load_commentaries_file(self):
        """
        Load commentaries file
        """
        pass

    def get_event_priorities(self):
        """
        Gets the priority of events
        """
        return [event["priority"] for event in self.enabled_events]

    def generate_event(self, game_time: float):
        """
        Generates events for the match based on their priorities and available events.
        """
        priorities = self.get_event_priorities()
        ev_chosen = random.choices(self.enabled_events, priorities)[0]
        self.event = self.event_factory.generate_event(ev_chosen, game_time, self.show_commentary, self.queue)
        self.event_history.append(self.event)
