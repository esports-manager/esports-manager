#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
from esm.core.esports.moba.simulation.moba_event_type import MobaEventType

MOBA_EVENT_DEF = {
    MobaEventType.NOTHING: {
        "probability": 50,
        "points": 0.0,
        "start_time": 0.0,
        "cooldown": 0.0,
        "end_time": 0.0,
    },
    MobaEventType.FIGHT: {
        "probability": 20,
        "points": 15.0,
        "start_time": 0.0,
        "cooldown": 0.0,
        "end_time": 0.0,
    },
    MobaEventType.JUNGLE_GRUBS: {
        "probability": 20,
        "points": 5.0,
        "start_time": 6.0,
        "cooldown": 4.0,
        "end_time": 10.0,
    },
    MobaEventType.JUNGLE_HERALD: {
        "probability": 20,
        "points": 5.0,
        "start_time": 5.0,
        "cooldown": 5.0,
        "end_time": 0.0,
    },
    MobaEventType.JUNGLE_DRAKE: {
        "probability": 20,
        "points": 5.0,
        "start_time": 5.0,
        "cooldown": 5.0,
        "end_time": 0.0,
    },
    MobaEventType.JUNGLE_BARON: {
        "probability": 25,
        "points": 15.0,
        "start_time": 25.0,
        "cooldown": 6.0,
        "end_time": 0.0,
    },
    MobaEventType.INHIB_ASSAULT: {
        "probability": 20,
        "points": 10.0,
        "start_time": 0.0,
        "cooldown": 5.0,
        "end_time": 0.0,
    },
    MobaEventType.TOWER_ASSAULT: {
        "probability": 15,
        "points": 15.0,
        "start_time": 10.0,
        "cooldown": 0.0,
        "end_time": 0.0,
    },
    MobaEventType.NEXUS_ASSAULT: {
        "probability": 30,
        "points": 10.0,
        "start_time": 0.0,
        "cooldown": 0.0,
        "end_time": 0.0,
    },
}
