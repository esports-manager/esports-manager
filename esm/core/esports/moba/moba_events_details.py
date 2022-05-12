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

def get_moba_events():
    return [
        {
            "name": "NOTHING",
            "priority": 10,
            "points": 0
        },
        {
            "name": "KILL",
            "priority": 10,
            "points": 10
        },
        {
            "name": "TOWER ASSAULT",
            "priority": 30,
            "points": 15,
            "start_assault": 15.0
        },
        {
            "name": "INHIB ASSAULT",
            "priority": 50,
            "points": 15
        },
        {
            "name": "JUNGLE",
            "jg_name": "HERALD",
            "priority": 25,
            "points": 8,
            "spawn_time": 8.0,
            "cooldown": 6.0,
            "end_time": 19.5
        },
        {
            "name": "JUNGLE",
            "jg_name": "BARON",
            "priority": 50,
            "points": 25,
            "spawn_time": 20.0,
            "cooldown": 6.0,
            "end_time": 0.0
        },
        {
            "name": "JUNGLE",
            "jg_name": "DRAGON",
            "priority": 25,
            "points": 10,
            "spawn_time": 5.0,
            "cooldown": 5.0,
            "end_time": 0.0
        },
        {
            "name": "NEXUS ASSAULT",
            "priority": 80,
            "points": 100
        }
    ]
