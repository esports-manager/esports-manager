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

    def _tick_objective(
        self,
        objective: MapObjective,
        event_type: MobaEventType,
        event_time: float,
        enforce_end_time: bool = False,
    ):
        event_def = MOBA_EVENT_DEF[event_type]
        start_time = event_def["start_time"]
        end_time = event_def.get("end_time", float("inf"))
        if (
            not objective.alive
            and self.match_time >= start_time
            and (not enforce_end_time or self.match_time < end_time)
        ):
            if objective.respawn_timer > 0.0:
                objective.respawn_timer -= self.match_time - event_time
            else:
                objective.respawn_timer = 0.0
                objective.alive = True

    def tick(self, time: float):
        self.match_time += time

        self.void_grubs.alive = False
        self.baron.alive = False
        self.dragon.alive = False
        self.herald.alive = False

        self._tick_objective(self.void_grubs, MobaEventType.JUNGLE_GRUBS, time, True)
        self._tick_objective(self.herald, MobaEventType.JUNGLE_HERALD, time, True)
        self._tick_objective(self.dragon, MobaEventType.JUNGLE_DRAKE, time)
        self._tick_objective(self.baron, MobaEventType.JUNGLE_BARON, time)

    def is_dragon_alive(self):
        return self.dragon.alive

    def is_baron_alive(self):
        return self.baron.alive

    def is_void_grubs_alive(self):
        return self.void_grubs.alive

    def is_herald_alive(self):
        return self.herald.alive

    def take_drake(self):
        self.dragon.alive = False
        self.dragon.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_DRAKE][
            "cooldown"
        ]

    def take_baron(self):
        self.baron.alive = False
        self.baron.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_BARON][
            "cooldown"
        ]

    def take_void_grubs(self):
        self.void_grubs.alive = False
        self.void_grubs.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_GRUBS][
            "cooldown"
        ]

    def take_herald(self):
        self.herald.alive = False
        self.herald.respawn_timer = MOBA_EVENT_DEF[MobaEventType.JUNGLE_HERALD][
            "cooldown"
        ]
