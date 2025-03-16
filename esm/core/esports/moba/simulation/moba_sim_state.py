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
from dataclasses import dataclass, field
from typing import Optional

from esm.core.esports.moba.simulation.moba_event_def import MOBA_EVENT_DEF
from esm.core.esports.moba.simulation.moba_event_type import MobaEventType


@dataclass
class MapObjective:
    name: str
    alive: bool = True
    respawn_timer: float = 0.0


@dataclass
class MobaSimState:
    match_time: float = 0.0
    dragon: MapObjective = field(default_factory=lambda: MapObjective("Dragon", False))
    baron: MapObjective = field(default_factory=lambda: MapObjective("Baron", False))
    void_grubs: MapObjective = field(
        default_factory=lambda: MapObjective("Void Grubs", False)
    )
    herald: MapObjective = field(default_factory=lambda: MapObjective("Herald", False))

    def get_event_types(self) -> list[MobaEventType]:
        events = []
        if self.dragon.alive:
            events.append(MobaEventType.JUNGLE_DRAKE)
        if self.baron.alive:
            events.append(MobaEventType.JUNGLE_BARON)
        if self.herald.alive:
            events.append(MobaEventType.JUNGLE_HERALD)
        if self.void_grubs.alive:
            events.append(MobaEventType.JUNGLE_GRUBS)
        return events

    def tick(self, time: float):
        self.match_time += time

        self.void_grubs.alive = False
        self.baron.alive = False
        self.dragon.alive = False
        self.herald.alive = False

        if (
            not self.void_grubs.alive
            and MOBA_EVENT_DEF[MobaEventType.JUNGLE_GRUBS]["start_time"]
            <= self.match_time
            < MOBA_EVENT_DEF[MobaEventType.JUNGLE_GRUBS]["end_time"]
        ):
            if self.void_grubs.respawn_timer > 0.0:
                self.void_grubs.respawn_timer -= time
            else:
                self.void_grubs.respawn_timer = 0.0
                self.void_grubs.alive = True

        if (
            not self.herald.alive
            and MOBA_EVENT_DEF[MobaEventType.JUNGLE_HERALD]["start_time"]
            <= self.match_time
            < MOBA_EVENT_DEF[MobaEventType.JUNGLE_HERALD]["end_time"]
        ):
            if self.herald.respawn_timer > 0.0:
                self.herald.respawn_timer -= time
            else:
                self.herald.respawn_timer = 0.0
                self.herald.alive = True

        if (
            not self.dragon.alive
            and self.match_time
            >= MOBA_EVENT_DEF[MobaEventType.JUNGLE_DRAKE]["start_time"]
        ):
            if self.dragon.respawn_timer > 0.0:
                self.dragon.respawn_timer -= time
            else:
                self.dragon.respawn_timer = 0.0
                self.dragon.alive = True

        if (
            not self.baron.alive
            and self.match_time
            >= MOBA_EVENT_DEF[MobaEventType.JUNGLE_BARON]["start_time"]
        ):
            if self.baron.respawn_timer > 0.0:
                self.baron.respawn_timer -= time
            else:
                self.baron.respawn_timer = 0.0
                self.baron.alive = True

    def is_dragon_alive(self):
        return self.dragon.alive

    def is_baron_alive(self):
        return self.baron.alive

    def is_void_grubs_alive(self):
        return self.void_grubs.alive

    def is_herald_alive(self):
        return self.herald.alive

    def take_dragon(self):
        self.dragon.alive = False
        self.dragon.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_DRAKE][
            "cooldown"
        ]

    def take_baron(self):
        self.baron.alive = False
        self.dragon.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_BARON][
            "cooldown"
        ]

    def take_void_grubs(self):
        self.void_grubs.alive = False
        self.dragon.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_GRUBS][
            "cooldown"
        ]

    def take_herald(self):
        self.herald.alive = False
        self.dragon.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_HERALD][
            "cooldown"
        ]
